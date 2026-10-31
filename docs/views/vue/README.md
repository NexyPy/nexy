# Vue

Nexy renders Vue 3 single-file components on the server, then Vue takes them over in the browser. A
project uses Vue in one of two ways:

| Mode | `nexyconfig.py` | Pages are | Vue is |
|---|---|---|---|
| Server (default) | `useCSR = False` | `.nexy` files | [islands](islands.md) inside those pages |
| Client | `useCSR = True` | `.vue` files | the whole page, with [layouts](layouts.md) and a client router |

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

## In this section

- [Pages](pages.md): a `.vue` route, its params, server rendering
- [Layouts](layouts.md): the root `layout.vue` that owns `<html>`, nested layouts
- [Islands](islands.md): a Vue component inside a `.nexy` page
- [Actions and navigation](actions-and-navigation.md): call Python, link pages, read the URL

## Next steps

- [Views](../README.md): compare formats
- [Frontend](../../guides/frontend.md): Vite and the client build
