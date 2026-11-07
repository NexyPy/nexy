# От Nuxt к Nexy

В Nexy проект Nuxt сохраняет свои `.vue` страницы, макеты и компоненты, в то время как `server/api` обработчики, серверное промежуточное программное обеспечение и загрузка данных перемещаются в Python файлы рядом с ними.

В каждом разделе ниже показаны привычки Nuxt, затем то же самое в Nexy.

## Сначала выберите режим

| Ваше приложение Nuxt | Некси-режим | Страницы |
|---|---|---|
| приложение с клиентской навигацией | клиентский режим, `useCSR = True` | `.vue` файлы в папке `src/routes/` |
| в основном контент, несколько интерактивных частей | режим сервера, по умолчанию | `.nexy` страниц с Vue островами |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useCSR = True
    useAliases = {"@": "src"}
```

`nuxt.config.ts` становится этим файлом. В разделах ниже используется клиентский режим, если не указано иное.

## `pages/`

```vue filename="страницы/about.vue"
<template>
  <h1>About</h1>
</template>
```

```vue filename="src/маршруты/about.vue"
<template>
  <h1>About</h1>
</template>
```

`pages/index.vue` - это `src/routes/index.vue`, `pages/blog/index.vue` - это `src/routes/blog/index.vue`.

## Динамические страницы и `useRoute().params`

```vue filename="страницы/блог/[slug].vue"
<script setup lang="ts">
const route = useRoute();
</script>

<template>
  <h1>{{ route.params.slug }}</h1>
</template>
```

Сегменты попадают на страницу в качестве реквизита:

```vue filename="src/маршруты/блог/[слизень].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

В любом другом компоненте `useParams()` из `@nexy/client` возвращает их как вычисленную ссылку. `[...slug].vue` является универсальным, как и в Nuxt.

## `layouts/default.vue` и `app.vue`

```vue filename="макеты/default.vue"
<template>
  <header>My app</header>
  <main><slot /></main>
</template>
```

Нет `<NuxtLayout>` и `app.vue`: корневой элемент `layout.vue` владеет документом и оборачивает каждую страницу, а `layout.vue` в подпапке вложен внутри него.

```vue filename="src/маршруты/layout.vue"
<template>
  <html>
    <body>
      <header>My app</header>
      <main><slot /></main>
    </body>
  </html>
</template>
```

Именованный макет `definePageMeta({ layout: "admin" })` становится папкой с собственной `layout.vue` или группой маршрутов, например `(admin)/layout.vue`.

## `<NuxtLink>` и `navigateTo`

```vue filename="компоненты/Nav.vue"
<script setup lang="ts">
const go = () => navigateTo("/dashboard");
</script>

<template>
  <NuxtLink to="/about" active-class="active">About</NuxtLink>
  <button @click="go">Dashboard</button>
</template>
```

```vue filename="src/компоненты/Nav.vue"
<script setup lang="ts">
import { Link, useRouter } from "@nexy/client";

const router = useRouter();
</script>

<template>
  <Link href="/about" active-class="active">About</Link>
  <button @click="router.push('/dashboard')">Dashboard</button>
</template>
```

Компоненты не импортируются автоматически: импортируйте их там, где вы их используете.

## `server/api`

```ts filename="сервер/api/items/[id].get.ts"
export default defineEventHandler((event) => {
  const id = Number(getRouterParam(event, "id"));
  return { id };
});
```

Один файл Python на каждый URL, одна функция на метод, без суффикса `.get`:

```python filename="src/маршруты/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

## `readBody` и проверка

```ts filename="сервер/api/items/index.post.ts"
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

## `getQuery` и `createError`

```ts filename="сервер/api/orders/[id].get.ts"
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

## `useFetch` и `useAsyncData`

```vue filename="страницы/users.vue"
<script setup lang="ts">
const { data: users } = await useFetch("/api/users");
</script>

<template>
  <ul>
    <li v-for="user in users" :key="user.id">{{ user.name }}</li>
  </ul>
</template>
```

В клиентском режиме страница вызывает обработчик из браузера:

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

В режиме сервера заголовок страницы `.nexy` загружает данные, пока сервер их отображает:

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

## Мутации: `$fetch` на маршрут сервера.

```vue filename="компоненты/AddTodo.vue"
<script setup lang="ts">
const title = ref("");
const add = () => $fetch("/api/todos", { method: "POST", body: { title: title.value } });
</script>
```

Действие пропускает URL: Nexy генерирует типизированный клиент из функции Python.

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

```vue filename="src/компоненты/AddTodo.vue"
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

## Промежуточное программное обеспечение сервера

```ts filename="сервер/промежуточное ПО/app-header.ts"
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

## Промежуточное ПО маршрутизации

```ts filename="промежуточное программное обеспечение /auth.ts"
export default defineNuxtRouteMiddleware(() => {
  if (!useCookie("session").value) return navigateTo("/login");
});
```

`middleware.py` в папке запускается на сервере перед страницей или обработчиком:

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

## `useHead` и `useSeoMeta`

```vue filename="страницы/blog.vue"
<script setup lang="ts">
useSeoMeta({ title: "Blog", description: "Posts about Nexy" });
</script>
```

Страница `.vue` не имеет API метаданных в Nexy: поместите теги в корневой макет. В режиме сервера страница `.nexy` устанавливает их, а ее макет записывает их с помощью `{{ useMetadata().html() }}`:

```nexy filename="src/маршруты/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## `routeRules` с `swr` или `isr`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  routeRules: { "/news": { swr: 60 } },
});
```

Правило перемещается на страницу в режиме сервера:

```nexy filename="src/маршруты/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## Vue компоненты на страницах сервера

```vue filename="компоненты/Counter.vue"
<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{ start?: number }>();
const count = ref(props.start ?? 0);
</script>

<template>
  <button @click="count++">{{ count }}</button>
</template>
```

В режиме сервера компонент представляет собой островок страницы `.nexy`, аналогичный `<ClientOnly>` части страницы Nuxt, отображаемой на сервере, с директивой, указывающей, когда она гидратируется:

```nexy filename="src/маршруты/home.nexy"
---
from "@/components/Counter.vue" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

## `error.vue`

```vue filename="ошибка.vue"
<script setup lang="ts">
defineProps<{ error: { statusCode: number } }>();
</script>

<template>
  <h1>{{ error.statusCode }}</h1>
</template>
```

`src/routes/notfound.vue` отвечает на неизвестные URL-адреса в режиме клиента, `notfound.nexy` в режиме сервера, а клиенты API получают `{"detail": ...}`.

## `runtimeConfig`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  runtimeConfig: { databaseUrl: process.env.DATABASE_URL },
});
```

Настройки сервера - это переменные среды, читаемые в Python:

```python filename="источник/settings.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## Бег

| Нукст | Некси |
|---|---|
| `npx nuxi init` | `nx new`, шаблон `web-fbr-vue` |
| `nuxt dev` | `nx dev` |
| `nuxt build`, затем `node .output/server/index.mjs` | `nx build`, затем `nx start` |
| `nuxt generate` | нет статического экспорта: `nx start` обслуживает страницы |
| `public/` | `public/`, служил в `/` |

## Следующие шаги

- [Режим сервера и режим клиента](../routing/fbr/modes.md)
- [Vue в Некси](../views/vue/differences.md)
- [Действия](../guides/actions.md)
- [От Next.js до Некси](nextjs.md)
