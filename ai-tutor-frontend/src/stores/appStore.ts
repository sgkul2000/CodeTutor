import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, Problem, Language } from '../types';

interface AppState {
  // Auth
  authToken: string | null;
  refreshToken: string | null;
  currentUser: User | null;
  setAuth: (token: string, user: User, refreshToken?: string) => void;
  /** Update only the access token (used by silent refresh). */
  setAuthToken: (token: string) => void;
  clearAuth: () => void;

  // Problem
  currentProblem: Problem | null;
  setCurrentProblem: (p: Problem | null) => void;

  // Editor
  selectedLanguage: Language;
  setSelectedLanguage: (lang: Language) => void;

  // Assistance
  assistanceLevel: 1 | 2 | 3 | 4;
  setAssistanceLevel: (level: 1 | 2 | 3 | 4) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      authToken: null,
      refreshToken: null,
      currentUser: null,
      setAuth: (token, user, refreshToken) =>
        set({ authToken: token, currentUser: user, refreshToken: refreshToken ?? null }),
      setAuthToken: (token) => set({ authToken: token }),
      clearAuth: () => set({ authToken: null, refreshToken: null, currentUser: null }),

      currentProblem: null,
      setCurrentProblem: (p) => set({ currentProblem: p }),

      selectedLanguage: 'python',
      setSelectedLanguage: (lang) => set({ selectedLanguage: lang }),

      assistanceLevel: 2,
      setAssistanceLevel: (level) => set({ assistanceLevel: level }),
    }),
    {
      name: 'ai-tutor-store',
      partialize: (state) => ({
        authToken: state.authToken,
        refreshToken: state.refreshToken,
        currentUser: state.currentUser,
        selectedLanguage: state.selectedLanguage,
        assistanceLevel: state.assistanceLevel,
      }),
    }
  )
);
