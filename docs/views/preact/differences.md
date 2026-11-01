# Preact Differences

This guide focuses on the specific implementation details for Preact. For universal concepts (how pages, layouts, and islands work), see the [Frontend Contracts](../frontend/pages.md).

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
URL parameters are available via the `useParams` hook:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

## Layouts

### Implementation
The root layout defines the document shell. Nested layouts wrap the content.

```tsx filename="src/routes/layout.tsx"
import type { ComponentChildren } from "preact";

export default function RootLayout({ children }: { children: ComponentChildren }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

## Islands

In server mode, a Preact component imported into a `.nexy` file is an island.

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
Use the `useAction` hook to manage the state of an action call:

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const { run, pending, error, data } = useAction(add_todo);
// ...
<button onClick={() => run({ title: "New Task" })}>Add</button>
```

### Navigation
Use the `Link` component for client-side transitions. Note that Preact uses `class` instead of `className`:

```tsx
import { Link } from "@nexy/client";

<Link href="/about" class="nav" activeClassName="active">About</Link>
```

For programmatic navigation, use the `useRouter` hook:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### URL Access
- `usePathname()`: current path
- `useParams()`: dynamic segments
- `useSearchParams()`: query string
- `useLocation()`: full location object
