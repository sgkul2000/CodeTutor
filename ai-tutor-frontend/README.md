# CodeTutor — Frontend

React + TypeScript + Vite frontend for the AI-powered coding tutor platform.

## Stack

| Layer | Technology |
|---|---|
| Framework | React 19 + TypeScript |
| Build | Vite 7 |
| Styling | Tailwind CSS v4 |
| Editor | Monaco Editor |
| State | Zustand (persisted to localStorage) |
| HTTP | Axios (with silent token refresh) |
| Routing | React Router v6 |

## Features

- **Problem browser** — filterable list of DSA problems with difficulty & topic tags
- **Monaco editor** — syntax-highlighted code editor with Python / Java / JavaScript support
- **Code execution** — submit code and see pass/fail results with first failing test case
- **AI Tutor** — SSE-streamed hints and Socratic feedback from Claude, triggered automatically on wrong answers
- **4-level hint escalation** — Direction → Approach → Structure → Full Walkthrough
- **Dashboard** — personal stats and radar chart of topic proficiency
- **OAuth login** — Google and GitHub (plus a dev-mode shortcut)
- **Silent token refresh** — access tokens are refreshed automatically so long sessions never interrupt you

## Getting Started

### Prerequisites

- Node 20+
- Backend running at `http://localhost:8000` (see `../ai-tutor-backend/README.md`)

### Install & run

```bash
cd ai-tutor-frontend
npm install
npm run dev          # starts at http://localhost:5173
```

The Vite dev server proxies `/api/*` requests to `http://localhost:8000` automatically.

### Environment variables

Copy `.env.example` to `.env.local` and fill in as needed (all optional for local dev):

| Variable | Default | Description |
|---|---|---|
| `VITE_BACKEND_URL` | `http://localhost:8000` | Used only for OAuth redirect URLs (browser-facing) |

## Project Layout

```
src/
├── api/              # Axios client + per-resource API helpers
│   ├── client.ts     # Axios instance with auth & silent refresh interceptors
│   ├── problems.ts
│   ├── submissions.ts
│   └── tutor.ts      # streamTutor() — fetch-based SSE helper
├── components/
│   ├── CodeEditor/   # Monaco wrapper + language selector
│   ├── Layout/       # Navbar, SplitPane
│   ├── ProblemPanel/ # Problem description, test case viewer
│   ├── Results/      # Submission result card
│   └── TutorPanel/   # TutorChat, HintDisplay, AssistanceSlider, StreamingMessage
├── hooks/
│   ├── useAuth.ts
│   ├── useSubmission.ts
│   └── useTutor.ts   # SSE stream lifecycle + conversation state
├── pages/
│   ├── LoginPage.tsx
│   ├── OAuthCallbackPage.tsx
│   ├── ProblemListPage.tsx
│   ├── ProblemSolvePage.tsx
│   └── DashboardPage.tsx
├── stores/
│   └── appStore.ts   # Zustand store (auth, language, assistance level)
└── types/
    └── index.ts
```

## Available Scripts

```bash
npm run dev       # dev server with HMR
npm run build     # production build → dist/
npm run preview   # preview production build locally
npm run lint      # ESLint
```

## Auth Flow

1. **Google / GitHub OAuth** — browser is redirected to the backend, which exchanges the code, sets an HTTP-only `refresh_token` cookie, and redirects back to `/auth/callback/:provider?access_token=<jwt>`.
2. **Dev login** — `GET /api/auth/dev-login` returns both tokens directly (development only).
3. **Silent refresh** — Axios 401 interceptor calls `POST /api/auth/refresh` and retries the original request. Concurrent requests while refreshing are queued and replayed.
