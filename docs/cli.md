# CLI

The binary is `nx` (also installed as `nexy`). Without a global install, prefix with `uvx`:
`uvx nexy <command>`.

## Commands

| Command | Alias | What it does |
|---|---|---|
| `nx dev` | `nx d` | development server: compile on change, Vite, HMR |
| `nx start` | `nx s` | production server on the compiled output |
| `nx build` | `nx b` | production build |
| `nx new` | `nx n` | scaffold a project |
| `nx init` | `nx i` | add Nexy to an existing project |
| `nx migrate` | `nx m` | migrate from another framework |
| `nx check` | `nx c` | type-check: mypy on Python, `tsc` on TypeScript |
| `nx format` | `nx f` | format Python (ruff), JS/TS (prettier), `.nexy` files |
| `nx test` | - | run pytest; `--client` adds vitest |
| `nx translate` | `nx t`, `nx trans` | generate locale files |

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

## Build behaviour

`nx build` compiles the routes, then bundles the client when `useVite` is on.

> **Good to know**: there is no `--static` flag. Static hosting is a deployment choice, not a build
> mode - see [Deploy](deploy.md).

## Working on Nexy itself

Inside this repository the gates are:

```bash
python scripts/verify.py             # lint, format, typecheck, tests
python scripts/audit_dependencies.py # supply-chain audit against the lock
```

## Next steps

- [Getting started](getting-started.md): first project
- [Testing](testing.md): what `nx test` runs
- [Deploy](deploy.md): `build` and `start` in production
