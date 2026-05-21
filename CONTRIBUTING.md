# Contributing to Nexy

Thank you for your interest in contributing to Nexy. We welcome contributions
of all kinds: bug reports, feature requests, documentation improvements, and
code changes.

## Table of contents

- [Code of conduct](#code-of-conduct)
- [Getting started](#getting-started)
- [Development setup](#development-setup)
- [Project structure](#project-structure)
- [Development workflow](#development-workflow)
- [Coding standards](#coding-standards)
- [Testing](#testing)
- [Pull request process](#pull-request-process)
- [Release process](#release-process)

## Code of conduct

This project is governed by the [Contributor Covenant](CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code.

## Getting started

### Prerequisites

- **Python** 3.12+
- **Node.js** 20+ (for frontend builds and VS Code extension)
- **uv** package manager (recommended) or pip
- **pnpm** (for JavaScript dependencies)

### Fork and clone

1. Fork the repository on GitHub.
2. Clone your fork:

   ```bash
   git clone https://github.com/YOUR_USERNAME/nexy.git
   cd nexy
   ```

3. Add the upstream remote:

   ```bash
   git remote add upstream https://github.com/NexyPy/nexy.git
   ```

## Development setup

### Python environment

```bash
# Create and activate a virtual environment
uv venv
# On Windows: .venv\Scripts\activate
# On Unix/macOS: source .venv/bin/activate

# Install the package in editable mode with development dependencies
uv pip install -e ".[dev]"
```

### JavaScript dependencies (optional)

Only needed if working on the VS Code extension or frontend packages:

```bash
pnpm install --frozen-lockfile
```

### Verify the setup

```bash
# Run quality gates (in this order)
ruff check nexy/
ruff format nexy/ --check
python -m mypy nexy --strict
python -m pytest tests/ -v
```

All tests should pass. If you see failures in `test_format_attributes_*`,
these are pre-existing and unrelated to your changes.

## Project structure

```
nexy/
├── nexy/                   # Main package
│   ├── cli/                # Typer CLI (nx, nexy commands)
│   │   └── commands/       # dev, start, build, init, new
│   ├── compiler/           # .nexy parsing and code generation
│   │   ├── parser/         # scanner, sanitizer, template, logic
│   │   └── generator/      # Python output generation
│   ├── core/               # Config, models, types
│   ├── routers/            # AppServer, FBRouter, ModularRouter
│   ├── frontend/           # Framework integrations (React, Vue, etc.)
│   ├── utils/              # Dev server, init, server config
│   ├── i18n/               # Internationalization strings
│   ├── vfs/                # Virtual file system (PEP 302)
│   └── templates/          # Project scaffold templates
├── tests/                  # Test suite
├── extensions/vscode/      # VS Code extension
├── docs/                   # Documentation site (separate repository)
└── skills/                 # Development philosophy docs (KISS, SOLID, TDD)
```

For a detailed architectural overview, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Development workflow

### Branch naming

| Branch pattern | Purpose |
|---------------|---------|
| `feature/*` | New features |
| `fix/*` | Bug fixes |
| `docs/*` | Documentation |
| `refactor/*` | Code refactoring |
| `perf/*` | Performance improvements |
| `test/*` | Test additions or changes |

```bash
git checkout -b feature/my-feature
```

### Commit messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `chore`, `style`, `ci`

Examples:

```
feat(router): add wildcard route support
fix(compiler): handle empty frontmatter gracefully
docs: update README with new CLI commands
refactor(vfs): simplify module finder logic
```

### Keep your fork up to date

```bash
git fetch upstream
git rebase upstream/main
```

## Coding standards

### Python

- **Formatter**: Ruff (line length 100, target Python 3.12)
- **Linter**: Ruff (all default rules enabled)
- **Type checker**: mypy with `--strict` mode
- **Docstrings**: Google style (required for public APIs)

```bash
# Check before committing
ruff check nexy/
ruff format nexy/ --check
python -m mypy nexy --strict

# Auto-fix
ruff check nexy/ --fix
ruff format nexy/
```

### TypeScript (VS Code extension)

- **Linter**: ESLint
- **Type checker**: `tsc -b`

Rules:

- All code in English (no comments or variable names in other languages)
- Functions under 20 lines where possible
- Classes under 10 methods
- No premature abstraction

## Testing

### Python tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/unit/nexy/parser/test_scanner.py -v

# Run with coverage
python -m pytest tests/ --cov=nexy --cov-report=term
```

**Coverage target**: 95% per module.

### Test conventions

- Write the test first (TDD: red → green → refactor)
- One assertion per test
- Naming: `test_<thing>_<scenario>`
- Place tests in `tests/unit/` matching the module path

### JavaScript/TypeScript tests (VS Code extension)

```bash
cd extensions/vscode
npm run test
```

## Pull request process

### Before submitting

1. Ensure your code builds and passes all quality gates:

   ```bash
   ruff check nexy/
   ruff format nexy/ --check
   python -m mypy nexy --strict
   python -m pytest tests/ -v
   ```

2. Write tests for your changes (new feature = new tests, bug fix = test that
   reproduces the bug before the fix).

3. Update documentation if you change public APIs.

4. Keep your PR focused on a single concern. One module/feature per PR.

### PR checklist

When you open a pull request, ensure:

- [ ] Tests pass (`python -m pytest tests/ -v`)
- [ ] Lint passes (`ruff check nexy/`)
- [ ] Type checking passes (`python -m mypy nexy --strict`)
- [ ] Formatting is correct (`ruff format nexy/ --check`)
- [ ] New tests cover the changes
- [ ] Documentation is updated (if applicable)
- [ ] Commit messages follow conventional commits
- [ ] PR description explains the change and motivation
- [ ] No breaking changes without discussion in an issue first

### Review process

1. At least one maintainer review is required.
2. Address review feedback with additional commits (no force-pushing during review).
3. Once approved, maintainers will merge your PR.

## Release process

For maintainers only:

1. Update version in `nexy/__version__.py` and `pyproject.toml`.
2. Update `CHANGELOG.md`:

   ```bash
   npx git-cliff -o CHANGELOG.md
   ```

3. Create a git tag:

   ```bash
   git tag v<version>
   git push origin v<version>
   ```

4. Publish to PyPI:

   ```bash
   uv build
   uv publish
   ```

5. Create a GitHub Release from the tag.

## Questions?

If you have questions or need help, open a [Discussion](https://github.com/NexyPy/nexy/discussions)
or join our community chat (coming soon).
