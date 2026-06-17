# Python Service README Template

Copy this template and fill every placeholder. Do not ship a README with `<placeholder>` values.

---

```markdown
# <Service Name>

<One sentence: what this service does and which system it is part of.>

## Requirements

- Python 3.11+
- <Framework>: <version> (e.g., FastAPI 0.110+)
- <Database>: <version> (e.g., PostgreSQL 15+)
- `pip` 23+ or `uv`

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/businessnext/<service-name>.git
cd <service-name>

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install the project with development dependencies
pip install -e ".[dev]"

# 4. Copy the sample environment file and fill in your values
cp .env.example .env
```

## Configuration

All configuration is read from environment variables (or a `.env` file).

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DATABASE_URL` | `str` | — | PostgreSQL connection string. **Required.** |
| `JWT_SECRET` | `str` | — | Secret key for JWT signing. **Required.** |
| `ALLOWED_ORIGINS` | `str` | `http://localhost:3000` | Comma-separated list of allowed CORS origins. |
| `DEBUG` | `bool` | `false` | Enable debug mode (disables docs in production). |
| `LOG_LEVEL` | `str` | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`. |

Sample `.env` file:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/myservice
JWT_SECRET=local-dev-secret-change-in-production
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
DEBUG=true
LOG_LEVEL=DEBUG
```

## Running the Service Locally

```bash
# Start the server (reload on file changes)
uvicorn my_service.main:app --reload --port 8000

# Or use the Makefile shortcut
make dev
```

The service will be available at `http://localhost:8000`.  
Interactive API docs: `http://localhost:8000/docs` (only available when `DEBUG=true`).

## Running Tests

```bash
# Run the full test suite
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run a specific module
pytest tests/unit/test_user_service.py -v

# Run only fast (non-integration) tests
pytest -m "not integration"
```

## Project Layout

```
<service-name>/
├── src/
│   └── my_service/     ← application source code
├── tests/
│   ├── unit/           ← pure unit tests (no I/O)
│   └── integration/    ← tests requiring a database or HTTP
├── pyproject.toml      ← project metadata, dependencies, tool config
├── .env.example        ← sample environment variable file
└── Makefile            ← developer convenience commands
```

## API Overview

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/users` | Create a new user account |
| `GET` | `/users/{id}` | Retrieve a user by ID |
| `PUT` | `/users/{id}` | Update a user's profile |
| `DELETE` | `/users/{id}` | Deactivate a user account |
| `POST` | `/auth/login` | Authenticate and receive a JWT |
| `POST` | `/auth/refresh` | Refresh an expiring JWT |

Full OpenAPI schema available at `http://localhost:8000/openapi.json`.

## Contributing

1. Create a branch from `develop`: `git checkout -b feature/<ticket>-<description>`
2. Make your changes; all new code must have type annotations and docstrings
3. Run the quality gate before opening a PR:
   ```bash
   ruff check .
   mypy .
   pytest --cov=src
   ```
4. Commit using conventional format: `feat(<scope>): <description>`
5. Open a PR targeting `develop`

All PR checks (ruff, mypy, pytest, bandit) must pass before merge.
```
