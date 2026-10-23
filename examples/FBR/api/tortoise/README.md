# tortoise

RESTful API built with [Nexy](https://github.com/NexyPy/nexy), using **Tortoise-ORM** for data access.

## Getting started

```bash
# Install dependencies
uv sync

# Start development server
nexy dev
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/` | API root |

## Commands

| Command          | Description         |
|------------------|---------------------|
| `nexy dev`       | Start dev server    |
| `nexy build`     | Build for production|
| `nexy start`     | Start in production |

## Database

This example uses **Tortoise-ORM**. `.env.example` defaults to
`DATABASE_URL=sqlite://dev.db`; copy it to `.env` and change the URL for
PostgreSQL or MySQL (add the matching driver to `pyproject.toml`).

Migration directories are not included: initialize Alembic or Aerich
before the first schema change.
