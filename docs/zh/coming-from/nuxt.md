# 从 Nuxt 到 Nexy

在 Nexy 中，Nuxt 项目保留其 `.vue` 页面、布局和组件，而 `server/api` 处理程序、服务器中间件和数据加载则移动到它们旁边的 Python 文件。

下面的每个部分都显示了 Nuxt 习惯，然后是 Nexy 中的相同内容。

## 首先选择模式

| 您的 Nuxt 应用程序是 | 邻接模式 | 页面是 |
|---|---|---|
| 具有客户端导航功能的应用程序 | 客户端模式，`useCSR = True` | `src/routes/` 下的 `.vue` 文件 |
| 主要内容，一些互动部分 | 服务器模式，默认 | `.nexy` 页面包含 Vue 岛屿 |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useCSR = True
    useAliases = {"@": "src"}
```

`nuxt.config.ts` 成为此文件。除非另有说明，以下部分均使用客户端模式。

## `pages/`

```vue filename="页面/about.vue"
<template>
  <h1>About</h1>
</template>
```

```vue filename="src/routes/about.vue"
<template>
  <h1>About</h1>
</template>
```

`pages/index.vue` 是 `src/routes/index.vue`，`pages/blog/index.vue` 是 `src/routes/blog/index.vue`。

## 动态页面和 `useRoute().params`

```vue filename="页面/博客/[slug].vue"
<script setup lang="ts">
const route = useRoute();
</script>

<template>
  <h1>{{ route.params.slug }}</h1>
</template>
```

这些段作为 props 到达页面：

```vue filename="src/routes/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

在任何其他组件中，`@nexy/client` 中的 `useParams()` 将它们作为计算引用返回。 `[...slug].vue` 是一个包罗万象的东西，就像 Nuxt 中一样。

## `layouts/default.vue` 和 `app.vue`

```vue filename="布局/default.vue"
<template>
  <header>My app</header>
  <main><slot /></main>
</template>
```

没有 `<NuxtLayout>` 和 `app.vue`：根 `layout.vue` 拥有文档并包含每个页面，子文件夹中的 `layout.vue` 嵌套在其中。

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

命名布局 `definePageMeta({ layout: "admin" })` 成为具有自己的 `layout.vue` 的文件夹，或路由组（例如 `(admin)/layout.vue`）。

## `<NuxtLink>` 和 `navigateTo`

```vue filename="组件/Nav.vue"
<script setup lang="ts">
const go = () => navigateTo("/dashboard");
</script>

<template>
  <NuxtLink to="/about" active-class="active">About</NuxtLink>
  <button @click="go">Dashboard</button>
</template>
```

```vue filename="src/组件/Nav.vue"
<script setup lang="ts">
import { Link, useRouter } from "@nexy/client";

const router = useRouter();
</script>

<template>
  <Link href="/about" active-class="active">About</Link>
  <button @click="router.push('/dashboard')">Dashboard</button>
</template>
```

组件不会自动导入：在使用它们的地方导入它们。

## `server/api`

```ts filename="服务器/api/items/[id].get.ts"
export default defineEventHandler((event) => {
  const id = Number(getRouterParam(event, "id"));
  return { id };
});
```

每个 URL 一个 Python 文件，每个方法一个函数，没有 `.get` 后缀：

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

## `readBody` 和验证

```ts filename="服务器/api/items/index.post.ts"
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

## `getQuery` 和 `createError`

```ts filename="服务器/api/orders/[id].get.ts"
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

## `useFetch` 和 `useAsyncData`

```vue filename="页面/users.vue"
<script setup lang="ts">
const { data: users } = await useFetch("/api/users");
</script>

<template>
  <ul>
    <li v-for="user in users" :key="user.id">{{ user.name }}</li>
  </ul>
</template>
```

在客户端模式下，页面从浏览器调用处理程序：

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

在服务器模式下，`.nexy` 页面的 frontmatter 在服务器渲染数据时加载数据：

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

## 突变：`$fetch` 到服务器路由

```vue filename="组件/AddTodo.vue"
<script setup lang="ts">
const title = ref("");
const add = () => $fetch("/api/todos", { method: "POST", body: { title: title.value } });
</script>
```

操作会跳过 URL：Nexy 从 Python 函数生成类型化客户端。

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

## 服务器中间件

```ts filename="服务器/中间件/app-header.ts"
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

## 路由中间件

```ts filename="中间件/auth.ts"
export default defineNuxtRouteMiddleware(() => {
  if (!useCookie("session").value) return navigateTo("/login");
});
```

文件夹中的 `middleware.py` 在服务器上运行，位于页面或处理程序之前：

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

## `useHead` 和 `useSeoMeta`

```vue filename="页面/blog.vue"
<script setup lang="ts">
useSeoMeta({ title: "Blog", description: "Posts about Nexy" });
</script>
```

`.vue` 页面在 Nexy 中没有元数据 API：将标签放在根布局中。在服务器模式下，`.nexy` 页面设置它们，其布局用 `{{ useMetadata().html() }}`写入它们：

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## `routeRules` 与 `swr` 或 `isr`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  routeRules: { "/news": { swr: 60 } },
});
```

该规则在服务器模式下移入页面：

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## 服务器页面中的 Vue 组件

```vue filename="组件/Counter.vue"
<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{ start?: number }>();
const count = ref(props.start ?? 0);
</script>

<template>
  <button @click="count++">{{ count }}</button>
</template>
```

在服务器模式下，该组件是一个 `.nexy` 页面的孤岛，就像服务器渲染的 Nuxt 页面的 `<ClientOnly>` 部分一样，带有一个何时水合的指令：

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.vue" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

## `error.vue`

```vue filename="错误.vue"
<script setup lang="ts">
defineProps<{ error: { statusCode: number } }>();
</script>

<template>
  <h1>{{ error.statusCode }}</h1>
</template>
```

`src/routes/notfound.vue` 在客户端模式下回答未知 URL，`notfound.nexy` 在服务器模式下回答未知 URL，API 客户端得到 `{"detail": ...}`。

## `runtimeConfig`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  runtimeConfig: { databaseUrl: process.env.DATABASE_URL },
});
```

服务器设置是环境变量，在 Python中读取：

```python filename="src/设置.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## 跑步

| 努克斯特 | 内克西 |
|---|---|
| `npx nuxi init` | `nx new`，模板 `web-fbr-vue` |
| `nuxt dev` | `nx dev` |
| `nuxt build`，然后 `node .output/server/index.mjs` | `nx build`，然后 `nx start` |
| `nuxt generate` | 无静态导出：`nx start` 提供页面 |
| `public/` | `public/`，服务于 `/` |

## 后续步骤

- [服务器模式和客户端模式](../routing/fbr/modes.md)
- [Vue 在 Nexy](../views/vue/differences.md)
- [行动](../guides/actions.md)
- [从 Next.js 到 Nexy](nextjs.md)
