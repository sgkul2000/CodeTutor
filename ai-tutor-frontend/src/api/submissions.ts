import client from './client';
import type { Language, Submission } from '../types';

export const submitCode = async (body: {
  problem_id: string;
  language: Language;
  code: string;
}): Promise<Submission> => {
  const { data } = await client.post('/submissions', body);
  return data;
};

export const getSubmission = async (id: string): Promise<Submission> => {
  const { data } = await client.get(`/submissions/${id}`);
  return data;
};

export const getSubmissionHistory = async (problemId: string): Promise<Submission[]> => {
  const { data } = await client.get(`/submissions/history/${problemId}`);
  return data;
};
