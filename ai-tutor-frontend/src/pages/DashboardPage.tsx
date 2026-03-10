import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getDashboard } from '../api/users';
import type { DashboardData, RecentActivityItem } from '../api/users';
import { Navbar } from '../components/Layout/Navbar';
import { KnowledgeRadar } from '../components/Dashboard/KnowledgeRadar';

// ── Helpers ────────────────────────────────────────────────────────────────

const LEVEL_COLOR: Record<string, string> = {
  beginner: '#6ee7b7',
  intermediate: '#fbbf24',
  advanced: '#f87171',
};

const STATUS_COLOR: Record<string, string> = {
  accepted: 'var(--success)',
  wrong_answer: 'var(--danger)',
  time_limit: 'var(--warning)',
  runtime_error: 'var(--danger)',
  compile_error: 'var(--danger)',
  pending: 'var(--text-muted)',
};

const STATUS_LABEL: Record<string, string> = {
  accepted: '✓ Accepted',
  wrong_answer: '✗ Wrong Answer',
  time_limit: '⏱ Time Limit',
  runtime_error: '💥 Runtime Error',
  compile_error: '⚠ Compile Error',
  pending: '… Pending',
};

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

// ── Stat card ─────────────────────────────────────────────────────────────

interface StatCardProps {
  label: string;
  value: string | number;
  icon: string;
  accent?: boolean;
}

function StatCard({ label, value, icon, accent }: StatCardProps) {
  return (
    <div
      style={{
        background: 'var(--bg-secondary)',
        border: `1px solid ${accent ? 'var(--accent)' : 'var(--border-color)'}`,
        borderRadius: '10px',
        padding: '1rem 1.25rem',
        flex: 1,
        minWidth: '120px',
      }}
    >
      <div style={{ fontSize: '1.3rem', marginBottom: '0.25rem' }}>{icon}</div>
      <div
        style={{
          fontSize: '1.6rem',
          fontWeight: 700,
          color: accent ? 'var(--accent)' : 'var(--text-primary)',
          lineHeight: 1.1,
        }}
      >
        {value}
      </div>
      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
        {label}
      </div>
    </div>
  );
}

// ── Recent activity row ────────────────────────────────────────────────────

function ActivityRow({ item }: { item: RecentActivityItem }) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0.6rem 0',
        borderBottom: '1px solid var(--border-color)',
      }}
    >
      <div>
        <span style={{ color: 'var(--text-primary)', fontSize: '0.88rem' }}>
          {item.problem_title}
        </span>
        <span
          style={{
            marginLeft: '8px',
            background: 'var(--bg-tertiary)',
            borderRadius: '4px',
            padding: '1px 6px',
            fontSize: '0.72rem',
            color: 'var(--text-muted)',
          }}
        >
          {item.language}
        </span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <span
          style={{
            fontSize: '0.8rem',
            color: STATUS_COLOR[item.status] ?? 'var(--text-muted)',
            fontWeight: 500,
          }}
        >
          {STATUS_LABEL[item.status] ?? item.status}
        </span>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          {timeAgo(item.submitted_at)}
        </span>
      </div>
    </div>
  );
}

// ── Topic chip ────────────────────────────────────────────────────────────

function TopicChip({ label, variant }: { label: string; variant: 'weak' | 'strong' }) {
  return (
    <span
      style={{
        background: variant === 'weak' ? 'rgba(248,113,113,0.12)' : 'rgba(110,231,183,0.12)',
        border: `1px solid ${variant === 'weak' ? 'rgba(248,113,113,0.3)' : 'rgba(110,231,183,0.3)'}`,
        color: variant === 'weak' ? '#f87171' : '#6ee7b7',
        borderRadius: '20px',
        padding: '3px 10px',
        fontSize: '0.78rem',
        fontWeight: 500,
      }}
    >
      {label}
    </span>
  );
}

// ── Section card wrapper ───────────────────────────────────────────────────

function Card({ title, children, style }: { title: string; children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <div
      style={{
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border-color)',
        borderRadius: '10px',
        padding: '1.25rem',
        ...style,
      }}
    >
      <h3
        style={{
          margin: '0 0 1rem',
          fontSize: '0.85rem',
          fontWeight: 600,
          color: 'var(--text-muted)',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
        }}
      >
        {title}
      </h3>
      {children}
    </div>
  );
}

// ── Main page ──────────────────────────────────────────────────────────────

