# ── Stage 1: base image ───────────────────────────────────────────────────────
# We use the slim variant — full Python image is ~900MB, slim is ~130MB.
# "3.11-slim" means Python 3.11 on Debian slim. We pin the minor version so
# a future "3.12" release never silently changes our container.
FROM python:3.11-slim

# ── System dependencies ───────────────────────────────────────────────────────
# WeasyPrint (PDF generation) needs these C libraries at the OS level.
# We install them here before Python packages.
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*
# rm -rf cleans up apt cache — keeps image size small

# ── Working directory ─────────────────────────────────────────────────────────
# All subsequent commands run from /app inside the container
WORKDIR /app

# ── Install Python dependencies ───────────────────────────────────────────────
# We copy requirements.txt FIRST (before the app code) and install it.
# Docker caches layers. If requirements.txt hasn't changed, Docker reuses
# the cached install layer — making subsequent builds very fast.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# --no-cache-dir keeps image size down (no pip cache stored in image)

# ── Copy application code ─────────────────────────────────────────────────────
# This layer comes AFTER pip install so code changes don't trigger re-install
COPY . .

# ── Expose the port FastAPI will listen on ────────────────────────────────────
EXPOSE 8000

# ── Start command ─────────────────────────────────────────────────────────────
# uvicorn is the ASGI server. It runs our FastAPI app.
# --host 0.0.0.0 means "accept connections from outside the container"
# --reload means "restart when code changes" — for development only
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
