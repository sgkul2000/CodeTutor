import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../stores/appStore';
import client from '../api/client';
import type { User } from '../types';

export function useAuth() {
  const { authToken, currentUser, setAuth, clearAuth } = useAppStore();
  const navigate = useNavigate();

  const devLogin = useCallback(async () => {
    const { data } = await client.get('/auth/dev-login');
    // Store the refresh token so the silent-refresh interceptor can use it.
    setAuth(data.access_token, data.user as User, data.refresh_token);
    navigate('/problems');
  }, [setAuth, navigate]);

  const logout = useCallback(() => {
    clearAuth();
    navigate('/login');
  }, [clearAuth, navigate]);

  return {
    isAuthenticated: !!authToken,
    user: currentUser,
    devLogin,
    logout,
  };
}
