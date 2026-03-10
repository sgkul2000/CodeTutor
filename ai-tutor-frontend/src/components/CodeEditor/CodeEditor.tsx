import Editor from '@monaco-editor/react';
import type { Language } from '../../types';

const MONACO_LANG: Record<Language, string> = {
  python: 'python',
  java: 'java',
  javascript: 'javascript',
};

interface Props {
  language: Language;
  value: string;
  onChange: (code: string) => void;
}

export function CodeEditor({ language, value, onChange }: Props) {
  return (
    <Editor
      height="100%"
      language={MONACO_LANG[language]}
      value={value}
      theme="vs-dark"
      options={{
        fontSize: 14,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        wordWrap: 'on',
        tabSize: language === 'python' ? 4 : 2,
        automaticLayout: true,
        lineNumbers: 'on',
        renderLineHighlight: 'line',
        padding: { top: 12 },
      }}
      onChange={(v) => onChange(v ?? '')}
    />
  );
}
