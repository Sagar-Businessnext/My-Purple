# README Examples — User Management Service

A filled-in example README for a FastAPI user management microservice.

---

```markdown
# User Management Service

Core user lifecycle service for the BusinessNext platform — handles registration,
authentication, profile management, and role assignment for all BusinessNext products.

## Requirements

- Python 3.11+
- FastAPI 0.110+
- PostgreSQL 15+
- `pip` 23+

## Installation

```bash
git clone https://github.com/businessnext/user-management-service.git
cd user-management-service

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
cp .env.example .env
# Edit .env and set DATABASE_URL and JWT_SECRET
```

## Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DATABASE_URL` | `str` | — | PostgreSQL async connection string. **Required.** Example: `postgresql+asyncpg://postgres:postgres@localhost:5432/users` |
| `JWT_SECRET` | `str` | — | Secret for HMAC-SHA256 JWT signing. **Required.** Minimum 32 characters. |
| `JWT_EXPIRY_MINUTES` | `int` | `30` | Access token lifetime in minutes. |
| `ALLOWED_ORIGINS` | `str` | `http://localhost:3000` | Comma-separated CORS origin allowlist. |
| `MAX_LOGIN_ATTEMPTS` | `int` | `5` | Consecutive failed logins before account lockout. |
| `DEBUG` | `bool` | `false` | Enables `/docs` and verbose error responses. Set `false` in production. |
| `LOG_LEVEL` | `str` | `INFO` | One of `DEBUG`, `INFO`, `WARNING`, `ERROR`. |

Sample `.env`:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/users_dev
JWT_SECRET=dev-only-secret-minimum-32-characters-long
JWT_EXPIRY_MINUTES=60
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
DEBUG=true
LOG_LEVEL=DEBUG
```

## Running the Service Locally

```bash
# Ensure PostgreSQL is running and .env is configured
uvicorn user_management.main:app --reload --port 8001

# Or
make dev
```

Service: `http://localhost:8001`  
API docs: `http://localhost:8001/docs` (requires `DEBUG=true`)

## Running Tests

```bash
# Full suite (requires a test PostgreSQL database)
pytest

# Unit tests only (no database required)
pytest tests/unit/ -v

# With coverage
pytest --cov=src --cov-report=term-missing

# Single test file
pytest tests/unit/test_user_service.py::test_create_user_sends_welcome_email -v
```

The integration tests expect a PostgreSQL instance at
`postgresql+asyncpg://postgres:postgres@localhost:5432/users_test`.
Run `make db-test` to create the test database.

## Project Layout

```
user-management-service/
├── src/
│   └── user_management/    ← application source
│       ├── models/         ← SQLAlchemy ORM models
│       ├── schemas/        ← Pydantic request/response models
│       ├── routers/        ← FastAPI route handlers
│       ├── services/       ← business logic
│       ├── repositories/   ← database access layer
│       ├── exceptions.py   ← domain exceptions
│       ├── config.py       ← pydantic-settings configuration
│       └── main.py         ← FastAPI app factory
├── tests/
│   ├── unit/               ← pure unit tests
│   └── integration/        ← database and HTTP integration tests
├── pyproject.toml
├── Makefile
└── .env.example
```

## API Overview

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/auth/register` | None | Register a new user |
| `POST` | `/auth/login` | None | Authenticate and receive JWT |
| `POST` | `/auth/refresh` | JWT | Refresh an expiring token |
| `GET` | `/users/me` | JWT | Get the authenticated user's profile |
| `PUT` | `/users/me` | JWT | Update the authenticated user's profile |
| `GET` | `/users/{id}` | JWT + Admin | Get a user by ID (admin only) |
| `DELETE` | `/users/{id}` | JWT + Admin | Deactivate a user account (admin only) |

## Contributing

1. Branch from `develop`: `feature/<JIRA-ID>-<short-description>`
2. Write type-annotated code; add or update tests
3. Before PR: `ruff check . && mypy . && pytest --cov=src`
4. Open PR targeting `develop`; all CI checks must pass
```
