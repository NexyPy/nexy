# Dari SvelteKit hingga Nexy

Di Nexy, proyek SvelteKit mempertahankan halaman Svelte dan tata letaknya sebagai file `.svelte` biasa, sementara `+server.ts`, `+page.server.ts` memuat, tindakan formulir, dan kait dipindahkan ke file Python di sebelahnya.

Setiap bagian di bawah ini menunjukkan kebiasaan SvelteKit, lalu hal yang sama di Nexy.

## Pilih modenya terlebih dahulu

| Aplikasi SvelteKit Anda adalah | Modus Nexy | Halaman adalah |
|---|---|---|
| sebuah aplikasi dengan navigasi klien | mode klien, `useCSR = True` | `.svelte` file di bawah `src/routes/` |
| sebagian besar konten, beberapa bagian interaktif | mode server, default | `.nexy` halaman dengan Svelte pulau |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useCSR = True
    useAliases = {"@": "src"}
```

Bagian di bawah ini menggunakan mode klien kecuali dinyatakan lain.

## `+page.svelte`

```svelte filename="src/routes/about/+page.svelte"
<h1>About</h1>
```

Halaman adalah file itu sendiri, dinamai berdasarkan URL-nya:

```svelte filename="src/routes/about.svelte"
<h1>About</h1>
```

`src/routes/+page.svelte` adalah `src/routes/index.svelte`.

## Rute dinamis dan `params`

```svelte filename="src/routes/blog/[siput]/+halaman.svelte"
<script lang="ts">
  import { page } from "$app/state";
</script>

<h1>{page.params.slug}</h1>
```

Segmen mencapai halaman sebagai alat peraga:

```svelte filename="src/rute/blog/[siput].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

Di komponen lainnya, penyimpanan `params` dari `@nexy/client` menampungnya: `$params.slug`. Folder `[...rest]` dan `(group)` berfungsi seperti di SvelteKit.

## `+layout.svelte`

```svelte filename="src/routes/+layout.svelte"
<script lang="ts">
  let { children } = $props();
</script>

<header>My app</header>
<main>{@render children()}</main>
```

Tidak ada `app.html`: root `layout.svelte` memiliki dokumen tersebut.

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

Ekspor `GET` yang sama, di Python:

```python filename="src/routes/api/item/[id].py"
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

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `load` di `+page.server.ts`

```ts filename="src/routes/users/+page.server.ts"
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

Dalam mode klien, halaman meminta datanya kepada pengendali:

```python filename="src/routes/api/users.py"
async def GET():
    return [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
```

```svelte filename="src/routes/pengguna.svelte"
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

Dalam mode server, materi depan halaman `.nexy` adalah fungsi `load`, dan dijalankan saat server merender:

```nexy filename="src/rute/orang.nexy"
---
users = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Bentuk tindakan dan `use:enhance`

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

Suatu tindakan adalah fungsi Python dengan klien yang dihasilkan dan diketik:

```python filename="src/aksi/todos.py"
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

`revalidate("/todos")` memainkan peran `invalidateAll()`: halaman diambil kembali.

## `goto`, tautan dan `$app/state`

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

Tes jalurnya adalah foldernya. Root `middleware.py` membungkus semuanya, `dashboard/middleware.py` hanya rute di bawahnya:

```python filename="src/rute/middleware.py"
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

```python filename="src/route/dashboard/stats.py"
async def GET():
    return {"visits": 12}
```

## `prerender` dan `entries`

```ts filename="src/rute/blog/[siput]/+halaman.ts"
export const prerender = true;

export function entries() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

Ekspor `getStaticParams` dari halaman untuk satu dokumen pra-render per nilai:

```svelte filename="src/routes/posts/[siput].svelte"
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

Dalam mode server, `revalidate = 60` di bagian depan halaman `.nexy` menyimpannya dalam cache per URL:

```nexy filename="src/rute/berita.nexy"
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

Dalam mode klien, tulis tag di root `layout.svelte`. Dalam mode server, halaman `.nexy` mengaturnya, dan tata letaknya menuliskannya dengan `{{ useMetadata().html() }}`:

```nexy filename="src/rute/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## Svelte komponen di halaman server

```svelte filename="src/components/Counter.svelte"
<script lang="ts">
  let { start = 0 }: { start?: number } = $props();
  let count = $state(start);
</script>

<button onclick={() => count++}>{count}</button>
```

Dalam mode server, komponennya adalah pulau halaman `.nexy`:

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.svelte" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

## `+error.svelte`

`src/routes/notfound.svelte` menjawab URL yang tidak diketahui dalam mode klien, `notfound.nexy` dalam mode server, dan klien API mendapatkan `{"detail": ...}`.

## `$env/static/private`

```ts filename="src/lib/server/db.ts"
import { DATABASE_URL } from "$env/static/private";
```

```python filename="src/pengaturan.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## Berlari

| SvelteKit | Nexy |
|---|---|
| `npx sv create` | `nx new`, templat `web-fbr-svelte` |
| `vite dev` | `nx dev` |
| `vite build` dengan adaptor, lalu `node build` | `nx build`, lalu `nx start` |
| `static/` | `public/`, bertugas di `/` |
| `src/lib/` dan `$lib` | `src/components/` dan `@` |

## Langkah selanjutnya

- [Mode server dan mode klien](../routing/fbr/modes.md)
- [Svelte di Nexy](../views/svelte/differences.md)
- [Tindakan](../guides/actions.md)
- [Dari Nuxt ke Nexy](nuxt.md)
