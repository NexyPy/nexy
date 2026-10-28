# Changelog

All notable changes to Nexy are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/); versioning follows [SemVer](https://semver.org/).

## [Unreleased]

### Added

- **`redirect`, `permanentRedirect`, `notFound`, `forbidden` and `unauthorized`**, from `nexy` and
  `nexy.http`. One call leaves a page or answers 307/308, 404, 403 or 401 in a page, an API handler,
  a modular controller, an action or a guard. A redirect is a real redirect with no error page,
  also for an API client; a destination with a line break is refused. A `HTTPException` of 3xx
  that names a `Location` is now a real redirect too.
- **Page metadata**: `metadata = {...}` in the frontmatter, or `setMetadata(...)` for a title that
  depends on the data, and `{{ useMetadata().html() }}` in the root layout. Title and template,
  description, canonical, robots, icon, Open Graph, Twitter and extra tags; every value is
  escaped, and a request never sees the metadata of another.
- **Request hooks `useParams`, `useRequest`, `useHeaders`, `useUrl` and `useIsActive`.**
  `useParams` is the clear name of `useQuery`, which returned the path parameters and not the query
  string and stays as an alias. `useIsActive` is the server twin of the client hook, with the same
  rule, for the active link of a navigation bar.
- **A router choice in the docs sites**, like the one of the Next.js docs: *File-based* or
  *Modular*. The menu shows the pages of the chosen router and the pages both share, remembers the
  choice, and sets itself when a page of one router is opened. Both sites behave the same.
- **Two documentation sites in `sites/`**, both reading `docs/` so no text is written twice: a
  vanilla one (a Python script, plain HTML, CSS and JS, search, light and dark theme, published to
  GitHub Pages by `.github/workflows/pages.yml`) and one made with Nexy itself. Code is coloured
  when the site is built, every heading has a link, search shows the words found, there is a 404
  page that works under a project URL, and a keyboard user can skip the menu.
- **Recipes, a Python API reference and a glossary** in `docs/`. The code of the recipes (sign in
  with a session, a JSON API, a file upload) runs in the test suite, and the API page is checked
  against the exports of `nexy`, `nexy.http`, `nexy.decorators` and `nexy.testing`.
- **`UploadFile`, `File` and `Form`** in `nexy.http`.

### Changed

- **The docs say where `nexy` may run.** `uvx` comes with uv and only creates a project (`new`,
  `init`): it runs in an environment with none of the project's packages, so `uvx nexy dev` failed
  on any project that needs one (an ORM, for example). Every other command runs inside the
  project's virtual environment, or through `uv run`. The README, the installation, quick start and
  tutorial pages, the CLI reference, troubleshooting, the generated project's README and its
  AGENTS.md all say so; a test refuses a page that tells to run `uvx nexy dev`.
- **`nx new` creates the first migration and the tables** when you choose an ORM and give a
  database URL, so the users page answers on the first `nexy dev`. When the database does not
  answer, it says why and lists `nexy migrate -m "create tables"` and `nexy migrate --upgrade`.
- **The dev toolbar badge shows the Nexy mark, not a letter.** The round badge now holds the
  roof-cut N of the Nexy logo, drawn as an icon.

### Fixed

- **`revalidate` in a `.nexy` page now switches the ISR cache on.** The frontmatter runs inside the
  component, so `revalidate = 60` was a local variable the router never saw and the page answered
  with no cache header. A literal `revalidate` or `metadata` is now an attribute of the module.
- **A dynamic page with `revalidate` shows its own parameter.** It was rendered with no
  parameters and all its URLs shared one cache entry; each URL is now cached on its own.
- **A client catch-all route keeps its parameter.** `[...path].tsx` and a folder such as `v1.2`
  lost everything after their first dot; only the extension is cut now.
- **Error pages match by folder.** A `notfound` page of `/blog` no longer answers `/blogger`, and
  a custom 404 page is not served to a client that asks for JSON.
- **A new project now has its migration tool.** `alembic` (SQLModel, SQLAlchemy) was never
  installed in the project, so `nx new` initialised nothing on a machine without a global Alembic.
- **Alembic sees the models.** The generated `env.py` never imported them: with SQLModel the
  migration was empty, and with SQLAlchemy it imported `Base` from a module that does not export it.
  SQLModel migrations also import `sqlmodel`, without which applying them failed.
- **`nx migrate` works with Tortoise-ORM.** It ran `aerich revision --autogenerate` and
  `aerich upgrade head`, which Aerich does not have; it also looked for an `aerich.ini` that Aerich
  never writes, and checked Tortoise URLs with SQLAlchemy. It now runs `init-db`, `migrate --name`
  and `upgrade`.
- **Tortoise with SQLite wrote `sqlite:///dev.db` in `.env`**, which Tortoise reads as `/dev.db`,
  at the root of the disk. It writes `sqlite://dev.db`.
- Two links in `docs/` pointed to headings that no longer exist; a test now checks every
  `page.md#heading` link.
- **The tests run the same on Windows, Linux and macOS.** Root-layout paths, the Windows process
  kill and the temporary paths no longer depend on the host. `nx format`, `nx check` and `nx test`
  find `ruff`, `mypy` and `pytest` next to the running Python when they are not on `PATH`.
- **CI installs the client test packages** (`npm ci` in `tests/client`). Those tests now fail, not
  skip, when Node.js 22.18 or the packages are missing.
- **No test is skipped any more**: `sqlalchemy`, `itsdangerous` and `python-multipart` joined the
  dev dependencies, and the starter and skill checks run for every framework.

## [2.2.0] - 2026-10-27

### Removed

- **The "Built with Nexy" badge** and its `useBadge` setting. The development toolbar stays
  (`useDevTools`). A `useBadge` line left in a `nexyconfig.py` is ignored.

### Changed

- **MDX is compiled by Vite only.** The Python compiler no longer parses or renders `.mdx` through
  the `.nexy` pipeline: it writes the thin wrapper that serves the route, like for `.tsx`, `.vue`
  and `.svelte`. `nx check` no longer compiles `.mdx` files.
- **The starter has a new design for every framework and both modes.** With Tailwind or UnoCSS, a
  new file-based project (React, Preact, Solid, Vue, Svelte, or server-rendered `.nexy`) gets the
  same pages written with utility classes in the idiom of its framework: a home page that confirms
  the app is running and lists the first three steps, an About page, and the same set of reusable
  components (`Button`, `Frame`, `Header`, `Footer`, `ThemeToggle` and more). The framework's own
  logo shows on the home page, and its colour is the accent. The theme switch keeps its state the
  way the framework does (a hook, a signal, a ref, a rune) instead of a global script; server pages
  use a short script inside the component that owns it. Plain CSS and the modular router keep their
  previous starter.
- **UnoCSS reads `.nexy` files** in a server project, so utility classes written in pages are
  generated.
- **The development toolbar** follows the page: white in a light theme, dark in a dark theme. Its
  close control is an icon, and the Routes tab lists the routes again.
- **Package layout**: `nexy/utils/` is now `nexy/helpers/` - a transversal
  layer with zero upward imports (`common`, `fs`, `imports`, `server`).
  All feature code moved under `nexy/modules/` (`cli`, `compiler`, `frontend`,
  `routers`, `runtime`, `i18n`, `builder`). The public facade exported by
  `nexy/__init__.py` is unchanged.
- **CLI scaffolding**: project templates (`web-fbr`, `web-modular`, `api-fbr`,
  `api-modular`, `alembic`, `_shared`) now live inside
  `nexy/modules/cli/templates/`.
- **Dev tooling**: the file watcher and `__pycache__` management moved to
  `nexy/modules/cli/devtools/` (`watcher.py`, `pycache.py`).
- **Scaffolds**: the Counter, Card, and Theme templates were rewritten -
  consistent utility classes across frameworks, explicit state hooks on
  Preact, and a table-of-contents layout for markdown pages.

### Fixed

- **`nx dev` no longer stops on a server error.** When uvicorn cannot start or crashes, dev
  reports the reason, keeps Vite and the watcher running, and starts again at the next file
  change. Only Ctrl+C stops it.
- **The development toolbar's Routes tab** printed `[object HTMLDivElement]` instead of the list.
- **Documentation that did not match the code.** A `.nexy` component renders its children with
  `<Slot />` (capital S), not `<slot />`; the MDX framework is Preact when the file imports
  `preact` and React otherwise; the README and `llms.txt` linked pages that do not exist. A
  `.nexy` component file is named in PascalCase, since it is imported as a Python module.
- **Production SSR for default exports**: the static-site generator looked up
  `<name>.default.html` while the build emits `<name>.Default.html`, so the
  server-rendered payload was silently empty for default-export routes on
  case-sensitive filesystems. The lookup now matches emitted names.
- **SSG pipeline**: React, Preact, and Solid are prerendered through per-file
  esbuild builds with a CPU-bound worker pool instead of Vite, and SSR
  failures now surface the real error in the build warning instead of a
  generic message.

### Added

- **`nx skills` and `nx new --no-agents`.** `nx new` writes `AGENTS.md` (tailored to the stack),
  `CLAUDE.md` (which imports it) and the skills that fit the project into `.agents/skills/` and
  `.claude/skills/`, the folders Codex, OpenCode and Claude Code read. `nx skills` does the same
  for an existing project and never overwrites a file or a skill of the project. The skills ship in
  the wheel.
- **A `nexy-security` skill** for dependencies, input, sessions, authorization and secrets, and
  tests that check every skill against the code (format, examples, imports, configuration fields,
  commands, paths) and every relative link of the documentation.
- **Skills for coding agents** in `skills/`: principles (order of work, KISS, SOLID, TDD, one
  function one treatment, no emoji, real SVG icons, human text), a UX and information-architecture
  audit to run before any view, and one skill each for `.nexy`, Markdown and MDX, React, Preact,
  Solid, Vue, Svelte, styling, the backend, the modular router, testing and work on the framework
  itself. An
  `AGENTS.md` snippet carries the rules to OpenCode and Codex.
- Compiler regression suites: byte-level route compile matrix (8 route
  kinds), compiler dispatch contract, markdown route compiler tests, and the
  frontend `useFF` contract tests backed by `vite_entry.normalize_ff`.

### Removed

- Dead code: the unused `BaseFrontendGenerator` abstraction, the unused
  `helpers/common/constants.py`, empty stub modules, and the `Task()`/`Job()`
  decorator stubs. Contract tests lost with the dead abstraction were ported
  to the production code they verify.

## [2.1.1] and earlier

See [GitHub releases](https://github.com/NexyPy/nexy/releases) for the
release history of versions 2.1.1 and earlier.
