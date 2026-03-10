import ReactMarkdown from 'react-markdown';
import type { Problem } from '../../types';

const DIFFICULTY_COLOR: Record<string, string> = {
  easy: 'var(--success)',
  medium: 'var(--warning)',
  hard: 'var(--danger)',
};

interface Props {
  problem: Problem;
}

export function ProblemDescription({ problem }: Props) {
  return (
    <div style={{ padding: '1.25rem', color: 'var(--text-primary)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
        <h2 style={{ margin: 0, fontSize: '1.15rem' }}>{problem.title}</h2>
        <span
          style={{
            color: DIFFICULTY_COLOR[problem.difficulty],
            fontSize: '0.8rem',
            fontWeight: 600,
            textTransform: 'capitalize',
          }}
        >
          {problem.difficulty}
        </span>
      </div>

      <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
        {problem.category.map((cat) => (
          <span
            key={cat}
            style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-color)',
              borderRadius: '12px',
              padding: '2px 10px',
              fontSize: '0.75rem',
              color: 'var(--text-muted)',
            }}
          >
            {cat}
          </span>
        ))}
      </div>

      <div
        className="prose-content"
        style={{ fontSize: '0.9rem', lineHeight: 1.7, color: 'var(--text-primary)' }}
      >
        <ReactMarkdown>{problem.description}</ReactMarkdown>
      </div>

      {problem.constraints && (
        <div style={{ marginTop: '1rem' }}>
          <h4 style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '0.4rem' }}>
            Constraints
          </h4>
          <pre
            style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              padding: '0.75rem',
              fontSize: '0.8rem',
              color: 'var(--text-primary)',
              whiteSpace: 'pre-wrap',
            }}
          >
            {problem.constraints}
          </pre>
        </div>
      )}
    </div>
  );
}
