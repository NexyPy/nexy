# Vue Differences

This guide focuses on the specific implementation details for Vue. For universal concepts (how pages, layouts, and islands work), see the [Frontend Contracts](../frontend/pages.md).

## Pages

In client mode (`useCSR = True`), a page is a `.vue` file.

### Page Component
The page is the component defined by the `<script setup>` block.

```vue filename="src/routes/index.vue"
<template>
  <h1>Hello</h1>
</template>
```

### Dynamic Segments
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

### Hydration Directives
Use the `directive` prop to control when the island hydrates:
- `client:load` (default): immediately
- `client:idle`: when browser is idle
- `client:visible`: when it scrolls into view
- `client:media`: when media query matches

## Actions and Navigation

### Calling Actions
Use the `useAction` hook to manage the state of an action call. In Vue, the returned state (`pending`, `data`, `error`) are computed refs.

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

### URL Access
All location hooks return computed refs:
- `usePathname()`: current path
- `useParams()`: dynamic segments
- `useSearchParams()`: query string
- `useLocation()`: full location object
