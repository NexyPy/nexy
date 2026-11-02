# Contributing to Nexy

**First time here?** Start with a [good first issue](https://github.com/NexyPy/nexy/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) - curated for new contributors.

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
uv pip install -e . --group dev

# 3. Enable the commit-msg hook (rejects AI attribution trailers)
git config core.hooksPath .githooks

# 4. Verify everything works
ruff check nexy/ && ruff format nexy/ --check && python -m mypy nexy --strict && python -m pytest tests/ -v
```

**Total time: ~2 minutes.**

## Development setup

### Prerequisites

- **Python** 3.12+
- **Node.js** 20+ (for frontend builds and VS Code extension)
- **uv** package manager (recommended) or pip
- **bun**, **pnpm**, or **npm** for JavaScript dependencies (Nexy prefers bun, then pnpm, then npm)

### Python environment

```bash
# Create and activate
uv venv
# Windows: .venv\Scripts\activate
# Unix/macOS: source .venv/bin/activate

# Install in editable mode with dev deps (dev is a dependency group, not an extra)
uv pip install -e . --group dev
```

### JavaScript dependencies (optional)

Only needed for the VS Code extension:

```bash
cd extensions/vscode
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

All tests should pass - the suite is fully green on `main`. If it fails on
your fresh clone, verify your Python version (3.12+) before suspecting your
changes.

## Project structure

```
nexy/
├── nexy/                      # Main Python package
│   ├── app.py                 # uvicorn target: nexy.app:app
│   ├── core/                  # config, models, types
│   ├── helpers/               # transversal layer (fs, imports, server, common)
│   └── modules/               # cli, compiler, frontend, routers, runtime, i18n, builder
├── templates/                 # test fixtures (scaffold layouts per framework)
├── tests/                     # pytest suite
├── extensions/vscode/         # VS Code extension (LSP)
└── docs/                      # Documentation - plain Markdown, index in docs/README.md
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full package layout and a deep dive.

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

#### Attribution

The human who writes and reviews the change owns the contribution. Keep AI
tools out of the Git metadata:

- No AI in `Co-authored-by`. GitHub counts every co-author trailer as a
  contributor, so a bot trailer permanently adds that account to the project's
  contributor list.
- No `Generated with ...`, `Generated-by:`, `Assisted-by:`, or equivalent
  footer, including the boilerplate that Claude Code, Codebuff/Freebuff,
  Copilot, Cursor, and similar tools append.
- No bot account as commit author or PR author.
- Do not describe agent output as independently reviewed. If you produced it,
  you are not its reviewer.

The `commit-msg` hook enforces this locally once you run
`git config core.hooksPath .githooks`. To audit a branch:

```bash
python scripts/check_attribution.py --range origin/main..HEAD
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

- **Linter**: ESLint + TypeScript (the extension ships its own `tsconfig.json`; run `pnpm install --frozen-lockfile` in `extensions/vscode/` first)
- **Format**: Prettier (via ESLint)

### General rules

- All code in English
- Functions < 20 lines, classes < 10 methods
- No premature abstraction
- KISS before clever

### Writing documentation

`docs/` is plain Markdown: index in [docs/README.md](docs/README.md), machine entry point in
[llms.txt](llms.txt). A page is a contract, not an essay: a contributor must be able to write a
conforming page without reading the other 86.

#### 1. Two page contracts

Pick one shape per page. Never both.

| Page | Answers | Shape |
|---|---|---|
| Conceptual | how something works | eight sections, in this order: Definition · How it works · Lifecycle · When to use · Configuration · Example · Limitations · Next steps |
| Reference | what the options of one thing are | one strict table: name, type, default, description, example, constraints, related options. No narrative paragraph. |

The eighth heading is `## Next steps`, not `## Related`: the pages that exist already use it, and
renaming it everywhere is a separate decision.

Shared behaviour - how a page is served, how layouts nest, what an action cycle is - is written
once in the shared contracts under `docs/views/frontend/`. A page under `docs/views/<framework>/`
only adds the syntax that differs, and links back to the shared page instead of repeating it.

#### 2. Three guarantee levels

One sentence carries one level. Never mix two.

| Form | Means | The reader can |
|---|---|---|
| **Nexy guarantees ...** | tested framework behaviour | rely on it; a test fails when it changes |
| **By convention ...** | what the structure expects of you | follow it, or diverge knowingly |
| **Your application is responsible for ...** | authorization, data, i18n, secrets | expect no code from Nexy |

"Nexy guarantees the route is mounted, but authorization is yours" is two levels in one sentence:
split it.

#### 3. Imposed vocabulary

Ten words, one definition each, no synonym. The definitions live in
[Core concepts](docs/getting-started/core-concepts.md) and [Views](docs/views/README.md); a page
links to them and never restates them.

| Word | Means | Never write instead |
|---|---|---|
| **route** | a URL pattern, produced by the path of a file | path, URL, slug |
| **page** | a route file that renders a view | screen, template, view |
| **view** | what produces the body of a page | page, template |
| **component** | a reusable piece a page imports | widget, partial |
| **layout** | a `layout.*` file that wraps the pages below its folder | template, wrapper, shell |
| **handler** | the function of a `.py` route file, named after the HTTP method | controller, view function |
| **endpoint** | the pair (URL, method) that a handler answers | route, URL, API |
| **action** | a Python function marked `@Action`, served as a `POST` | mutation, RPC, form handler |
| **island** | a client component whose HTML the server renders and the browser hydrates | widget, partial |
| **mode** | who produces the HTML and when: server mode or client mode per project, SSR, ISR, CSR or islands per page | strategy, renderer |

#### 4. Mechanical rules

- **One page, one question.** If the title needs "and", it is two pages.
- **Every executable code example carries `filename=`**, with the path it would have in a project:
  `filename="src/routes/index.py"` on the fence. Documentation code is run, not illustrated.
- **Every new `.md` in `docs/` enters the navigation** in [docs/README.md](docs/README.md) and the
  index in [llms.txt](llms.txt), in the same change. A page missing from both is invisible, and the
  suite fails on it.
- **No performance promise without a link** to [Performance](docs/deployment/performance.md). Numbers
  live there, not in the page that would like to be fast.
- **Docs are in English.** French is fine in `TASKS/`, which is not published.

#### 5. Written to be found

The documentation aims to be the first result for the question it answers. Both sites give a search
engine three things per page (`sites/shared/seo.py`): the canonical address
`{site}/docs/{slug}/`, the opening paragraph cut at 200 characters as the description, and the menu
trail as the breadcrumb. A page therefore has four handles, and all four say the same thing:

- **Title** — the question in the words a person types, not an internal name: "Choose a router", not
  "Routing: architecture".
- **Opening paragraph** — the answer, complete in one sentence, before any context: it becomes the
  search result.
- **Headings** — the words of the query, one idea per heading, so an excerpt answers on its own.
- **Slug** — the same words again, so the address says what the page is about without the menu.

One question, one page. Two pages on the same words compete with each other, and a search engine
ranks the pair below either one alone; a page that goes away redirects through
`sites/shared/docs_source.py` instead of staying online. A page links to its siblings with the words
of their question, never "here".

#### 6. Conformance

The mechanical half is checked: relative links resolve
(`tests/unit/nexy/docs/test_links.py`), `llms.txt` is exhaustive
(`tests/unit/nexy/docs/test_llms_index.py`), and every documentation code block runs
(`tests/unit/nexy/docs/test_recipes.py`).

The editorial half - two contracts, three guarantee levels, one vocabulary - is a human review. A
reviewer rejects a page that mixes two guarantee levels, adds a `## Related`, or renames a word, and
no test will catch it for them. That is the cost of the rule, and it is accepted.

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

**Coverage floor**: 84% overall (enforced by the test suite). Aspire to 95%
per module when touching one.

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

- [ ] `python -m pytest tests/ -v` - tests pass
- [ ] `ruff check nexy/` - lint passes
- [ ] `ruff format nexy/ --check` - formatting correct
- [ ] `python -m mypy nexy --strict` - type checks
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

1. Bump the version in `nexy/__version__.py` and `pyproject.toml`.
2. Update the changelog:
   ```bash
   npx git-cliff -o CHANGELOG.md
   ```
3. Commit the version bump and changelog on `main`, then tag and push. The
   tag must match the package version exactly (for example, `v2.1.1`), and
   its commit must already be on `main`; the workflow rejects tags from
   other branches:
   ```bash
   git tag v<version>
   git push origin v<version>
   ```
4. The `Release` workflow builds the sdist and wheel, smoke-tests both, and
   publishes to PyPI with trusted publishing.
5. Create the GitHub Release from the tag.

The workflow requires a PyPI trusted publisher configured for
`NexyPy/nexy`, workflow `release.yml`, and environment `pypi`. It stores no
long-lived PyPI token.

## Getting help

- **Bug reports**: open a [GitHub Issue](https://github.com/NexyPy/nexy/issues/new/choose)
- **Questions**: [GitHub Discussions](https://github.com/NexyPy/nexy/discussions)
- **Security issues**: see [SECURITY.md](SECURITY.md)
- **Everything else**: see [SUPPORT.md](SUPPORT.md)
