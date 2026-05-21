# Contributing to Nexy

**First time here?** Check out [good first issues](https://github.com/NexyPy/nexy/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
— curated for new contributors.

<p align="center">
  <a href="https://github.com/NexyPy/nexy/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22">
    <img src="https://img.shields.io/github/issues/NexyPy/nexy/good%20first%20issue?color=%2334D058&label=good%20first%20issues" alt="Good first issues">
  </a>
  <a href="CODE_OF_CONDUCT.md">
    <img src="https://img.shields.io/badge/code%20of-conduct-%2334D058" alt="Code of Conduct">
  </a>
</p>

## Table of contents

- [Code of conduct](#code-of-conduct)
- [Quick start](#quick-start)
- [Development setup](#development-setup)
- [Project structure](#project-structure)
- [Development workflow](#development-workflow)
- [Coding standards](#coding-standards)
- [Testing](#testing)
- [Pull request process](#pull-request-process)
- [Release process](#release-process)
- [Getting help](#getting-help)

## Code of conduct

This project is governed by the [Contributor Covenant](CODE_OF_CONDUCT.md).
By participating, you agree to uphold this code.

## Quick start

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/nexy.git
cd nexy

# 2. Set up Python
uv venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e ".[dev]"

# 3. Verify everything works
ruff check nexy/ && ruff format nexy/ --check && python -m mypy nexy --strict && python -m pytest tests/ -v
```

**Total time: ~2 minutes.**

## Development setup

### Prerequisites

- **Python** 3.12+
- **Node.js** 20+ (for frontend builds and VS Code extension)
- **uv** package manager (recommended) or pip
- **pnpm** (for JavaScript dependencies)

### Python environment

```bash
# Create and activate
uv venv
# Windows: .venv\Scripts\activate
# Unix/macOS: source .venv/bin/activate

# Install in editable mode with dev deps
uv pip install -e ".[dev]"
```

### JavaScript dependencies (optional)

Only needed for the VS Code extension:

```bash
pnpm install --frozen-lockfile
```

### Verify your setup

```bash
# Lint → Format → Typecheck → Test (in this order)
ruff check nexy/
ruff format nexy/ --check
python -m mypy nexy --strict
python -m pytest tests/ -v
```

All tests should pass. Pre-existing failures in `test_format_attributes_*` are
known and unrelated to your changes.

## Project structure

```
nexy/
├── nexy/                   # Main Python package
│   ├── cli/                # CLI commands (dev, build, start, new)
│   ├── compiler/           # .nexy → Jinja2 pipeline
│   ├── routers/            # AppServer, FBRouter, ModularRouter
│   ├── frontend/           # React, Vue, Svelte, Solid, Preact
│   ├── vfs/                # Virtual File System
│   └── templates/          # Project scaffold templates
├── tests/                  # pytest suite
├── extensions/vscode/      # VS Code extension (LSP)
└── docs/                   # Documentation site (separate repo)
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for a deep dive.

## Development workflow

### 1. Pick an issue

Start with a [good first issue](https://github.com/NexyPy/nexy/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
or discuss your idea in [GitHub Discussions](https://github.com/NexyPy/nexy/discussions)
before opening a PR for a new feature.

### 2. Create a branch

| Branch pattern | Purpose |
|---------------|---------|
| `feature/*` | New features |
| `fix/*` | Bug fixes |
| `docs/*` | Documentation |
| `refactor/*` | Code refactoring |
| `perf/*` | Performance |
| `test/*` | Tests |

```bash
git checkout -b feature/my-feature
```

### 3. Make changes

Follow the [coding standards](#coding-standards) and write tests first (TDD).

### 4. Commit

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
```

Types: `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `chore`

```
feat(router): add wildcard route support
fix(compiler): handle empty frontmatter
docs: update README with CLI examples
```

### 5. Push and open a PR

```bash
git push origin feature/my-feature
```

Then open a pull request on GitHub. Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md).

### Stay updated

```bash
git fetch upstream
git rebase upstream/main
```

## Coding standards

### Python

- **Formatter**: Ruff (line-length=100, target-version=py312)
- **Linter**: Ruff (all rules)
- **Type checker**: mypy `--strict`
- **Docstrings**: Google style (public APIs)

```bash
# Quality gates
ruff check nexy/
ruff format nexy/ --check
python -m mypy nexy --strict
```

### TypeScript (VS Code extension)

- **Linter**: ESLint (via `tsc -b`)
- **Format**: Prettier (via ESLint)

### General rules

- All code in English
- Functions < 20 lines, classes < 10 methods
- No premature abstraction
- KISS before clever

## Testing

### Python

```bash
# All tests
python -m pytest tests/ -v

# Single file
python -m pytest tests/unit/nexy/parser/test_scanner.py -v

# Coverage
python -m pytest tests/ --cov=nexy --cov-report=term
```

**Coverage target**: 95% per module.

### Conventions

- **TDD**: test first (red → green → refactor)
- one assertion per test
- Naming: `test_<thing>_<scenario>`
- Tests in `tests/unit/` mirroring the module path

### TypeScript

```bash
cd extensions/vscode
npm run test
```

## Pull request process

### Checklist

- [ ] `python -m pytest tests/ -v` — tests pass
- [ ] `ruff check nexy/` — lint passes
- [ ] `ruff format nexy/ --check` — formatting correct
- [ ] `python -m mypy nexy --strict` — type checks
- [ ] New tests cover my changes
- [ ] Documentation updated (if public API change)
- [ ] Conventional commit messages
- [ ] One module/feature per PR

### Review

1. At least one maintainer review required
2. Address feedback with additional commits (no force-push during review)
3. Maintainers squash-merge approved PRs

## Release process

For maintainers only:

```bash
# 1. Bump version in nexy/__version__.py + pyproject.toml

# 2. Update changelog
npx git-cliff -o CHANGELOG.md

# 3. Tag and push
git tag v<version>
git push origin v<version>

# 4. Publish to PyPI
uv build && uv publish

# 5. Create GitHub Release
```

## Getting help

- **Bug reports**: open a [GitHub Issue](https://github.com/NexyPy/nexy/issues/new/choose)
- **Questions**: [GitHub Discussions](https://github.com/NexyPy/nexy/discussions)
- **Security issues**: see [SECURITY.md](SECURITY.md)
- **Everything else**: see [SUPPORT.md](SUPPORT.md)
