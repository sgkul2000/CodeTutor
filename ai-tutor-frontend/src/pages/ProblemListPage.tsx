import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProblems } from '../api/problems';
import { Navbar } from '../components/Layout/Navbar';
import type { ProblemSummary, Difficulty } from '../types';

const DIFFICULTY_COLOR: Record<Difficulty, string> = {
  easy: 'var(--success)',
  medium: 'var(--warning)',
  hard: 'var(--danger)',
};

const ALL_CATEGORIES = [
  'array', 'hash-map', 'linked-list', 'stack-queue', 'tree', 'graph',
  'dynamic-programming', 'binary-search', 'sliding-window', 'sorting', 'string', 'greedy',
];

export function ProblemListPage() {
  const [problems, setProblems] = useState<ProblemSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [diffFilter, setDiffFilter] = useState('');
  const [catFilter, setCatFilter] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    getProblems({ difficulty: diffFilter || undefined, category: catFilter || undefined })
      .then(setProblems)
      .finally(() => setLoading(false));
  }, [diffFilter, catFilter]);

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />

      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '2rem 1.5rem' }}>
        <h2 style={{ margin: '0 0 1.5rem', color: 'var(--text-primary)' }}>Problems</h2>

        {/* Filters */}
        <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem' }}>
          <select
            value={diffFilter}
            onChange={(e) => setDiffFilter(e.target.value)}
            style={{
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              color: 'var(--text-primary)',
              padding: '6px 12px',
              fontSize: '0.85rem',
            }}
          >
            <option value="">All difficulties</option>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>

          <select
            value={catFilter}
            onChange={(e) => setCatFilter(e.target.value)}
            style={{
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              color: 'var(--text-primary)',
              padding: '6px 12px',
              fontSize: '0.85rem',
            }}
          >
            <option value="">All categories</option>
            {ALL_CATEGORIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        {/* Problem table */}
        {loading ? (
          <p style={{ color: 'var(--text-muted)' }}>Loading…</p>
        ) : (
          <div
            style={{
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              overflow: 'hidden',
            }}
          >
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  {['#', 'Title', 'Difficulty', 'Topics'].map((h) => (
                    <th
                      key={h}
                      style={{
                        padding: '0.75rem 1rem',
                        textAlign: 'left',
                        color: 'var(--text-muted)',
                        fontSize: '0.82rem',
                        fontWeight: 500,
                      }}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {problems.map((p, i) => (
                  <tr
                    key={p.id}
                    onClick={() => navigate(`/problems/${p.slug}`)}
                    style={{
                      borderBottom: '1px solid var(--border-color)',
                      cursor: 'pointer',
                      transition: 'background 0.1s',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-tertiary)')}
                    onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                  >
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                      {i + 1}
                    </td>
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--text-primary)', fontSize: '0.9rem' }}>
                      {p.title}
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <span style={{ color: DIFFICULTY_COLOR[p.difficulty], fontSize: '0.85rem', textTransform: 'capitalize' }}>
                        {p.difficulty}
                      </span>
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
                        {p.category.map((c) => (
                          <span
                            key={c}
                            style={{
                              background: 'var(--bg-tertiary)',
                              border: '1px solid var(--border-color)',
                              borderRadius: '10px',
                              padding: '1px 8px',
                              fontSize: '0.75rem',
                              color: 'var(--text-muted)',
                            }}
                          >
                            {c}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {problems.length === 0 && (
              <p style={{ padding: '1.5rem', color: 'var(--text-muted)', textAlign: 'center' }}>
                No problems found.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
