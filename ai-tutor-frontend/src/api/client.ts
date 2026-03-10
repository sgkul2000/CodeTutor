import axios, { type InternalAxiosRequestConfig } from 'axios';
import { useAppStore } from '../stores/appStore';

const apiClient = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// ── Request interceptor — attach current access token ────────────────────────

apiClient.interceptors.request.use((config) => {
  const token = useAppStore.getState().authToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Response interceptor — silent token refresh on 401 ───────────────────────
//
// Pattern: "retry queue"
//   - First 401 triggers a single POST /auth/refresh call.
//   - Any other requests that 401 while the refresh is in-flight are queued.
//   - On refresh success: all queued requests are replayed with the new token.
//   - On refresh failure: auth is cleared and user is sent to /login.

type QueueEntry = {
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
};

let isRefreshing = false;
let pendingQueue: QueueEntry[] = [];

function drainQueue(err: unknown, token: string | null) {
  pendingQueue.forEach(({ resolve, reject }) =>
    err ? reject(err) : resolve(token as string)
  );
  pendingQueue = [];
}

// A minimal bare axios instance used exclusively for the refresh call so it
// doesn't go through apiClient's interceptors (which would cause a loop).
const refreshClient = axios.create({ baseURL: '/api' });

apiClient.interceptors.response.use(
  (res) => res,
  async (error) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Only attempt refresh for 401 errors that haven't already been retried.
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    // If a refresh is already in-flight, queue this request and wait.
    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        pendingQueue.push({ resolve, reject });
      }).then((newToken) => {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const { refreshToken } = useAppStore.getState();

      // Send refresh token as Bearer header (dev login) or rely on the
      // HTTP-only cookie the backend set during OAuth (browser includes it
      // automatically on same-origin requests via Vite proxy).
      const refreshHeaders: Record<string, string> = {};
      if (refreshToken) {
        refreshHeaders.Authorization = `Bearer ${refreshToken}`;
      }

      const { data } = await refreshClient.post('/auth/refresh', null, {
        headers: refreshHeaders,
      });

      const newAccessToken: string = data.access_token;
      useAppStore.getState().setAuthToken(newAccessToken);

      drainQueue(null, newAccessToken);

      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      return apiClient(originalRequest);
    } catch (refreshError) {
      drainQueue(refreshError, null);
      useAppStore.getState().clearAuth();
      window.location.href = '/login';
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

export default apiClient;
