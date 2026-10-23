# Preact

Preact 10 routes: server-rendered first, then hydrated by Vite in the browser.

## Enable Preact

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import preact


class NexyConfig(NexyConfigModel):
    useFF = preact()
    useAliases = {"@": "src"}
```

- Extensions: `.tsx`, `.jsx`
- Runtime: Preact 10 (`preact`, `preact-render-to-string`)
- Build: `@preact/preset-vite`

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

> **Good to know**: `.mdx` files are compiled with Preact too when their imports resolve to Preact -
> see [Markdown](markdown.md).

## Rendering

Server rendering is on by default. Set `useCSR = True` for
[client-side rendering](../routing/fbr/csr.md).

## Next steps

- [Views](README.md): compare formats
- [Markdown and MDX](markdown.md): `.mdx` routes
- [Frontend](../frontend.md): Vite and the client build
