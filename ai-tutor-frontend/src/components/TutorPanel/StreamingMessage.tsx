import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface Props {
  text: string;
  isStreaming?: boolean;
}

export function StreamingMessage({ text, isStreaming }: Props) {
  return (
    <div style={{ fontSize: '0.88rem', lineHeight: 1.7, color: 'var(--text-primary)' }}>
      <ReactMarkdown
        components={{
          code({ node, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className ?? '');
            const inline = !match;
            return inline ? (
              <code
                style={{
                  background: 'var(--bg-tertiary)',
                  borderRadius: '3px',
                  padding: '1px 5px',
                  fontSize: '0.85em',
                  color: 'var(--accent)',
                }}
                {...props}
              >
                {children}
              </code>
            ) : (
              <SyntaxHighlighter
                style={vscDarkPlus as Record<string, React.CSSProperties>}
                language={match[1]}
                PreTag="div"
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            );
          },
          p({ children }) {
            return <p style={{ margin: '0 0 0.75rem' }}>{children}</p>;
          },
          strong({ children }) {
            return <strong style={{ color: 'var(--accent)' }}>{children}</strong>;
          },
        }}
      >
        {text}
      </ReactMarkdown>
      {isStreaming && (
        <span
          style={{
            display: 'inline-block',
            width: '8px',
            height: '14px',
            background: 'var(--accent)',
            borderRadius: '2px',
            animation: 'blink 0.8s step-end infinite',
          }}
        />
      )}
      <style>{`@keyframes blink { 50% { opacity: 0; } }`}</style>
    </div>
  );
}
