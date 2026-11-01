# Svelte Differences

This guide focuses on the specific implementation details for Svelte. For universal concepts (how pages, layouts, and islands work), see the [Frontend Contracts](../frontend/pages.md).

## Pages

In client mode (`useCSR = True`), a page is a `.svelte` file.

### Page Component
The page is the component defined by the script block of the `.svelte` file.

```svelte filename="src/routes/index.svelte"
<script lang="ts">
</script>

<h1>Hello</h1>
```

### Dynamic Segments
URL parameters reach the page as props via the `$props()` rune:

```svelte filename="src/routes/blog/[slug].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

Alternatively, use the `$params` store from `@nexy/client` in any component.

## Layouts

### Implementation
The root layout defines the document shell. Nested layouts wrap the content using the `children` snippet.

```svelte filename="src/routes/layout.svelte"
<script lang="ts">
  import type { Snippet } from "svelte";
  let { children }: { children?: Snippet } = $props();
</script>

<html>
  <body>
    <header>My app</header>
    <main>{@render children?.()}</main>
  </body>
</html>
```

## Islands

In server mode, a Svelte component imported into a `.nexy` file is an island.

### Importing
Import components in the frontmatter of the `.nexy` file:

```nexy filename="src/routes/index.md"
---
from "@/components/Counter.svelte" import Counter
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
Use the `useAction` hook to manage the state of an action call. In Svelte, this returns a store (read with `$`).

```svelte
<script lang="ts">
  import { useAction } from "@nexy/client";
  import { add_todo } from "@nexy/actions";

  let title = $state("");
  const save = useAction(add_todo, { onSuccess: () => (title = "") });
</script>

<form onsubmit={(e) => { e.preventDefault(); save.run({ title }); }}>
  <input bind:value={title} />
  <button disabled={$save.pending}>Add</button>
</form>
```

### Navigation
Use the `Link` component for client-side transitions:

```svelte
<script lang="ts">
  import Link from "@nexy/Link.svelte";
</script>

<Link href="/about" activeClass="active">About</Link>
```

For programmatic navigation, use the `router` object from `@nexy/client`:

```ts
import { router } from "@nexy/client";

router.push("/dashboard");
```

### URL Access
All location data is provided as stores:
- `$pathname`: current path
- `$params`: dynamic segments
- `$searchParams`: query string
- `$location`: full location object
