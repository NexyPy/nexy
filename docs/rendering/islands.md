# Islands and hydration

## Definition

An island is a client component - React, Vue, Svelte, Solid or Preact - imported into a `.nexy`
page. The server renders its HTML; the browser makes that one component interactive. The rest of the
page stays HTML.

Islands exist in server mode. In client mode the components *are* the pages: see [CSR](csr.md).

## How it works

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter directive="client:visible" />
```

Nexy renders the component at build time, stores its HTML, and places it inside the page. The page
response carries that HTML plus the props as a JSON attribute. In the browser, the island runtime
loads the component and takes over the container.

`directive` decides **when** that happens. Without one, the island hydrates as soon as its runtime
is ready.

## Rendering lifecycle

1. At build, every client component is rendered to HTML and written under `__nexy__/client/static/`.
2. A request renders the `.nexy` page; the island's HTML is inserted in place of the tag.
3. The response carries the HTML, the props, and the directive as attributes.
4. In the browser, the runtime schedules hydration according to the directive.
5. Hydration replaces the static HTML with the live component; the rest of the page is untouched.

In development there is no build snapshot: the container is empty and the component renders in the
browser. The page looks the same, but the first paint differs from production.

## When to use

- A page that is mostly content and has one or two interactive spots.
- A widget that must exist in the HTML for crawlers and still work.
- A component that needs the browser but should not drag the whole page into client rendering.

## Configuration

| Directive | Hydrates |
|---|---|
| none, or `client:load` | immediately |
| `client:idle` | when the browser is idle (`requestIdleCallback`, 2 s timeout) |
| `client:visible` | when the island enters the viewport, 200 px early |
| `client:media` | when a media query matches; set it with the `media` prop |

```nexy
<Chart directive="client:media" media="(min-width: 768px)" />
```

`client:media` defaults to `(min-width: 768px)` when `media` is absent, and hydrates once. On a
browser without `IntersectionObserver`, `client:visible` falls back to idle.

`directive` and `media` are consumed by Nexy: they are not passed to your component.

## Example

```tsx filename="src/components/Counter.tsx"
import { useState } from "react"

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Count</h1>
<Counter start=3 directive="client:idle" />
```

## Limitations

- **`client:only` never hydrates.** It is accepted, but the runtime skips it, so the server HTML stays
  inert. Use a client route ([CSR](csr.md)) when a component cannot render on the server.
- **`client:manual` has no public trigger.** It is also skipped automatically, and the handle that
  resumes it is internal.
- **Props must be JSON.** They are serialized with `json.dumps`; a value that cannot be serialized is
  dropped, and the island receives `{}` - silently.
- **An island is not a client component with shared state.** Two islands do not share state without a
  mechanism you add yourself.
- **The island is not re-rendered by the server.** Its HTML is the build snapshot, plus whatever the
  component does once hydrated.
- **A page of islands is a CSR page in disguise.** If every block needs to talk to every other, pick
  client mode instead.

## Next steps

- [Rendering](README.md): the four modes
- [Components](../views/nexy/components.md): how a `.nexy` page imports one
- [React](../views/react/differences.md), [Vue](../views/vue/differences.md),
  [Svelte](../views/svelte/differences.md), [Solid](../views/solid/differences.md),
  [Preact](../views/preact/differences.md)
