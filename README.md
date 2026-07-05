# 🚀 Doc2Draw AI

**Turn Word documents, PDF notes, and video courses into stunning, interactive Excalidraw visual maps in seconds.**

A complete, working implementation of the
[Full-Stack Implementation Guide](Doc2Draw_FullStack_Implementation_Guide.md)
(and the original [blueprint](Word_to_Excalidraw_AI_Product_Blueprint.md)) — every phase, end to end:

| Phase | Layer | Tech | Status |
| :--- | :--- | :--- | :--- |
| **1** | Core engine (`doc2draw/`) | Python package + CLI | ✅ Built & tested |
| **2** | Backend API (`backend/`) | FastAPI · Celery/in-process · services/core/models | ✅ Built & tested |
| **3** | Web app (`frontend/`) | Next.js 14 · Tailwind · Excalidraw SDK · SWR | ✅ Built & type-checked |
| **4** | Auth · DB · Billing | Supabase JWT · PostgreSQL/RLS · Stripe | ✅ Built (optional) |
| **5** | DevOps | Dockerfiles · docker-compose · Redis | ✅ Authored |

Everything runs **out of the box with zero external infrastructure** — no Redis, no
cloud account, no API keys. Supabase (auth/db/storage), Redis/Celery, Stripe, and S3
are **optional** upgrades that activate automatically when their env vars are present;
without them the code degrades gracefully (in-process jobs, local storage, anonymous
access, no billing).

---

## 🧭 Architecture

```
        Next.js 14 web app  ──REST──▶  FastAPI backend  ──▶  doc2draw core
 (landing · dashboard · wizard        (api/core/services/       (parse → structure →
  · live Excalidraw editor)            workers/models)           layout → compile)
        │                                   │  │
   Supabase Auth (opt)      Celery+Redis (opt) │  local FS / Supabase Storage (opt)
   Stripe billing (opt)     in-process (default)│  PostgreSQL + RLS (opt)
```

The core design pattern is preserved: **the LLM decides _what_ to draw and _how things
relate_; a deterministic Python engine decides _where_ to draw them** (exact X/Y
coordinates, card heights, arrow routing).

---

## 📁 Project layout

```
doc2draw/                 Phase 1 — core engine
├── parsers/              .docx, .pdf, video/image frame extraction (parse_media)
├── ai/                   semantic extraction (schemas.py, extractor.py + rule-based)
├── layout/               deterministic grid engine + Excalidraw element primitives
├── compiler/             Excalidraw JSON compiler + schema validator
└── cli.py                `python -m doc2draw <file>`

backend/                  Phase 2 — FastAPI API
└── app/
    ├── main.py           app entry (CORS, exception handlers, router)
    ├── config.py         Pydantic settings — all integrations optional
    ├── api/v1/           router + endpoints/ (projects, users, webhooks)
    ├── core/             auth (Supabase JWT), exceptions, security
    ├── services/         generator · storage · billing
    ├── workers/          Celery task + in-process fallback + job store
    └── models/           request/response schemas + SQLModel DB models

frontend/                 Phase 3 — Next.js 14 app (src/)
├── app/                  landing · dashboard · dashboard/new · editor/[id] · (auth)
├── components/           ui/ (shadcn-style) · upload · canvas · dashboard
├── hooks/                useProjectStatus (SWR) · useExcalidraw
└── lib/                  api (axios) · supabase · utils · projects

supabase/schema.sql       Phase 4 — PostgreSQL DDL + RLS + signup trigger
docker-compose.yml        Phase 5 — redis + backend + worker + frontend
backend/Dockerfile · frontend/Dockerfile
tests/                    pytest suite (core + backend integration)
```

---

## ⚡ Quick start (local, no infra)

**Prerequisites:** Python 3.9+ (tested 3.12), Node 18+ (tested 26).

```bash
pip install -r backend/requirements.txt   # or: pip install -e .
./run.ps1        # Windows  (or ./run.sh on macOS/Linux/Git Bash)
```
Open **http://localhost:3000** → *Create a visual map* → drop a `.docx` → *Generate*.

### CLI (no server needed)
```bash
python -m doc2draw "Make.com Masterclass - Complete Guide.docx"
python -m doc2draw lecture.mp4 --screenshots
```

---

## 🐳 Full stack with Docker (Phase 5)

```bash
cp .env.example .env        # optional: fill in Supabase/Stripe to enable them
docker compose up --build
```
Brings up **redis + backend + celery worker + frontend**. The backend and worker share
a `storage` volume and coordinate job status through Redis, so progress polling works
across containers. Frontend → http://localhost:3000, API docs → http://localhost:8000/docs.

---

## 🌐 Backend API

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `POST` | `/api/v1/projects/upload` | Ingest `.docx`/`.pdf`/`.txt`/video/image |
| `POST` | `/api/v1/projects/generate` | Trigger a background generation job |
| `GET`  | `/api/v1/projects/{job_id}/status` | Poll progress (parsing → structuring → compiling) |
| `GET`  | `/api/v1/projects/{project_id}/excalidraw` | Compiled Excalidraw JSON |
| `GET`  | `/api/v1/projects/{project_id}/download` | Download `.excalidraw` file |
| `GET`  | `/api/v1/users/me` | Current user + quota (anonymous when auth off) |
| `POST` | `/api/v1/webhooks/stripe` | Subscription lifecycle (503 until configured) |
| `GET`  | `/health` | Liveness + active feature flags |

---

## 🔌 Optional integrations (all graceful)

| Feature | Off (default) | On |
| :--- | :--- | :--- |
| **AI structuring** | Rule-based extractor | `OPENAI_API_KEY` (+ `pip install instructor openai`) |
| **Auth** | Anonymous access | `SUPABASE_JWT_SECRET` → JWT verification |
| **Database** | In-memory / localStorage | `DATABASE_URL` → SQLModel persistence + run `supabase/schema.sql` |
| **Job queue** | In-process threads | `REDIS_URL` → Celery worker + Redis-shared status |
| **Storage** | Local `backend/storage/` | Supabase Storage mirror |
| **Billing** | Disabled | `STRIPE_SECRET_KEY` + `STRIPE_WEBHOOK_SECRET` |

See `backend/.env.example` and `.env.example` for every variable.

---

## 🧪 Testing & verification

```bash
python -m pytest tests/ -v      # 13 tests: core engine + backend API
cd frontend && npm run build    # type-check + production build (8 routes)
```
The suite verifies (guide Step 1.4) that every generated `.excalidraw` passes schema
validation — required attributes, unique ids, valid bound-text containers, resolvable
image `fileId`s. The full flow (upload → generate → editor canvas) is browser-tested
end-to-end with a clean console.

---

*Implementation of the Doc2Draw AI Full-Stack Guide — built for scale, aesthetic excellence, and rapid execution.*
