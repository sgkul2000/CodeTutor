/**
 * OAuthCallbackPage
 *
 * The backend redirects here after completing the OAuth code-exchange:
 *   GET /auth/callback/:provider?access_token=<jwt>
 *
 * This page:
 *  1. Reads the access_token from the URL search params
 *  2. Fetches the current user profile from /api/auth/me
 *  3. Persists the token + user into Zustand (and localStorage via persist middleware)
 *  4. Redirects to /problems
 *
 * On any error it clears auth state and redirects to /login with an error message.
 */
import { useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAppStore } from '../stores/appStore';
import type { User } from '../types';

const BACKEND_BASE = import.meta.env.VITE_BACKEND_URL ?? 'http://localhost:8000';

export function OAuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setAuth, clearAuth } = useAppStore();
  const handled = useRef(false); // prevent double-run in React StrictMode

  useEffect(() => {
    if (handled.current) return;
    handled.current = true;

    const token = searchParams.get('access_token');

    if (!token) {
      clearAuth();
      navigate('/login?error=oauth_failed', { replace: true });
      return;
    }

    // Fetch the user profile using the new token
    fetch(`${BACKEND_BASE}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(`Profile fetch failed: ${res.status}`);
        return res.json() as Promise<User>;
      })
      .then((user) => {
        setAuth(token, user);
        navigate('/problems', { replace: true });
      })
      .catch(() => {
        clearAuth();
        navigate('/login?error=profile_fetch_failed', { replace: true });
      });
  }, [searchParams, navigate, setAuth, clearAuth]);

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--bg-primary)',
        gap: '1rem',
      }}
    >
      {/* Simple spinner */}
      <div
        style={{
          width: '40px',
          height: '40px',
          borderRadius: '50%',
          border: '3px solid var(--border-color)',
          borderTopColor: 'var(--accent)',
          animation: 'spin 0.8s linear infinite',
        }}
      />
      <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
        Signing you in…
      </p>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
