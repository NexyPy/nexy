# dashboard

Web application built with [Nexy](https://github.com/NexyPy/nexy), using **React** for client components.

## Getting started

```bash
# Install dependencies (creates .venv)
uv sync

# Activate the virtual environment: every nexy command runs inside it
.venv\Scripts\activate   # Windows; on macOS and Linux: source .venv/bin/activate

# Start development server
nexy dev
```

Outside the virtual environment a package of this project (your ORM, for example) cannot be found.
To skip the activation, run `uv run nexy dev`.

## Project structure

```
src/
  apps/            # Modular application modules
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
