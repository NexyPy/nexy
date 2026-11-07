# SvelteKit سے Nexy تک

Nexy میں ایک SvelteKit پروجیکٹ اپنے Svelte صفحات اور ترتیب کو سادہ `.svelte` فائلوں کے طور پر رکھتا ہے، جبکہ `+server.ts`، `+page.server.ts` لوڈ، فارم ایکشنز اور ہکس ان کے ساتھ Python فائلوں میں منتقل ہوتے ہیں۔

ذیل میں ہر سیکشن SvelteKit کی عادت دکھاتا ہے، پھر Nexy میں وہی چیز۔

## پہلے موڈ کا انتخاب کریں۔

| آپ کی SvelteKit ایپ ہے۔ | نیکسی موڈ | صفحات ہیں۔ |
|---|---|---|
| کلائنٹ نیویگیشن کے ساتھ ایک ایپ | کلائنٹ موڈ، `useCSR = True` | `.svelte` فائلیں `src/routes/` کے تحت |
| زیادہ تر مواد، چند انٹرایکٹو حصے | سرور موڈ، ڈیفالٹ | `.nexy` صفحات Svelte جزائر کے ساتھ |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useCSR = True
    useAliases = {"@": "src"}
```

ذیل کے حصے کلائنٹ موڈ کا استعمال کرتے ہیں جب تک کہ وہ دوسری صورت میں نہ کہیں۔

## `+page.svelte`

```svelte filename="src/routes/about/+page.svelte"
<h1>About</h1>
```

ایک صفحہ خود فائل ہے، جس کا نام اس کے URL کے نام پر رکھا گیا ہے:

```svelte filename="src/routes/about.svelte"
<h1>About</h1>
```

`src/routes/+page.svelte` ہے `src/routes/index.svelte`۔

## متحرک راستے اور `params`

```svelte filename="src/routes/blog/[slug]/+page.svelte"
<script lang="ts">
  import { page } from "$app/state";
</script>

<h1>{page.params.slug}</h1>
```

طبقات صفحہ پر بطور پروپس پہنچتے ہیں:

```svelte filename="src/routes/blog/[slug].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

کسی دوسرے جزو میں، `params` کا ذخیرہ `@nexy/client` انہیں رکھتا ہے: `$params.slug`۔ `[...rest]` اور `(group)` فولڈرز SvelteKit کی طرح کام کرتے ہیں۔

## `+layout.svelte`

```svelte filename="src/routes/+layout.svelte"
<script lang="ts">
  let { children } = $props();
</script>

<header>My app</header>
<main>{@render children()}</main>
```

کوئی `app.html` نہیں ہے: جڑ `layout.svelte` دستاویز کا مالک ہے۔

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

وہی `GET` برآمد، Python میں:

```python filename="src/routes/api/items/[id].py"
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

## `load` `+page.server.ts` میں

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

کلائنٹ موڈ میں صفحہ اپنے ڈیٹا کے لیے ایک ہینڈلر سے پوچھتا ہے:

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

سرور موڈ میں `.nexy` صفحہ کا فرنٹ میٹر `load` فنکشن ہوتا ہے، اور یہ اس وقت چلتا ہے جب سرور پیش کرتا ہے:

```nexy filename="src/routes/people.nexy"
---
users = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## فارم کے اعمال اور `use:enhance`

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

ایک ایکشن ایک Python فنکشن ہے جس میں تیار کردہ، ٹائپ شدہ کلائنٹ ہے:

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

`revalidate("/todos")` `invalidateAll()` کا حصہ ادا کرتا ہے: صفحہ خود کو دوبارہ لاتا ہے۔

## `goto`، لنکس اور `$app/state`

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

پاتھ ٹیسٹ فولڈر ہے۔ ایک جڑ `middleware.py` ہر چیز کو سمیٹتی ہے، ایک `dashboard/middleware.py` صرف اس کے نیچے والے راستے:

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

## `prerender` اور `entries`

```ts filename="src/routes/blog/[slug]/+page.ts"
export const prerender = true;

export function entries() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

فی قیمت ایک پہلے سے پیش کردہ دستاویز کے لیے صفحہ سے `getStaticParams` برآمد کریں:

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

سرور موڈ میں، `revalidate = 60` صفحہ کے فرنٹ میٹر میں `.nexy` اس کی بجائے اسے فی یو آر ایل کیش کرتا ہے:

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

کلائنٹ موڈ میں، ٹیگز کو روٹ `layout.svelte` میں لکھیں۔ سرور موڈ میں ایک `.nexy` صفحہ انہیں سیٹ کرتا ہے، اور اس کی ترتیب انہیں `{{ useMetadata().html() }}` کے ساتھ لکھتی ہے:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## Svelte سرور کے صفحات میں اجزاء

```svelte filename="src/components/Counter.svelte"
<script lang="ts">
  let { start = 0 }: { start?: number } = $props();
  let count = $state(start);
</script>

<button onclick={() => count++}>{count}</button>
```

سرور موڈ میں جزو ایک `.nexy` صفحہ کا جزیرہ ہے:

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.svelte" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

## `+error.svelte`

`src/routes/notfound.svelte` کلائنٹ موڈ میں نامعلوم URLs کا جواب دیتا ہے، سرور موڈ میں `notfound.nexy`، اور API کلائنٹس کو `{"detail": ...}` ملتا ہے۔

## `$env/static/private`

```ts filename="src/lib/server/db.ts"
import { DATABASE_URL } from "$env/static/private";
```

```python filename="src/settings.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## چل رہا ہے۔

| SvelteKit | نیکسی |
|---|---|
| `npx sv create` | `nx new`، سانچہ `web-fbr-svelte` |
| `vite dev` | `nx dev` |
| `vite build` ایک اڈاپٹر کے ساتھ، پھر `node build` | `nx build`، پھر `nx start` |
| `static/` | `public/`، پر خدمت کی `/` |
| `src/lib/` اور `$lib` | `src/components/` اور `@` |

## اگلے اقدامات

- [سرور موڈ اور کلائنٹ موڈ](../routing/fbr/modes.md)
- [Svelte Nexy میں](../views/svelte/differences.md)
- [اعمال](../guides/actions.md)
- [Nuxt سے Nexy تک](nuxt.md)
