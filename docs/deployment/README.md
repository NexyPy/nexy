# Deploy

Two commands: `nx build` produces the artifacts, `nx start` serves them.

**Before you start:** a project that builds locally with `nx build`, and - for client pages - the
frontend toolchain that `nx new` installed.

```bash
nx build
nx start --host 0.0.0.0 --port 8000
```

The runtime needs Python only. Uvicorn serves the compiled app and the static assets; no Node
process and no Vite process are involved.

## What the build produces

`__nexy__/` contains the compiled route modules, the client bundle under `__nexy__/client/`, and the
pre-rendered HTML for framework routes. Copy the project - source plus `__nexy__/` - or build inside
the image.

## Docker

The build stage needs Node (for Vite) and Python (for the compiler). The runtime stage needs Python
only.

```dockerfile filename="Dockerfile"
FROM node:22-bookworm-slim AS build
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen && uv run nx build

FROM python:3.13-slim
WORKDIR /app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["nx", "start", "--host", "0.0.0.0", "--port", "8000"]
```

`uv` fetches a managed Python when the base image has none, which is why the build stage can start
from a Node image.

## Behind a reverse proxy

Run `nx start` on localhost and let Nginx, Caddy or the platform proxy terminate TLS:

```bash
nx start --host 127.0.0.1 --port 8000
```

Make sure the proxy forwards WebSocket upgrades if you use `SOCKET` handlers, and that it forwards
the original host - FastAPI builds absolute URLs from it.

## Health check

Add a handler file, `src/routes/api/health.py`, and probe `/api/health` - rather than a page that may
render slowly:

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```

## Static hosting

Every page is HTML, but Nexy assumes a server for routing and for API handlers.

> [!NOTE]
> there is no `--static` build mode. A purely static export has to be generated in
> your pipeline from the `nx build` output.

## Checklist

- [ ] `nx build` in CI, no warnings for routes you expect to render on the server
- [ ] `nx start` exits with code 1, and starts nothing, when a route file cannot load
- [ ] `NEXY_ACTION_SECRET` set, or `__nexy__/action.key` kept with the build
- [ ] `useDocs = False` in production if the API schema should not be public
- [ ] `useTrustedHost` and `useHTTPSRedirect` set for public deployments
- [ ] `__nexy__/` not committed

## Next steps

- [Config](../reference/config.md): HTTPS, trusted hosts, sessions
- [Frontend](../guides/frontend.md): what Vite builds
- [Testing](../guides/testing.md): the commands to run in CI
