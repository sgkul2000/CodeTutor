import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { ProblemListPage } from './pages/ProblemListPage';
import { ProblemSolvePage } from './pages/ProblemSolvePage';
import { OAuthCallbackPage } from './pages/OAuthCallbackPage';
import { DashboardPage } from './pages/DashboardPage';
import { useAppStore } from './stores/appStore';

function RequireAuth({ children }: { children: React.ReactNode }) {
  const token = useAppStore((s) => s.authToken);
  return token ? <>{children}</> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        {/* OAuth callback — backend redirects here after code exchange */}
        <Route path="/auth/callback/:provider" element={<OAuthCallbackPage />} />

        <Route
          path="/problems"
          element={
            <RequireAuth>
              <ProblemListPage />
            </RequireAuth>
          }
        />
        <Route
          path="/problems/:slug"
          element={
            <RequireAuth>
              <ProblemSolvePage />
            </RequireAuth>
          }
        />
        <Route
          path="/dashboard"
          element={
            <RequireAuth>
              <DashboardPage />
            </RequireAuth>
          }
        />
        <Route path="*" element={<Navigate to="/problems" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
