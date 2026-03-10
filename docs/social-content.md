# CodeTutor — Social Media & Portfolio Content

---

## LinkedIn Post

---

🧑‍🏫 **I built an AI coding tutor that teaches like a mentor, not a search engine.**

Most coding practice platforms tell you if your solution passes or fails. That's useful — but it doesn't help you *learn*.

So I built **CodeTutor**: a full-stack platform that submits your code, runs it against real test cases, and then streams personalised feedback from Claude — pointing out what you're doing right, asking Socratic questions, and guiding you to the fix without just handing you the answer.

**What makes it different:**

🔁 **4-level hint escalation** — Start with a nudge. If you're still stuck, escalate from Direction → Approach → Structure → Full Walkthrough. You control how much help you get.

⚡ **Real-time streaming** — Feedback appears token-by-token as Claude generates it, so you're reading as it "thinks."

💬 **Follow-up chat** — Ask questions mid-session. The full conversation history is maintained so the tutor has context.

📊 **Knowledge profiling** — A radar chart tracks your proficiency across data structure topics so you can see exactly where to focus.

**The stack:**
- React 19 + TypeScript + Monaco Editor (VS Code's editor in the browser)
- FastAPI + Python + MongoDB + Redis
- Anthropic Claude via Server-Sent Events streaming
- OAuth 2.0 (Google + GitHub) with silent JWT refresh
- Docker Compose for local infra

It was a great exercise in building real-time streaming APIs, handling concurrent SSE connections, and designing an AI interaction pattern that feels like a conversation rather than a query.

Repo is open source — link in the comments 👇

\#buildinpublic \#ai \#python \#react \#fastapi \#opensource \#softwareengineering \#coding

---

## Personal Website — Project Description

---

### CodeTutor

**An AI-powered coding practice platform with real-time tutoring, hint escalation, and knowledge profiling.**

#### Overview

CodeTutor is a full-stack web application that reimagines how developers practise algorithms. Instead of a binary pass/fail verdict, every code submission triggers an AI tutoring session powered by Anthropic's Claude. The tutor analyses your code, identifies conceptual gaps, and guides you toward a solution using the Socratic method — asking questions rather than giving answers.

#### The Problem It Solves

Traditional online judges (LeetCode, HackerRank) tell you *what* is wrong but not *why* or *how* to think about it differently. Experienced engineers have a mental model of how to break down problems. CodeTutor tries to build that same intuition through guided dialogue.

#### Key Features

- **Streaming AI feedback** — Claude's analysis streams to the browser token-by-token via Server-Sent Events, giving the feeling of a live conversation
- **4-level hint system** — Users choose how much help they want. Level 1 is a directional nudge; Level 4 is a full worked walkthrough
- **Follow-up chat** — The full conversation history is sent with each request, so the tutor maintains context across the session
- **Monaco code editor** — The same editor that powers VS Code, embedded in the browser with Python, Java, and JavaScript support
- **Code execution** — Solutions are run against real test cases via the Piston execution engine
- **Knowledge radar chart** — Tracks proficiency across Arrays, Strings, Hash Maps, Stack/Queue, Graphs, and Dynamic Programming

#### Technical Highlights

**Streaming architecture** — The backend uses FastAPI's `EventSourceResponse` with an `async for` generator. The Anthropic SDK's streaming client yields text deltas which are forwarded as SSE `data:` events. The frontend reconstructs the stream using the Fetch API and a `ReadableStream` reader.

**Silent token refresh** — JWT access tokens expire after 15 minutes. A custom Axios interceptor catches 401 responses, pauses all in-flight requests, fires a single refresh call, then replays every queued request with the new token — all transparently.

**Hint escalation** — Each hint level sends the full conversation history to Claude along with a level-specific instruction appended as a new user turn. The conversation always ends on a user message to satisfy the Anthropic API's alternating-turn constraint.

**OAuth 2.0** — Supports Google and GitHub. The backend exchanges the authorization code server-side, issues its own JWT pair, and sets the refresh token as an HTTP-only cookie. The access token is passed to the frontend via a URL query parameter on redirect.

#### Stack

| | |
|---|---|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, Zustand |
| Editor | Monaco Editor |
| Backend | FastAPI, Python 3.12, async/await |
| Database | MongoDB 7 (Beanie ODM) |
| Cache | Redis 7.2 |
| AI | Anthropic Claude (claude-sonnet-4-5) |
| Execution | Piston API |
| Auth | OAuth 2.0, JWT |
| Infra | Docker Compose |

#### Links

- **GitHub:** [github.com/sgkul2000/CodeTutor](https://github.com/sgkul2000/CodeTutor)
