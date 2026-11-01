# Svelte

Nexy renders Svelte 5 components on the server, then Svelte takes them over in the browser. Pages,
layouts, islands and actions are the same in every framework: this page covers setup, then the parts
that differ from the [shared contracts](../frontend/pages.md).

| Mode | `nexyconfig.py` | Pages are | Svelte is |
|---|---|---|---|
| Server (default) | `useCSR = False` | `.nexy` files | [islands](../frontend/islands.md) inside those pages |
| Client | `useCSR = True` | `.svelte` files | the whole page, with [layouts](../frontend/layouts.md) and a client router |

## Start a project

```bash
nx new my-app --template web-fbr-svelte
```

The template is a server-mode project with Svelte islands. Run `nx new my-app` without a template to
answer the prompts instead: the router, the project type, whether to use client-side routing, then
the framework.

## Enable Svelte in an existing project

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), svelte()],
  customLogger: nexy.log(),
});
```

`nx new` writes this file; Nexy writes `__nexy__/vite.ts` itself, so do not edit it.

| Package | Version `nx new` writes |
|---|---|
| `svelte` | `^5.20.2` |
| `@sveltejs/vite-plugin-svelte` | `^5.0.0` |

## Rules

- **Svelte 5.** Components use runes: `$props()`, `$state()`, and snippets for children.
- **One framework per project.** `useFF` takes exactly one framework; `useFF = [svelte(), vue()]`
  stops the server at startup.
- **One component per file.** The name you import a `.svelte` file under is only the tag you write.
- **Components live outside `src/routes/`**, usually in `src/components/`, so they are not pages.
- **A server-mode project has no `.svelte` page**, and a client-mode project has no `.nexy` page: Nexy
  refuses to start and names the file. See [modes](../../routing/fbr/modes.md).

## Pages

In client mode (`useCSR = True`), a page is a `.svelte` file.

### Page component

The page is the component defined by the script block of the `.svelte` file.

```svelte filename="src/routes/index.svelte"
<script lang="ts">
</script>

<h1>Hello</h1>
```

### Dynamic segments

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

The root layout defines the document shell. Nested layouts wrap the content using the `children`
snippet.

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

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.svelte" import Counter
---
<Counter start=3 />
```

### Hydration directives

Use the `directive` prop to control when the island hydrates:

- `client:load` (default): immediately
- `client:idle`: when the browser is idle
- `client:visible`: when it scrolls into view
- `client:media`: when the media query matches

## Actions and navigation

### Calling actions

Use the `useAction` hook to manage the state of an action call. In Svelte, this returns a store (read
with `$`).

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

### URL access

All location data is provided as stores:

- `$pathname`: current path
- `$params`: dynamic segments
- `$searchParams`: query string
- `$location`: full location object

## Next steps

- [Views](../README.md): compare the formats a page can use
- [Frontend](../../guides/frontend.md): Vite and the client build
