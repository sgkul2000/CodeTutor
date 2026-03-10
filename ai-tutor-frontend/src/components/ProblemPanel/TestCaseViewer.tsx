import type { Example } from '../../types';

interface Props {
  examples: Example[];
}

export function TestCaseViewer({ examples }: Props) {
  return (
    <div style={{ padding: '0 1.25rem 1.25rem' }}>
      <h4 style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '0.75rem' }}>
        Examples
      </h4>
      {examples.map((ex, i) => (
        <div
          key={i}
          style={{
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-color)',
            borderRadius: '6px',
            padding: '0.75rem',
            marginBottom: '0.75rem',
            fontSize: '0.85rem',
          }}
        >
          <div style={{ marginBottom: '0.35rem' }}>
            <span style={{ color: 'var(--text-muted)' }}>Input: </span>
            <code style={{ color: 'var(--text-primary)' }}>{ex.input}</code>
          </div>
          <div style={{ marginBottom: ex.explanation ? '0.35rem' : 0 }}>
            <span style={{ color: 'var(--text-muted)' }}>Output: </span>
            <code style={{ color: 'var(--success)' }}>{ex.output}</code>
          </div>
          {ex.explanation && (
            <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '0.25rem' }}>
              {ex.explanation}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
