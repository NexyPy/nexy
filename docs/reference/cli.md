# CLI

The binary is `nx` (also installed as `nexy`). `uvx nexy new` creates a project (`uvx` comes with
uv). Run every other command inside the project's virtual environment, or through `uv run`, for
example `uv run nexy dev`: that is where your own packages are.

## Commands

| Command | Alias | What it does |
|---|---|---|
| `nx dev` | `nx d` | development server: compile on change, Vite, HMR |
| `nx start` | `nx s` | production server on the compiled output |
| `nx build` | `nx b` | production build |
| `nx new` | `nx n` | scaffold a project |
| `nx init` | `nx i` | add Nexy to an existing project |
| `nx add` | - | add a UI component from the registry or a URL to `src/components/ui` |
| `nx migrate` | `nx m` | create or apply database migrations with Alembic or Aerich |
| `nx check` | `nx c` | type-check: mypy on Python, `tsc` on TypeScript |
| `nx format` | `nx f` | format Python (ruff), JS/TS (prettier), `.nexy` files |
| `nx test` | - | run pytest; `--client` adds vitest |
| `nx skills` | - | add or refresh the skills, `AGENTS.md` and `CLAUDE.md` for coding agents |

## Flags

| Command | Flag | Default |
|---|---|---|
| `dev`, `start` | `--port` | `usePort`, `3000` |
| `dev`, `start` | `--host` | `useHost`, `0.0.0.0` |
| `build` | `--check` | off - runs ruff and mypy after the build |
| `format` | `--check` | off - report instead of rewriting |
| `test` | `--client` | off - also run vitest instead of pytest alone |
| `test` | `--no-server` | on - skip pytest when you only want client tests |
| `new` | `--template`, `-t` | none - clone a registered template without prompts |
| `new` | `--no-agents` | agents on - skip `AGENTS.md` and the agent skills |
| `add` | `--ui`, `--url` | off - force a registry name or a URL when it is ambiguous |
| `add` | `--all`, `-a` | off - add every component of the registry |
| `add` | `--sha256` | none - expected digest of a remote component; a mismatch aborts |
| `migrate` | `--init` | off - write the Alembic or Aerich setup |
| `migrate` | `--upgrade`, `-u` | off - apply the migrations instead of writing a new one |
| `migrate` | `--message`, `-m` | empty - name of the new revision |

## Output

Long steps (installing packages, compiling, bundling) show a spinner with the elapsed time, then
leave one line behind: `✔ uv sync .venv  1.4s`. A group of steps (the installs of `nx new`) shows a
progress bar with the number of finished steps, `━━━━────  2/5`; a single step (`nx add`) shows a
bar that pulses while it runs. Dev logs read `GET » /about 200 in 12ms` for requests and
`vite » ...` for Vite. A failing step prints the last
lines of the command's output instead of hiding it. Terminals that cannot render Unicode get
`+` and `x`.

## Errors while `nx dev` runs

Saving a broken file never stops the server. A `.py` file with a syntax error is reported with its
file and line, and the server keeps serving the last working version until you fix it:

```text
  nexy » error  src/routes/users.py:3
  SyntaxError: invalid syntax

    1 | import json
    2 |
  > 3 | def GET(:
                ^
    4 |     x = 1
    5 |     return {"v": 2}

  Fix it and save: the server keeps its last working version.
```

A file that parses but fails when the application loads (a missing import, an error at module
level) is reported the same way and `nx dev` waits for your next save; nothing is served until the
application loads again. A valid save reads `nexy » update <file>` while the server reloads. Markdown files outside
`src/routes`, such as `README.md`, are not pages and do not trigger anything.
`nx start` is stricter: it exits with code 1, and starts nothing, if a route file cannot load.

## Questions of `nx new`

`nx new` asks, in this order: file-based router, project type (web or API), client-side routing,
client framework, how to style the app, import alias, ORM, database and database URL. Every option has a short
description and the current one is highlighted. Questions that do not apply are skipped (an API
project has no framework or style; choosing **No database** as the ORM skips the database and URL).
Move with the arrow keys (or `j`/`k`, or a number), confirm with `enter`, go back to the previous
question with `←` or `esc`, quit with `ctrl+c`.

| Question | Choices |
|---|---|
| Import alias | `@` (`@/components/...` points to `src/`), or another prefix such as `~` or `#app` |
| Style | Tailwind CSS, UnoCSS, Vanilla CSS, Other (no CSS tool, same plain stylesheet as Vanilla) |
| ORM | SQLModel, SQLAlchemy, Tortoise-ORM, No database |
| Database (with an ORM) | SQLite, PostgreSQL, Neon, MySQL / MariaDB, Other (you type the URL) |

The database driver for the chosen ORM is installed with it (`psycopg`, `pymysql`, `asyncpg` or
`aiomysql`), and the URL is written to `.env`.

Before installing packages, `nx new` checks the connection. Without one, it skips the installs and
tells you to run `uv sync` and your package manager's install later. With one, it prints the
latency and download speed, and warns when the connection is slow (over 400 ms, or under
100 KB/s). Each install line names the tool and the folder it fills, for example
`pnpm install node_modules` or `uv sync .venv`.

## What `dev`, `build` and `start` create

Before they run, the three commands create an empty `__init__.py` in `src/` and in every folder
under it that holds a `.py` or `.nexy` file, so a route such as `src/routes/users.py` imports the
same way in all of them. Existing files are never touched, and `nx dev` does the same again when
you add a folder. Python bytecode goes to `__nexy__/__pycache__`, so no `__pycache__` folder
appears next to your sources.

## Language

The command line speaks English, Chinese, Hindi, Spanish, Portuguese, French, German, Japanese,
Russian, Korean, Indonesian and Arabic. It uses the first of these that it supports:

1. the `NEXY_LANG` environment variable (`NEXY_LANG=ja nx dev`);
2. the locale variables of your shell (`LC_ALL`, `LC_MESSAGES`, `LANG`, then `LANGUAGE`);
3. the language of your operating system.

Anything else is English, and so is any message a language does not have yet. Only what `nx`
prints is translated: compiler errors, tracebacks and the output of the tools it runs stay as they
are. The translations have not been reviewed by native speakers yet:
corrections are welcome as pull requests to `nexy/modules/i18n/<language>.json`.

## Build behaviour

`nx build` compiles the routes, then bundles the client when `useVite` is on.

> [!NOTE]
> there is no `--static` flag. Static hosting is a deployment choice, not a build
> mode - see [Deploy](../deployment/README.md).

## Working on Nexy itself

Inside this repository the gates are:

```bash
python scripts/verify.py             # lint, format, typecheck, tests
python scripts/audit_dependencies.py # supply-chain audit against the lock
```

## Next steps

- [Getting started](../getting-started/quick-start.md): first project
- [Testing](../guides/testing.md): what `nx test` runs
- [Deploy](../deployment/README.md): `build` and `start` in production
