---
name: python-readme-template
description: README template structure for BusinessNext Python services — required sections, content guidelines, and examples. Used by python-doc-writer.
user-invocable: false
argument-hint: ""
---

Standard README structure for Python microservices at BusinessNext. Every service repository must have a README.md with these sections so that any developer can install, run, test, and understand the service without prior context.

## Additional Resources

- [reference/template-structure.md](reference/template-structure.md) — the full section-by-section template with placeholders
- [reference/examples.md](reference/examples.md) — filled-in examples from a real-style Python FastAPI service

## Steps

1. **Title and description** — service name as the heading; one sentence describing what the service does and who uses it
2. **Requirements** — Python version, key runtime dependencies (framework, database driver), development tool versions
3. **Installation** — step-by-step from clone to running locally; include virtualenv creation and `pip install -e ".[dev]"`
4. **Running the service** — how to start the server locally; environment variable requirements; sample `.env` content
5. **Running tests** — `pytest` command; how to run with coverage; how to run a specific module
6. **Project layout** — directory tree with a one-line description of each top-level folder
7. **Configuration reference** — table of all environment variables with type, default, and description
8. **API overview** — table of endpoints (method, path, description) — not a full reference, just a map
9. **Contributing** — branch naming, commit format, how to run the full quality gate before a PR

## Rules

- **Every section is mandatory** — a README missing "Running tests" forces the next developer to read the CI config to figure it out
- **Commands must be copy-pasteable** — no placeholders like `<your-database-url>`; use a clearly labeled sample value
- **Configuration table must be complete** — every env var the service reads must appear; omitting one causes production incidents
- **Keep the layout table shallow** — list only `src/`, `tests/`, and top-level config files; do not recursively list every module
- **Do not duplicate the API reference** — the README table shows paths and one-line descriptions; full schema documentation lives in `/docs` or the OpenAPI spec
