# react-sqlmodel

Web application built with [Nexy](https://github.com/NexyPy/nexy), using **React** for client components.

## Getting started

```bash
# Install dependencies
uv sync

# Start development server
nexy dev
```

## Project structure

```
src/
  routes/          # File-based routes
  components/      # Shared UI components
  models/          # Data models
  configs/         # Application configuration
public/            # Static assets
```

## Commands

| Command          | Description         |
|------------------|---------------------|
| `nexy dev`       | Start dev server    |
| `nexy build`     | Build for production|
| `nexy start`     | Start in production |

## Database

This example uses **SQLModel**. `.env.example` defaults to
`DATABASE_URL=sqlite:///dev.db`; copy it to `.env` and change the URL for
PostgreSQL or MySQL (add the matching driver to `pyproject.toml`).

Migration directories are not included: initialize Alembic or Aerich
before the first schema change.
