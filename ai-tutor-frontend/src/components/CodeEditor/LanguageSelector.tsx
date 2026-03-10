import type { Language } from '../../types';

const LANGUAGES: { value: Language; label: string }[] = [
  { value: 'python', label: 'Python' },
  { value: 'java', label: 'Java' },
  { value: 'javascript', label: 'JavaScript' },
];

interface Props {
  value: Language;
  onChange: (lang: Language) => void;
}

export function LanguageSelector({ value, onChange }: Props) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value as Language)}
      style={{
        background: 'var(--bg-tertiary)',
        border: '1px solid var(--border-color)',
        borderRadius: '6px',
        color: 'var(--text-primary)',
        padding: '4px 10px',
        fontSize: '0.85rem',
        cursor: 'pointer',
      }}
    >
      {LANGUAGES.map((l) => (
        <option key={l.value} value={l.value}>
          {l.label}
        </option>
      ))}
    </select>
  );
}
