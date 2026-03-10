import client from './client';
import type { Problem, ProblemSummary } from '../types';

export const getProblems = async (filters?: {
  difficulty?: string;
  category?: string;
}): Promise<ProblemSummary[]> => {
  const { data } = await client.get('/problems', { params: filters });
  return data;
};

export const getProblem = async (slug: string): Promise<Problem> => {
  const { data } = await client.get(`/problems/${slug}`);
  return data;
};

export const getRelatedProblems = async (slug: string): Promise<ProblemSummary[]> => {
  const { data } = await client.get(`/problems/${slug}/related`);
  return data;
};
