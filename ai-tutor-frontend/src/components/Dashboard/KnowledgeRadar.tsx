import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import type { DashboardKnowledgeProfile } from '../../api/users';

const TOPIC_LABELS: Record<string, string> = {
  'array': 'Arrays',
  'hash-map': 'Hash Maps',
  'linked-list': 'Linked List',
  'stack-queue': 'Stack/Queue',
  'tree': 'Trees',
  'graph': 'Graphs',
  'dynamic-programming': 'DP',
  'binary-search': 'Binary Search',
  'sliding-window': 'Sliding Window',
  'sorting': 'Sorting',
  'string': 'Strings',
  'greedy': 'Greedy',
};

interface Props {
  profile: DashboardKnowledgeProfile;
}

// Custom tooltip for the radar chart
function CustomTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: { topic: string; score: number } }> }) {
  if (!active || !payload?.length) return null;
  const { topic, score } = payload[0].payload;
  return (
    <div
      style={{
        background: 'var(--bg-primary)',
        border: '1px solid var(--border-color)',
        borderRadius: '6px',
        padding: '8px 12px',
        fontSize: '0.8rem',
        color: 'var(--text-primary)',
      }}
    >
      <div style={{ fontWeight: 600 }}>{topic}</div>
      <div style={{ color: 'var(--accent)' }}>{score}% proficiency</div>
    </div>
  );
}

export function KnowledgeRadar({ profile }: Props) {
  const entries = Object.entries(profile.topics);

  if (entries.length === 0) {
    return (
      <div
        style={{
          height: '280px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.5rem',
          color: 'var(--text-muted)',
        }}
      >
        <div style={{ fontSize: '2rem' }}>📊</div>
        <p style={{ margin: 0, fontSize: '0.85rem', textAlign: 'center' }}>
          Solve problems to build your<br />topic proficiency radar
        </p>
      </div>
    );
  }

  const radarData = entries.map(([topic, stats]) => ({
    topic: TOPIC_LABELS[topic] ?? topic,
    score: Math.round(stats.proficiency_score * 100),
    fullMark: 100,
  }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
        <PolarGrid stroke="var(--border-color)" />
        <PolarAngleAxis
          dataKey="topic"
          tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
        />
        <PolarRadiusAxis
          angle={90}
          domain={[0, 100]}
          tickCount={4}
          tick={{ fill: 'var(--text-muted)', fontSize: 9 }}
        />
        <Radar
          name="Proficiency"
          dataKey="score"
          stroke="var(--accent)"
          fill="var(--accent)"
          fillOpacity={0.25}
          strokeWidth={2}
          dot={{ fill: 'var(--accent)', r: 3 }}
        />
        <Tooltip content={<CustomTooltip />} />
      </RadarChart>
    </ResponsiveContainer>
  );
}
