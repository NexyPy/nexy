# Security

How Nexy keeps its own attack surface small, which versions it requires, and how to check a project.

## Version floors

Nexy depends on FastAPI, Starlette, Jinja2, Vite and React. A floor is the lowest version Nexy
allows; each one answers a published advisory.

| Package | Floor | Why |
|---|---|---|
| `starlette` | 1.3.1 | CVE-2026-48710 (BadHost, fixed in 1.0.1): a crafted `Host` header changes the path Starlette reports to middleware, which bypasses authorization written on `request.url.path`; listed as exploited by CISA. CVE-2026-48817 and CVE-2026-48818 (request dispatch, `StaticFiles` on Windows, fixed in 1.1.0), CVE-2026-54282 (request path not validated, 1.3.0) and CVE-2026-54283 (`request.form()` limits, 1.3.1). |
| `python-dotenv` | 1.2.2 | CVE-2026-28684, in the reader of the `.env` file `nx migrate` loads |
| `fastapi` | 0.133.0 | the first release that accepts a fixed Starlette |
| `jinja2` | 3.1.6 | sandbox escape through the `attr` filter (CVE-2025-27516) |
| `vite` (scaffolded projects) | 6.4.5 | `server.fs.deny` bypasses (CVE-2026-53571 on Windows alternate paths; GHSA-rq7h-c2jc-7f22, fixed in 6.4.4; GHSA-8g5g-mxqh-grgj, a query bypass 6.4.4 itself brought, fixed in 6.4.5), and the `launch-editor` advisories fixed in 6.4.4 |
| `svelte` (scaffolded projects) | 5.55.7 | six server-rendering XSS advisories through spread attributes, dynamic tag names and `bind:innerText` |
| `esbuild` (scaffolded projects) | 0.28.1 | arbitrary file read through the development server (GHSA-g7r4-m6w7-qqqr) |
| `react`, `react-dom` | 19.2.5 | the 2026 React advisories concern the `react-server-dom-*` packages, which Nexy does not use; the floor keeps the line patched |

`python scripts/audit_dependencies.py` checks every floor against OSV after the lock, in CI too: a new advisory on a floor fails the audit.

Check your resolved versions:

```bash
uv pip list | grep -i -E "starlette|fastapi|jinja2"
npm ls vite
```

## Rules Nexy follows

- **Never trust the Host header for paths.** Nexy reads `scope["path"]`, not `request.url.path`, in
  its own middleware (directory middleware). Do the same in yours.
- **Escape what reaches HTML.** Props passed to client components, `Link` attributes, `Image`,
  `Audio` and `Video` attributes, table-of-contents anchors and `HTTPException` details are all
  HTML-escaped. A `.nexy` template does not escape on its own: write `{{ value | e }}` for any
  value that comes from a visitor or the database, and never `| safe` on user input.
- **Developer endpoints are loopback-only and narrow.** The dev render endpoint
  (`/__nexy__/render`) only accepts files under `src/routes/` with a `.tsx` or `.jsx` extension, and
  is reachable only through the dev server, which refuses foreign `Host` headers.
- **Error details do not leak.** An error page that itself fails shows only the status code.
- **Production answers carry safe headers.** `X-Content-Type-Options: nosniff` and
  `Referrer-Policy: strict-origin-when-cross-origin`, unless your code sets its own. The `Server`
  header is not sent. Add `Strict-Transport-Security` and a `Content-Security-Policy` in your
  proxy or a middleware: they depend on your domain.
- **A crash shows a reference, not the error.** See [Error pages](../routing/fbr/errors/README.md#unhandled-exceptions).
- **No `eval` and no `shell=True` in Nexy's Python code.** External programs run with an argument list.

## Running the audits

```bash
python scripts/audit_dependencies.py        # Python dependencies against the lock
npm audit                                    # in a scaffolded project
uv run bandit -r nexy -c .bandit             # static analysis of Nexy itself
```

Nexy's own repository runs the first and the third in its checks. A new advisory on a floor above is handled by raising the
floor in `pyproject.toml` or in the scaffolded `package.json`, then regenerating the lock.

## Deploying safely

- Set `useTrustedHost` to your domains: it rejects unexpected `Host` headers before any route.
- Do not expose the Vite dev server: `nx dev` keeps it on loopback behind the Nexy origin.
- Set `useDocs = False` if the API schema should not be public.

See [Middleware and security](../guides/middleware-and-security.md).

## Sources

- [CVE-2026-48710 (BadHost) in Starlette](https://www.penligent.ai/hackinglabs/cve-2026-48710/)
- [Vite advisory GHSA-fx2h-pf6j-xcff](https://github.com/advisories/GHSA-fx2h-pf6j-xcff) and
  [GHSA-v2wj-q39q-566r](https://github.com/advisories/GHSA-v2wj-q39q-566r)
- [Jinja2 CVE-2025-27516](https://advisories.gitlab.com/pypi/jinja2/CVE-2025-27516/)
- [React server packages CVE-2026-44907](https://www.wiz.io/vulnerability-database/cve/cve-2026-44907)

## Next steps

- [Middleware and security](../guides/middleware-and-security.md)
- [Deploy](../deployment/README.md)
- [Config](config.md)
