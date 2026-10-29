# Installation

## Requirements

| Requirement | Why |
|---|---|
| Python 3.12+ | `requires-python` in `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | creates the project, installs its packages and runs Nexy |
| Node.js 18+ | only for a client framework (React, Vue, Svelte, Solid, Preact) |

A project without a client framework needs no Node.js at all.

## Install uv first

`uvx` is not a separate tool: it comes with uv, so install uv before anything else.

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Check it with `uv --version` and `uvx --version`.

## Create a project

```bash
uvx nexy new my-app
```

`uvx` runs Nexy in a temporary environment and leaves nothing behind. That is enough to **create** a
project (`new`, `init`) and nothing more: the temporary environment holds Nexy and no other
package. `nexy new` creates the project's own virtual environment, `.venv`, and installs its packages
there.

`nexy new my-app` asks four questions: router (file-based or modular), project type (web or API),
client framework, ORM. The installation of Python and Node dependencies then runs with one line per
step and its duration. See [CLI](../reference/cli.md).

Skip the prompts with a registered template:

```bash
uvx nexy new my-app --template <name>
```

## Work inside the project's virtual environment

Every other command (`nexy dev`, `nexy build`, `nexy migrate`...) must run **inside the project's
virtual environment**. That is where your own packages live: your ORM, your libraries, and the Nexy
the project was built with. Outside it, a project that needs `sqlmodel` fails with
`ModuleNotFoundError: No module named 'sqlmodel'`.

Activate it once per terminal, from the project folder:

| Shell | Command |
|---|---|
| PowerShell, cmd (Windows) | `.venv\Scripts\activate` |
| macOS, Linux | `source .venv/bin/activate` |

The prompt then starts with `(.venv)`. From there:

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

Open <http://localhost:3000>.

To skip the activation, let uv do it for one command: `uv run nexy dev`.

> [!NOTE]
> `nexy` and `nx` are the same binary. A copy installed with `uv tool install
> nexy` lives in its own environment, like `uvx`, so use it to create projects and run everything
> else from the project's environment.

## Add Nexy to an existing project

Run it from the project's virtual environment, with Nexy among its packages (`uv add nexy`):

```bash
nexy init
```

## Next steps

- [Quick start](quick-start.md)
- [Tutorial](tutorial.md)
- [Project structure](project-structure.md)
- [Troubleshooting](../guides/troubleshooting.md)
