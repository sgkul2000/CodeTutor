import { useState, useCallback } from 'react';
import { submitCode, getSubmission } from '../api/submissions';
import type { Language, Submission } from '../types';

export function useSubmission() {
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = useCallback(
    async (problemId: string, language: Language, code: string) => {
      setIsSubmitting(true);
      setError(null);
      setSubmission(null);

      try {
        const initial = await submitCode({ problem_id: problemId, language, code });
        setSubmission(initial);

        // Poll until status is no longer pending
        if (initial.status === 'pending') {
          await poll(initial.submission_id);
        }
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Submission failed');
      } finally {
        setIsSubmitting(false);
      }
    },
    []
  );

  const poll = async (id: string) => {
    for (let i = 0; i < 30; i++) {
      await new Promise((r) => setTimeout(r, 1000));
      const result = await getSubmission(id);
      setSubmission(result);
      if (result.status !== 'pending') return result;
    }
  };

  return { submission, isSubmitting, error, submit };
}
