# SvelteKit থেকে Nexy পর্যন্ত

Nexy-এ একটি SvelteKit প্রকল্প তার Svelte পৃষ্ঠা এবং বিন্যাসগুলিকে প্লেইন `.svelte` ফাইল হিসাবে রাখে, যখন `+server.ts`, `+page.server.ts` লোড হয়, ফর্ম অ্যাকশন এবং হুকগুলি তাদের পাশের Python ফাইলগুলিতে চলে যায়।

নীচের প্রতিটি বিভাগ একটি SvelteKit অভ্যাস দেখায়, তারপর Nexy তে একই জিনিস।

## প্রথমে মোডটি বেছে নিন

| আপনার SvelteKit অ্যাপটি | নেক্সি মোড | পৃষ্ঠাগুলি হল |
|---|---|---|
| ক্লায়েন্ট নেভিগেশন সহ একটি অ্যাপ | ক্লায়েন্ট মোড, `useCSR = True` | `.svelte` ফাইল `src/routes/` এর অধীনে |
| বেশিরভাগ বিষয়বস্তু, কয়েকটি ইন্টারেক্টিভ অংশ | সার্ভার মোড, ডিফল্ট | `.nexy` Svelte দ্বীপ সহ পৃষ্ঠা |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useCSR = True
    useAliases = {"@": "src"}
```

নীচের বিভাগগুলি ক্লায়েন্ট মোড ব্যবহার করে যদি না তারা অন্যথায় বলে।

## `+page.svelte`

```svelte filename="src/routes/about/+page.svelte"
<h1>About</h1>
```

একটি পৃষ্ঠা নিজেই ফাইল, এর URL এর নামানুসারে:

```svelte filename="src/routes/about.svelte"
<h1>About</h1>
```

`src/routes/+page.svelte` হল `src/routes/index.svelte`।

## গতিশীল রুট এবং `params`

```svelte filename="src/routes/blog/[slug]/+page.svelte"
<script lang="ts">
  import { page } from "$app/state";
</script>

<h1>{page.params.slug}</h1>
```

অংশগুলি প্রপ হিসাবে পৃষ্ঠায় পৌঁছায়:

```svelte filename="src/routes/blog/[slug].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

অন্য কোনো উপাদানে, `@nexy/client` এর `params` স্টোরটি তাদের ধরে রাখে: `$params.slug`। `[...rest]` এবং `(group)` ফোল্ডারগুলি SvelteKit-এর মতো কাজ করে।

## `+layout.svelte`

```svelte filename="src/routes/+layout.svelte"
<script lang="ts">
  let { children } = $props();
</script>

<header>My app</header>
<main>{@render children()}</main>
```

কোন `app.html` নেই: মূল `layout.svelte` নথির মালিক।

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

একই `GET` রপ্তানি, Python এ:

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

## `load` `+page.server.ts` মধ্যে

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

ক্লায়েন্ট মোডে পৃষ্ঠাটি তার ডেটার জন্য একজন হ্যান্ডলারকে জিজ্ঞাসা করে:

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

সার্ভার মোডে একটি `.nexy` পৃষ্ঠার ফ্রন্টম্যাটার হল `load` ফাংশন, এবং সার্ভার রেন্ডার করার সময় এটি চলে:

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

## ফর্ম কর্ম এবং `use:enhance`

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

একটি অ্যাকশন হল একটি Python ফাংশন যার জেনারেট করা, টাইপ করা ক্লায়েন্ট:

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

`revalidate("/todos")` `invalidateAll()` এর অংশটি খেলে: পৃষ্ঠাটি আবার নিজেকে নিয়ে আসে।

## `goto`, লিঙ্ক এবং `$app/state`

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

পাথ পরীক্ষা হল ফোল্ডার। একটি রুট `middleware.py` সবকিছু গুটিয়ে রাখে, একটি `dashboard/middleware.py` শুধুমাত্র তার নীচের রুটগুলি:

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

## `prerender` এবং `entries`

```ts filename="src/routes/blog/[slug]/+page.ts"
export const prerender = true;

export function entries() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

প্রতি মান প্রতি একটি প্রাক-রেন্ডার করা নথির জন্য পৃষ্ঠা থেকে `getStaticParams` রপ্তানি করুন:

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

সার্ভার মোডে, `revalidate = 60` একটি `.nexy` পৃষ্ঠার ফ্রন্টম্যাটারে এটি প্রতি URL এর পরিবর্তে ক্যাশে করে:

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

ক্লায়েন্ট মোডে, মূলে ট্যাগ লিখুন `layout.svelte`। সার্ভার মোডে একটি `.nexy` পৃষ্ঠা তাদের সেট করে এবং এর বিন্যাস তাদের `{{ useMetadata().html() }}` দিয়ে লেখে:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## Svelte সার্ভার পৃষ্ঠাগুলিতে উপাদান

```svelte filename="src/components/Counter.svelte"
<script lang="ts">
  let { start = 0 }: { start?: number } = $props();
  let count = $state(start);
</script>

<button onclick={() => count++}>{count}</button>
```

সার্ভার মোডে উপাদানটি একটি `.nexy` পৃষ্ঠার একটি দ্বীপ:

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.svelte" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

## `+error.svelte`

`src/routes/notfound.svelte` ক্লায়েন্ট মোডে অজানা URL, সার্ভার মোডে `notfound.nexy` উত্তর দেয় এবং API ক্লায়েন্টরা `{"detail": ...}` পায়।

## `$env/static/private`

```ts filename="src/lib/server/db.ts"
import { DATABASE_URL } from "$env/static/private";
```

```python filename="src/settings.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## চলছে

| SvelteKit | নেক্সি |
|---|---|
| `npx sv create` | `nx new`, টেমপ্লেট `web-fbr-svelte` |
| `vite dev` | `nx dev` |
| `vite build` একটি অ্যাডাপ্টার সহ, তারপর `node build` | `nx build`, তারপর `nx start` |
| `static/` | `public/`, `/` এ পরিবেশিত |
| `src/lib/` এবং `$lib` | `src/components/` এবং `@` |

## পরবর্তী পদক্ষেপ

- [সার্ভার মোড এবং ক্লায়েন্ট মোড](../routing/fbr/modes.md)
- [Svelte নেক্সিতে](../views/svelte/differences.md)
- [কর্ম](../guides/actions.md)
- [Nuxt থেকে Nexy ](nuxt.md)
