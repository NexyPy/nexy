# layout.nexy

The layout file of server mode (`useCSR = False`). The root one owns the HTML document.

## Root layout

```nexy filename="src/routes/layout.nexy"
---
from nexy import Vite

children: prop[NexyElement]
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My app</title>
  <Vite />
</head>
<body>
  <main>{{ children | safe }}</main>
</body>
</html>
```

- `<!DOCTYPE html>`, `<html>`, `<head>` and `<body>` live here and nowhere else.
- `<Vite />` injects the client scripts and styles once, in the `<head>`.
- `{{ children | safe }}` is where the page, or the next nested layout, renders.

## Nested layouts

A `layout.nexy` in a subdirectory wraps that subtree and renders inside its parent. It does not repeat
the document tags:

```nexy filename="src/routes/blog/layout.nexy"
---
children: prop[NexyElement]
---
<nav>...</nav>
<article>{{ children | safe }}</article>
```

`blog/[slug].nexy` renders as `layout.nexy > blog/layout.nexy > page`.

## Components and islands

A layout can import `.nexy` components (a header, a footer) and client components. A client
component in a layout is an [island](../../../rendering/islands.md) like any other:

```nexy
---
from "@/components/Header.nexy" import Header
from "@/components/theme/theme.tsx" import Theme
---
<Header />
<Theme directive="client:idle" />
```

## Without a layout

A project without `layout.nexy` still answers with a valid document: Nexy falls back to a minimal
shell with `<!DOCTYPE html>`, the viewport meta and the Vite tags. Add a layout as soon as you need
a title, fonts or navigation.

## In the modular router

Controllers choose their views, so they compose the layout themselves:

```python
return useViews("src/apps/layout.nexy", context={"children": useViews("src/apps/app_view.nexy")})
```

## What it cannot do

- It cannot coexist with `layout.tsx`, `layout.vue` or `layout.svelte`: a server-mode project has
  no client routes ([modes](../modes.md)).
- It does not run on the client: use an island for interactivity.

## Next steps

- [Layouts](README.md)
- [Inheritance](../inheritance.md)
- [.nexy files](../../../views/nexyfile.md)
