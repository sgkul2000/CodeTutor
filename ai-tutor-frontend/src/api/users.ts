import client from './client';

export interface DashboardStats {
  problems_attempted: number;
  problems_solved: number;
  hints_used: number;
  streak_days: number;
  acceptance_rate: number;
}

export interface TopicStat {
  proficiency_score: number;
  problems_attempted: number;
  problems_solved: number;
  avg_hints_per_solve: number;
}

export interface DashboardKnowledgeProfile {
  overall_level: string;
  weakest_topics: string[];
  strongest_topics: string[];
  topics: Record<string, TopicStat>;
  last_updated: string;
}

export interface RecentActivityItem {
  submission_id: string;
  problem_id: string;
  problem_title: string;
  status: string;
  language: string;
  submitted_at: string;
}

export interface DashboardData {
  user: {
    id: string;
    display_name: string;
    username: string;
    avatar_url?: string;
    is_admin: boolean;
    member_since: string;
  };
  stats: DashboardStats;
  knowledge_profile: DashboardKnowledgeProfile;
  recent_activity: RecentActivityItem[];
}

export async function getDashboard(): Promise<DashboardData> {
  const { data } = await client.get<DashboardData>('/users/dashboard');
  return data;
}

export async function updatePreferences(prefs: {
  default_language?: string;
  assistance_level?: number;
  theme?: string;
}) {
  const { data } = await client.patch('/users/preferences', prefs);
  return data;
}
