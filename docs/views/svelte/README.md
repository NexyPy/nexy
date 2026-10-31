# Svelte

Nexy renders Svelte 5 components on the server, then Svelte takes them over in the browser. A
project uses Svelte in one of two ways:

| Mode | `nexyconfig.py` | Pages are | Svelte is |
|---|---|---|---|
| Server (default) | `useCSR = False` | `.nexy` files | [islands](islands.md) inside those pages |
| Client | `useCSR = True` | `.svelte` files | the whole page, with [layouts](layouts.md) and a client router |

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

## In this section

- [Pages](pages.md): a `.svelte` route, its params, server rendering
- [Layouts](layouts.md): the root `layout.svelte` that owns `<html>`, nested layouts
- [Islands](islands.md): a Svelte component inside a `.nexy` page
- [Actions and navigation](actions-and-navigation.md): call Python, link pages, read the URL

## Next steps

- [Views](../README.md): compare formats
- [Frontend](../../guides/frontend.md): Vite and the client build
