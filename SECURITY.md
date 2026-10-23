# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported |
|---------|-----------|
| >= 2.0.0 | :white_check_mark: |
| < 2.0.0 | :x: |

## Reporting a Vulnerability

We take security issues seriously. Please do **not** report security
vulnerabilities via public GitHub issues.

Instead, report them privately by emailing the maintainer at
**[hopcy.forcy@gmail.com](mailto:hopcy.forcy@gmail.com)**.

You should receive a response within **48 hours**. If for some reason you
do not, please follow up to ensure we received your original message.

### What to include

- Description of the vulnerability
- Steps to reproduce (if applicable)
- Potential impact
- Suggested fix (if any)
- Your contact information for follow-up

### Disclosure policy

When we receive a security report, we will:

1. Confirm receipt within 48 hours.
2. Assess the issue and determine affected versions.
3. Develop and test a fix.
4. Release a security patch as soon as possible, coordinated
   with the disclosure date (typically 90 days after the report).

We believe in coordinated disclosure and will work with reporters to
determine an appropriate timeline for public disclosure.

## Security-related configuration

### Production deployment

- Always use environment variables for secrets (database URLs, API keys).
- Set `DEBUG=False` in production (`nexyconfig.py`).
- Use HTTPS in production (configure via `nexyconfig.py` or a reverse proxy).
- Keep your Nexy version up to date.

### Reporting non-security bugs

