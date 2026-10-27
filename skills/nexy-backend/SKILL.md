---
name: nexy-backend
description: Writing the Python side of a Nexy project - API handlers in src/routes, @Action functions, WebSocket SOCKET handlers, ISR, middleware.py, dependencies.py and error pages. Load it for any .py file in a project built with Nexy.
---

# Backend

## API handlers

A `.py` file under `src/routes/` is an API. Functions named `GET`, `POST`, `PUT`, `PATCH`,
`DELETE`, `OPTIONS`, `HEAD` become endpoints at the path of the file.

```python
# src/routes/api/items.py
from nexy.http import Request
from pydantic import BaseModel


class Item(BaseModel):
    name: str


async def GET(request: Request):
    return {"items": []}


async def POST(request: Request, body: Item):
    return {"created": body.name}
```

- Import the HTTP vocabulary from `nexy.http`.
- Path segment `[id]` is the argument `id`, converted to its annotation. A value that cannot be
  converted is a `404`.
- Return a `dict`, a list or a `BaseModel` for JSON, or a response object when the status or type
  matters.
- Raise `HTTPException` for client errors.
- One handler, one treatment: a function validates, or loads, or saves. Put shared logic in a
  service module under a folder named for its intention, not in the handler.

## Actions

`@Action` turns a function into a typed `POST` endpoint with a generated path.

```python
# src/actions/user.py
from nexy.decorators import Action, revalidate


@Action
async def create_user(name: str, age: int = 0) -> dict[str, str | int]:
    revalidate()
    return {"name": name, "age": age}
```

- The parameters are the input, validated by Pydantic. `request` and `response` are injected.
- Types are generated to `@nexy/actions`; the client calls it with `useAction`.
- Call `revalidate()` so the open page refreshes after a change.
- Authorization is yours: read the session or cookies from `request` and raise `HTTPException(403)`.
- Test the function directly; never hard-code the generated `/_nx_...` path.

## WebSocket

Define `async def SOCKET(websocket: WebSocket)` in a `.py` route file. The path is the file path.

## Caching a page (ISR)

In a `.nexy` page, `revalidate = 60` caches it per path with stale-while-revalidate. API handlers
are not cached this way.

## Middleware and dependencies

- `middleware.py`: `async def middleware(request, call_next)` wrapping the directory and below.
- `dependencies.py`: `dependencies = [fn, ...]` applied to the directory and below.

## Error pages

`notfound.nexy` renders 404 and `errors.nexy` renders 500, each scoped to its directory. A client
that sends `Accept: application/json` receives `{"detail": "..."}` instead. Error text follows
[nexy-principles](../nexy-principles/SKILL.md): what happened, what to do.

## Rules

- Configuration comes from `nexyconfig.py`, not from scattered constants.
- No side effects at import time: no connections, no file handles, no network calls.
- Type everything; `mypy --strict` must pass.
- Write the test first ([nexy-testing](../nexy-testing/SKILL.md)).
