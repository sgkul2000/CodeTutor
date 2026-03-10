import { useCallback } from 'react';
import client from '../../api/client';
import { useAppStore } from '../../stores/appStore';

const LEVELS = [
  { value: 1 as const, label: 'Figure it out', desc: 'Minimal hints only' },
  { value: 2 as const, label: 'Nudge me', desc: 'Standard guidance' },
  { value: 3 as const, label: 'Guide me', desc: 'Detailed feedback' },
  { value: 4 as const, label: 'Teach me', desc: 'Full explanations' },
];

export function AssistanceSlider() {
  const { assistanceLevel, setAssistanceLevel } = useAppStore();

  const handleChange = useCallback(async (level: 1 | 2 | 3 | 4) => {
    setAssistanceLevel(level);
    try {
      await client.patch('/users/preferences', { assistance_level: level });
    } catch {
      // Non-critical — preference is stored locally in Zustand regardless
    }
  }, [setAssistanceLevel]);

  return (
    <div style={{ padding: '0.6rem 1rem', borderBottom: '1px solid var(--border-color)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 500 }}>
          Assistance level
        </span>
        <span style={{ fontSize: '0.78rem', color: 'var(--accent)', fontWeight: 600 }}>
          {LEVELS[assistanceLevel - 1].label}
        </span>
      </div>

      {/* 4-stop segmented control */}
      <div style={{ display: 'flex', gap: '3px' }}>
        {LEVELS.map((lvl) => {
          const active = assistanceLevel === lvl.value;
          return (
            <button
              key={lvl.value}
              title={lvl.desc}
              onClick={() => handleChange(lvl.value)}
              style={{
                flex: 1,
                padding: '4px 0',
                fontSize: '0.72rem',
                border: `1px solid ${active ? 'var(--accent)' : 'var(--border-color)'}`,
                borderRadius: '4px',
                background: active ? 'rgba(88,166,255,0.15)' : 'var(--bg-tertiary)',
                color: active ? 'var(--accent)' : 'var(--text-muted)',
                cursor: 'pointer',
                transition: 'all 0.15s',
                fontWeight: active ? 600 : 400,
              }}
            >
              {lvl.value}
            </button>
          );
        })}
      </div>

      {/* Description of current level */}
      <p style={{ margin: '0.35rem 0 0', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
        {LEVELS[assistanceLevel - 1].desc}
      </p>
    </div>
  );
}
