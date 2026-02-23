# Phase 5 Implementation Plan: Containerization & Deployment Architecture

This plan documents the containerization strategy executed for the Banking REST Service. The goal is to provide a reproducible, isolated, and lean production environment using Docker, while securing the multi-stage build requirements.

## Proposed Architecture

### 1. `Dockerfile` (Multi-Stage Build)
We will implement a multi-stage Docker build to keep the final image incredibly lean by stripping out compilation tools and raw requirements files. We will use `python:3.9-slim` to match the local environment and prevent `backports.asyncio.runner` incompatibility.

#### Stage 1: Builder
- **Base Image:** `python:3.9-slim`
- **Actions:** 
  - Install heavy C-compilation dependencies (`gcc`, `libffi-dev`) required for asynchronous drivers.
  - Instantiate a Python virtual environment at `/opt/venv`.
  - Install `requirements.txt` into the virtual environment.

#### Stage 2: Runner
- **Base Image:** `python:3.9-slim`
- **Actions:**
  - Copy ONLY the fully compiled `/opt/venv` from the Builder stage.
  - Set strict Python environment variables (`PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`).
  - Copy the application source code (`app/`, `alembic/`, `alembic.ini`).
  - **Lifecycle `CMD`:** Chain commands using the shell (`alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000`) to guarantee that the database schema is validated and initialized *before* the API server accepts traffic.

---

### 2. `.dockerignore`
We will create a strict exclusion list to prevent sensitive or unnecessary local files from bloating the Docker context.
- **Excluded:** `.venv/`, `__pycache__/`, `tests/`, `tests/coverage/`, `.coverage`, `.git/`, `data/`, `*.db`, and `ai_brain/`.

---

### 3. `docker-compose.yml`
We will configure a local orchestration stack to make spinning up the environment seamless.
- **Service Name:** `api`
- **Port Mapping:** Expose the internal container port `8000` to the host port `8000`.
- **Environment Injection:** Override the database connection string explicitly to `sqlite+aiosqlite:///./data/banking.db`.
- **Volume Mapping (Persistence):** Critically, map the local `./data:/app/data` directory. This ensures that the SQLite database survives container teardown sequences.

---

## Verification Plan
1. **Build & Up:** Run `docker-compose up --build -d`.
2. **Log Audit:** Run `docker-compose logs -f api` to verify that `alembic.runtime.migration` executes successfully, followed immediately by Uvicorn booting perfectly.
3. **Data Persistence QA:** 
   - Create a test user via the API (`POST /auth/signup`).
   - Run `docker-compose down` to execute total container destruction.
   - Run `docker-compose up -d` to revive the system.
   - Attempt to log in with the test user; a successful login proves the host-mapped volume successfully persisted the SQLite database.
