from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.models.user import User
from app.services.auth_service import (
    create_access_token,
    create_refresh_token,
    ALGORITHM,
)
from jose import JWTError, jwt

router = APIRouter()
security = HTTPBearer()

DEV_USER_EMAIL = "dev@codetutor.local"
DEV_USER_USERNAME = "devuser"

SUPPORTED_PROVIDERS = ("google", "github")


# ── Dev login (development only) ─────────────────────────────────────────────

@router.get("/dev-login")
async def dev_login():
    """Dev-only: returns a JWT for a hardcoded admin user. Disabled in production."""
    if not settings.is_development:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    user = await User.find_one(User.email == DEV_USER_EMAIL)
    if not user:
        user = User(
            email=DEV_USER_EMAIL,
            username=DEV_USER_USERNAME,
            display_name="Dev User",
            oauth_provider="dev",
            oauth_id="dev-0001",
            is_admin=True,
        )
        await user.insert()

    return {
        "access_token": create_access_token(str(user.id)),
        "refresh_token": create_refresh_token(str(user.id)),
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "display_name": user.display_name,
            "is_admin": user.is_admin,
        },
    }


# ── OAuth 2.0 (Google + GitHub) ───────────────────────────────────────────────

@router.get("/{provider}")
async def oauth_redirect(provider: str, request: Request):
    """Redirect the browser to the OAuth provider's consent screen."""
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

    if not settings.google_client_id and provider == "google":
        raise HTTPException(status_code=501, detail="Google OAuth not configured")
    if not settings.github_client_id and provider == "github":
        raise HTTPException(status_code=501, detail="GitHub OAuth not configured")

    from app.services.auth_service import get_oauth_client
    oauth = get_oauth_client()
    client = getattr(oauth, provider)
    # Redirect URI must point to THIS backend's callback endpoint so we can
    # exchange the code for a token server-side before handing off to frontend.
    redirect_uri = f"{settings.backend_url}/api/auth/{provider}/callback"
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/{provider}/callback")
async def oauth_callback(provider: str, request: Request, response: Response):
    """
    Handle the OAuth callback:
    1. Exchange the authorization code for a provider access token
    2. Fetch the user's profile from the provider
    3. Upsert the user in MongoDB
    4. Issue our own JWT access + refresh tokens
    5. Redirect to the frontend with the access token as a URL param
       and the refresh token as an HTTP-only cookie
    """
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

    from app.services.auth_service import get_oauth_client
    oauth = get_oauth_client()
    client = getattr(oauth, provider)

    try:
        token = await client.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {e}")

    # Fetch user profile from provider
    profile = await _fetch_profile(provider, token, client)

    # Upsert user
    user = await User.find_one(
        User.oauth_provider == provider,
        User.oauth_id == profile["oauth_id"],
    )
    if not user:
        # Also check by email (account merge)
        user = await User.find_one(User.email == profile["email"])

    if user:
        user.display_name = profile["display_name"]
        user.avatar_url = profile.get("avatar_url")
        if not user.oauth_id:
            user.oauth_provider = provider
            user.oauth_id = profile["oauth_id"]
        await user.save()
    else:
        user = User(
            email=profile["email"],
            username=profile["username"],
            display_name=profile["display_name"],
            avatar_url=profile.get("avatar_url"),
            oauth_provider=provider,
            oauth_id=profile["oauth_id"],
        )
        await user.insert()

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    # Redirect to frontend OAuthCallbackPage with token in URL fragment
    redirect_url = (
        f"{settings.frontend_url}/auth/callback/{provider}"
        f"?access_token={access_token}"
    )
    resp = RedirectResponse(url=redirect_url)
    resp.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.is_development,
        samesite="lax",
        max_age=settings.jwt_refresh_token_expire_days * 86400,
    )
    return resp


async def _fetch_profile(provider: str, token: dict, client) -> dict:
    """Normalise provider-specific profile responses into a common dict."""
    if provider == "google":
        user_info = token.get("userinfo") or {}
        if not user_info:
            resp = await client.get("https://openidconnect.googleapis.com/v1/userinfo",
                                    token=token)
            user_info = resp.json()
        return {
            "oauth_id": str(user_info["sub"]),
            "email": user_info["email"],
            "display_name": user_info.get("name", user_info["email"].split("@")[0]),
            "username": user_info["email"].split("@")[0],
            "avatar_url": user_info.get("picture"),
        }

    if provider == "github":
        import httpx
        headers = {"Authorization": f"token {token['access_token']}",
                   "Accept": "application/json"}
        async with httpx.AsyncClient() as http:
            profile_resp = await http.get("https://api.github.com/user", headers=headers)
            profile = profile_resp.json()
            # Email may be null on GitHub if user keeps it private — fetch separately
            email = profile.get("email")
            if not email:
                emails_resp = await http.get("https://api.github.com/user/emails",
                                             headers=headers)
                emails = emails_resp.json()
                primary = next((e for e in emails if e.get("primary")), None)
                email = primary["email"] if primary else f"{profile['login']}@users.noreply.github.com"

        return {
            "oauth_id": str(profile["id"]),
            "email": email,
            "display_name": profile.get("name") or profile["login"],
            "username": profile["login"],
            "avatar_url": profile.get("avatar_url"),
        }

    raise ValueError(f"Unknown provider: {provider}")


# ── Token management ──────────────────────────────────────────────────────────

@router.post("/refresh")
async def refresh_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    refresh_token_cookie: Optional[str] = Cookie(None, alias="refresh_token"),
):
    """Exchange a valid refresh token for a new access token.

    Accepts the token from either:
    - ``Authorization: Bearer <token>`` header  (dev login — token stored client-side)
    - ``refresh_token`` HTTP-only cookie        (OAuth login — set by the callback handler)
    """
    token = (credentials.credentials if credentials else None) or refresh_token_cookie

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "refresh":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await User.get(user_id)
    if not user:
        raise credentials_exception

    return {"access_token": create_access_token(str(user.id)), "token_type": "bearer"}


@router.get("/me")
async def get_me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Return the current authenticated user's profile."""
    from app.services.auth_service import get_current_user
    user = await get_current_user(credentials)
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "is_admin": user.is_admin,
        "preferences": user.preferences.model_dump(),
        "stats": user.stats.model_dump(),
    }
