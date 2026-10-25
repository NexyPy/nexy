# Installation

## Requirements

| Requirement | Why |
|---|---|
| Python 3.12+ | `requires-python` in `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | runs Nexy and manages the project environment |
| Node.js 18+ | only for a client framework (React, Vue, Svelte, Solid, Preact) |

A project without a client framework needs no Node.js at all.

## Run without installing

```bash
uvx nexy new my-app
```

`uvx` fetches Nexy for the command and leaves nothing behind.

## Install the CLI

```bash
uv tool install nexy
```

This adds two binaries to your `PATH`: `nx` and `nexy`.

```bash
nx --help
```

## Create a project

`nx new my-app` asks four questions: router (file-based or modular), project type (web or API),
client framework, ORM. The installation of Python and Node dependencies then runs with one line per
step and its duration. See [CLI](../reference/cli.md).

Skip the prompts with a registered template:

```bash
nx new my-app --template <name>
```

## Add Nexy to an existing project

```bash
nx init
```

## Check the setup

```bash
cd my-app
nx dev
```

Open <http://localhost:3000>.

## Next steps

- [Quick start](quick-start.md)
- [Tutorial](tutorial.md)
- [Project structure](project-structure.md)
