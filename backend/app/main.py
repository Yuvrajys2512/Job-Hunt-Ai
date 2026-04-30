"""
JobHunt AI — FastAPI Application Entry Point

This file creates the FastAPI app instance, registers all routers (URL groups),
configures CORS, and defines startup/shutdown lifecycle events.

Think of this file as the "reception desk" of your backend — it doesn't do
the actual work, but it routes every incoming request to the right handler.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import init_db
from app.api.routes import health, auth, jobs, resumes, applications


# ── Lifespan: startup and shutdown logic ──────────────────────────────────────
# FastAPI's modern way to run code on startup and shutdown.
# asynccontextmanager turns it into an async context manager.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: runs before the first request is served
    await init_db()                   # create tables if they don't exist yet
    print("✓ Database initialized")
    print("✓ JobHunt AI API is ready")
    yield
    # SHUTDOWN: runs when the server is stopping (Ctrl+C, container stop, etc.)
    print("JobHunt AI API shutting down...")


# ── Create the FastAPI app instance ───────────────────────────────────────────
app = FastAPI(
    title="JobHunt AI",
    description="Agentic AI job search, resume generation, and application platform",
    version="0.1.0",
    lifespan=lifespan,
    # In production we'd set docs_url=None to hide the API docs
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


# ── CORS middleware ────────────────────────────────────────────────────────────
# CORS (Cross-Origin Resource Sharing): browsers block JS from calling APIs on
# a different domain by default (security feature). This middleware tells the
# browser: "yes, requests from our frontend are allowed."
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # list of allowed frontend URLs
    allow_credentials=True,                   # allow cookies (needed for auth)
    allow_methods=["*"],                      # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],                      # Authorization, Content-Type, etc.
)


# ── Register routers ───────────────────────────────────────────────────────────
# Each router is a group of related endpoints.
# prefix="/api/v1" means all routes start with /api/v1/...
# The "v1" is important — when you make breaking API changes, you add v2
# without breaking existing clients still using v1.

app.include_router(health.router,       prefix="/api/v1")
app.include_router(auth.router,         prefix="/api/v1/auth",         tags=["Auth"])
app.include_router(jobs.router,         prefix="/api/v1/jobs",         tags=["Jobs"])
app.include_router(resumes.router,      prefix="/api/v1/resumes",      tags=["Resumes"])
app.include_router(applications.router, prefix="/api/v1/applications", tags=["Applications"])
