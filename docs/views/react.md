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

A `layout.tsx` wraps the pages below it and receives them as `children`. It never writes `<html>`:
the document stays in `layout.nexy`. See [Layouts](../routing/layouts.md).

## Rendering

Server rendering is on by default. Set `useCSR = True` for
[client-side rendering](../routing/fbr/csr.md).

## Next steps

- [Views](README.md): compare formats
- [Components](components.md): import a component from a `.nexy` page
- [Frontend](../frontend.md): Vite and the client build
