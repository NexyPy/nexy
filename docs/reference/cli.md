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

## Output

Long steps (installing packages, compiling, bundling) show a spinner with the elapsed time, then
leave one line behind: `✔ Installed Python dependencies  1.4s`. A failing step prints the last
lines of the command's output instead of hiding it. Terminals that cannot render Unicode get
`+` and `x`.

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

> **Good to know**: there is no `--static` flag. Static hosting is a deployment choice, not a build
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
