# Vue

Vue 3 single-file-component routes: server-rendered first, then hydrated by Vite in the browser.

## Enable Vue

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useAliases = {"@": "src"}
```

- Extension: `.vue`
- Runtime: Vue 3.5
- Build: `@vitejs/plugin-vue`

## Create a route

```vue filename="src/routes/index.vue"
<script setup lang="ts">
import Counter from "@/components/Counter.vue";
</script>

<template>
  <main>
    <h1>Hello</h1>
    <Counter />
  </main>
</template>
```

Single-file component with `<script setup>`. Nexy renders it on the server and mounts it in the
browser.

> **Good to know**: a `.nexy` template that contains `{{` in JavaScript must wrap it in
> `{% raw %}...{% endraw %}`.

## Rendering

Server rendering is on by default. Set `useCSR = True` for
[client-side rendering](../routing/fbr/csr.md).

## Next steps

- [Views](README.md): compare formats
- [Frontend](../frontend.md): Vite and the client build
- [.nexy files](nexyfile.md): mixing server logic and Vue islands
