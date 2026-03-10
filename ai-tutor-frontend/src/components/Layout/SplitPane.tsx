import { useState, useRef, useCallback, type ReactNode } from 'react';

interface SplitPaneProps {
  left: ReactNode;
  right: ReactNode;
  defaultSplit?: number; // 0-100 (% for left panel)
}

export function SplitPane({ left, right, defaultSplit = 40 }: SplitPaneProps) {
  const [split, setSplit] = useState(defaultSplit);
  const dragging = useRef(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const onMouseDown = useCallback(() => {
    dragging.current = true;
    document.body.style.userSelect = 'none';
    document.body.style.cursor = 'col-resize';
  }, []);

  const onMouseMove = useCallback((e: React.MouseEvent) => {
    if (!dragging.current || !containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const pct = ((e.clientX - rect.left) / rect.width) * 100;
    setSplit(Math.max(20, Math.min(75, pct)));
  }, []);

  const onMouseUp = useCallback(() => {
    dragging.current = false;
    document.body.style.userSelect = '';
    document.body.style.cursor = '';
  }, []);

  return (
    <div
      ref={containerRef}
      onMouseMove={onMouseMove}
      onMouseUp={onMouseUp}
      style={{ display: 'flex', height: '100%', overflow: 'hidden' }}
    >
      <div style={{ width: `${split}%`, overflow: 'auto', flexShrink: 0 }}>{left}</div>

      {/* Divider */}
      <div
        onMouseDown={onMouseDown}
        style={{
          width: '4px',
          background: 'var(--border-color)',
          cursor: 'col-resize',
          flexShrink: 0,
          transition: 'background 0.1s',
        }}
        onMouseEnter={(e) => ((e.target as HTMLDivElement).style.background = 'var(--accent)')}
        onMouseLeave={(e) => ((e.target as HTMLDivElement).style.background = 'var(--border-color)')}
      />

      <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        {right}
      </div>
    </div>
  );
}
