import { useState, useCallback, useRef } from 'react';
import { streamTutor, getConversation } from '../api/tutor';
import { useAppStore } from '../stores/appStore';
import type { Conversation, Message } from '../types';

export function useTutor() {
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [streamingText, setStreamingText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const cleanupRef = useRef<(() => void) | null>(null);

  // Use a ref so SSE callbacks always read the latest token without stale closures
  const tokenRef = useRef<string>(useAppStore.getState().authToken ?? '');
  useAppStore.subscribe((s) => { tokenRef.current = s.authToken ?? ''; });

  /** Reload the full conversation from the server after any streaming completes. */
  const _reload = useCallback(async (submissionId: string) => {
    try {
      const conv = await getConversation(submissionId);
      setConversation(conv);
      setStreamingText('');
    } catch {
      // conversation may not exist yet on very first analysis — ignore
    }
  }, []);

  const analyze = useCallback((submissionId: string) => {
    setStreamingText('');
    setIsStreaming(true);
    cleanupRef.current?.();

    cleanupRef.current = streamTutor(
      '/tutor/analyze',
      { submission_id: submissionId },
      tokenRef.current,
      (text) => setStreamingText((prev) => prev + text),
      (_data) => {
        setIsStreaming(false);
        _reload(submissionId);
      },
      (err) => {
        setIsStreaming(false);
        console.error('Tutor analyze error:', err);
      }
    );
  }, [_reload]);

  const ask = useCallback((conversationId: string, submissionId: string, message: string) => {
    // Optimistically append the user message immediately for snappy UX
    const userMsg: Message = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };
    setConversation((prev) =>
      prev ? { ...prev, messages: [...prev.messages, userMsg] } : null
    );

    setStreamingText('');
    setIsStreaming(true);
    cleanupRef.current?.();

    cleanupRef.current = streamTutor(
      '/tutor/ask',
      { conversation_id: conversationId, message },
      tokenRef.current,
      (text) => setStreamingText((prev) => prev + text),
      (_data) => {
        setIsStreaming(false);
        _reload(submissionId);
      },
      (err) => {
        setIsStreaming(false);
        console.error('Tutor ask error:', err);
      }
    );
  }, [_reload]);

  const requestHint = useCallback((conversationId: string, submissionId: string) => {
    setStreamingText('');
    setIsStreaming(true);
    cleanupRef.current?.();

    cleanupRef.current = streamTutor(
      '/tutor/hint',
      { conversation_id: conversationId },
      tokenRef.current,
      (text) => setStreamingText((prev) => prev + text),
      (data) => {
        setIsStreaming(false);
        // Optimistically bump hint level so the UI updates immediately
        if (data.hint_level !== undefined) {
          setConversation((prev) =>
            prev ? { ...prev, hint_level_reached: Number(data.hint_level) } : null
          );
        }
        _reload(submissionId);
      },
      (err) => {
        setIsStreaming(false);
        console.error('Hint error:', err);
      }
    );
  }, [_reload]);

  const loadConversation = useCallback(async (submissionId: string) => {
    await _reload(submissionId);
  }, [_reload]);

  /** Cancel any in-progress SSE stream (e.g. when a new submission starts). */
  const cancelStream = useCallback(() => {
    cleanupRef.current?.();
    cleanupRef.current = null;
    setIsStreaming(false);
    setStreamingText('');
  }, []);

  return {
    conversation,
    streamingText,
    isStreaming,
    analyze,
    ask,
    requestHint,
    loadConversation,
    cancelStream,
  };
}
