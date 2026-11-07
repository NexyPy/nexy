# Nuxt سے Nexy تک

Nexy میں ایک Nuxt پروجیکٹ اپنے `.vue` صفحات، ترتیب اور اجزاء کو رکھتا ہے، جبکہ `server/api` ہینڈلرز، سرور مڈل ویئر اور ڈیٹا لوڈنگ پر منتقل ہوتا ہے۔ Python فائلیں ان کے ساتھ ہیں۔

ذیل میں ہر سیکشن ایک Nuxt عادت دکھاتا ہے، پھر Nexy میں وہی چیز۔

## پہلے موڈ کا انتخاب کریں۔

| آپ کی Nuxt ایپ ہے۔ | نیکسی موڈ | صفحات ہیں۔ |
|---|---|---|
| کلائنٹ نیویگیشن کے ساتھ ایک ایپ | کلائنٹ موڈ، `useCSR = True` | `.vue` فائلیں `src/routes/` کے تحت |
| زیادہ تر مواد، چند انٹرایکٹو حصے | سرور موڈ، ڈیفالٹ | `.nexy` صفحات Vue جزائر کے ساتھ |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useCSR = True
    useAliases = {"@": "src"}
```

`nuxt.config.ts` یہ فائل بن جاتی ہے۔ ذیل کے حصے کلائنٹ موڈ کا استعمال کرتے ہیں جب تک کہ وہ دوسری صورت میں نہ کہیں۔

## `pages/`

```vue filename="صفحات/about.vue"
<template>
  <h1>About</h1>
</template>
```

```vue filename="src/routes/about.vue"
<template>
  <h1>About</h1>
</template>
```

`pages/index.vue` ہے `src/routes/index.vue`، `pages/blog/index.vue` ہے `src/routes/blog/index.vue`۔

## متحرک صفحات اور `useRoute().params`

```vue filename="pages/blog/[slug].vue"
<script setup lang="ts">
const route = useRoute();
</script>

<template>
  <h1>{{ route.params.slug }}</h1>
</template>
```

طبقات صفحہ پر بطور پروپس پہنچتے ہیں:

```vue filename="src/routes/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

کسی بھی دوسرے جزو میں، `useParams()` سے `@nexy/client` انہیں ایک حسابی حوالہ کے طور پر واپس کرتا ہے۔ `[...slug].vue` ایک کیچ آل ہے، جیسا کہ نکسٹ میں ہے۔

## `layouts/default.vue` اور `app.vue`

```vue filename="layouts/default.vue"
<template>
  <header>My app</header>
  <main><slot /></main>
</template>
```

کوئی `<NuxtLayout>` اور کوئی `app.vue` نہیں ہے: جڑ `layout.vue` دستاویز کا مالک ہے اور ہر صفحے کو لپیٹتا ہے، اور اس کے اندر ایک ذیلی فولڈر میں ایک `layout.vue` گھوںسلا ہے۔

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

ایک نامزد لے آؤٹ، `definePageMeta({ layout: "admin" })`، اپنے `layout.vue`، یا روٹ گروپ جیسے `(admin)/layout.vue` کے ساتھ ایک فولڈر بن جاتا ہے۔

## `<NuxtLink>` اور `navigateTo`

```vue filename="اجزاء/Nav.vue"
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

اجزاء خودکار درآمد نہیں ہوتے ہیں: جہاں آپ انہیں استعمال کرتے ہیں انہیں درآمد کریں۔

## `server/api`

```ts filename="server/api/items/[id].get.ts"
export default defineEventHandler((event) => {
  const id = Number(getRouterParam(event, "id"));
  return { id };
});
```

ایک Python فائل فی یو آر ایل، ایک فنکشن فی طریقہ، بغیر `.get` لاحقہ کے:

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

## `readBody` اور توثیق

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

## `getQuery` اور `createError`

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

## `useFetch` اور `useAsyncData`

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

کلائنٹ موڈ میں صفحہ براؤزر سے ہینڈلر کو کال کرتا ہے:

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

سرور موڈ میں، `.nexy` صفحہ کا فرنٹ میٹر ڈیٹا کو لوڈ کرتا ہے جب کہ سرور اسے پیش کرتا ہے:

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

## اتپریورتن: سرور کے راستے میں `$fetch`

```vue filename="اجزاء/AddTodo.vue"
<script setup lang="ts">
const title = ref("");
const add = () => $fetch("/api/todos", { method: "POST", body: { title: title.value } });
</script>
```

ایک عمل URL کو چھوڑ دیتا ہے: Nexy Python فنکشن سے ٹائپ شدہ کلائنٹ تیار کرتا ہے۔

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

## سرور مڈل ویئر

```ts filename="server/midleware/app-header.ts"
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

## روٹ مڈل ویئر

```ts filename="Middleware/auth.ts"
export default defineNuxtRouteMiddleware(() => {
  if (!useCookie("session").value) return navigateTo("/login");
});
```

فولڈر میں ایک `middleware.py` صفحہ یا ہینڈلر سے پہلے سرور پر چلتا ہے:

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

## `useHead` اور `useSeoMeta`

```vue filename="pages/blog.vue"
<script setup lang="ts">
useSeoMeta({ title: "Blog", description: "Posts about Nexy" });
</script>
```

ایک `.vue` صفحہ کا Nexy میں کوئی میٹا ڈیٹا API نہیں ہے: ٹیگز کو روٹ لے آؤٹ میں ڈالیں۔ سرور موڈ میں ایک `.nexy` صفحہ انہیں ترتیب دیتا ہے، اور اس کی ترتیب انہیں `{{ useMetadata().html() }}` کے ساتھ لکھتی ہے:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## `routeRules` `swr` یا `isr` کے ساتھ

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  routeRules: { "/news": { swr: 60 } },
});
```

قاعدہ سرور موڈ میں صفحہ میں منتقل ہوتا ہے:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## Vue سرور کے صفحات میں اجزاء

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

سرور موڈ میں جزو ایک `.nexy` صفحہ کا ایک جزیرہ ہے، جیسا کہ سرور کی طرف سے پیش کردہ Nuxt صفحہ کا ایک `<ClientOnly>` حصہ، اس کے لیے ہدایت کے ساتھ کہ یہ کب ہائیڈریٹ ہوتا ہے:

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

`src/routes/notfound.vue` کلائنٹ موڈ میں نامعلوم URLs کا جواب دیتا ہے، سرور موڈ میں `notfound.nexy`، اور API کلائنٹس کو `{"detail": ...}` ملتا ہے۔

## `runtimeConfig`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  runtimeConfig: { databaseUrl: process.env.DATABASE_URL },
});
```

سرور کی ترتیبات ماحولیاتی متغیرات ہیں، Python میں پڑھیں:

```python filename="src/settings.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## چل رہا ہے۔

| نکسٹ | نیکسی |
|---|---|
| `npx nuxi init` | `nx new`، سانچہ `web-fbr-vue` |
| `nuxt dev` | `nx dev` |
| `nuxt build`، پھر `node .output/server/index.mjs` | `nx build`، پھر `nx start` |
| `nuxt generate` | کوئی جامد برآمد نہیں: `nx start` صفحات کی خدمت کرتا ہے۔ |
| `public/` | `public/`، `/` میں خدمت کی |

## اگلے اقدامات

- [سرور موڈ اور کلائنٹ موڈ](../routing/fbr/modes.md)
- [Vue Nexy میں](../views/vue/differences.md)
- [اعمال](../guides/actions.md)
- [سے Next.js سے Nexy](nextjs.md)
