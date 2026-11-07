# من SvelteKit إلى Nexy

في Nexy، يحتفظ مشروع SvelteKit بصفحاته وتخطيطاته Svelte كملفات `.svelte` عادية، بينما يتم تحميل `+server.ts` و `+page.server.ts`، وتنتقل إجراءات النموذج والخطافات إلى الملفات Python المجاورة لها.

يعرض كل قسم أدناه عادة SvelteKit، ثم نفس الشيء في Nexy.

## اختر الوضع أولاً

| تطبيق SvelteKit الخاص بك هو | وضع نكسي | الصفحات هي |
|---|---|---|
| التطبيق مع الملاحة العميل | وضع العميل، `useCSR = True` | `.svelte` الملفات ضمن `src/routes/` |
| في الغالب المحتوى، وبعض الأجزاء التفاعلية | وضع الخادم، الافتراضي | `.nexy` صفحة بها Svelte جزر |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useCSR = True
    useAliases = {"@": "src"}
```

تستخدم الأقسام أدناه وضع العميل ما لم تنص على خلاف ذلك.

## `+page.svelte`

```svelte filename="src/routes/about/+page.svelte"
<h1>About</h1>
```

الصفحة هي الملف نفسه، المسمى باسم عنوان URL الخاص به:

```svelte filename="src/routes/about.svelte"
<h1>About</h1>
```

`src/routes/+page.svelte` هو `src/routes/index.svelte`.

## المسارات الديناميكية و `params`

```svelte filename="src/routes/blog/[slug]/+page.svelte"
<script lang="ts">
  import { page } from "$app/state";
</script>

<h1>{page.params.slug}</h1>
```

تصل المقاطع إلى الصفحة كدعائم:

```svelte filename="src/routes/blog/[slug].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

وفي أي مكون آخر فإن مخزن `params` من `@nexy/client` يحملهم: `$params.slug`. تعمل المجلدات `[...rest]` و `(group)` كما هو الحال في SvelteKit.

## `+layout.svelte`

```svelte filename="src/routes/+layout.svelte"
<script lang="ts">
  let { children } = $props();
</script>

<header>My app</header>
<main>{@render children()}</main>
```

لا يوجد `app.html`: الجذر `layout.svelte` يملك الوثيقة.

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

نفس `GET` التصدير، في Python:

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

## `load` في `+page.server.ts`

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

في وضع العميل، تطلب الصفحة من المعالج بياناتها:

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

في وضع الخادم، تكون المادة الأمامية لصفحة `.nexy` هي الوظيفة `load`، ويتم تشغيلها أثناء عرض الخادم:

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

## إجراءات النموذج و `use:enhance`

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

الإجراء هو وظيفة Python مع عميل تم إنشاؤه وكتابته:

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

`revalidate("/todos")` يلعب دور `invalidateAll()`: الصفحة تجلب نفسها مرة أخرى.

## `goto`، روابط و `$app/state`

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

اختبار المسار هو المجلد. الجذر `middleware.py` يغطي كل شيء، `dashboard/middleware.py` فقط المسارات الموجودة تحته:

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

## `prerender` و `entries`

```ts filename="src/routes/blog/[slug]/+page.ts"
export const prerender = true;

export function entries() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

تصدير `getStaticParams` من الصفحة لمستند واحد معروض مسبقًا لكل قيمة:

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

في وضع الخادم، يقوم `revalidate = 60` في الجزء الأمامي من صفحة `.nexy` بتخزينه مؤقتًا لكل عنوان URL بدلاً من ذلك:

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

في وضع العميل، اكتب العلامات في الجذر `layout.svelte`. في وضع الخادم، تقوم صفحة `.nexy` بتعيينها، ويكتبها تخطيطها باستخدام `{{ useMetadata().html() }}`:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## Svelte المكونات الموجودة في صفحات الخادم

```svelte filename="src/components/Counter.svelte"
<script lang="ts">
  let { start = 0 }: { start?: number } = $props();
  let count = $state(start);
</script>

<button onclick={() => count++}>{count}</button>
```

في وضع الخادم، يكون المكون عبارة عن جزيرة من صفحة `.nexy`:

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.svelte" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

## `+error.svelte`

`src/routes/notfound.svelte` يجيب على عناوين URL غير المعروفة في وضع العميل، `notfound.nexy` في وضع الخادم، ويحصل عملاء API على `{"detail": ...}`.

## `$env/static/private`

```ts filename="src/lib/server/db.ts"
import { DATABASE_URL } from "$env/static/private";
```

```python filename="src/settings.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## الجري

| SvelteKit | نكسي |
|---|---|
| `npx sv create` | `nx new`، القالب `web-fbr-svelte` |
| `vite dev` | `nx dev` |
| `vite build` مع محول، ثم `node build` | `nx build`، ثم `nx start` |
| `static/` | `public/`، خدم في `/` |
| `src/lib/` و `$lib` | `src/components/` و `@` |

## الخطوات التالية

- [وضع الخادم ووضع العميل](../routing/fbr/modes.md)
- [Svelte في نكسي](../views/svelte/differences.md)
- [الإجراءات](../guides/actions.md)
- [من نوكست إلى نكسي](nuxt.md)
