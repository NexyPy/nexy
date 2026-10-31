# Vue pages

In client mode a page is a `.vue` file under `src/routes/`. Nexy renders it on the server for the
first response, Vue takes it over in the browser, and the client router swaps pages from there.

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useFF = vue()
    useCSR = True
```

## A page

```vue filename="src/routes/index.vue"
<script setup lang="ts">
import Counter from "@/components/Counter.vue";
</script>

<template>
  <h1>Hello</h1>
  <Counter />
</template>
```

```vue filename="src/components/Counter.vue"
<script setup lang="ts">
import { ref } from "vue";

const count = ref(0);
</script>

<template>
  <button @click="count++">{{ count }}</button>
</template>
```

The file path is the URL, as for every route:

| File | URL |
|---|---|
| `src/routes/index.vue` | `/` |
| `src/routes/about.vue` | `/about` |
| `src/routes/blog/[slug].vue` | `/blog/{slug}` |
| `src/routes/docs/[...path].vue` | `/docs/{path:path}` |
| `src/routes/(app)/settings.vue` | `/settings` |

The page is the default export of the file, the component `<script setup>` defines.

## Dynamic segments

The segments of the URL reach the page as props. Declare them, or Vue copies them onto the root
element as HTML attributes:

```vue filename="src/routes/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

`useParams()` from `@nexy/client` reads the same values, as a computed ref, in any component below
the page. A catch-all gives one string with the slashes: `/docs/a/b` gives `path == "a/b"`.

## Data

A client page has no Python frontmatter. Its data comes from Python in one of two ways:

- an [action](../../guides/actions.md): a typed function you call with `useAction`, see
  [Actions and navigation](actions-and-navigation.md);
- an API handler next to the pages, `src/routes/api/posts.py`, that you `fetch`.

## How the page is rendered

| Moment | What happens |
|---|---|
| `nx dev` | Vite renders the layouts and the page in Node for each request. |
| `nx build` | Every static page is rendered once to HTML. A dynamic page is built without its page content, filled in the browser. |
| `nx start` | Python serves the pre-rendered HTML. No Node process runs. |
| Browser | Vue builds the body and swaps it in for the one the server sent; `<html>` and `<head>` stay. |
| A click on a link | The client router imports the next page and renders it; the layouts stay mounted. |

Vue does not hydrate the server body in client mode: it renders its own and replaces it, so the
first paint is the server's HTML and the page becomes interactive once Vue has built it.

## Rules

- `.md` and `.mdx` files stay routes in client mode: Nexy renders them inside your layouts.
- A `.py` file under `src/routes/` is an API handler, not a page. Do not give it the same URL as a
  page.
- Code that reads `window` or `document` belongs in `onMounted`: the first render runs in Node.

## Next steps

- [Layouts](layouts.md): the document and the nested layouts
- [Actions and navigation](actions-and-navigation.md): links, hooks, actions
- [Dynamic routes](../../routing/fbr/pages/dynamic-routes.md): segments, catch-alls, groups
- [CSR](../../rendering/csr.md): client-side rendering
