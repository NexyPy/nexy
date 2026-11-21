# Custom router: an existing FastAPI app inside Nexy

A library had a FastAPI service before it had a website. This sample plugs that service into Nexy
as it is, with one line, and adds a page next to it:

```python filename="nexyconfig.py"
useRouter = service.router
```

| File | What it is |
|---|---|
| `src/library/` | the FastAPI app, untouched: two routers, `include_router`, a token dependency. Nothing there imports Nexy |
| `src/routes/index.nexy` | a Nexy page that reads the same books |
| `src/routes/api/v2/books.py` | the first route moved from the service to a file of Nexy |

The old `GET /api/v1/books` keeps answering while clients move to `GET /api/v2/books`: that is a
gradual migration, one route at a time. [The custom router guide](../../docs/routing/custom/README.md)
has the details.

## What changes for the service inside Nexy

Most of it works as in FastAPI: path and body validation, `Depends`, `HTTPException`, response
models. Three things to know:

- **Errors answer the client in its format.** A client that sends `Accept: application/json` gets
  `{"detail": "No such book."}`; a browser gets the 404 page. Have API clients send that header.
- **A path value of the wrong type is a 404**, not FastAPI's 422: `/api/v1/books/one` is an address
  that does not exist.
- **Pages are not wrapped by `layout.nexy`** while `useRouter` is set: `index.nexy` is a whole
  document.

The loans are kept in memory, so `nexyconfig.py` sets `useWorkers = 1`: `nx start` otherwise runs
one process per CPU on Linux and macOS, each with its own books.

## Run it

You need Python 3.12 or newer, [uv](https://docs.astral.sh/uv/), and Node.js with npm, pnpm or
bun.

```bash
git clone https://github.com/NexyPy/nexy
cd nexy/examples/custom-router
uv sync
npm install          # or pnpm install, bun install
uv run nexy dev
```

```bash
curl -H "Accept: application/json" localhost:3000/api/v1/books
curl -X POST -H "X-Staff-Token: demo-staff-token" localhost:3000/api/v1/books/1/loan
```

`demo-staff-token` is for a first run only: set `LIBRARY_STAFF_TOKEN` to your own.

## Test it

```bash
uv run pytest
```

The tests call the routes of the service, its dependency with and without a token, the moved route
and the page, and pin the three differences above.
