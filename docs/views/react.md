# React

React 19 routes: server-rendered first, then hydrated by Vite in the browser.

## Enable React

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

- Extensions: `.tsx`, `.jsx`
- Runtime: React 19 (`react`, `react-dom`)
- Build: `@vitejs/plugin-react`

## Create a route

```tsx filename="src/routes/index.tsx"
import Counter from "@/components/Counter";

export default function Home() {
  return (
    <main>
      <h1>Hello</h1>
      <Counter />
    </main>
  );
}
```

The default export is the page component; a named export also works.

> **Good to know**: keep components outside `src/routes/` (usually `src/components/`) so they are
> not treated as pages.

## Layouts

In client mode (`useCSR = True`) the root `layout.tsx` owns the HTML document, like the root layout
of the Next.js App Router, and nested `layout.tsx` files wrap the pages below them. See
[layout.tsx](../routing/fbr/layouts/layout.tsx.md). In server mode React components are
[islands](../rendering/islands.md) inside `.nexy` pages and there is no `layout.tsx`.

## Rendering

Server rendering is on by default. Set `useCSR = True` for
[client-side rendering](../rendering/csr.md).

## Next steps

- [Views](README.md): compare formats
- [Components](components.md): import a component from a `.nexy` page
- [Frontend](../guides/frontend.md): Vite and the client build
