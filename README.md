# Banking REST Service

A production-ready Banking REST Service built with an asynchronous Python backend and a responsive React frontend. This project demonstrates clean architecture, robust security, strict double-entry ledger mathematics, and full containerization.

## System Overview & Architecture

*   **Backend:** FastAPI, Python 3.9+, Async SQLAlchemy 2.0, SQLite (via `aiosqlite`).
*   **Frontend:** React 18, Vite, Tailwind CSS, React Router DOM, Axios.
*   **Security:** JWT Authentication (15-minute strict timeouts), bcrypt password hashing, IDOR protection.
*   **Infrastructure:** Docker, Docker Compose, Nginx.

---

## Prerequisites

To run this application, you must have the following installed on your machine:
*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/)

---

## Entry Point 1: The Quickstart Script

The absolute easiest way to evaluate this application is via the included interactive bash script. It will automatically build the images, start the containers in the background, and prompt you to inject synthetic testing data.

1.  Make the script executable (if not already):
    ```bash
    chmod +x start.sh
    ```
2.  Run the script:
    ```bash
    ./start.sh
    ```
3.  When prompted, type `y` to seed the database with synthetic users, accounts, and realistic transaction histories.

**Access the Applications:**
*   **Frontend Dashboard:** [http://localhost:8080](http://localhost:8080)
*   **Interactive API documentation (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Entry Point 2: Manual Step-by-Step Deployment

If you prefer to stand up the environment manually or need to debug specific components:

### 1. Environment Variables
Both services use defaults, but you can override ports by creating an `.env` file in the root directory:
```env
API_PORT=8000
FRONTEND_PORT=8080
```

### 2. Starting the Backend Standalone
```bash
docker-compose up -d --build api
```
*The API evaluates the `data/banking.db` SQLite file locally using volume mapping to persist data across container restarts.*

### 3. Starting the Frontend Standalone
```bash
docker-compose up -d --build frontend
```
*The frontend uses a multi-stage Docker build to compile the React/Vite assets down to static files, serving them blazing fast behind an Alpine Nginx web server configured for SPA fallback routing.*

### 4. Executing Database Migrations/Seeding Manually
If you opted not to use the Quickstart script, you can seed the SQLite database manually:
```bash
docker-compose exec api python seed_data.py
```

---

## Testing

The backend includes a comprehensive, 23-assertion test suite that validates unit logic (bypassing HTTP) and end-to-end integration logic. The suite uses a dedicated, isolated in-memory SQLite database to prevent polluting production data.

To execute the test suite (requires an active Python virtual environment with `pytest` installed):
```bash
# Ensure you are at the project root
pytest tests/
```
*Coverage includes robust negative testing (e.g., overdrafts, invalid emails, 401 unauthenticated requests) and IDOR boundaries.*

---

## Design Decisions Extract

1.  **Strict Double-Entry Accounting:** In `app/services/transfer_service.py`, money is never generically manipulated. Database transactions create two strict `Transaction` records (a negative debit for the sender, and a positive credit for the receiver) to guarantee mathematical integrity.
2.  **Legacy Data Compatibility:** The frontend `TransactionHistory.jsx` evaluates ledger rendering based on raw arithmetic (`amount > 0`) rather than semantic string labels. This ensures UI resilience even if anomalous data enters the historical ledger.
3.  **Entity Resolution over UUIDs:** In Phase 6, the system upgraded transfer routing to natively resolve counterparties by `email` (`to_identifier`) via dynamic database table joins, insulating the React frontend from managing obscure UUID lookups.
4.  **Security Fail-Safes:** JWT tokens expire automatically after 15 minutes. The frontend implements a global Axios interceptor to catch `401 Unauthorized` responses and defensively purge Chrome's `localStorage` to force re-authentication.