For non-security bugs, please open a [GitHub issue](https://github.com/NexyPy/nexy/issues/new/choose).

## Security audit (2026-10-19)

Static analysis with [Bandit](https://bandit.readthedocs.io/) over `nexy/`
(70 findings: 10 High, 10 Medium, 50 Low). Every finding was triaged against
the FastAPI security guidance (<https://fastapi.tiangolo.com/tutorial/security/>)
and the OWASP API Security Top 10.

**Result: 0 High, 0 Medium, 0 Low** (`bandit -r nexy/ -c .bandit` exits 0).
Every residual risk is an inline `# nosec <ID>` with a one-line justification:
no rule is skipped globally (`.bandit` sets `skips: []`) and every `# nosec`
has a matching entry in the register below.

### Fixed

| Finding | Site | Fix |
|---|---|---|
| B602 `shell=True` (command injection) | `utils/init/dependencies.py` | Executables resolved with `shutil.which`, run as a list without a shell |
| B102 `exec` (dead sandbox module) | `core/sandbox.py` | Module deleted; it was unreferenced (see the accepted risk on `.nexy` logic instead) |
| B101 `assert` as control flow | `compiler/generator/logic.py` | Replaced with explicit `raise RuntimeError` on invariants |
| B110 `except: pass` | `watcher.py`, `engine.py`, `clone.py`, `_cli.py`, `server.py` | Narrowed to typed exceptions (`OSError`, `ImportError`, `shutil.Error`, ...) with a comment on why silent handling is correct |
| B112 `except: continue` | `translate.py`, `fbrouter/dependencies.py`, `_cli.py` | Narrowed to typed exceptions with the same rationale |
| B310 `urlopen` readiness probe | `utils/server/server.py` | Probe replaced by a TCP connect (`socket.create_connection`); no URL is built or fetched |
| B324 weak MD5 (4 sites) | `frontend_route.py`, `vite_entry.py`, `ncc.py` | `usedforsecurity=False`: deterministic non-cryptographic IDs, digest unchanged |
| B607 partial-path executables | `check.py`, `test.py`, `template_setup.py`, `server.py` | `shutil.which` resolution before every spawn (tsc, npx, git, uv, taskkill) |

### Residual risk register (`# nosec` sites)

Every `# nosec` below is intentional and reviewed. Process launches marked
**"fixed argv"** always pass the first argument from `shutil.which` or a
hard-coded tool name, never from untrusted input.

#### B701 - Jinja2 environments without autoescape (4 sites)

Nexy renders **its own Python/TS/HTML source code and server-side HTML**, not
attacker-controlled HTML documents. Turning autoescape on would
double-escape the framework's own emitted HTML props (`{{ children }}`,
`{{ toc_html | safe }}`) and corrupt code-generation output (`env.py`,
scaffolding files). Dynamic data reaching user templates is the project
author's own responsibility and is escaped with `|e` where needed.

| Site | What the environment emits |
|---|---|
| `nexy/template.py:71` | server-side route HTML (`{{ children }}`, props) |
| `nexy/modules/cli/commands/migrate.py:66` | generated Python (`alembic/env.py`) |
| `nexy/modules/cli/init/template_setup.py:257` | generated Python (`alembic/env.py`) |
| `nexy/modules/cli/init/renderer.py:43` | scaffolding sources (Python/TS/HTML files) |

#### B104 - dev default host `0.0.0.0` (7 sites)

Binding all interfaces is the documented developer convenience default, so a
phone or colleague can test on a LAN machine. Production users are expected
to set `useHost` (reverse proxy / 127.0.0.1). Comparison sites are literals,
not binds.

| Site | Note |
|---|---|
| `nexy/core/config.py:44`, `nexy/core/models.py:197` | `useHost` field defaults |
| `nexy/modules/cli/commands/dev.py:108`, `nexy/modules/cli/commands/start.py:24` | literal comparison to pick the LAN IP to display |
| `nexy/helpers/server/ports.py:12`, `ports.py:25` | literal comparison; the availability probe never binds |

#### B310 - `urlopen` in `nexy/modules/cli/commands/add.py:39`

`nexy add <url>` fetches the component the user explicitly named; the CLI's
job is to fetch what the user asks. Scheme restricted to http(s) by the guard
above (done during the audit), so no `file://`/`ftp://` readback.

#### B404 - `import subprocess` (12 sites)

Harmless by itself: every import site is followed by argv-array launches
triaged under B603. Sites: `modules/cli/commands/{build,check,dev,test,format}.py`,
`utils/common/{process,report}.py`, `utils/init/{clone,dependencies,template_setup}.py`,
`utils/server/server.py` (import + `Popen` type-only import).

#### B603 - `subprocess.run`/`Popen` without shell (argv array, 22 sites)

Every flagged call launches an explicit argv array (never a shell string),
with the first element pinned to `shutil.which(...)` or a fixed tool name.
What reaches argv:

- **Tool checks** (`check.py`, `test.py`, `format.py`, `build.py`): the tool
  name is resolved on PATH; arguments come from the project layout or the
  user's own CLI flags. A developer passing hostile flags to `nexy check` on
  their own machine is out of threat model.
- **Dependency install** (`utils/init/dependencies.py`): package list is the
  registry-known name set.
- **Git scaffold** (`utils/init/clone.py`, `init_git` in `template_setup.py`):
  fixed verbs (`init`, `fetch`, `checkout`, `merge`); the only interpolated
  value is the repo URL / subpath the user chose.
- **Dev server spawner** (`utils/server/server.py`): `sys.executable` with a
  launcher built from resolved config values, or the devtool argv returned by
  `_detect_pm`.

To re-run the audit: `python -m bandit -r nexy/ -c .bandit`

### Dependency audit register (pip-audit)

CI audits the full lock envelope (`uv export --frozen` + `pip-audit
--disable-pip --strict`). Known vulnerabilities must be **fixed** (bump the
package) or, when there is no fixed release, **ignored per ID with a written
justification here** - never with a blanket `--ignore-vulns all`.

| ID | Package (locked) | Why ignored | Revisit when |
|---|---|---|---|
| PYSEC-2022-252 | `deep-translator` 1.11.4 | The 2022 account compromise shipped malicious releases **after** 1.11.4 was published; OSV marks every version >= 1.8.5 affected and defines no fixed release, so even the current upstream release stays flagged. Our envelope pins the exact 1.11.4 wheel by sha256 in `uv.lock` (2023-06-28, pre-compromise), and `uv sync --frozen` verifies it. Code-execution risk is therefore not in our envelope. | deep-translator publishes a release recorded as fixed in OSV, or `nexy translate` moves to a first-party translation client (then drop the dependency). |
