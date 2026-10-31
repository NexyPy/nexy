# React pages

In client mode a page is a `.tsx` file under `src/routes/`. Nexy renders it on the server for the
first response, React hydrates it, and the client router swaps pages from there.

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

## A page

```tsx filename="src/routes/index.tsx"
import Counter from "@/components/Counter";

export default function Home() {
  return (
    <>
      <h1>Hello</h1>
      <Counter />
    </>
  );
}
```

```tsx filename="src/components/Counter.tsx"
import { useState } from "react";

export default function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

The file path is the URL, as for every route:

| File | URL |
|---|---|
| `src/routes/index.tsx` | `/` |
| `src/routes/about.tsx` | `/about` |
| `src/routes/blog/[slug].tsx` | `/blog/{slug}` |
| `src/routes/docs/[...path].tsx` | `/docs/{path:path}` |
| `src/routes/(app)/settings.tsx` | `/settings` |

## Which export is the page

1. `export default`, when the file has one.
2. Otherwise the first `export function`, `export const` or `export class`.
3. Otherwise the file name in PascalCase: `user-card.tsx` is `UserCard`.

Keep one component per route file and export it as default; put the others in `src/components/`.

## Dynamic segments

The segments of the URL reach the page as props, `Post({ slug }: { slug: string })`, and through
`useParams()`:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

`useParams()` reads the same values from the client router, so a deeply nested component does not
need them passed down. A catch-all gives one string with the slashes: `/docs/a/b` gives
`path == "a/b"`.

## Data

A client page has no Python frontmatter. Its data comes from Python in one of two ways:

- an [action](../../guides/actions.md): a typed function you call with `useAction`, see
  [Actions and navigation](actions-and-navigation.md);
- an API handler next to the pages, `src/routes/api/posts.py`, that you `fetch`.

## How the page is rendered

| Moment | What happens |
|---|---|
| `nx dev` | Vite renders the layouts and the page in Node for each request, then React hydrates. |
| `nx build` | Every static page is rendered once to HTML. A dynamic page is built as a shell: its layouts around an empty page, filled in the browser. |
| `nx start` | Python serves the pre-rendered HTML. No Node process runs. |
| A click on a link | The client router imports the next page and renders it; the layouts stay mounted. |

## Rules

- Only `.tsx` pages are routes. A `.jsx` file is fine as a component, not as a page.
- `.md` and `.mdx` files stay routes in client mode: Nexy renders them inside your layouts.
- A `.py` file under `src/routes/` is an API handler, not a page. Do not give it the same URL as a
  page.
- Code that reads `window` or `document` must run in `useEffect`: the first render runs in Node.

## Next steps

- [Layouts](layouts.md): the document and the nested layouts
- [Actions and navigation](actions-and-navigation.md): links, hooks, actions
- [Dynamic routes](../../routing/fbr/pages/dynamic-routes.md): segments, catch-alls, groups
- [CSR](../../rendering/csr.md): client-side rendering
