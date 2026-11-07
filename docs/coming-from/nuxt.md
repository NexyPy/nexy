# From Nuxt to Nexy

In Nexy a Nuxt project keeps its `.vue` pages, layouts and components, while `server/api` handlers,
server middleware and data loading move to Python files next to them.

Each section below shows a Nuxt habit, then the same thing in Nexy.

## Pick the mode first

| Your Nuxt app is | Nexy mode | Pages are |
|---|---|---|
| an app with client navigation | client mode, `useCSR = True` | `.vue` files under `src/routes/` |
| mostly content, a few interactive parts | server mode, the default | `.nexy` pages with Vue islands |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useCSR = True
    useAliases = {"@": "src"}
```

`nuxt.config.ts` becomes this file. The sections below use client mode unless they say otherwise.

## `pages/`

```vue filename="pages/about.vue"
<template>
  <h1>About</h1>
</template>
```

```vue filename="src/routes/about.vue"
<template>
  <h1>About</h1>
</template>
```

`pages/index.vue` is `src/routes/index.vue`, `pages/blog/index.vue` is `src/routes/blog/index.vue`.

## Dynamic pages and `useRoute().params`

```vue filename="pages/blog/[slug].vue"
<script setup lang="ts">
const route = useRoute();
</script>

<template>
  <h1>{{ route.params.slug }}</h1>
</template>
```

The segments reach the page as props:

```vue filename="src/routes/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

In any other component, `useParams()` from `@nexy/client` returns them as a computed ref.
`[...slug].vue` is a catch-all, as in Nuxt.

## `layouts/default.vue` and `app.vue`

```vue filename="layouts/default.vue"
<template>
  <header>My app</header>
  <main><slot /></main>
</template>
```

There is no `<NuxtLayout>` and no `app.vue`: the root `layout.vue` owns the document and wraps every
page, and a `layout.vue` in a subfolder nests inside it.

```vue filename="src/routes/layout.vue"
<template>
  <html>
    <body>
      <header>My app</header>
      <main><slot /></main>
    </body>
  </html>
</template>
```

A named layout, `definePageMeta({ layout: "admin" })`, becomes a folder with its own `layout.vue`,
or a route group such as `(admin)/layout.vue`.

## `<NuxtLink>` and `navigateTo`

```vue filename="components/Nav.vue"
<script setup lang="ts">
const go = () => navigateTo("/dashboard");
</script>

<template>
  <NuxtLink to="/about" active-class="active">About</NuxtLink>
  <button @click="go">Dashboard</button>
</template>
```

```vue filename="src/components/Nav.vue"
<script setup lang="ts">
import { Link, useRouter } from "@nexy/client";

const router = useRouter();
</script>

<template>
  <Link href="/about" active-class="active">About</Link>
  <button @click="router.push('/dashboard')">Dashboard</button>
</template>
```

Components are not auto-imported: import them where you use them.

## `server/api`

```ts filename="server/api/items/[id].get.ts"
export default defineEventHandler((event) => {
  const id = Number(getRouterParam(event, "id"));
  return { id };
});
```

One Python file per URL, one function per method, without the `.get` suffix:

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

## `readBody` and validation

```ts filename="server/api/items/index.post.ts"
import { z } from "zod";

const NewItem = z.object({ name: z.string(), price: z.number().positive() });

export default defineEventHandler(async (event) => {
  const item = await readValidatedBody(event, NewItem.parse);
  setResponseStatus(event, 201);
  return item;
});
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

## `getQuery` and `createError`

```ts filename="server/api/orders/[id].get.ts"
export default defineEventHandler((event) => {
  const id = Number(getRouterParam(event, "id"));
  const { currency = "EUR" } = getQuery(event);
  if (id > 100) throw createError({ statusCode: 404, statusMessage: "No such order" });
  return { id, currency };
});
```

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `useFetch` and `useAsyncData`

```vue filename="pages/users.vue"
<script setup lang="ts">
const { data: users } = await useFetch("/api/users");
</script>

<template>
  <ul>
    <li v-for="user in users" :key="user.id">{{ user.name }}</li>
  </ul>
