import client from './client';
import type { Conversation } from '../types';

export const analyzeSubmission = (
  _submissionId: string,
  _onToken: (text: string) => void,
  _onDone: (conversationId: string) => void,
  _onError: (msg: string) => void
): EventSource => {
  // POST then stream — we use fetch + ReadableStream for SSE with body
  // For GET-based SSE (no body), EventSource works directly
  // Since our endpoint accepts POST, we use fetch + SSE manually
  throw new Error('Use streamTutor helper instead');
};

export const getConversation = async (submissionId: string): Promise<Conversation> => {
  const { data } = await client.get(`/tutor/conversation/${submissionId}`);
  return data;
};

export type SSECleanup = () => void;

/** POST to a streaming tutor endpoint and handle SSE token events. */
export const streamTutor = (
  endpoint: string,
  body: Record<string, string>,
  token: string,
  onToken: (text: string) => void,
  onDone: (data: Record<string, string>) => void,
  onError: (msg: string) => void
): SSECleanup => {
  const controller = new AbortController();

  fetch(`/api${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) {
        const text = await res.text();
        onError(text);
        return;
      }
      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';

        for (const line of lines) {
          if (line.startsWith('event: token')) continue;
          if (line.startsWith('event: done')) continue;
          if (line.startsWith('event: error')) continue;
          if (line.startsWith('data: ')) {
            const raw = line.slice(6).trim();
            if (!raw) continue;
            try {
              const parsed = JSON.parse(raw);
              if (parsed.text !== undefined) {
                onToken(parsed.text);
              } else if (parsed.complete || parsed.conversation_id || parsed.hint_level !== undefined) {
                onDone(parsed);
              } else if (parsed.error) {
                onError(parsed.error);
              }
            } catch {
              // skip malformed lines
            }
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== 'AbortError') onError(String(err));
    });

  return () => controller.abort();
};
