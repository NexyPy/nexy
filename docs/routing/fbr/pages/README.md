# Pages

A page file returns HTML. Which file type you use changes how it is produced: see
[views](../../../views/README.md). This section covers the routing rules that apply to every page
format.

| Page | What it covers |
|---|---|
| [Dynamic routes](dynamic-routes.md) | `[slug]`, `[...path]`, route groups, typed segments |
| [Error pages](../errors/README.md) | `notfound.nexy`, `errors.nexy`, JSON for API clients |
| [Layouts](../layouts/README.md) | One page per layout file type |
| [Inheritance](../inheritance.md) | How layouts and dependencies stack |

## A minimal page

```nexy filename="src/routes/about.nexy"
---
title: prop[str] = "About"
---
<h1>{{ title }}</h1>
```

It is served at `/about`. The frontmatter between the `---` lines is Python; the markup below it is
Jinja2. See [.nexy files](../../../views/nexy/README.md).

## Page formats

| Mode | File | Produces |
|---|---|---|
| Server | `.nexy` | server-rendered HTML from Python and Jinja2 |
| Server | `.md`, `.mdx` | content pages |
| Client | `.tsx`, `.jsx`, `.vue`, `.svelte` | framework components, rendered and navigated in the browser |

The two modes cannot be mixed in one project. See [Server mode and client mode](../modes.md).
Client components can still appear in server mode, as [islands](../../../rendering/islands.md)
inside a `.nexy` page.

## Incremental caching

Add `revalidate = 60` to a `.nexy` page to cache it with stale-while-revalidate. See
[ISR](../../../rendering/isr.md).

## Reading the request

A page reads the path, query string, cookies and session through hooks. See
[Hooks](../navigation/hooks.md).

## Next steps

- [Dynamic routes](dynamic-routes.md)
- [Error pages](../errors/README.md)
- [Modular routing](../../modular/README.md): controllers instead of files
