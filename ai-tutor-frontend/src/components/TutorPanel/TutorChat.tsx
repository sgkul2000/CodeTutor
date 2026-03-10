import { useState, useRef, useEffect } from 'react';
import { StreamingMessage } from './StreamingMessage';
import { HintDisplay } from './HintDisplay';
import { AssistanceSlider } from './AssistanceSlider';
import type { Conversation } from '../../types';

interface Props {
  conversation: Conversation | null;
  streamingText: string;
  isStreaming: boolean;
  onAsk: (message: string) => void;
  onRequestHint: () => void;
  onAnalyze: () => void;
  hasSubmission: boolean;
  submissionStatus: string;
}

export function TutorChat({
  conversation,
  streamingText,
  isStreaming,
  onAsk,
  onRequestHint,
  onAnalyze,
  hasSubmission,
  submissionStatus,
}: Props) {
  const [input, setInput] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation?.messages.length, streamingText]);

  const handleSend = () => {
    const msg = input.trim();
    if (!msg || isStreaming) return;
    setInput('');
    if (conversation) {
      onAsk(msg);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        background: 'var(--bg-primary)',
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '0.6rem 1rem',
          background: 'var(--bg-secondary)',
          borderBottom: '1px solid var(--border-color)',
          fontSize: '0.85rem',
          color: 'var(--text-muted)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <span>🧑‍🏫 AI Tutor</span>
        {hasSubmission && submissionStatus !== 'accepted' && !conversation && (
          <button
            onClick={onAnalyze}
            disabled={isStreaming}
            style={{
              background: 'var(--accent)',
              border: 'none',
              borderRadius: '6px',
              color: '#fff',
              padding: '4px 12px',
              fontSize: '0.82rem',
              cursor: 'pointer',
              opacity: isStreaming ? 0.5 : 1,
            }}
          >
            Get feedback
          </button>
        )}
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflow: 'auto', padding: '1rem' }}>
        {!hasSubmission && (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', textAlign: 'center', marginTop: '2rem' }}>
            Submit your code to get AI feedback.
          </p>
        )}

        {hasSubmission && submissionStatus === 'accepted' && !conversation && (
          <div
            style={{
              background: 'rgba(63,185,80,0.1)',
              border: '1px solid var(--success)',
              borderRadius: '8px',
              padding: '1rem',
              fontSize: '0.88rem',
              color: 'var(--success)',
            }}
          >
            ✓ Solution accepted! Great work.
          </div>
        )}

        {conversation?.messages.map((msg, i) => (
          <div
            key={i}
            style={{
              marginBottom: '1rem',
              display: 'flex',
              flexDirection: 'column',
              alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            <div
              style={{
                maxWidth: '90%',
                background: msg.role === 'user' ? 'var(--bg-tertiary)' : 'transparent',
                border: msg.role === 'user' ? '1px solid var(--border-color)' : 'none',
                borderRadius: '8px',
                padding: msg.role === 'user' ? '0.5rem 0.75rem' : '0',
                fontSize: '0.88rem',
              }}
            >
              {msg.role === 'assistant' ? (
                <StreamingMessage text={msg.content} />
              ) : (
                <span style={{ color: 'var(--text-primary)' }}>{msg.content}</span>
              )}
            </div>
          </div>
        ))}

        {/* Live streaming token */}
        {isStreaming && streamingText && (
          <div style={{ marginBottom: '1rem' }}>
            <StreamingMessage text={streamingText} isStreaming />
          </div>
        )}

        {isStreaming && !streamingText && (
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Thinking…</div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Assistance level slider — always visible */}
      <AssistanceSlider />

      {/* Hint controls */}
      {conversation && (
        <HintDisplay
          currentLevel={conversation.hint_level_reached}
          onRequestHint={onRequestHint}
          isStreaming={isStreaming}
        />
      )}

      {/* Input */}
      {conversation && (
        <div
          style={{
            display: 'flex',
            gap: '0.5rem',
            padding: '0.6rem 1rem',
            borderTop: '1px solid var(--border-color)',
            background: 'var(--bg-secondary)',
          }}
        >
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a follow-up question…"
            rows={2}
            style={{
              flex: 1,
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              color: 'var(--text-primary)',
              padding: '6px 10px',
              fontSize: '0.85rem',
              resize: 'none',
              fontFamily: 'inherit',
            }}
          />
          <button
            onClick={handleSend}
            disabled={isStreaming || !input.trim()}
            style={{
              background: 'var(--accent)',
              border: 'none',
              borderRadius: '6px',
              color: '#fff',
              padding: '6px 14px',
              fontSize: '0.85rem',
              cursor: 'pointer',
              alignSelf: 'flex-end',
              opacity: isStreaming || !input.trim() ? 0.5 : 1,
            }}
          >
            Send
          </button>
        </div>
      )}
    </div>
  );
}
