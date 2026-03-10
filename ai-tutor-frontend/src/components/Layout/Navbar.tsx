import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const NAV_LINKS = [
  { to: '/problems', label: 'Problems' },
  { to: '/dashboard', label: 'Dashboard' },
];

export function Navbar() {
  const { user, logout } = useAuth();
  const { pathname } = useLocation();

  return (
    <nav
      style={{
        background: 'var(--bg-secondary)',
        borderBottom: '1px solid var(--border-color)',
        padding: '0 1.5rem',
        height: '52px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}
    >
      {/* Logo */}
      <Link
        to="/problems"
        style={{ color: 'var(--text-primary)', fontWeight: 600, fontSize: '1.1rem', textDecoration: 'none' }}
      >
        🧑‍🏫 CodeTutor
      </Link>

      {/* Nav links — only shown when logged in */}
      {user && (
        <div style={{ display: 'flex', gap: '0.25rem' }}>
          {NAV_LINKS.map(({ to, label }) => {
            const active = pathname === to || pathname.startsWith(to + '/');
            return (
              <Link
                key={to}
                to={to}
                style={{
                  padding: '5px 14px',
                  borderRadius: '6px',
                  fontSize: '0.88rem',
                  fontWeight: active ? 600 : 400,
                  color: active ? 'var(--accent)' : 'var(--text-muted)',
                  background: active ? 'rgba(99,102,241,0.1)' : 'transparent',
                  textDecoration: 'none',
                  transition: 'background 0.15s, color 0.15s',
                }}
              >
                {label}
              </Link>
            );
          })}
        </div>
      )}

      {/* Right side: name + logout */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {user && (
          <>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
              {user.display_name}
            </span>
            <button
              onClick={logout}
              style={{
                background: 'transparent',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                color: 'var(--text-muted)',
                padding: '4px 12px',
                fontSize: '0.85rem',
                cursor: 'pointer',
              }}
            >
              Logout
            </button>
          </>
        )}
      </div>
    </nav>
  );
}
