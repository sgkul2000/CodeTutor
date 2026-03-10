const HINT_LABELS: Record<number, string> = {
  1: 'Direction',
  2: 'Approach',
  3: 'Structure',
  4: 'Full Walkthrough',
};

interface Props {
  currentLevel: number;
  onRequestHint: () => void;
  isStreaming: boolean;
}

export function HintDisplay({ currentLevel, onRequestHint, isStreaming }: Props) {
  const isMaxLevel = currentLevel >= 4;

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        padding: '0.5rem 1rem',
        borderTop: '1px solid var(--border-color)',
        background: 'var(--bg-secondary)',
      }}
    >
      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        Hint level: <strong style={{ color: 'var(--text-primary)' }}>{HINT_LABELS[currentLevel]}</strong>
      </span>

      {!isMaxLevel && (
        <button
          onClick={onRequestHint}
          disabled={isStreaming}
          style={{
            background: 'transparent',
            border: '1px solid var(--border-color)',
            borderRadius: '6px',
            color: 'var(--accent)',
            padding: '4px 12px',
            fontSize: '0.82rem',
            opacity: isStreaming ? 0.5 : 1,
          }}
        >
          {isStreaming ? 'Thinking…' : 'Deeper hint →'}
        </button>
      )}

      {isMaxLevel && (
        <span style={{ fontSize: '0.8rem', color: 'var(--warning)' }}>
          Full walkthrough shown
        </span>
      )}
    </div>
  );
}
