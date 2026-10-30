# Vue layouts

A `layout.vue` wraps every page below it, in client mode (`useCSR = True`). The root `layout.vue` defines the whole
document; a `layout.vue` in a subdirectory wraps the pages below it, renders them in its default slot
and keeps its state while the user navigates.

## Root layout

```vue filename="src/routes/layout.vue"
<script setup lang="ts">
// The layout declares no props, so the route params are not copied onto <html> as attributes.
defineOptions({ inheritAttrs: false });

// Set through v-html: Vue escapes the text of a <script> element, which would break `&&`.
const themeScript = `
  document.documentElement.classList.toggle(
    "dark",
    localStorage.getItem("nexy-theme") === "dark" ||
      (!("nexy-theme" in localStorage) && window.matchMedia("(prefers-color-scheme: dark)").matches),
  );
`;
</script>

<template>
  <html lang="en" class="dark">
    <head>
      <meta charset="UTF-8" />
      <title>My app</title>
      <script v-html="themeScript"></script>
    </head>
    <body>
      <header>My app</header>
      <main><slot /></main>
    </body>
  </html>
</template>
```

`nx new` with Vue and `useCSR = True` creates this file. `<!DOCTYPE html>` is added for you.

## Nested layouts

```vue filename="src/routes/dashboard/layout.vue"
<template>
  <section>
    <aside>Sidebar</aside>
    <slot />
  </section>
</template>
```

`dashboard/index.vue` renders as `root layout > dashboard layout > page`. Each layout also receives
the route's props as attributes.

## How the document is produced

| Moment | What happens |
|---|---|
| `nx dev` | each request asks the Vite dev server to render the layouts and the page in Node. |
| `nx build` | every static route is rendered to a complete document; a dynamic route is rendered without its page. |
| `nx start` | Python serves the pre-rendered file and adds the client assets. No Node process runs. |
| Browser | Vue builds the body and swaps it in; `<html>` and `<head>` stay as sent. See [how the browser takes over](../../routing/fbr/layouts/README.md#how-the-browser-takes-over-the-document). |

For the browser, Nexy removes `<html>`, `<head>` and `<body>` from the root layout before Vue compiles
it: Vue cannot create those elements there, and the server already sent them.

## Navigation

A click on a `Link` updates the page and leaves the layouts mounted. The layouts that differ between
two pages are rebuilt.

## Rules

- Only the **root** layout writes `<html>`, `<head>` and `<body>`. A `.tsx` page is not wrapped by it, and a project has one
  frontend framework ([modes](../../routing/fbr/modes.md)).
- It cannot coexist with `layout.nexy`.
- Pages under a layout are mounted in the browser: they have no server-rendered snapshot.

## Next steps

- [Islands](islands.md): Vue inside a server-mode page, with `layout.nexy`
- [Actions and navigation](actions-and-navigation.md): the `Link` that keeps layouts mounted
- [Layouts](../../routing/fbr/layouts/README.md): how Nexy resolves a chain of layouts
