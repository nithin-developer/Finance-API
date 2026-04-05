# Finance Dashboard Backend API

Production-style backend built with FastAPI and PostgreSQL for a Role-Based Finance Dashboard system.

The system is designed for organizational finance tracking, where data is globally visible based on role. This enables meaningful analytics and aggregation. The architecture also supports extending to user-specific data scoping if required.

---

## Highlights

* JWT authentication with role-based claims
* Strict Role-Based Access Control (RBAC)

  * viewer: dashboard only
  * analyst: dashboard + read records
  * admin: full access
* Financial record CRUD with filtering, search, and pagination
* Dashboard analytics APIs

  * summary
  * category breakdown
  * monthly trends
  * recent transactions
* Soft delete for data safety
* Uses Decimal-safe money fields (`NUMERIC(14,2)`), not floats.
* Audit logging support
* Configurable CORS middleware
* Configurable per-client rate limiting with 429 protection (SlowAPI)
* Structured error handling

---

## Tech Stack

* FastAPI
* SlowAPI (rate limiting)
* SQLAlchemy 2.0 (async)
* PostgreSQL (asyncpg)
* Alembic (migrations)
* Pydantic (validation)
* Pytest + HTTPX (testing)

---

## Project Structure


```
finance-backend
├─ alembic
│  ├─ env.py
│  ├─ script.py.mako
│  └─ versions
│     └─ 0001_initial_schema.py
├─ alembic.ini
├─ app
│  ├─ core
│  │  ├─ config.py
│  │  ├─ errors.py
│  │  ├─ security.py
│  │  └─ __init__.py
│  ├─ db
│  │  ├─ database.py
│  │  └─ __init__.py
│  ├─ dependencies
│  │  ├─ auth.py
│  │  ├─ rbac.py
│  │  └─ __init__.py
│  ├─ main.py
│  ├─ models
│  │  ├─ audit_log.py
│  │  ├─ financial_record.py
│  │  ├─ user.py
│  │  └─ __init__.py
│  ├─ routes
│  │  ├─ auth.py
│  │  ├─ dashboard.py
│  │  ├─ records.py
│  │  ├─ users.py
│  │  └─ __init__.py
│  ├─ schemas
│  │  ├─ auth.py
│  │  ├─ common.py
│  │  ├─ dashboard.py
│  │  ├─ record.py
│  │  ├─ user.py
│  │  └─ __init__.py
│  ├─ services
│  │  ├─ audit_service.py
│  │  ├─ dashboard_service.py
│  │  ├─ record_service.py
│  │  └─ __init__.py
│  └─ __init__.py
├─ README.md
├─ requirements.txt
└─ tests
   ├─ conftest.py
   ├─ test_auth.py
   ├─ test_dashboard.py
   ├─ test_rbac.py
   ├─ test_records.py
   └─ __init__.py

```

---

## Design Decisions

* The system is designed as an organizational finance dashboard rather than a personal expense tracker.
* Data is globally visible based on role to enable aggregation and insights.
* RBAC is enforced using FastAPI dependencies for clean and reusable access control.
* Business logic is separated into service layers for maintainability.
* Soft delete is used to preserve historical data instead of permanent deletion.

---

## Environment Setup

Copy `.env.example` to `.env` and configure:

* DATABASE_URL
* SECRET_KEY
* FIRST_ADMIN_EMAIL
* FIRST_ADMIN_PASSWORD
* CORS_ALLOW_ORIGINS
* RATE_LIMIT_REQUESTS
* RATE_LIMIT_WINDOW_SECONDS

If AUTO_CREATE_TABLES=true, tables will be created automatically on startup for local development.

Recommended for local frontend integration:

* `CORS_ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000`
* `CORS_ALLOW_METHODS=GET,POST,PUT,PATCH,DELETE,OPTIONS`
* `CORS_ALLOW_HEADERS=Authorization,Content-Type`

Rate limiting defaults:

* `RATE_LIMIT_ENABLED=true`
* `RATE_LIMIT_REQUESTS=100`
* `RATE_LIMIT_WINDOW_SECONDS=60`
* `RATE_LIMIT_EXEMPT_PATHS=/health,/docs,/redoc,/openapi.json`

---

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Run the API

```bash
uvicorn app.main:app --reload
```

API Docs:

* Swagger UI: http://127.0.0.1:8000/docs
* ReDoc: http://127.0.0.1:8000/redoc

---

## Database Migration

```bash
alembic upgrade head
```

---

## Authentication Flow

1. User logs in via `/auth/login`
2. Receives a JWT token
3. Token must be sent in headers:

Authorization: Bearer <token>

4. Role is extracted from the token for access control

---

## API Overview

### Auth

* POST /auth/register (admin)
* POST /auth/login
* GET /auth/me
* POST /auth/change-password

---

### Users

* GET /users (admin)
* GET /users/{id} (admin)
* PUT /users/{id}/role (admin)
* PUT /users/{id}/status (admin)
* PUT /users/me (profile update)
* DELETE /users/{id} (admin, soft delete)

---

### Records

* POST /records (admin)
* GET /records (analyst, admin)
* GET /records/{id} (analyst, admin)
* PUT /records/{id} (admin)
* DELETE /records/{id} (admin, soft delete)

Filtering example:

GET /records?type=income&category=food&start_date=2026-01-01

Pagination example:

GET /records?page=1&limit=10

Search example:

GET /records?q=rent

---

### Dashboard

* GET /dashboard/summary
* GET /dashboard/category-breakdown
* GET /dashboard/monthly-trends
* GET /dashboard/recent

---

## Role Matrix

| Role    | Dashboard | Read Records | Write Records | User Management |
| ------- | --------- | ------------ | ------------- | --------------- |
| viewer  | Yes       | No           | No            | No              |
| analyst | Yes       | Yes          | No            | No              |
| admin   | Yes       | Yes          | Yes           | Yes             |

---

## Database Schema

### Users

* id (UUID)
* name
* email
* password_hash
* role
* is_active
* created_at

### Financial Records

* id (UUID)
* user_id
* amount
* type (income / expense)
* category
* date
* notes
* created_at

---

## Example Responses

### Dashboard Summary

```json
{
  "total_income": 50000,
  "total_expense": 20000,
  "net_balance": 30000
}
```

### Category Breakdown

```json
[
  { "category": "Food", "total": 5000 },
  { "category": "Rent", "total": 10000 }
]
```

---

## Error Handling

The API returns structured error responses:

```json
{
  "detail": "Unauthorized"
}
```

Common status codes:

* 400: Bad Request
* 401: Unauthorized
* 403: Forbidden
* 404: Not Found
* 422: Validation Error
* 429: Too Many Requests (rate limit exceeded)

---

## Initial Setup

On first run, an admin user is created using:

* FIRST_ADMIN_EMAIL
* FIRST_ADMIN_PASSWORD

---

## Quick Test Flow

1. Login using admin credentials
2. Create records via `/records`
3. Access dashboard endpoints
4. Test role restrictions using different users

---

## Testing

```bash
pytest -q
```

---

## Future Improvements

* Multi-tenant support (organization-based isolation)
* Granular permission system beyond roles
* Export reports (CSV/PDF)
* Real-time analytics

---

## Notes

This project focuses on clean backend architecture, correct data handling, and clear API design rather than unnecessary complexity.

---

> Thanks for checking out the Finance Dashboard Backend API! Feel free to explore the code and reach out if you have any questions or suggestions. Built with ❤️ by Nithin.