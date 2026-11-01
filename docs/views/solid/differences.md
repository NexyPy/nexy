# Solid Differences

This guide focuses on the specific implementation details for Solid. For universal concepts (how pages, layouts, and islands work), see the [Frontend Contracts](../frontend/pages.md).

## Pages

In client mode (`useCSR = True`), a page is a `.tsx` file.

### Page Component
A page is the default export of the file. If no default export exists, Nexy picks the first named export.

```tsx filename="src/routes/index.tsx"
export default function Home() {
  return <h1>Hello</h1>;
}
```

### Dynamic Segments
URL parameters are available via the `useParams` hook, which returns an accessor:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const params = useParams<{ slug: string }>();
  return <h1>{params().slug}</h1>;
}
```

## Layouts

### Implementation
The root layout defines the document shell. Nested layouts wrap the content.

```tsx filename="src/routes/layout.tsx"
import type { JSX } from "solid-js";

export default function RootLayout(props: { children: JSX.Element }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{props.children}</main>
      </body>
    </html>
  );
}
```
Note: Do not destructure `props.children`, as Solid reads it lazily.

## Islands

In server mode, a Solid component imported into a `.nexy` file is an island.

### Importing
Import components in the frontmatter of the `.nexy` file:

```nexy filename="src/routes/index.md"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```

### Hydration Directives
Use the `directive` prop to control when the island hydrates:
- `client:load` (default): immediately
- `client:idle`: when browser is idle
- `client:visible`: when it scrolls into view
- `client:media`: when media query matches

## Actions and Navigation

### Calling Actions
Use the `useAction` hook to manage the state of an action call. In Solid, this returns accessors (call them as functions).

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const save = useAction(add_todo);
// ...
<button disabled={save.pending()}>Add</button>
```

### Navigation
Use the `Link` component for client-side transitions:

```tsx
import { Link } from "@nexy/client";

<Link href="/about">About</Link>
```

For programmatic navigation, use the `useRouter` hook:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### URL Access
All location hooks return accessors:
- `usePathname()`: current path
- `useParams()`: dynamic segments
- `useSearchParams()`: query string
- `useLocation()`: full location object
