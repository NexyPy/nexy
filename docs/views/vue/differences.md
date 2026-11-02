# Vue

Nexy renders Vue 3 single-file components on the server, then Vue takes them over in the browser.
Pages, layouts, islands and actions are the same in every framework: this page covers setup, then the
parts that differ from the [shared contracts](../frontend/pages.md).

| Mode | `nexyconfig.py` | Pages are | Vue is |
|---|---|---|---|
| Server (default) | `useCSR = False` | `.nexy` files | [islands](../../rendering/islands.md) inside those pages |
| Client | `useCSR = True` | `.vue` files | the whole page, with [layouts](../frontend/layouts.md) and a client router |

## Start a project

```bash
nx new my-app --template web-fbr-vue
```

The template is a server-mode project with Vue islands. Run `nx new my-app` without a template to
answer the prompts instead: the router, the project type, whether to use client-side routing, then
the framework.

## Enable Vue in an existing project

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), vue()],
  customLogger: nexy.log(),
});
```

`nx new` writes this file; Nexy writes `__nexy__/vite.ts` itself, so do not edit it.

| Package | Version `nx new` writes |
|---|---|
| `vue` | `^3.5.33` |
| `@vitejs/plugin-vue` | `^6.0.0` |

## Rules

- **One framework per project.** `useFF` takes exactly one framework; `useFF = [vue(), react()]` stops
  the server at startup.
- **One component per file.** A `.vue` file exports its component as default; the name you import it
  under is only the tag you write.
- **Components live outside `src/routes/`**, usually in `src/components/`, so they are not pages.
- **A server-mode project has no `.vue` page**, and a client-mode project has no `.nexy` page: Nexy
  refuses to start and names the file. See [modes](../../routing/fbr/modes.md).

## Pages

In client mode (`useCSR = True`), a page is a `.vue` file.

### Page component

The page is the component defined by the `<script setup>` block.

```vue filename="src/routes/index.vue"
<template>
  <h1>Hello</h1>
</template>
```

### Dynamic segments

URL parameters reach the page as props. You can declare them using `defineProps`:

```vue filename="src/routes/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

Alternatively, use the `useParams` hook from `@nexy/client` in any component.

## Layouts

### Implementation

The root layout defines the document shell. Nested layouts wrap the content in their default slot.

```vue filename="src/routes/layout.vue"
<template>
  <html>
    <body>
      <header>My app</header>
      <main><slot /></main>
    </body>
  </html>
</template>
```

## Islands

In server mode, a Vue component imported into a `.nexy` file is an island.

### Importing

Import components in the frontmatter of the `.nexy` file:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.vue" import Counter
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

Use the `useAction` hook to manage the state of an action call. In Vue, the returned state
(`pending`, `data`, `error`) are computed refs.

```vue
<script setup lang="ts">
import { ref } from "vue";
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const title = ref("");
const { run, pending, error, data } = useAction(add_todo, {
  onSuccess: () => (title.value = ""),
});
</script>

<template>
  <form @submit.prevent="run({ title })">
    <input v-model="title" />
    <button :disabled="pending">Add</button>
  </form>
</template>
```

### Navigation

Use the `Link` component for client-side transitions:

```vue
<template>
  <Link href="/about" active-class="active">About</Link>
</template>
```

For programmatic navigation, use the `useRouter` hook:

```ts
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### URL access

All location hooks return computed refs:

- `usePathname()`: current path
- `useParams()`: dynamic segments
- `useSearchParams()`: query string
- `useLocation()`: full location object

## Next steps

- [Views](../README.md): compare the formats a page can use
- [Frontend](../../guides/frontend.md): Vite and the client build
