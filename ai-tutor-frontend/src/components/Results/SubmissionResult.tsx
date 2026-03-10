import type { Submission } from '../../types';

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  accepted: { label: 'Accepted ✓', color: 'var(--success)' },
  wrong_answer: { label: 'Wrong Answer', color: 'var(--danger)' },
  time_limit: { label: 'Time Limit Exceeded', color: 'var(--warning)' },
  runtime_error: { label: 'Runtime Error', color: 'var(--danger)' },
  compile_error: { label: 'Compile Error', color: 'var(--danger)' },
  pending: { label: 'Running…', color: 'var(--text-muted)' },
};

interface Props {
  submission: Submission;
}

export function SubmissionResult({ submission }: Props) {
  const cfg = STATUS_CONFIG[submission.status] ?? { label: submission.status, color: 'var(--text-muted)' };
  const r = submission.execution_results;

  return (
    <div
      style={{
        borderTop: `3px solid ${cfg.color}`,
        background: 'var(--bg-secondary)',
        padding: '0.75rem 1rem',
        fontSize: '0.9rem',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
        <span style={{ color: cfg.color, fontWeight: 600 }}>{cfg.label}</span>

        {r && (
          <span style={{ color: 'var(--text-muted)' }}>
            {r.passed_test_cases}/{r.total_test_cases} tests passed
          </span>
        )}
        {r?.runtime_ms != null && (
          <span style={{ color: 'var(--text-muted)' }}>{r.runtime_ms} ms</span>
        )}
        {r?.memory_kb != null && (
          <span style={{ color: 'var(--text-muted)' }}>
            {(r.memory_kb / 1024).toFixed(1)} MB
          </span>
        )}
      </div>

      {r?.failed_test_case && (
        <div
          style={{
            marginTop: '0.6rem',
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-color)',
            borderRadius: '6px',
            padding: '0.6rem 0.8rem',
            fontSize: '0.82rem',
          }}
        >
          <div>
            <span style={{ color: 'var(--text-muted)' }}>Input: </span>
            <code>{r.failed_test_case.input}</code>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)' }}>Expected: </span>
            <code style={{ color: 'var(--success)' }}>{r.failed_test_case.expected}</code>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)' }}>Got: </span>
            <code style={{ color: 'var(--danger)' }}>{r.failed_test_case.actual}</code>
          </div>
        </div>
      )}

      {r?.stderr && (
        <pre
          style={{
            marginTop: '0.6rem',
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--danger)',
            borderRadius: '6px',
            padding: '0.6rem',
            fontSize: '0.8rem',
            color: 'var(--danger)',
            whiteSpace: 'pre-wrap',
            maxHeight: '120px',
            overflow: 'auto',
          }}
        >
          {r.stderr}
        </pre>
      )}
    </div>
  );
}
