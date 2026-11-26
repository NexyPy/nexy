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

## Rate limiting

`useRateLimit` answers `429 Too Many Requests` to a client address that sends more than `requests`
requests in one window of `per` seconds.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useRateLimit = {"requests": 60, "per": 60, "paths": ["/api/", "/_nx_"]}
```

Nexy guarantees that a request over the limit gets a `429` with a `Retry-After` header, the seconds
left in the window, and never reaches your routes, actions or middleware.

Nexy guarantees that without `useRateLimit` no rate limit middleware is added.

Nexy guarantees that the `useHealth` probes are never limited.

`paths` is optional: without it every path is limited. Server actions are served under `/_nx_`, so
that prefix limits all of them.

The window is fixed and shared by all clients: the counts start again at each multiple of `per`
seconds. A client can therefore send up to twice `requests` across the edge of a window.

The counts live in the memory of each worker. With `useWorkers` above one, a client can send
`requests` to each worker, and the counts start again when the server restarts.

The client address is the one uvicorn gives the request. Behind a reverse proxy on the same machine,
uvicorn reads it from `X-Forwarded-For`; for a proxy on another machine, list its address in the
`FORWARDED_ALLOW_IPS` environment variable, or every client shares the address of the proxy.

Your application is responsible for a limit shared by several workers or servers: a reverse proxy
or a store such as Redis.

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
