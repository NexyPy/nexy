# De SvelteKit a Nexy

En Nexy, un proyecto SvelteKit mantiene sus Svelte páginas y diseños como archivos simples `.svelte`, mientras que `+server.ts`, `+page.server.ts` carga, forma acciones y enlaces se mueven a Python archivos junto a ellos.

Cada sección a continuación muestra un hábito de SvelteKit, luego lo mismo en Nexy.

## Elige el modo primero

| Tu aplicación SvelteKit es | Modo Nexy | Las páginas son |
|---|---|---|
| una aplicación con navegación del cliente | modo cliente, `useCSR = True` | `.svelte` archivos en `src/routes/` |
| principalmente contenido, algunas partes interactivas | modo servidor, el predeterminado | `.nexy` páginas con Svelte islas |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useCSR = True
    useAliases = {"@": "src"}
```

Las secciones siguientes utilizan el modo cliente a menos que indiquen lo contrario.

## `+page.svelte`

```svelte filename="src/rutas/acerca de/+página.svelte"
<h1>About</h1>
```

Una página es el archivo en sí, llamado así por su URL:

```svelte filename="src/rutas/about.svelte"
<h1>About</h1>
```

`src/routes/+page.svelte` es `src/routes/index.svelte`.

## Rutas dinámicas y `params`

```svelte filename="src/routes/blog/[slug]/+página.svelte"
<script lang="ts">
  import { page } from "$app/state";
</script>

<h1>{page.params.slug}</h1>
```

Los segmentos llegan a la página como accesorios:

```svelte filename="src/routes/blog/[slug].esbelto"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

En cualquier otro componente, el almacén `params` de `@nexy/client` los contiene: `$params.slug`. Las carpetas `[...rest]` y `(group)` funcionan como en SvelteKit.

## `+layout.svelte`

```svelte filename="src/rutas/+layout.svelte"
<script lang="ts">
  let { children } = $props();
</script>

<header>My app</header>
<main>{@render children()}</main>
```

No existe `app.html`: la raíz `layout.svelte` es propietaria del documento.

```svelte filename="src/routes/layout.svelte"
<script lang="ts">
  import type { Snippet } from "svelte";
  let { children }: { children?: Snippet } = $props();
</script>

<html>
  <body>
    <header>My app</header>
    <main>{@render children?.()}</main>
  </body>
</html>
```

## `+server.ts`

```ts filename="src/routes/api/items/[id]/+server.ts"
import { json } from "@sveltejs/kit";

export function GET({ params }) {
  return json({ id: Number(params.id) });
}
```

La misma exportación `GET`, en Python:

```python filename="src/rutas/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

```python filename="src/rutas/api/items/index.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## `error()`

```ts filename="src/routes/api/orders/[id]/+server.ts"
import { error, json } from "@sveltejs/kit";

export function GET({ params, url }) {
  if (Number(params.id) > 100) error(404, "No such order");
  return json({ id: Number(params.id), currency: url.searchParams.get("currency") ?? "EUR" });
}
```

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `load` en `+page.server.ts`

```ts filename="src/rutas/usuarios/+page.server.ts"
export async function load() {
  return { users: await db.user.findMany() };
}
```

```svelte filename="src/rutas/usuarios/+página.svelte"
<script lang="ts">
  let { data } = $props();
</script>

<ul>
  {#each data.users as user (user.id)}
    <li>{user.name}</li>
  {/each}
</ul>
```

En modo cliente, la página solicita sus datos a un controlador:

```python filename="src/rutas/api/usuarios.py"
async def GET():
    return [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
```

```svelte filename="src/rutas/usuarios.svelte"
<script lang="ts">
  let users = $state<{ id: number; name: string }[]>([]);

  $effect(() => {
    fetch("/api/users").then((response) => response.json()).then((list) => (users = list));
  });
</script>

<ul>
  {#each users as user (user.id)}
    <li>{user.name}</li>
  {/each}
</ul>
```

En modo servidor, el front-matter de una página `.nexy` es la función `load` y se ejecuta mientras el servidor procesa:

```nexy filename="src/rutas/personas.nexy"
---
users = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Acciones de formulario y `use:enhance`

```ts filename="src/rutas/todos/+page.server.ts"
export const actions = {
  default: async ({ request }) => {
    const data = await request.formData();
    await db.todo.create({ title: data.get("title") });
  },
};
```

```svelte filename="src/rutas/todos/+página.svelte"
<script lang="ts">
  import { enhance } from "$app/forms";
</script>

<form method="POST" use:enhance>
  <input name="title" />
  <button>Add</button>
</form>
```

Una acción es una función Python con un cliente generado y escrito:

```python filename="src/acciones/todos.py"
from pydantic import BaseModel

