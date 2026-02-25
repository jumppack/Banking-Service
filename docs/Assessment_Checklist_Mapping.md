# Assessment Checklist Mapping

This document provides a direct map between the requested assessment deliverables and the corresponding implementations within the `mulitple-environemtn` branch of this repository.

## 1. Project Requirements

| Requirement | Endpoint(s) | Code Location | Tests | Docs | How to Verify |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Signing Up** | `POST /auth/signup` | `app/api/routers/auth.py` | `tests/api/test_auth.py` | README - Auth | `curl -X POST /auth/signup -d '{"email":"test@test.com", "password":"pw"}'` |
| **Authentication** | `POST /auth/login` | `app/api/routers/auth.py` | `tests/api/test_auth.py` | README - Auth | `curl -X POST /auth/login` to retrieve JWT token |
| **Account Holders** | `GET /account-holders/me`<br>`PATCH /account-holders/me` | `app/api/routers/account_holders.py` | `tests/api/test_account_holders.py` | README - Account Holders | Call `GET /account-holders/me` with Bearer token |
| **Accounts** | `GET /accounts/me`<br>`POST /accounts/` | `app/api/routers/accounts.py` | `tests/api/test_accounts.py` | README - Accounts | Call `GET /accounts/me` with Bearer token |
| **Transactions (List)** | `GET /accounts/{account_id}/transactions` | `app/api/routers/transactions.py`<br>`app/services/transaction_service.py` | `tests/api/test_transactions.py` | README - Transactions | Call `GET /accounts/{id}/transactions` |
| **Transactions (Post)** | `POST /accounts/{id}/transactions/deposit`<br>`POST /accounts/{id}/transactions/withdraw` | `app/api/routers/transactions.py`<br>`app/services/transaction_service.py` | `tests/api/test_transaction_posting.py` | README - Transactions | Call `POST` deposit endpoint with valid amount > 0 |
| **Money Transfer** | `POST /transfers/` | `app/api/routers/transfers.py`<br>`app/services/transfer_service.py` | `tests/api/test_transfers.py` | README - Transfers | Call `POST /transfers/` with `gt=0` amount |
| **Cards** | `POST /cards/`<br>`GET /cards/` | `app/api/routers/cards.py` | `tests/api/test_cards.py` | - | Call `POST /cards/` to generate a 16-digit card |
| **Statements** | `GET /accounts/{account_id}/statement` | `app/api/routers/statements.py` | `tests/api/test_statements.py` | README - Statements | Call `GET /accounts/{id}/statement` |
| **Database (SQLite)** | N/A | `app/db/session.py`<br>`data/banking.db` | `tests/conftest.py` | - | Check `sqlite+aiosqlite` in config |
| **Database Migrations** | N/A | `alembic/versions/` | - | - | Run `alembic upgrade head` (auto-runs in Docker) |
| **Test Suite** | N/A | `tests/` directory | - | README - Testing | Run `pytest tests/` |
| **Dockerfile** | N/A | `Dockerfile`<br>`frontend/Dockerfile` | - | - | Inspect `Dockerfile` for multi-stage structure |
| **docker-compose** | N/A | `docker-compose.yml` | - | - | Run `docker compose up --build` |
| **Structured Logs** | N/A | `app/core/logging.py` | - | - | Check container stdout or `logs/banking.log` |
| **Error Tracking** | N/A | `app/main.py` (Middlewares) | `tests/api/test_request_id.py` | README - Error Tracking | Check `X-Request-ID` and `error_id` on 500s |
| **Health Checks** | `GET /health`<br>`GET /ready`<br>`GET /live` | `app/api/routers/health.py` | `tests/api/test_probes.py` | README - Probes | `curl http://localhost:8000/ready` |
| **Graceful Shutdown** | N/A | `app/main.py` | - | - | Stop container and observe lifespan context exit |

## 2. Deliverables

| Requirement | Implementation Details | Location |
| :--- | :--- | :--- |
| **Source Code Organization** | Clean architecture separating routers (`app/api`), logic (`app/services`), ORM (`app/models`), and schemas (`app/schemas`). | `/app` directory |
| **Environment Configurations** | Strict overrides: `OS ENV` > `.env.{ENVIRONMENT}` > `.env`. File templates exist for development, testing, and production. | `.env.example`, `.env.development.example`, `.env.test.example`, `.env.production.example`, `app/core/config.py` |
| **Startup Scripts** | `start.sh` (Mac/Linux) and `start.ps1` (Windows) accept environment arguments (`./start.sh production`). They safely copy templates to `.env` and utilize cryptographic libraries to construct the secure `SECRET_KEY` natively to prevent exposing system secrets in git. | `start.sh`, `start.ps1` |
| **Documentation** | README provides Quickstart and core endpoint details. Detailed deployment instructions sit in `Deployment.md`. | `README.md`, `docs/Deployment.md`, `docs/Assessment_Checklist_Mapping.md` |
| **AI Usage Report** | Summary of LLM involvement, prompts used, and debugging assistance. | `AI_Usage_Report.md` |
| **Bonus: Frontend** | Native React Vite application interfacing with the complete API. | `/frontend` directory |

> **Note on downloading:** If downloading the source zip from GitHub directly instead of cloning, macOS and Linux sometimes hide dotfiles like `.env.development.example` by default. Ensure your extraction utility preserves hidden items, or clone the repository via `git clone`.

## 3. Quick Reviewer Flow

To evaluate the application from a completely cold start, run the automated setup wrappers:

```bash
# Evaluate Development configuration
./start.sh development

# Evaluate Production configuration
./start.sh production
```

Verify backend health natively:
```bash
curl http://localhost:8000/ready
curl http://localhost:8000/live
```

Execute the full comprehensive 40+ assertion integration suite natively (Ensure you have hydrated the python venv `pip install -r requirements.txt` first).
```bash
pytest tests/
```

**What to do if something fails:**
Every request yields a unique `X-Request-ID` trace header. Any internal logic fault (500 Server Error) transmits a specific `error_id` downstream. Search the application logs (`logs/banking.log`) or the Docker console stdout using the specific `error_id` to locate the exact python exception generating the fault.
