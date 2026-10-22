# Remix / React Router — Single-Fetch + Routes Mechanism

Deep dive into `remix-run/react-router` (captured mid-2026).

## 1. Route config

`packages/react-router-dev/config/routes.ts`:

- `RouteConfigEntry` = `{ id, path, index, caseSensitive, file, children }` — a plain
  config-based manifest, no filesystem scanning at request time.
- Helpers `route()`, `index()`, `layout()` build the tree declaratively.

**Nexy gap**: Nexy scans the FS and derives `modules_meta`
(`fbrouter/__init__.py:189-318`); no generated `RouteConfigEntry`-style manifest shared
with the client.

## 2. Single-fetch protocol

`packages/react-router/lib/server-runtime/single-fetch.ts`:

- Actions and loaders are collected and dispatched in **one** request: `singleFetchAction`.
- `.data` URL convention: `<route>.data` returns serialized loader data, not HTML.
- `X-Remix-Response` header marks the response as a single-fetch payload.
- `encodeViaTurboStream` — loader/action results streamed over `text/vnd.turbo-stream.html`.
- `staticHandler.query` used server-side; `skipLoaderErrorBubbling` and `skipRevalidation`
  control cache revalidation.
- `normalizePath` + CSRF: `throwIfPotentialCSRFAttack` compared against
  `build.allowedActionOrigins`.

**Nexy gap**: Nexy `@Action` (`nexy/decorators.py:411`, engine
`nexy/routers/actions/engine.py:13`) is POST-only, returns plain data, no `.data` URL
convention, no TurboStream, no CSRF guard.

## 3. Data from the server to the client

- Loader data is the single source of truth; the client uses it directly (no re-fetch).
- `useActionData` re-runs the action during navigation; pitfalls documented upstream
  (`remix#5105`).

**Nexy gap**: no loaders; data lives only in `data-nexy-props` on `<ncc>` tags.

## 4. Progressive enhancement

- Forms without JS still work (HTML POST); JS upgrades them to fetch.
- `Form` + `useActionData` handle pending/error states declaratively.

**Nexy gap**: `nexy.Form` is `pass` — no progressive enhancement, no action states.

## Nexy gaps → epics

- Loaders / typed GET data → `TASKS/10-data-layer/loaders/`
- Client router consuming loader data → `TASKS/08-route-tree/client-side-routing/`
- Action CSRF + multi-protocol → `TASKS/10-data-layer/`
- Form progressive enhancement → (component-level, tracked under data layer)