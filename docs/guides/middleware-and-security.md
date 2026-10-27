# Middleware and security

Nexy runs on FastAPI and Starlette, so their middleware applies. The common ones are one line in
`nexyconfig.py`.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {
        "allow_origins": ["https://app.example.com"],
        "allow_methods": ["GET", "POST"],
        "allow_credentials": True,
    }
    useGZip = {"minimum_size": 1000}
    useTrustedHost = {"allowed_hosts": ["example.com", "*.example.com"]}
    useHTTPSRedirect = True
    useSession = {"secret_key": "change-me"}
```

Each `use*` dictionary is passed as keyword arguments to the matching Starlette middleware:
`CORSMiddleware`, `GZipMiddleware`, `TrustedHostMiddleware`, `SessionMiddleware`.

## Your own middleware

```python filename="nexyconfig.py"
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` takes ASGI middleware classes.

## HTTPS

Serve HTTPS directly with `useSslKeyfile` and `useSslCertfile`, or terminate TLS at a reverse proxy
and set `useHTTPSRedirect`. In development the Vite dev server stays on loopback HTTP behind the
Nexy origin, so TLS never reaches it.

## Production checklist

- `useDocs = False` if the OpenAPI schema should not be public.
- `useTrustedHost` set to your domains, to block host-header attacks.
- `useCORS` with explicit origins, never `["*"]` together with credentials.
- A real `secret_key` for sessions, read from the environment.
- Props passed to client components are HTML-escaped by Nexy. Do not mark user input `| safe` in
  templates.

## Guards and dependencies

Per-route protection uses FastAPI dependencies. A `dependencies.py` in a routes directory applies to
everything below it: see [Dependencies](../routing/fbr/dependencies/README.md). In the modular router use
[`@UseGuard`](../routing/modular/guards-and-metadata.md).

## Next steps

- [Config](../reference/config.md): every middleware field
- [Deploy](../deployment/README.md)
- [Performance](../deployment/performance.md)
