# Do SvelteKit ao Nexy

No Nexy, um projeto SvelteKit mantém suas Svelte páginas e layouts como arquivos `.svelte` simples, enquanto `+server.ts`, `+page.server.ts` carregam, ações de formulário e ganchos se movem para Python arquivos próximos a eles.

Cada seção abaixo mostra um hábito do SvelteKit e a mesma coisa no Nexy.

## Escolha o modo primeiro

| Seu aplicativo SvelteKit é | Modo Nexy | As páginas são |
|---|---|---|
| um aplicativo com navegação do cliente | modo cliente, `useCSR = True` | `.svelte` arquivos em `src/routes/` |
| principalmente conteúdo, algumas partes interativas | modo de servidor, o padrão | `.nexy` páginas com Svelte ilhas |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useCSR = True
    useAliases = {"@": "src"}
```

As seções abaixo usam o modo cliente, a menos que seja indicado o contrário.

## `+page.svelte`

```svelte filename="src/routes/about/+page.svelte"
<h1>About</h1>
```

Uma página é o próprio arquivo, nomeado de acordo com sua URL:

```svelte filename="src/rotas/about.svelte"
<h1>About</h1>
```

`src/routes/+page.svelte` é `src/routes/index.svelte`.

## Rotas dinâmicas e `params`

```svelte filename="src/routes/blog/[slug]/+page.svelte"
<script lang="ts">
  import { page } from "$app/state";
</script>

<h1>{page.params.slug}</h1>
```

Os segmentos chegam à página como adereços:

```svelte filename="src/routes/blog/[slug].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

Em qualquer outro componente, o armazenamento `params` de `@nexy/client` os contém: `$params.slug`. As pastas `[...rest]` e `(group)` funcionam como no SvelteKit.

## `+layout.svelte`

```svelte filename="src/rotas/+layout.svelte"
<script lang="ts">
  let { children } = $props();
</script>

<header>My app</header>
<main>{@render children()}</main>
```

Não há `app.html`: a raiz `layout.svelte` possui o documento.

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

A mesma exportação `GET`, em Python:

```python filename="src/rotas/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

```python filename="src/routes/api/items/index.py"
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

```python filename="src/rotas/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `load` em `+page.server.ts`

```ts filename="src/rotas/usuários/+page.server.ts"
export async function load() {
  return { users: await db.user.findMany() };
}
```

```svelte filename="src/routes/users/+page.svelte"
<script lang="ts">
  let { data } = $props();
</script>

<ul>
  {#each data.users as user (user.id)}
    <li>{user.name}</li>
  {/each}
</ul>
```

No modo cliente, a página solicita seus dados a um manipulador:

```python filename="src/routes/api/users.py"
async def GET():
    return [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
```

```svelte filename="src/routes/users.svelte"
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

No modo servidor, o frontmatter de uma página `.nexy` é a função `load`, e ela é executada enquanto o servidor renderiza:

```nexy filename="src/rotas/pessoas.nexy"
---
users = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Ações de formulário e `use:enhance`

```ts filename="src/routes/todos/+page.server.ts"
export const actions = {
  default: async ({ request }) => {
    const data = await request.formData();
    await db.todo.create({ title: data.get("title") });
  },
};
```

```svelte filename="src/routes/todos/+page.svelte"
<script lang="ts">
  import { enhance } from "$app/forms";
</script>

<form method="POST" use:enhance>
  <input name="title" />
  <button>Add</button>
</form>
```

Uma ação é uma função Python com um cliente gerado e digitado:

```python filename="src/actions/todos.py"
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

`revalidate("/todos")` faz o papel de `invalidateAll()`: a página se busca novamente.

## `goto`, links e `$app/state`

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

```ts filename="src/hooks.server.ts"
export async function handle({ event, resolve }) {
  if (event.url.pathname.startsWith("/dashboard") && !event.cookies.get("session")) {
    return new Response(null, { status: 307, headers: { location: "/login" } });
  }
  const response = await resolve(event);
  response.headers.set("x-app", "demo");
  return response;
}
```

O teste do caminho é a pasta. Uma raiz `middleware.py` envolve tudo, uma `dashboard/middleware.py` apenas as rotas abaixo dela:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

```python filename="src/routes/dashboard/middleware.py"
from nexy.http import RedirectResponse, Request


async def middleware(request: Request, call_next):
    if "session" not in request.cookies:
        return RedirectResponse("/login", status_code=307)
    return await call_next(request)
```

```python filename="src/routes/dashboard/stats.py"
async def GET():
    return {"visits": 12}
```

## `prerender` e `entries`

```ts filename="src/routes/blog/[slug]/+page.ts"
export const prerender = true;

export function entries() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

Exporte `getStaticParams` da página para um documento pré-renderizado por valor:

```svelte filename="src/routes/posts/[slug].svelte"
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

No modo servidor, `revalidate = 60` no frontmatter de uma página `.nexy` armazena em cache por URL:

```nexy filename="src/routes/news.nexy"
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

No modo cliente, escreva as tags na raiz `layout.svelte`. No modo servidor, uma página `.nexy` os define, e seu layout os grava com `{{ useMetadata().html() }}`:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## Svelte componentes em páginas do servidor

```svelte filename="src/components/Counter.svelte"
<script lang="ts">
  let { start = 0 }: { start?: number } = $props();
  let count = $state(start);
</script>

<button onclick={() => count++}>{count}</button>
```

No modo servidor, o componente é uma ilha de uma página `.nexy`:

```nexy filename="src/rotas/home.nexy"
---
from "@/components/Counter.svelte" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

## `+error.svelte`

`src/routes/notfound.svelte` responde URLs desconhecidos no modo cliente, `notfound.nexy` no modo servidor e os clientes API obtêm `{"detail": ...}`.

## `$env/static/private`

```ts filename="src/lib/server/db.ts"
import { DATABASE_URL } from "$env/static/private";
```

```python filename="src/settings.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## Correndo

| Kit Svelte | Nexy |
|---|---|
| `npx sv create` | `nx new`, modelo `web-fbr-svelte` |
| `vite dev` | `nx dev` |
| `vite build` com um adaptador, então `node build` | `nx build`, então `nx start` |
| `static/` | `public/`, servido em `/` |
| `src/lib/` e `$lib` | `src/components/` e `@` |

## Próximas etapas

- [Modo servidor e modo cliente](../routing/fbr/modes.md)
- [Svelte em Nexy](../views/svelte/differences.md)
- [Ações](../guides/actions.md)
- [De Nuxt a Nexy](nuxt.md)