</template>
```

In client mode the page calls the handler from the browser:

```python filename="src/routes/api/users.py"
async def GET():
    return [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
```

```vue filename="src/routes/users.vue"
<script setup lang="ts">
import { onMounted, ref } from "vue";

const users = ref<{ id: number; name: string }[]>([]);
onMounted(async () => {
  users.value = await (await fetch("/api/users")).json();
});
</script>

<template>
  <ul>
    <li v-for="user in users" :key="user.id">{{ user.name }}</li>
  </ul>
</template>
```

In server mode, the frontmatter of a `.nexy` page loads the data while the server renders it:

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

## Mutations: `$fetch` to a server route

```vue filename="components/AddTodo.vue"
<script setup lang="ts">
const title = ref("");
const add = () => $fetch("/api/todos", { method: "POST", body: { title: title.value } });
</script>
```

An action skips the URL: Nexy generates a typed client from the Python function.

```python filename="src/actions/todos.py"
from pydantic import BaseModel

from nexy.decorators import Action


class Todo(BaseModel):
    title: str
    done: bool = False


@Action
async def add_todo(title: str) -> Todo:
    return Todo(title=title)
```

```vue filename="src/components/AddTodo.vue"
<script setup lang="ts">
import { ref } from "vue";
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const title = ref("");
const { run, pending, data } = useAction(add_todo, {
  onSuccess: () => (title.value = ""),
});
</script>

<template>
  <form @submit.prevent="run({ title })">
    <input v-model="title" />
    <button :disabled="pending">Add</button>
    <p v-if="data">Added {{ data.title }}</p>
  </form>
</template>
```

## Server middleware

```ts filename="server/middleware/app-header.ts"
export default defineEventHandler((event) => {
  setResponseHeader(event, "x-app", "demo");
});
```

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Route middleware

```ts filename="middleware/auth.ts"
export default defineNuxtRouteMiddleware(() => {
  if (!useCookie("session").value) return navigateTo("/login");
});
```

A `middleware.py` in the folder runs on the server, before the page or the handler:

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

## `useHead` and `useSeoMeta`

```vue filename="pages/blog.vue"
<script setup lang="ts">
useSeoMeta({ title: "Blog", description: "Posts about Nexy" });
</script>
```

A `.vue` page has no metadata API in Nexy: put the tags in the root layout. In server mode a `.nexy`
page sets them, and its layout writes them with `{{ useMetadata().html() }}`:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## `routeRules` with `swr` or `isr`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  routeRules: { "/news": { swr: 60 } },
});
```

The rule moves into the page, in server mode:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## Vue components in server pages

```vue filename="components/Counter.vue"
<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{ start?: number }>();
const count = ref(props.start ?? 0);
</script>

<template>
  <button @click="count++">{{ count }}</button>
</template>
```

In server mode the component is an island of a `.nexy` page, like a `<ClientOnly>` part of a
server-rendered Nuxt page, with a directive for when it hydrates:

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.vue" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

## `error.vue`

```vue filename="error.vue"
<script setup lang="ts">
defineProps<{ error: { statusCode: number } }>();
</script>

<template>
  <h1>{{ error.statusCode }}</h1>
</template>
```

`src/routes/notfound.vue` answers unknown URLs in client mode, `notfound.nexy` in server mode, and
API clients get `{"detail": ...}`.

## `runtimeConfig`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  runtimeConfig: { databaseUrl: process.env.DATABASE_URL },
});
```

Server settings are environment variables, read in Python:

```python filename="src/settings.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## Running

| Nuxt | Nexy |
|---|---|
| `npx nuxi init` | `nx new`, template `web-fbr-vue` |
| `nuxt dev` | `nx dev` |
| `nuxt build`, then `node .output/server/index.mjs` | `nx build`, then `nx start` |
| `nuxt generate` | no static export: `nx start` serves the pages |
| `public/` | `public/`, served at `/` |

## Next steps

- [Server mode and client mode](../routing/fbr/modes.md)
- [Vue in Nexy](../views/vue/differences.md)
- [Actions](../guides/actions.md)
- [From Next.js to Nexy](nextjs.md)
