# Inheritance

Several files in `src/routes/` apply to everything below their directory. They all resolve the same
way: Nexy starts at the route's directory and walks up to `src/routes/`.

```text
src/routes/
├─ layout.nexy               1. outermost
├─ dependencies.py           1. runs first
├─ middleware.py             1. wraps first
├─ notfound.nexy             fallback for every URL
├─ (shop)/                   a group is a directory: it takes part, it is not in the URL
│  ├─ layout.nexy            2.
│  ├─ dependencies.py        2.
│  └─ cart/
│     ├─ layout.nexy         3. innermost
│     ├─ dependencies.py     3. runs last
│     └─ index.nexy          the page
```

| File | Rule |
|---|---|
| `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` | every layout from the root to the page wraps it, **outermost first** |
| `middleware.py` | every file from the root to the route wraps the request, **outermost first**, before dependencies |
| `dependencies.py` | every file from the root to the route runs, **outermost first**, then the handler's own guards |
| `notfound.nexy`, `errors.nexy` | the **nearest** one wins, per status code |

For the page above, the layouts nest as
`root layout > (shop) layout > cart layout > page`, and the dependencies run as
`root > (shop) > cart > handler guards`.

## Why outermost first

An outer layout draws the frame and an outer dependency decides who may come in at all. Putting them
first means the inner ones can rely on them: a directory that requires authentication runs before a
handler that reads the user.

## Layouts

All layout files of a folder family stack: see [Layouts](layouts/README.md). Different families do
not mix: a `layout.vue` never wraps a `.tsx` page, and a project has either `layout.nexy` or client
layouts, never both ([modes](modes.md)).

## Middleware files

See [Middleware files](middleware/README.md): they run before dependencies and can answer
without reaching the route.

## Dependencies

See [Dependencies](dependencies/README.md) for the order in a handler file, including `@UseGuard`
and `@Middleware`.

## Error pages

`notfound.nexy` and `errors.nexy` are installed once at the routes root; a copy in a subdirectory
refines the page for that prefix. See [Error pages](errors/README.md).

## Next steps

- [Layouts](layouts/README.md)
- [Dependencies](dependencies/README.md)
- [Error pages](errors/README.md)
