# Nexy Examples

Minimal, runnable examples that replace the former demo application that used to
live in `src/`. Each subfolder is a self-contained Nexy app: run it from inside
the folder so the config and the file-based router resolve against it.

## Structure

```text
examples/
├── FBR/                          # File-based router
│   ├── api/
│   │   ├── minimal/              # No ORM
│   │   ├── sqlmodel/
│   │   ├── sqlalchemy/
│   │   └── tortoise/
│   └── web/
│       ├── basics/               # Server-rendered .nexy pages
│       │   ├── minimal/          # Hand-written, smallest possible app
│       │   ├── none/             # `nexy new` without a client framework
│       │   ├── react/
│       │   ├── preact/
│       │   ├── solid/
│       │   ├── svelte/
│       │   ├── vue/
│       │   └── react-sqlmodel/
│       └── CSR/                  # Client-side routing
│           ├── react/
│           ├── preact/
│           ├── solid/
│           ├── svelte/
│           └── vue/
└── Modular/                      # Module/controller/service router
    ├── api/
    │   ├── minimal/              # No ORM
    │   ├── sqlmodel/
    │   ├── sqlalchemy/
    │   └── tortoise/
    └── web/
        └── basics/
            ├── none/             # `nexy new` without a client framework
            ├── react/
            ├── preact/
            ├── solid/
            ├── svelte/
            ├── vue/
            └── react-sqlalchemy/
```

## Matrix

### File-based router (`FBR/`)

| Example | Type | Frontend | Notes |
|---|---|---|---|
| `FBR/api/minimal` | API | none | No ORM |
| `FBR/api/sqlmodel` | API | none | SQLModel |
| `FBR/api/sqlalchemy` | API | none | SQLAlchemy |
| `FBR/api/tortoise` | API | none | Tortoise-ORM |
| `FBR/web/basics/minimal` | Web | server-rendered `.nexy` | Hand-written, 4 files |
| `FBR/web/basics/none` | Web | server-rendered `.nexy` | Generated, no client framework |
| `FBR/web/basics/react` | Web | React | |
| `FBR/web/basics/preact` | Web | Preact | |
| `FBR/web/basics/solid` | Web | Solid | |
| `FBR/web/basics/svelte` | Web | Svelte | |
| `FBR/web/basics/vue` | Web | Vue | |
| `FBR/web/basics/react-sqlmodel` | Web | React | SQLModel |
| `FBR/web/CSR/react` | Web | React | Client-side routing |
| `FBR/web/CSR/preact` | Web | Preact | Client-side routing |
| `FBR/web/CSR/solid` | Web | Solid | Client-side routing |
| `FBR/web/CSR/svelte` | Web | Svelte | Client-side routing |
| `FBR/web/CSR/vue` | Web | Vue | Client-side routing |

### Modular router (`Modular/`)

| Example | Type | Frontend | Notes |
|---|---|---|---|
| `Modular/api/minimal` | API | none | No ORM |
| `Modular/api/sqlmodel` | API | none | SQLModel |
| `Modular/api/sqlalchemy` | API | none | SQLAlchemy |
| `Modular/api/tortoise` | API | none | Tortoise-ORM |
| `Modular/web/basics/none` | Web | server-rendered `.nexy` | Generated, no client framework |
| `Modular/web/basics/react` | Web | React | |
| `Modular/web/basics/preact` | Web | Preact | |
| `Modular/web/basics/solid` | Web | Solid | |
| `Modular/web/basics/svelte` | Web | Svelte | |
| `Modular/web/basics/vue` | Web | Vue | |
| `Modular/web/basics/react-sqlalchemy` | Web | React | SQLAlchemy |

- **File-based** (`FBR`): routes are files under `src/routes/`
  (`index.nexy`, `about.tsx`, `[slug].nexy`, `layout.nexy`…).
- **Modular**: routes are declared by an `AppModule` in `src/apps/`, with
  controllers and services next to it.
- **CSR**: client-side routing; there are no `.nexy` pages, and the routes are
  framework files under `src/routes/`.
- **ORM**: adds `src/configs/db.py`, a user model/service, and for the modular
  router a `users` app.

The non-CSR, no-ORM projects are the official template snapshots cloned by
`nexy new -t`. The CSR and ORM projects are rendered from the templates bundled
with the package, using the same configuration as the interactive
questionnaire.

Dependencies are intentionally **not** installed in the generated examples:
they are source snapshots, so the repository stays light.

## Run an example

```bash
cd examples/FBR/web/basics/react
uv sync          # Python dependencies (published nexy)
pnpm install     # or: bun install
nexy dev
```

API examples need no Node step:

```bash
cd examples/FBR/api/sqlmodel
uv sync
cp .env.example .env
nexy dev
```

CSR examples are run the same way as the other web examples:

```bash
cd examples/FBR/web/CSR/react
uv sync
pnpm install
nexy dev
```

To run an example against this checkout instead of the published package:

```bash
uv venv
uv pip install -e ../..
nexy dev
```

## Database

ORM examples ship an `.env.example` whose default is SQLite
(`DATABASE_URL=sqlite:///dev.db`, or `sqlite://dev.db` for Tortoise-ORM).
Copy it to `.env` and change the URL for PostgreSQL or MySQL, adding the
matching driver to `pyproject.toml`.

Migration directories are not included: initialize Alembic (SQLModel,
SQLAlchemy) or Aerich (Tortoise-ORM) before the first schema change.

## Regenerate the generated examples

```bash
python scripts/scaffold_examples.py           # skip existing directories
python scripts/scaffold_examples.py --force   # overwrite them
```

The generator writes the 27 generated projects into this tree. It skips
dependency installation and migration initialization on purpose.
`FBR/web/basics/minimal` is hand-written and is never touched by the script.

## Conventions

- `.nexy` files use `---` frontmatter for Python logic, then HTML-like markup.
- The file-based router reads `src/routes` relative to the app directory
  (`ROUTER_PATH` in `nexy/config`), one route file per path.
- `layout.nexy` wraps child routes and receives them through the `children`
  prop.

See `docs/` for the full router, component, and configuration reference.
