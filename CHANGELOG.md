# Changelog

All notable changes to Nexy are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/); versioning follows [SemVer](https://semver.org/).

## [2.6.4] - 2026-11-18

### Added

- **`nx routes` lists the application's routes**, their HTTP methods, paths and source files,
  sorted by path (#455).

### Fixed

- **`useTransition` follows a client navigation**, in every adapter. It never saw one start, so
  a loading indicator stayed hidden; it is now `pending` from the click until the next page is
  shown, and idle again when the navigation ends, stops or is replaced (#430, #432).
- **`ErrorBoundary` catches a render error**, in every adapter. Nothing ever set its error, so a
  page that threw broke the whole page; the fallback now shows, and `reset` renders the children
  again. A Svelte project now gets `@nexy/ErrorBoundary.svelte` (#431, #433).
- **`useMatch()` without a path matches the current page**, in every adapter. Svelte matched `/`
  whatever the page, and React and Preact required the path (#434, #435).
- **A client route's async static params are pre-rendered.** `getStaticParams` returning a promise
  was dropped, and a route with static params lost its shell, so a path it did not list got no
  page (#427, #428).

### Security

- **The Modular React example's lock asks for anyio 4.14.2 and starlette 1.10.0**, for the
  advisories of anyio 4.13.0 (one critical) and starlette 1.0.0 (#437).
- **The VS Code extension's development tools carry no advisory that has a fix**: esbuild 0.28.2,
  vite 8.3.8, and glob 14, minimatch 11 and serialize-javascript 7 through pnpm overrides.
  picomatch has no fixed release yet (#437).

### Documentation

- How to pre-render a dynamic route from its static params (#303, #429).
- `useTransition`, `useMatch` and `ErrorBoundary`, with what the boundary does not catch (#305,
  #436).

## [2.6.3] - 2026-11-18

### Fixed

- **`nexy build` shows why a client build failed.** When the bundle did not build, an unresolved
  import for instance, the static pages were built anyway and their "Manifest not found. Run vite
  build first." took the place of the real error. They are now built only once the bundle is
  written (#413, #414).
- **A new file-based project no longer has a `src/src/routes/` folder.** Every `*-fbr` starter got
  copies of the 403 and 401 pages there, where the router never looks; a styled web starter still
  has them in `src/routes/` (#415, #416).

### Security

- **New web projects ask for glob 14.0.2**, for CVE-2026-118773 in glob and CVE-2026-118764 in
  minimatch through it; they asked for glob 13 (#408, #409).
- **The VS Code extension's lock is refreshed**: nothing it ships carries a known advisory. What is
  left is in development tools, and picomatch has no fixed release yet (#410).
- **Every example builds again, on locks with no advisory that has a fix.** Nine lacked the
  packages the build scripts import, and seven had a bug of their own (#412, #420).

## [2.6.2] - 2026-11-18

### Fixed

- **`nexy new -t <template>` creates the project again.** The twelve framework names, such as
  `web-fbr-vue` or `web-modular-react`, were fetched from a folder of the repository removed on
  2026-10-23, so each failed with "Failed to extract files from template" since 2.1.2. A name now
  renders the starter shipped in the package with the config the prompts would give, offline,
  like the interactive `nexy new` (#403, #404).

## [2.6.1] - 2026-11-17

### Changed

- **A request through Nexy costs less.** The security headers, the body limit and the access log
  are lighter: on one uvicorn worker with the access log on, an `async` route answers about 11%
  more requests per second. A body whose length is declared is no longer counted byte by byte;
  a chunked or HTTP/2 body still is, and a body over the limit is still a 413. The access log
  writes the lines of one turn of the event loop at once, and each line still shows at once
  (#397).
- **The agent skills that `nx skills` copies say when a change is done:** every added line runs in
  a test, security has tests that send the hostile input, and a hot path has a speed budget
  (#396).

### Fixed

- **A security header the application sets is no longer sent twice.** A `Referrer-Policy` or
  `X-Content-Type-Options` written in another case than the default went out with the default
  beside it (#397).

## [2.6.0] - 2026-11-17

### Added

- **Every web starter has a `/connection` page** that calls the Python backend and says what it
  answered and how long the round trip took; the API starters answer `GET /ping` (#390).
- **The plain-CSS starters with client-side routing have the mobile sheet** of the other starters,
  for React, Preact, Solid, Vue and Svelte (#389).
- **`useMaxBodySize` in `nexyconfig.py`**: the largest request body a worker reads, 1 MiB by
  default, `0` for no limit (#386).

### Changed

- **The CLI prints the way uv does.** `nx new`, `nx init`, `nx check`, `nx format`, `nx test`,
  `nx build`, `nx dev`, `nx start`, `nx add` and `nx skills` write one line per finished step with
  its duration, and `error:`, `warning:`, `hint:` and `cause:` lines. The build summary is a list
  instead of a tree, and the output has no check marks, arrows or warning signs (#384, #391).
- **Behaviour change: `/docs` and `/openapi.json` are served by `nx dev` only.** `useDocs` takes a
  third value, `"dev"`, the new default. A project that uses them in production sets
  `useDocs = True` (#387).
- **File routes written as the starters write them are about four times faster.**
  `def GET() -> dict[str, str]` answers 7,560 requests per second instead of 1,900 on one worker,
  and its `async` form 15,250 instead of 8,800. The bytes and the errors are the same (#392).
- **Server actions answer 9,250 requests per second instead of 6,400** on one worker (#388).

### Fixed

- **A request body over the limit is refused with a 413.** A worker read any body whole, so a few
  large posts filled its memory (#386).
- **A form posted without JavaScript no longer redirects to another site.** A `Referer` whose path
  started with `//` or `/\` sent the visitor there after the action (#385).

## [2.5.0] - 2026-11-16

### Added

- **`useORM` in `nexyconfig.py` names the ORM of a project.** `nx new` writes it for SQLModel,
  SQLAlchemy and Tortoise-ORM, and `nx migrate` reads it first. Before, `nx migrate` guessed from
  the installed packages, so a SQLAlchemy project whose environment also held `sqlmodel` got the
  SQLModel migrations. A project without the field keeps the old guess (#376).
- **The mobile menu of every starter is a modal sheet.** Tab and Shift+Tab stay inside it, Escape
  and the scrim close it, the focus goes back to the menu button, and it slides back before it
  hides. It has one close button, a title that names the dialog, and 44 px links. Widening the
  screen closes it. The same in the server, React, Preact, Solid, Vue, Svelte and plain-CSS
  starters (#377).
- **The bug report form asks for a minimal reproduction and how often the bug happens**, and the
  pull request template asks how the change was tested (#378).

### Fixed

- **SQLAlchemy migrations.** A model outside `user_model.py` is now migrated: the alembic env
  imports every `*_model.py`. The scaffolded `Base` names its constraints, so adding a foreign key
  works on SQLite and a downgrade no longer renders `drop_constraint(None)` (#376).
- **The access log writes control characters of a path as `%XX`.** A request for `/%1b[2J`
  cleared the terminal that showed the log, and `/%0aGET%20/admin` wrote a forged request line
  (#379).
- **Conduct reports go to the address that exists**: the code of conduct printed `gamil.com`
  (#378).

### Changed

- **A plain route answers about 52,000 requests per second instead of 6,000**, on 4 workers. The
  access log no longer parses Rich markup for each request, a page made as a string goes out in
  one response, and small files of `public/` are served from memory (#371, closes #369).
- **A production worker no longer loads the Vite dev proxy**, nor httpx and websockets with it:
  about 8 MB less per worker (#380).

## [2.4.1] - 2026-11-15

### Fixed

- **`nx start` refuses a project that `nx build` has not built.** It used to serve the pages without
  their layout: a 200 with `<div data-nexy-error="Layout not available"></div>`. `nx build` now
  writes `__nexy__/build.json` (Nexy version, time) once it succeeds, and a failed build leaves
  none; without that file `nx start` exits with code 1 and says to run `nx build`, in the twelve
  languages of the command line (#370).

### Changed

- **The command line reference says that `nx start` needs a build first**, with its translations.

## [2.4.0] - 2026-11-14

### Added

- **Health endpoints for load balancers and Kubernetes probes**, with `useHealth = True` in
  `nexyconfig.py`. `/health/live` answers 200 while the process answers; `/health/ready` answers
  200 once the application has started, and 503 while it starts or is asked to stop. A probe skips
  the access log, the trusted host check and the HTTPS redirect, and neither path is in the OpenAPI
  schema. Off by default: a project that does not set it keeps every path (#86).
- **A page on fetching data in a component with `useFetch`**, in the views docs.

### Fixed

- **Chrome DevTools no longer floods the dev log.** The 404 it causes on every inspected page
  (`/.well-known/appspecific/com.chrome.devtools.json`) writes no line in dev; production still logs
  every path it answers, and the probe still gets its 404 (#82). `AccessLogMiddleware` takes a
  `quiet` tuple of paths to keep out of the log.
- **A multipart form without `python-multipart` names the fix.** An action that received
  `multipart/form-data` answered a bare 500 whose traceback buried the package name; the error now
  names the package and the command, `uv add python-multipart`. A urlencoded form still needs
  nothing (#83).

### Changed

- **The docs say when a form needs `python-multipart`**, in the actions guide and the reference.
- **The health endpoint pages are translated** into every language of the docs.
- **Every text file is checked out with LF endings** (`.gitattributes`), so a clone edited on
  Windows no longer rewrites the whole tree.

- **The agent rules forbid the characters a person does not type**: em and en dashes, arrows,
  the ellipsis character, curly quotes, bullets, middle dots, check marks, box drawing and invisible
  spaces, in text and in design (a menu separator is a CSS border or gap). A test keeps them out of
  the interfaces of the docs sites and of the starters.

### Security

- **opentelemetry-api 1.45.2 and soupsieve 4.1.1** in the lock, for CVE-2026-126360 and
  CVE-2026-126190. opentelemetry-api comes with FastAPI; soupsieve only with the translator of the
  docs, a development tool.

## [2.3.0] - 2026-11-08

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
- **`useFetch` in `@nexy/client`**, for React, Preact, Solid, Vue and Svelte. One state per URL:
  the first reader sends the request and the others reuse the answer, a refresh keeps the data
  until the new answer arrives, and two refreshes at once send one request. An error status is a
  `FetchError` with the server's detail; `refreshAll()` fetches every URL of the page again, and
  an action that revalidates dispatches `nexy:revalidate` so the data is fetched again with the
  page.
- **HEAD answers with the body of GET**, on every page and API route. A route that answered GET
  refused HEAD with 405; a route's own HEAD handler still answers first.
- **A tutorial that is a course.** Fourteen chapters, each a runnable step of the same notes app,
  from `nx new` to a React island that ticks a note without a reload; each chapter ends where the
  next one starts, and the eleven translated trees carry the same chapters.
- **A "Coming from" section**: sixteen pages mapping Astro, Django, Elysia, Express, FastAPI,
  Fastify, Flask, Hono, Laravel, NestJS, Next.js, Nuxt, Rails, Remix, Spring Boot and SvelteKit to
  Nexy.
- **A "Databases" section**: SQLite, PostgreSQL, Neon, and MySQL or MariaDB.
- **The COM brand kit and its social pipeline.** `scripts/publish_social.py` lists, checks, packs
  and rehearses a post; `scripts/make_com_media.py` draws the cards as HTML and CSS, renders them
  in Chrome at twice the size and reduces them to 1080x1350, and writes the repository banner.
  A caption that reads like every other caption, a post no network would accept, and a card whose
  text overflows or whose fonts fall back are refused.
- **`@Controller("/cats")`**: the argument of a modular controller is `path`, first and
  positional. `prefix=` still works and warns that it is deprecated; giving both is refused.

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
- **The mobile menu of the starter is a sheet from the left edge.** It was a dropdown under the
  header, too small for a thumb and easy to miss. It is now a `Sheet` component, one per client
  framework plus the server-rendered header: a dialog role, a scrim, a close button, Escape, and a
  page that does not scroll behind it. The entry animation lives in the stylesheet rather than in a
  utility class: Tailwind and UnoCSS both read `globale.css`, and no utility carries keyframes.
- **The README is the front door PyPI shows**: the promise, the three doors and a measured number,
  with absolute links because PyPI renders the page outside the repository.
- **The package metadata PyPI shows** now carries a license, an author, the classifiers, the
  project URLs, and a description and keyword list a search can read (PEP 639
  `License-Expression: MIT`).
- **The plain-CSS starter's mobile menu is a sheet from the left edge too**: a modal sheet over a
  scrim, closed by its button, the scrim or Escape, with focus moved in and back and the page
  behind not scrolling. A reduced-motion preference turns the slide off.
- **The docs sites take the mobile bar and drawer of Fumadocs**: the drawer opens on the controls
  of the page, the theme switch keeps the size its knob is drawn for on a phone, and the language
  list fits in either direction.

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
- **`useSession()` answers `{}` when sessions are off.** Starlette's `request.session` asserts
  instead of raising `AttributeError`, so the `getattr` default never applied and the page
  answered 500.
- **`nx migrate` exits with the code of a failing migration tool.** The return code of alembic or
  aerich was dropped, so a migration that failed ended with exit 0 and CI took it for a success.
- **A middleware class listed bare in `useMiddlewares` is applied.** `collect_middlewares` kept
  only `(class, options)` pairs, so `useMiddlewares = [RequestIdMiddleware]`, the form the docs
  show, installed nothing.
- **`notfound.nexy`, `forbidden.nexy` and `unauthorized.nexy` stay error pages** in a project with
  a `nexyconfig.py`: loading the config rebuilt the special file names from a list that knew only
  `layout`, `errors` and `loading`, so the files were served as `/notfound`, `/forbidden` and
  `/unauthorized`.
- **SQLite migrations can add a foreign key to an existing table.** SQLite cannot alter a
  constraint, so the upgrade failed halfway: the column was added and the revision never recorded.
  `env.py` migrates SQLite in batch mode and names the SQLModel constraints, which batch mode
  needs.
- **The Alembic env imports every `*_model.py`** under `src/` when it runs, so a model added after
  init is not written as a `drop_table`; it takes the scaffold's user model when present, else the
  first `*_model.py`.
- **The translator keeps an indented code fence out of its hands.** The fence pattern was
  anchored at column zero, so a fence inside a list item travelled as prose: German turned its
  backticks into a low quote, Urdu lost one and translated the code.
- **The client bundles are built after `vite build`**, not when `vite dev` stops. Vite calls
  `closeBundle` on both, so the plugin ran a script `nexy dev` never copies and printed an
  `ERR_MODULE_NOT_FOUND` stack each time Nexy stopped Vite.
- **The API reference no longer hides a route in silence.** `nx dev` and `nx start` print, for a
  page at `/docs` or `/openapi.json`, the file and the setting to change.
- **The security page says a `.nexy` template does not escape on its own.** It read as if
  autoescape were on and `| safe` turned it off; `| e` is the author's to add, as `SECURITY.md`
  says. Translated into the eleven languages.
- **The test suite runs in English whatever the machine locale.** `NEXY_LANG=en` is set for the
  test process and the subprocesses it starts; 21 tests that read the English messages failed on
  a machine with `LANG=fr_FR.UTF-8`.

## [2.2.2] - 2026-11-05

### Fixed

- **`uvx nexy` on Python 3.15 and Windows.** `cmarkgfm` has no wheel there, so uv
  built it from source and demanded Microsoft C++ Build Tools before Nexy was
  installed at all. `markdown-it-py` replaces it: pure Python, GFM output and
  heading IDs unchanged. Raw HTML in a `.md` page is now shown as text instead of
  being dropped, and a bare `www.` address is no longer turned into a link: write
  the scheme (`https://`).
- **`mypy --strict` on Python 3.15.** The 3.15 stubs type `spec_from_loader`
  more strictly than 3.12 to 3.14; the module spec of a compiled module is now
  built by hand.
- **`uvicorn` extras** listed one by one, without `pyyaml`, which Nexy never used.

### Added

- **A GitHub release for every tag**, written after PyPI accepted the files, so
  a version nobody can install is never announced.
- **CI on a pushed branch.** `feature/*`, `fix/*`, `docs/*` and `perf/*` run the
  matrix without waiting for a pull request. When a pull request already covers
  the branch, its run is the only one.

### Changed

- **The README and the issue templates** link the published documentation
  instead of raw Markdown files and an unrelated site. Blank issues are closed:
  a question, an idea and a security report each have their own place.

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