from nexy.decorators import Action, revalidate


class Todo(BaseModel):
    title: str
    done: bool = False


@Action
async def add_todo(title: str) -> Todo:
    revalidate("/todos")
    return Todo(title=title)
```

```svelte filename="src/routes/todos.svelte"
<script lang="ts">
  import { useAction } from "@nexy/client";
  import { add_todo } from "@nexy/actions";

  let title = $state("");
  const save = useAction(add_todo, { onSuccess: () => (title = "") });
</script>

<form onsubmit={(e) => { e.preventDefault(); save.run({ title }); }}>
  <input bind:value={title} />
  <button disabled={$save.pending}>Add</button>
</form>
```

`revalidate("/todos")` hace el papel de `invalidateAll()`: la página vuelve a buscarse a sí misma.

## `goto`, enlaces y `$app/state`

```svelte filename="src/lib/Nav.svelte"
<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/state";
</script>

<a href="/about">About</a>
<span>{page.url.pathname}</span>
<button onclick={() => goto("/dashboard")}>Dashboard</button>
```

```svelte filename="src/components/Nav.svelte"
<script lang="ts">
  import Link from "@nexy/Link.svelte";
  import { pathname, router } from "@nexy/client";
</script>

<Link href="/about" activeClass="active">About</Link>
<span>{$pathname}</span>
<button onclick={() => router.push("/dashboard")}>Dashboard</button>
```

## `hooks.server.ts`

```ts filename="src/hooks.servidor.ts"
export async function handle({ event, resolve }) {
  if (event.url.pathname.startsWith("/dashboard") && !event.cookies.get("session")) {
    return new Response(null, { status: 307, headers: { location: "/login" } });
  }
  const response = await resolve(event);
  response.headers.set("x-app", "demo");
  return response;
}
```

La ruta de prueba es la carpeta. Una raíz `middleware.py` envuelve todo, una `dashboard/middleware.py` solo las rutas debajo de ella:

```python filename="src/rutas/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

```python filename="src/rutas/dashboard/middleware.py"
from nexy.http import RedirectResponse, Request


async def middleware(request: Request, call_next):
    if "session" not in request.cookies:
        return RedirectResponse("/login", status_code=307)
    return await call_next(request)
```

```python filename="src/rutas/dashboard/stats.py"
async def GET():
    return {"visits": 12}
```

## `prerender` y `entries`

```ts filename="src/routes/blog/[slug]/+página.ts"
export const prerender = true;

export function entries() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

Exporte `getStaticParams` desde la página para un documento pre-renderizado por valor:

```svelte filename="src/routes/posts/[slug].esbelto"
<script lang="ts" module>
  export function getStaticParams() {
    return [{ slug: "hello" }, { slug: "world" }];
  }
</script>

<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

En modo servidor, `revalidate = 60` en la portada de una página `.nexy` la almacena en caché por URL:

```nexy filename="src/rutas/noticias.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## `<svelte:head>`

```svelte filename="src/routes/blog/+page.svelte"
<svelte:head>
  <title>Blog</title>
</svelte:head>
```

En modo cliente, escriba las etiquetas en la raíz `layout.svelte`. En modo servidor una página `.nexy` los establece, y su diseño los escribe con `{{ useMetadata().html() }}`:

```nexy filename="src/rutas/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## Svelte componentes en páginas del servidor

```svelte filename="src/components/Counter.svelte"
<script lang="ts">
  let { start = 0 }: { start?: number } = $props();
  let count = $state(start);
</script>

<button onclick={() => count++}>{count}</button>
```

En modo servidor, el componente es una isla de una página `.nexy`:

```nexy filename="src/rutas/home.nexy"
---
from "@/components/Counter.svelte" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

## `+error.svelte`

`src/routes/notfound.svelte` responde URL desconocidas en modo cliente, `notfound.nexy` en modo servidor y los clientes API obtienen `{"detail": ...}`.

## `$env/static/private`

```ts filename="src/lib/server/db.ts"
import { DATABASE_URL } from "$env/static/private";
```

```python filename="src/configuración.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## corriendo

| Kit esbelto | nexy |
|---|---|
| `npx sv create` | `nx new`, plantilla `web-fbr-svelte` |
| `vite dev` | `nx dev` |
| `vite build` con un adaptador, luego `node build` | `nx build`, luego `nx start` |
| `static/` | `public/`, servido en `/` |
| `src/lib/` y `$lib` | `src/components/` y `@` |

## Próximos pasos

- [Modo servidor y modo cliente](../routing/fbr/modes.md)
- [Svelte en Nexy](../views/svelte/differences.md)
- [Acciones](../guides/actions.md)
- [De Nuxt a Nexy](nuxt.md)
