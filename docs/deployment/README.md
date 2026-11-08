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

<!-- router:fbr,custom -->
Add a handler file, `src/routes/api/health.py`, and probe `/api/health` - rather than a page that may
render slowly:

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```
<!-- /router -->

<!-- router:modular -->
Add a controller, and probe `/health/` - rather than a view that may render slowly:

```python filename="src/apps/health_controller.py"
from nexy.decorators import Controller


@Controller("/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```

List it in the `controllers` of the root module.
<!-- /router -->

### Built-in endpoints

A load balancer or Kubernetes asks two questions: is the process alive, and may it receive traffic?
Set `useHealth` and Nexy answers both, with no handler file and no controller:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useHealth = True
```

| Endpoint | Answers 200 | Answers 503 |
|---|---|---|
| `GET /health/live` | while the process answers | never |
| `GET /health/ready` | once the application has started | while it starts, and once the server asks it to stop |

Nexy guarantees that `/health/ready` follows the startup and shutdown of the server.

Nexy guarantees that both endpoints stay out of the access log and out of the OpenAPI schema.

Nexy guarantees that both endpoints answer before `useTrustedHost` and `useHTTPSRedirect`, so a
probe sent over HTTP to the address of a pod is not refused.

By convention you keep your own routes off `/health/live` and `/health/ready` while `useHealth` is
on: the endpoints of Nexy answer first. `useHealth` is `False` by default, so a project that does
not set it keeps both paths.

Your application is responsible for checking what it depends on: `/health/ready` reports the
lifecycle of the server, not the state of a database.

Point the probes of a Kubernetes `Deployment` at them:

```yaml filename="k8s/deployment.yaml"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      containers:
        - name: app
          image: registry.example.com/app:1.0
          ports:
            - containerPort: 8000
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8000
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
            periodSeconds: 5
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
- [ ] `useHealth = True` when a load balancer or Kubernetes probes the app
- [ ] `__nexy__/` not committed

## Next steps

- [Config](../reference/config.md): HTTPS, trusted hosts, sessions
- [Frontend](../guides/frontend.md): what Vite builds
- [Testing](../guides/testing.md): the commands to run in CI
