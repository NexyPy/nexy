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
**[hopcy.forcy@gamil.com](mailto:hopcy.forcy@gamil.com)**.

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
and the OWASP API Security Top 10. Accepted risks are listed in `.bandit` with
their justification; nothing is skipped without an entry here.

**Result: 0 High, 0 Medium remaining** (remaining Low findings are the
subprocess/hashlib classes reviewed above).

### Fixed

| Finding | Site | Fix |
|---|---|---|
| B602 `shell=True` (command injection) | `utils/init/dependencies.py` | Executables resolved with `shutil.which`, run as a list without a shell |
| B310 `urlopen` on arbitrary scheme | `cli/commands/add.py` | http(s)-only scheme allowlist (`file://`, `ftp://` rejected) + regression tests |
| B324 weak MD5 (4 sites) | `frontend_route.py`, `vite_entry.py`, `ncc.py` | `usedforsecurity=False`: deterministic non-cryptographic IDs, digest unchanged |

### Accepted risks (documented in `.bandit`)

- **Jinja2 without autoescape** (`template.py`): templates are the project's
  own server-side code; enabling autoescape would break existing HTML props.
  Mitigation for dynamic data: escape with `|e`.
- **Dev server binds `0.0.0.0`** (`core/config.py`): deliberate dev default;
  set `useHost = "127.0.0.1"` to restrict to localhost.
- **`exec` of component logic** (`core/sandbox.py`): executes the project
  author's own code with a restricted builtins set; it limits accidents, not
  a hostile project author.
- **`urlopen` readiness probe** (`utils/server/server.py`): URL built from a
  literal http(s) protocol and a numeric port only.

To re-run the audit: `python -m bandit -r nexy/ -c .bandit`
