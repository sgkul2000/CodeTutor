import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getProblem } from '../api/problems';
import { Navbar } from '../components/Layout/Navbar';
import { SplitPane } from '../components/Layout/SplitPane';
import { ProblemDescription } from '../components/ProblemPanel/ProblemDescription';
import { TestCaseViewer } from '../components/ProblemPanel/TestCaseViewer';
import { CodeEditor } from '../components/CodeEditor/CodeEditor';
import { LanguageSelector } from '../components/CodeEditor/LanguageSelector';
import { SubmissionResult } from '../components/Results/SubmissionResult';
import { TutorChat } from '../components/TutorPanel/TutorChat';
import { useSubmission } from '../hooks/useSubmission';
import { useTutor } from '../hooks/useTutor';
import { useAppStore } from '../stores/appStore';
import type { Problem, Language } from '../types';

export function ProblemSolvePage() {
  const { slug } = useParams<{ slug: string }>();
  const [problem, setProblem] = useState<Problem | null>(null);
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(true);

  const { selectedLanguage, setSelectedLanguage } = useAppStore();
  const { submission, isSubmitting, submit } = useSubmission();
  const { conversation, streamingText, isStreaming, analyze, ask, requestHint, cancelStream } =
    useTutor();

  // Load problem
  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    getProblem(slug)
      .then((p) => {
        setProblem(p);
        setCode(p.starter_code[selectedLanguage] ?? '');
      })
      .finally(() => setLoading(false));
  }, [slug]);

  // When language changes, load starter code
  const handleLanguageChange = (lang: Language) => {
    setSelectedLanguage(lang);
    if (problem) setCode(problem.starter_code[lang] ?? '');
  };

  const handleSubmit = async () => {
    if (!problem) return;
    cancelStream();   // cancel any in-progress AI stream before running a new submission
    await submit(problem.id, selectedLanguage, code);
  };

  // Auto-trigger AI analysis on failed submission
  useEffect(() => {
    if (
      submission &&
      submission.status !== 'accepted' &&
      submission.status !== 'pending' &&
      submission.ai_analysis_available &&
      !conversation &&
      !isStreaming
    ) {
      analyze(submission.submission_id);
    }
  }, [submission?.submission_id, submission?.status]);

  const handleAsk = (message: string) => {
    if (conversation && submission) ask(conversation.id, submission.submission_id, message);
  };

  const handleHint = () => {
    if (conversation && submission) requestHint(conversation.id, submission.submission_id);
  };

  const handleAnalyze = () => {
    if (submission) analyze(submission.submission_id);
  };

  if (loading) {
    return (
      <div style={{ background: 'var(--bg-primary)', minHeight: '100vh' }}>
        <Navbar />
        <div style={{ padding: '2rem', color: 'var(--text-muted)' }}>Loading problem…</div>
      </div>
    );
  }

  if (!problem) {
    return (
      <div style={{ background: 'var(--bg-primary)', minHeight: '100vh' }}>
        <Navbar />
        <div style={{ padding: '2rem', color: 'var(--danger)' }}>Problem not found.</div>
      </div>
    );
  }

  const leftPanel = (
    <div
      style={{
        height: '100%',
        overflow: 'auto',
        background: 'var(--bg-secondary)',
        borderRight: '1px solid var(--border-color)',
      }}
    >
      <ProblemDescription problem={problem} />
      <TestCaseViewer examples={problem.examples} />
    </div>
  );

  const rightPanel = (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Editor toolbar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          padding: '6px 12px',
          background: 'var(--bg-secondary)',
          borderBottom: '1px solid var(--border-color)',
        }}
      >
        <LanguageSelector value={selectedLanguage} onChange={handleLanguageChange} />
        <div style={{ flex: 1 }} />
        <button
          onClick={handleSubmit}
          disabled={isSubmitting}
          style={{
            background: 'var(--accent)',
            border: 'none',
            borderRadius: '6px',
            color: '#fff',
            padding: '5px 18px',
            fontSize: '0.88rem',
            fontWeight: 600,
            cursor: 'pointer',
            opacity: isSubmitting ? 0.6 : 1,
          }}
        >
          {isSubmitting ? 'Running…' : 'Submit'}
        </button>
      </div>

      {/* Editor + results + tutor, split vertically */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Code editor (takes ~55% height) */}
        <div style={{ flex: '0 0 55%', overflow: 'hidden' }}>
          <CodeEditor language={selectedLanguage} value={code} onChange={setCode} />
        </div>

        {/* Results */}
        {submission && <SubmissionResult submission={submission} />}

        {/* Tutor panel */}
        <div style={{ flex: 1, overflow: 'hidden', borderTop: '1px solid var(--border-color)' }}>
          <TutorChat
            conversation={conversation}
            streamingText={streamingText}
            isStreaming={isStreaming}
            onAsk={handleAsk}
            onRequestHint={handleHint}
            onAnalyze={handleAnalyze}
            hasSubmission={!!submission}
            submissionStatus={submission?.status ?? ''}
          />
        </div>
      </div>
    </div>
  );

  return (
    <div style={{ background: 'var(--bg-primary)', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <div style={{ flex: 1, overflow: 'hidden' }}>
        <SplitPane left={leftPanel} right={rightPanel} defaultSplit={40} />
      </div>
    </div>
  );
}
