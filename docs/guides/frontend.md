# Frontend

Nexy does not ship its own component system for the client. It builds on Vite: React, Vue, Svelte,
Solid and Preact are all supported, and vanilla pages work with no client framework at all.

## Enable a framework

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()   # vue(), svelte(), solid(), preact()
```

`useVite` defaults to `True`; keep it on when a framework is configured.

## Route files

| Extension | Rendered |
|---|---|
| `.nexy`, `.md` | by Nexy at request time |
| `.mdx`, `.tsx`, `.jsx`, `.vue`, `.svelte` | by the client framework; pre-rendered to HTML at build time, then taken over by the client bundle |

A framework route is a normal page, not a client-only island: the HTML exists before the bundle runs,
so the first paint does not wait for JavaScript.

Per-framework setup: [React](../views/react.md), [Vue](../views/vue.md), [Svelte](../views/svelte.md),
[Solid](../views/solid.md), [Preact](../views/preact.md).

## Development

`nx dev` starts one server on one port:

1. the app recompiles the routes you change, server and client;
2. Vite runs on an internal port and serves framework modules;
3. Nexy proxies Vite's endpoints through its own origin.

The browser only ever talks to port `3000`. There is no second URL to open and no CORS to configure.

## Build

`nx build` produces:

- pre-rendered HTML for framework routes;
- the client bundle, with assets under `__nexy__/client/`;
- the compiled Python routes.

Vite handles the client bundle; SSR HTML is produced per file by esbuild.

> [!NOTE]
> a route whose server render fails is reported as a client-only route instead of
> failing the whole build.

## Styling

`nexy new` asks for a style mode and sets it up for the client framework you pick: Tailwind,
UnoCSS or plain CSS. The design tokens (colours, fonts, the dark theme) are CSS variables in
`src/globale.css`, the file the scaffold creates.

| Mode | The starter pages are written with |
|---|---|
| Tailwind, UnoCSS | utility classes in the markup, with the tokens mapped to class names |
| Plain CSS | semantic class names and the CSS in `src/globale.css` |

Follow the mode of your project when you add a page: utility classes in a utility project, CSS in a
plain-CSS one. Keep component CSS that utilities cannot express in the component's `<style>` block.
In a server project (`.nexy` pages) UnoCSS reads the `.nexy` files for classes; Tailwind finds them
on its own.

## Fonts, images, scripts

Put static files in `public/` - they are served from `/` in both development and production.

## Next steps

- [Views](../views/README.md): choose a page format
- [Config](../reference/config.md): `useFF`, `useVite`, aliases
- [Deploy](../deployment/README.md): what the build produces
