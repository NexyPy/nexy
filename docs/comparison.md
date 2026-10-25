# Coming from another framework

Nexy is FastAPI plus file-based routing, server-rendered pages and optional React, Vue, Svelte,
Solid or Preact islands. This page maps what you already know.

## From FastAPI

| FastAPI | Nexy |
|---|---|
| `@app.get("/users")` in a module you import | `GET` function in `src/routes/users.py` |
| `app.include_router(router)` | the file path is the URL; nothing to register |
| Path param `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | still `Depends(...)`: handlers are FastAPI handlers |
| Jinja2 `TemplateResponse` | a `.nexy` page next to the endpoint |
| Run with `uvicorn main:app` | `nx dev`, then `nx build && nx start` |

Everything under `src/routes/*.py` is ordinary FastAPI: dependencies, Pydantic models, middleware
and `/docs` keep working.

## From Next.js

| Next.js | Nexy |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` or `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (owns `<html>`) | `src/routes/layout.nexy` (owns `<html>`) |
| nested `layout.tsx` | nested `layout.nexy`, or `layout.tsx` for React and Preact |
| Route handlers `route.ts` | `src/routes/api/x.py`, written in Python |
| `(group)` folders | same: `(group)/` |
| Server Actions | [`@Action`](actions.md) functions called from a form |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

The backend is Python, so your API shares code with your data and ML work. Client components
hydrate as islands instead of a whole-page React tree.

## From Express or Node backends

| Express | Nexy |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` with `async def GET(id)` |
| `app.use(middleware)` | FastAPI middleware, registered from `nexyconfig.py` |
| `res.json(obj)` | return a dict or a Pydantic model |
| EJS / Pug views | `.nexy` (Jinja2) pages |
| `npm run dev` | `nx dev` |

## Choosing a router

| Use | When |
|---|---|
| File-based router | pages and endpoints mapped from files; the default |
| Modular router | controllers, modules and dependency injection, NestJS-style |

Both are scaffolded by `nx new` and covered by the same end-to-end tests. See
[Routing](routing/README.md) and [Modular routing](routing/modular.md).
