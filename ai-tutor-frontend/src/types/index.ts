export type Language = 'python' | 'java' | 'javascript';
export type Difficulty = 'easy' | 'medium' | 'hard';
export type SubmissionStatus =
  | 'pending'
  | 'accepted'
  | 'wrong_answer'
  | 'time_limit'
  | 'runtime_error'
  | 'compile_error';

export interface User {
  id: string;
  email: string;
  username: string;
  display_name: string;
  avatar_url?: string;
  is_admin: boolean;
  preferences: UserPreferences;
  stats: UserStats;
}

export interface UserPreferences {
  default_language: Language;
  assistance_level: 1 | 2 | 3 | 4;
  theme: string;
}

export interface UserStats {
  problems_attempted: number;
  problems_solved: number;
  hints_used: number;
  streak_days: number;
}

export interface ProblemSummary {
  id: string;
  title: string;
  slug: string;
  difficulty: Difficulty;
  category: string[];
}

export interface Example {
  input: string;
  output: string;
  explanation?: string;
}

export interface StarterCode {
  python: string;
  java: string;
  javascript: string;
}

export interface Problem extends ProblemSummary {
  description: string;
  constraints: string;
  examples: Example[];
  starter_code: StarterCode;
  hints_metadata: {
    common_mistakes: string[];
    related_problems: string[];
  };
}

export interface FailedTestCase {
  input: string;
  expected: string;
  actual: string;
}

export interface ExecutionResults {
  total_test_cases: number;
  passed_test_cases: number;
  failed_test_case?: FailedTestCase;
  runtime_ms?: number;
  memory_kb?: number;
  stderr?: string;
}

export interface Submission {
  submission_id: string;
  status: SubmissionStatus;
  language: Language;
  submitted_at: string;
  execution_results?: ExecutionResults;
  ai_analysis?: { triggered: boolean; conversation_id?: string };
  ai_analysis_available: boolean;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  hint_level?: number;
  timestamp: string;
}

export interface Conversation {
  id: string;
  hint_level_reached: number;
  messages: Message[];
  metadata: { total_tokens_used: number; model_used: string; resolved: boolean };
}

export interface KnowledgeProfile {
  overall_level: string;
  weakest_topics: string[];
  strongest_topics: string[];
  topics: Record<string, { proficiency_score: number; problems_attempted: number; problems_solved: number }>;
  last_updated: string;
}
