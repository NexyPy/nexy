---
name: nexy-vue
description: Writing Vue 3.5 single-file components, routes and layouts in a Nexy project in idiomatic Vue - script setup, ref, computed, composables, never hand-written DOM scripts. Load it for any .vue file when useFF = vue().
---

# Vue in Nexy

## Idiomatic Vue only

Use `<script setup lang="ts">` and the Composition API.

- State: `ref` and `reactive`. Derived values: `computed`. Side effects: `watch`, `watchEffect`,
  `onMounted`, `onUnmounted`.
- Shared logic goes in composables (`useTheme`, `useCopy`) in `src/composables/`.
- Props with `defineProps<{ ... }>()`, events with `defineEmits`, two-way binding with
  `defineModel`.
- Template directives (`v-if`, `v-for` with `:key`, `v-model`, `@click`), not DOM calls. No
  `document.querySelector`, no document-level listeners, no `innerHTML`; use `v-html` only for
  trusted content and a template `ref` when the DOM is truly needed.

The one allowed script is a short one in the layout head that sets the saved theme class on
`<html>` before the first paint. Written with `v-html` in `<head>`.

```vue
<script setup lang="ts">
import { ref } from "vue";

const count = ref(0);
</script>

<template>
  <button type="button" @click="count++">Clicked {{ count }} times</button>
</template>
```

## Files

- `src/routes/*.vue`: pages. `src/components/*.vue`: components, never inside `src/routes/`.
- `src/routes/layout.vue`: the root one owns the document; every layout renders its page in the
  default `<slot />`.

## Rules

- One component per file, `PascalCase` file or tag names consistently with the project.
- Buttons are `<button type="button">`; navigation is a link. Labels on every field.
- Import with `@/`. Server calls: `useAction` from `@nexy/client` returns refs (`pending`, `data`,
  `error`).
- Icons are SVG components. No emoji.
- Inside a `.nexy` template, wrap Vue's `{{ }}` in `{% raw %}...{% endraw %}`.

Run `nexy-ux-audit` before building a view, follow
`nexy-styling`, and test first (`nexy-testing`).
