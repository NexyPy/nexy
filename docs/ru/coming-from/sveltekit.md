# От SvelteKit до Nexy

В Nexy проект SvelteKit сохраняет свои Svelte страницы и макеты как простые `.svelte` файлы, в то время как `+server.ts`, `+page.server.ts` загружаются, действия формы и перехваты перемещаются в Python файлы рядом с ними.

В каждом разделе ниже показаны привычки SvelteKit, затем то же самое в Nexy.

## Сначала выберите режим

| Ваше приложение SvelteKit | Некси-режим | Страницы |
|---|---|---|
| приложение с клиентской навигацией | клиентский режим, `useCSR = True` | `.svelte` файлы в папке `src/routes/` |
| в основном контент, несколько интерактивных частей | режим сервера, по умолчанию | `.nexy` страницы с Svelte островами |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useCSR = True
    useAliases = {"@": "src"}
```

В разделах ниже используется клиентский режим, если не указано иное.

## `+page.svelte`

```svelte filename="src/routes/about/+page.svelte"
<h1>About</h1>
```

Страница - это сам файл, названный по его URL-адресу:

```svelte filename="src/routes/about.svelte"
<h1>About</h1>
```

`src/routes/+page.svelte` - это `src/routes/index.svelte`.

## Динамические маршруты и `params`

```svelte filename="src/routes/blog/[slug]/+page.svelte"
<script lang="ts">
  import { page } from "$app/state";
</script>

<h1>{page.params.slug}</h1>
```

Сегменты попадают на страницу в качестве реквизита:

```svelte filename="src/routes/blog/[slug].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

В любом другом компоненте они хранятся в хранилище `params` из `@nexy/client`: `$params.slug`. Папки `[...rest]` и `(group)` работают как в SvelteKit.

## `+layout.svelte`

```svelte filename="src/routes/+layout.svelte"
<script lang="ts">
  let { children } = $props();
</script>

<header>My app</header>
<main>{@render children()}</main>
```

`app.html` нет: документ принадлежит корню `layout.svelte`.

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

Тот же экспорт `GET` в Python:

```python filename="src/маршруты/api/items/[id].py"
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

## `load` в `+page.server.ts`

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

В клиентском режиме страница запрашивает у обработчика свои данные:

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

В режиме сервера главным элементом страницы `.nexy` является функция `load` и она выполняется во время рендеринга сервера:

```nexy filename="src/маршруты/people.nexy"
---
users = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Формируйте действия и `use:enhance`

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

Действие - это функция Python со сгенерированным типизированным клиентом:

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

`revalidate("/todos")` играет роль `invalidateAll()`: страница загружается снова.

## `goto`, ссылки и `$app/state`

```svelte filename="src/lib/Nav.svelte"
<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/state";
</script>

<a href="/about">About</a>
<span>{page.url.pathname}</span>
<button onclick={() => goto("/dashboard")}>Dashboard</button>
```

```svelte filename="src/компоненты/Nav.svelte"
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

Тест пути - это папка. Корень `middleware.py` охватывает все, а `dashboard/middleware.py` - только маршруты ниже него:

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

## `prerender` и `entries`

```ts filename="src/routes/blog/[slug]/+page.ts"
export const prerender = true;

export function entries() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

Экспортируйте `getStaticParams` со страницы для одного предварительно обработанного документа на каждое значение:

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

В режиме сервера `revalidate = 60` в заголовке страницы `.nexy` вместо этого кэширует ее для каждого URL-адреса:

```nexy filename="src/маршруты/news.nexy"
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

В режиме клиента записывайте теги в корень `layout.svelte`. В режиме сервера страница `.nexy` устанавливает их, а ее макет записывает их с помощью `{{ useMetadata().html() }}`:

```nexy filename="src/маршруты/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## Svelte компоненты на страницах сервера

```svelte filename="src/компоненты/Counter.svelte"
<script lang="ts">
  let { start = 0 }: { start?: number } = $props();
  let count = $state(start);
</script>

<button onclick={() => count++}>{count}</button>
```

В режиме сервера компонент представляет собой остров страницы `.nexy`:

```nexy filename="src/маршруты/home.nexy"
---
from "@/components/Counter.svelte" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

## `+error.svelte`

`src/routes/notfound.svelte` отвечает на неизвестные URL-адреса в режиме клиента, `notfound.nexy` в режиме сервера, а клиенты API получают `{"detail": ...}`.

## `$env/static/private`

```ts filename="src/lib/server/db.ts"
import { DATABASE_URL } from "$env/static/private";
```

```python filename="источник/settings.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## Бег

| SvelteKit | Некси |
|---|---|
| `npx sv create` | `nx new`, шаблон `web-fbr-svelte` |
| `vite dev` | `nx dev` |
| `vite build` с адаптером, затем `node build` | `nx build`, затем `nx start` |
| `static/` | `public/`, служил в `/` |
| `src/lib/` и `$lib` | `src/components/` и `@` |

## Следующие шаги

- [Режим сервера и режим клиента](../routing/fbr/modes.md)
- [Svelte в Некси](../views/svelte/differences.md)
- [Действия](../guides/actions.md)
- [От Nuxt до Nexy](nuxt.md)
