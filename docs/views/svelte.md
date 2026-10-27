# Svelte

Svelte 5 single-file-component routes: server-rendered first, then hydrated by Vite in the browser.

## Enable Svelte

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useAliases = {"@": "src"}
```

- Extension: `.svelte`
- Runtime: Svelte 5
- Build: `@sveltejs/vite-plugin-svelte`

## Create a route

```svelte filename="src/routes/index.svelte"
<script lang="ts">
  import Counter from "@/components/Counter.svelte";
</script>

<main>
  <h1>Hello</h1>
  <Counter />
</main>
```

Single-file component. Nexy renders it on the server and mounts it in the browser.

> **Good to know**: a `.nexy` template that contains `{{` in JavaScript must wrap it in
> `{% raw %}...{% endraw %}`.

## Rendering

Server rendering is on by default. Set `useCSR = True` for
[client-side rendering](../rendering/csr.md).

## Layouts

In client mode the root `layout.svelte` owns the HTML document and every `layout.svelte` renders its
page with `{@render children?.()}`. See [layout.svelte](../routing/fbr/layouts/layout.svelte.md).

## Next steps

- [Views](README.md): compare formats
- [Frontend](../guides/frontend.md): Vite and the client build
- [.nexy files](nexyfile.md): mixing server logic and Svelte islands
