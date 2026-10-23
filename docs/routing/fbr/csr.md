# CSR (client-side rendering)

Client-side rendering turns navigation over to the browser after the first load. Enable it in
`nexyconfig.py`.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useFF = "react"
    useCSR = True
```

## Rules

- `useCSR` requires `useFF`. Validation rejects `useCSR = True` without a client framework.
- `.nexy` pages are disabled in CSR mode and skipped with a warning. Use framework routes or
  `.md`/`.mdx`.
- `useRouter` is incompatible with `useCSR`.
- Only navigable framework route files are handled by the client router: `.tsx`, `.jsx`, `.vue`,
  `.svelte`.
- `.md` routes can be served with a CSR shell.

## Behaviour

The first load returns HTML. After that, the client router handles navigation between navigable
routes in the browser. Framework routes are mounted client-side.

## Next steps

- [SSR](ssr.md): the default mode
- [ISR](isr.md): cache server-rendered pages
- [Frontend](../../frontend.md): the dev server and the client build
