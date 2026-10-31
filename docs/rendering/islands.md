# Islands and hydration

A client component (React, Vue, Svelte, Solid, Preact) imported in a `.nexy` page is an **island**:
the server renders its HTML, then the browser makes it interactive. The `directive` prop chooses
when.

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter directive="client:visible" />
```

## Directives

| Directive | Hydrates |
|---|---|
| none, or `client:load` | immediately (default) |
| `client:idle` | when the browser is idle |
| `client:visible` | when the island scrolls into view (200px margin) |
| `client:media` | when a media query matches; set it with the `media` prop |
| `client:only` | never on the server: the browser renders it from scratch |
| `client:manual` | never automatically: your code triggers it |

```nexy
<Chart directive="client:media" media="(min-width: 768px)" />
```

`directive` and `media` are consumed by Nexy and are not passed to your component as props.

## Props

Props written on the tag are serialized to the island. Values are HTML-escaped in the page, so a
string containing quotes or tags cannot break out of the markup.

## When to use which

- Above the fold and needed immediately: the default.
- Below the fold: `client:visible`.
- Non-essential widgets: `client:idle`.
- Desktop-only components: `client:media`.
- Components that read `window` during render: `client:only`.

## Next steps

- [Rendering](README.md)
- [Components](../views/nexy/components.md)
- [React](../views/react/README.md), [Vue](../views/vue/README.md), [Svelte](../views/svelte/README.md)
