# Banking REST Service

A production-ready Banking REST Service built with an asynchronous Python backend and a responsive React frontend. This project demonstrates clean architecture, robust security, strict double-entry ledger mathematics, and full containerization.

## System Overview & Architecture

- **Backend:** FastAPI, Python 3.9+, Async SQLAlchemy 2.0, SQLite (via `aiosqlite`).
- **Frontend:** React 18, Vite, Tailwind CSS, React Router DOM, Axios.
- **Security:** JWT Authentication (15-minute strict timeouts), bcrypt password hashing, IDOR protection.
- **Infrastructure:** Docker, Docker Compose, Nginx.

---

## Prerequisites

To run this application, you must have the following installed on your machine:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

---

## Deployment

The absolute easiest way to evaluate this application is via the included interactive script. It will automatically build the images, start the containers in the background, and prompt you to inject synthetic testing data (users, accounts, simulated transaction matrices).

*For manual deployment steps, architecture details, and troubleshooting, please see [docs/Deployment.md](docs/Deployment.md).*

**For Mac/Linux:**

1.  Make the script executable: `chmod +x start.sh`
2.  Run the script: `./start.sh`

**For Windows (PowerShell):**

1.  Run the script from your terminal: `.\start.ps1`

_Note: The script contains defensive file-existence checks. If `seed_data.py` is missing from the image for any reason, the pipeline will gracefully warn you rather than crashing._

**Access the Applications:**

- **Frontend Dashboard:** [http://localhost:8080](http://localhost:8080)
- **Interactive API documentation (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Testing

The backend includes a comprehensive, 23-assertion test suite that validates unit logic (bypassing HTTP) and end-to-end integration logic. The suite uses a dedicated, isolated in-memory SQLite database to prevent polluting production data.

To execute the test suite (requires an active Python virtual environment with `pytest` installed):

```bash
# Ensure you are at the project root
pytest tests/
```

_Coverage includes robust negative testing (e.g., overdrafts, invalid emails, 401 unauthenticated requests) and IDOR boundaries._

---

## API Documentation

While the API exposes an interactive Swagger UI at `/docs` when running, below is a quick reference for the core REST endpoints.

**Authentication:**  
Except for `signup` and `login`, all endpoints require a Bearer token. Pass this in the `Authorization` header:
`Authorization: Bearer <your_jwt_token>`

### Core Endpoints

#### Auth

**Register a New User**

- `POST /auth/signup`
- **Description:** Registers a new user account.
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123"
  }
  ```

**Login**

- `POST /auth/login`
- **Description:** Authenticates a user and returns a 15-minute JWT Bearer token.
- **Body:**
  ```json
  {
    "username": "user@example.com",
    "password": "securepassword123"
  }
  ```

#### Account Holders

**Get My Profile**

- `GET /account-holders/me`
- **Description:** Returns the current authenticated user's profile.

**Update My Profile**

- `PATCH /account-holders/me`
- **Description:** Updates the current user's profile (email only).
- **Body:**
  ```json
  {
    "email": "new.email@example.com"
  }
  ```

#### Accounts

**Get My Accounts**

- `GET /accounts/me`
- **Description:** Retrieves all financial bank accounts linked to the authenticated user.

#### Transfers

**Execute Transfer**

- `POST /transfers/`
- **Description:** Executes a mathematically strict transfer between accounts.
- **Body:**
  ```json
  {
    "from_account_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "to_identifier": "receiver@example.com",
    "amount": 5000
  }
  ```
  _(Note: Amounts are heavily enforced as integer cents. e.g., `5000` = $50.00)_

#### Transactions

**List Transactions**

- `GET /accounts/{account_id}/transactions`
- **Description:** Fetches a paginated ledger of debits and credits for a specific account.

#### Statements

**Generate Statement**

- `GET /accounts/{account_id}/statement`
- **Description:** Generates a summarized financial statement with starting/ending balances.


---

## Design Decisions Extract

1.  **Strict Double-Entry Accounting:** In `app/services/transfer_service.py`, money is never generically manipulated. Database transactions create two strict `Transaction` records (a negative debit for the sender, and a positive credit for the receiver) to guarantee mathematical integrity.
2.  **Legacy Data Compatibility:** The frontend `TransactionHistory.jsx` evaluates ledger rendering based on raw arithmetic (`amount > 0`) rather than semantic string labels. This ensures UI resilience even if anomalous data enters the historical ledger.
3.  **Entity Resolution over UUIDs:** In Phase 6, the system upgraded transfer routing to natively resolve counterparties by `email` (`to_identifier`) via dynamic database table joins, insulating the React frontend from managing obscure UUID lookups.
4.  **Security Fail-Safes:** JWT tokens expire automatically after 15 minutes. The frontend implements a global Axios interceptor to catch `401 Unauthorized` responses and defensively purge Chrome's `localStorage` to force re-authentication.
