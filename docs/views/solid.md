# Solid

Solid 1.9 routes: server-rendered first, then hydrated by Vite in the browser.

## Enable Solid

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import solid


class NexyConfig(NexyConfigModel):
    useFF = solid()
    useAliases = {"@": "src"}
```

- Extensions: `.tsx`, `.jsx`
- Runtime: Solid 1.9 (`solid-js`)
- Build: `vite-plugin-solid`

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

> [!NOTE]
> Solid components run once. Use signals and memos rather than re-reading values
> in the component body.

## Rendering

Server rendering is on by default. Set `useCSR = True` for
[client-side rendering](../rendering/csr.md).

## Layouts

In client mode the root `layout.tsx` owns the HTML document, as in React, and every `layout.tsx` renders
its page with `props.children`. See [layout.tsx](../routing/fbr/layouts/layout.tsx.md).

## Next steps

- [Views](README.md): compare formats
- [Frontend](../guides/frontend.md): Vite and the client build
- [.nexy files](nexy/README.md): mixing server logic and Solid islands
