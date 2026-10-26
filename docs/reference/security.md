# Security

How Nexy keeps its own attack surface small, which versions it requires, and how to check a project.

## Version floors

Nexy depends on FastAPI, Starlette, Jinja2, Vite and React. A floor is the lowest version Nexy
allows; each one answers a published advisory.

| Package | Floor | Why |
|---|---|---|
| `starlette` | 1.0.1 | CVE-2026-48710 (BadHost): a crafted `Host` header changes the path Starlette reports to middleware, which bypasses authorization written on `request.url.path`. Listed as exploited by CISA. |
| `fastapi` | 0.133.0 | the first release that accepts a fixed Starlette |
| `jinja2` | 3.1.6 | sandbox escape through the `attr` filter (CVE-2025-27516) |
| `vite` (scaffolded projects) | 6.4.3 | `server.fs.deny` bypass on Windows alternate paths (CVE-2026-53571); the earlier query-string bypass (CVE-2026-39364) affects only Vite 7.1-7.3.1 and 8.0.0-8.0.4 |
| `react`, `react-dom` | 19.2.5 | the 2026 React advisories concern the `react-server-dom-*` packages, which Nexy does not use; the floor keeps the line patched |

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
  HTML-escaped. `| safe` in a template turns this off: never use it on user input.
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
