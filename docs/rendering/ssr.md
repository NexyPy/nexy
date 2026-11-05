# SSR (server rendering)

## Definition

SSR is the default: the server renders the page to HTML for each request. Nothing enables it, and
no flag turns it off - a server-mode project renders on every request unless a page declares
`revalidate`.

## How it works

| Route file | What produces the HTML | When |
|---|---|---|
| `.nexy` | the compiled Python module, through Jinja2 | every request |
| `.md` | Markdown, then the nearest layout | every request |
| `.mdx`, `.tsx`, `.vue`, `.svelte` | the framework, rendered in Node | at build when the route has no layout, otherwise in the browser |
| `.py` | nothing: it returns JSON or a `Response` | - |

A component route is the one case that needs a second sentence. In production, a component route
**without** a layout is served with the HTML produced at build, and the component hydrates it. With
a layout, or in development, the container is empty and the component renders in the browser - the
page is then a shell that fills itself.

## Rendering lifecycle

1. The request reaches the file-based router. The path is matched, and dynamic segments are cast to
   the types the component declares.
2. The component runs. One that waits on Node - a client document - runs in a thread pool, so it
   does not stall the event loop.
3. The body is streamed as `text/html`. A component that yields chunks streams them as it makes
   them.
4. The browser receives HTML. Islands hydrate according to their [directive](islands.md).

An error raised while rendering is turned into a page by `errors.nexy` when the project has one: see
[error pages](../routing/fbr/errors/README.md).

## When to use

- The page shows something the reader owns: a session, an account, a cart.
- The data must be fresh on every load.
- The content must be in the HTML for crawlers that do not run JavaScript.
- The page is cheap to render: one query, one template.

## Configuration

None. Two ways out, and they do not have the same grain:

| To leave SSR for | Do this | Grain |
|---|---|---|
| one page, with a cache | `revalidate = 60` in its frontmatter → [ISR](isr.md) | page |
| the whole project, client-routed | `useCSR = True` in `nexyconfig.py` → [CSR](csr.md) | project |

## Example

```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` runs this template once, with `slug` set to `hello`. A second request runs it
again: nothing is kept between the two. The query string is not a prop - read it with the hooks in
[navigation](../routing/fbr/navigation/hooks.md).

## Limitations

- **One render per request.** Two visitors in the same second each pay for the render and for the
  queries behind it.
- **No cache.** There is no shared response cache to warm: [ISR](isr.md) adds one, per URL.
- **Streaming only helps a component that yields.** A slow query at the top of the page still delays
  the first byte.
- **No static output.** In server mode nothing is frozen at build: there is no SSG mode, and no
  export command. See [Rendering](README.md).
- **Autoescaping is off** in `.nexy` templates. Escape untrusted values with `| e`.

## Next steps

- [ISR](isr.md): cache this page per URL
- [Islands](islands.md): keep SSR and make one widget interactive
- [CSR](csr.md): hand navigation to the browser
- [Performance](../deployment/performance.md)
