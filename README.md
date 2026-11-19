# Job-Hunt-Ai

The backend scaffold for an AI job-application agent. The plan: it searches listings, tailors a resume to each one with Claude, renders the resume to PDF, and submits applications through a browser-automation service while you track everything from one place.

> **Status: work in progress (Phase 1).** The service layout, data models, API routes and task queue are in place. The search and apply workers are still stubs.

## Architecture

```
FastAPI API ──► PostgreSQL (SQLAlchemy + Alembic)
    │
    └──► Celery workers (Redis broker, Flower dashboard)
            ├─ search_tasks  → find and score listings
            └─ apply_tasks   → tailor resume (Claude) → PDF (WeasyPrint) → submit via playwright-service
```

- `backend/app/api/routes/`: auth (JWT), jobs, resumes, applications, health
- `backend/app/models/`: user, job, resume, application
- `backend/app/workers/`: Celery app and tasks
- `playwright-service/`: separate container for browser automation

## Run it

```bash
cp .env.example .env    # fill in the database, Redis and ANTHROPIC_API_KEY values
docker compose up --build
```

The API comes up on the port set in `docker-compose.yml`, with a health check at `/health`.
