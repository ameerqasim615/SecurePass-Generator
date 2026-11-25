# ResumeAI - Smart AI Resume Builder

An AI-powered resume builder: React + TypeScript frontend, FastAPI backend, Supabase (Auth, Postgres, Storage), Google Gemini for AI features.

> **Status: Phase 1 of 10 (foundation).** The repo structure, backend skeleton and frontend shell exist and are connected. Auth, the resume builder, AI features, ATS analysis, templates, PDF export and the admin dashboard land in the following phases.

## Repository layout

```
resumeai/
├── frontend/            React + Vite + TypeScript + Tailwind
│   └── src/             components, pages, layouts, features, hooks, services, types, utils, lib
├── backend/             FastAPI service
│   ├── app/             api, core, models, schemas, services, middleware
│   └── tests/           pytest suite
├── supabase/
│   └── migrations/      SQL migrations (added in Phase 3)
└── README.md
```

## Prerequisites

- Node.js 20+ and npm
- Python 3.11+

## Run locally

**Backend** (http://localhost:8000, interactive docs at `/docs` outside production):

```bash
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload --env-file .env
```

**Frontend** (http://localhost:5173):

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The home page shows a live "Backend connection" status; it turns green when the frontend can reach the API.

## Tests and checks

```bash
cd backend  && pytest              # config, error handling, CORS, security headers
cd frontend && npm test            # env parsing, API client
cd frontend && npm run typecheck   # TypeScript
cd frontend && npm run build       # typecheck + production build
```

## Configuration

Each app has its own `.env.example` (they deploy to different hosts, so each reads its own variables):

| File | Used by | Notes |
| --- | --- | --- |
| `backend/.env.example` | FastAPI (Render) | `CORS_ORIGINS` is required in production; wildcards are rejected |
| `frontend/.env.example` | Vite (Netlify) | `VITE_*` values are public - never put secrets here |

Real `.env` files are git-ignored. Secrets (Supabase service role key, Gemini API key) are server-side only and arrive in Phases 3 and 5.

## Roadmap

| Phase | Scope | State |
| --- | --- | --- |
| 1 | Project setup and architecture | Done |
| 2 | Frontend UI and design system | Next |
| 3 | Authentication and Supabase database | Planned |
| 4 | Resume builder and live editor | Planned |
| 5 | Gemini AI integration | Planned |
| 6 | ATS analyzer | Planned |
| 7 | Templates, PDF export, cover letters | Planned |
| 8 | Admin dashboard and security hardening | Planned |
| 9 | Testing and bug fixing | Planned |
| 10 | Deployment and documentation | Planned |