export function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDashboard()
      .then(setData)
      .catch(() => setError('Failed to load dashboard'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />

      <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '2rem 1.5rem' }}>

        {/* Loading */}
        {loading && (
          <p style={{ color: 'var(--text-muted)' }}>Loading dashboard…</p>
        )}

        {/* Error */}
        {error && (
          <p style={{ color: 'var(--danger)' }}>{error}</p>
        )}

        {data && (
          <>
            {/* ── Hero ──────────────────────────────────────────────────── */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1.25rem',
                marginBottom: '2rem',
              }}
            >
              {/* Avatar */}
              <div
                style={{
                  width: '56px',
                  height: '56px',
                  borderRadius: '50%',
                  background: 'var(--accent)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.4rem',
                  fontWeight: 700,
                  color: '#fff',
                  flexShrink: 0,
                  overflow: 'hidden',
                }}
              >
                {data.user.avatar_url ? (
                  <img
                    src={data.user.avatar_url}
                    alt={data.user.display_name}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                ) : (
                  data.user.display_name.charAt(0).toUpperCase()
                )}
              </div>

              <div>
                <h1 style={{ margin: '0 0 0.2rem', fontSize: '1.4rem', color: 'var(--text-primary)' }}>
                  {data.user.display_name}
                </h1>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    @{data.user.username}
                  </span>
                  <span
                    style={{
                      background: LEVEL_COLOR[data.knowledge_profile.overall_level] + '22',
                      border: `1px solid ${LEVEL_COLOR[data.knowledge_profile.overall_level]}44`,
                      color: LEVEL_COLOR[data.knowledge_profile.overall_level],
                      borderRadius: '20px',
                      padding: '2px 10px',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      textTransform: 'capitalize',
                    }}
                  >
                    {data.knowledge_profile.overall_level}
                  </span>
                </div>
              </div>

              <Link
                to="/problems"
                style={{
                  marginLeft: 'auto',
                  background: 'var(--accent)',
                  color: '#fff',
                  padding: '8px 18px',
                  borderRadius: '8px',
                  fontSize: '0.88rem',
                  fontWeight: 600,
                  textDecoration: 'none',
                }}
              >
                Solve Problems →
              </Link>
            </div>

            {/* ── Stats row ─────────────────────────────────────────────── */}
            <div
              style={{
                display: 'flex',
                gap: '0.75rem',
                marginBottom: '1.5rem',
                flexWrap: 'wrap',
              }}
            >
              <StatCard icon="✅" label="Solved" value={data.stats.problems_solved} accent />
              <StatCard icon="🎯" label="Attempted" value={data.stats.problems_attempted} />
              <StatCard
                icon="📈"
                label="Acceptance"
                value={`${data.stats.acceptance_rate}%`}
              />
              <StatCard icon="🔥" label="Day Streak" value={data.stats.streak_days} />
              <StatCard icon="💡" label="Hints Used" value={data.stats.hints_used} />
            </div>

            {/* ── Middle: Radar + Recent Activity ───────────────────────── */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '1rem',
                marginBottom: '1rem',
              }}
            >
              <Card title="Topic Proficiency">
                <KnowledgeRadar profile={data.knowledge_profile} />
              </Card>

              <Card title="Recent Activity">
                {data.recent_activity.length === 0 ? (
                  <div
                    style={{
                      height: '200px',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'var(--text-muted)',
                      gap: '0.5rem',
                    }}
                  >
                    <div style={{ fontSize: '2rem' }}>📝</div>
                    <p style={{ margin: 0, fontSize: '0.85rem' }}>No submissions yet</p>
                  </div>
                ) : (
                  <div>
                    {data.recent_activity.map((item) => (
                      <ActivityRow key={item.submission_id} item={item} />
                    ))}
                  </div>
                )}
              </Card>
            </div>

            {/* ── Bottom: Weakest / Strongest topics ────────────────────── */}
            {(data.knowledge_profile.weakest_topics.length > 0 ||
              data.knowledge_profile.strongest_topics.length > 0) && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <Card title="Needs Practice">
                  {data.knowledge_profile.weakest_topics.length === 0 ? (
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0 }}>
                      All topics looking good!
                    </p>
                  ) : (
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                      {data.knowledge_profile.weakest_topics.map((t) => (
                        <TopicChip key={t} label={t} variant="weak" />
                      ))}
                    </div>
                  )}
                </Card>

                <Card title="Strongest Topics">
                  {data.knowledge_profile.strongest_topics.length === 0 ? (
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0 }}>
                      Keep solving to find your strengths!
                    </p>
                  ) : (
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                      {data.knowledge_profile.strongest_topics.map((t) => (
                        <TopicChip key={t} label={t} variant="strong" />
                      ))}
                    </div>
                  )}
                </Card>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
