# Nuxt থেকে Nexy

Nexy এ Nuxt প্রজেক্ট তার `.vue` পৃষ্ঠা, লেআউট এবং উপাদান রাখে, যখন `server/api` হ্যান্ডলার, সার্ভার মিডলওয়্যার এবং ডেটা লোডিং তাদের পাশের Python ফাইলে চলে যায়।

নীচের প্রতিটি বিভাগ একটি Nuxt অভ্যাস দেখায়, তারপর Nexy তে একই জিনিস।

## প্রথমে মোডটি বেছে নিন

| আপনার Nuxt অ্যাপটি | নেক্সি মোড | পৃষ্ঠাগুলি হল |
|---|---|---|
| ক্লায়েন্ট নেভিগেশন সহ একটি অ্যাপ | ক্লায়েন্ট মোড, `useCSR = True` | `.vue` ফাইল `src/routes/` এর অধীনে |
| বেশিরভাগ বিষয়বস্তু, কয়েকটি ইন্টারেক্টিভ অংশ | সার্ভার মোড, ডিফল্ট | Vue দ্বীপ সহ `.nexy` পৃষ্ঠা |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useCSR = True
    useAliases = {"@": "src"}
```

`nuxt.config.ts` এই ফাইলে পরিণত হয়। নীচের বিভাগগুলি ক্লায়েন্ট মোড ব্যবহার করে যদি না তারা অন্যথায় বলে।

## `pages/`

```vue filename="পৃষ্ঠা/about.vue"
<template>
  <h1>About</h1>
</template>
```

```vue filename="src/routes/about.vue"
<template>
  <h1>About</h1>
</template>
```

`pages/index.vue` হল `src/routes/index.vue`, `pages/blog/index.vue` হল `src/routes/blog/index.vue`।

## গতিশীল পৃষ্ঠা এবং `useRoute().params`

```vue filename="pages/blog/[slug].vue"
<script setup lang="ts">
const route = useRoute();
</script>

<template>
  <h1>{{ route.params.slug }}</h1>
</template>
```

অংশগুলি প্রপ হিসাবে পৃষ্ঠায় পৌঁছায়:

```vue filename="src/routes/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

অন্য কোনো উপাদানে, `useParams()` থেকে `@nexy/client` একটি গণনাকৃত রেফ হিসাবে তাদের প্রদান করে। `[...slug].vue` একটি ক্যাচ-অল, যেমন Nuxt-এ।

## `layouts/default.vue` এবং `app.vue`

```vue filename="layouts/default.vue"
<template>
  <header>My app</header>
  <main><slot /></main>
</template>
```

কোন `<NuxtLayout>` এবং কোন `app.vue` নেই: মূল `layout.vue` নথির মালিক এবং প্রতিটি পৃষ্ঠা মোড়ানো, এবং একটি `layout.vue` এটির ভিতরে একটি সাবফোল্ডার বাসা বাঁধে।

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

একটি নামযুক্ত লেআউট, `definePageMeta({ layout: "admin" })`, তার নিজস্ব `layout.vue`, বা একটি রুট গ্রুপ যেমন `(admin)/layout.vue` সহ একটি ফোল্ডারে পরিণত হয়।

## `<NuxtLink>` এবং `navigateTo`

```vue filename="উপাদান/Nav.vue"
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

উপাদানগুলি স্বয়ংক্রিয়ভাবে আমদানি করা হয় না: আপনি যেখানে সেগুলি ব্যবহার করেন সেগুলি আমদানি করুন৷

## `server/api`

```ts filename="server/api/items/[id].get.ts"
export default defineEventHandler((event) => {
  const id = Number(getRouterParam(event, "id"));
  return { id };
});
```

ইউআরএল প্রতি একটি Python ফাইল, প্রতি পদ্ধতিতে একটি ফাংশন, `.get` প্রত্যয় ছাড়া:

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

## `readBody` এবং বৈধতা

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

## `getQuery` এবং `createError`

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

## `useFetch` এবং `useAsyncData`

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

ক্লায়েন্ট মোডে পৃষ্ঠাটি ব্রাউজার থেকে হ্যান্ডলারকে কল করে:

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

সার্ভার মোডে, একটি `.nexy` পৃষ্ঠার ফ্রন্টম্যাটার ডেটা লোড করে যখন সার্ভার এটি রেন্ডার করে:

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

## মিউটেশন: `$fetch` একটি সার্ভার রুটে

```vue filename="components/AddTodo.vue"
<script setup lang="ts">
const title = ref("");
const add = () => $fetch("/api/todos", { method: "POST", body: { title: title.value } });
</script>
```

একটি ক্রিয়া URL এড়িয়ে যায়: Nexy Python ফাংশন থেকে একটি টাইপ করা ক্লায়েন্ট তৈরি করে।

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

## সার্ভার মিডলওয়্যার

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

## রুট মিডলওয়্যার

```ts filename="Middleware/auth.ts"
export default defineNuxtRouteMiddleware(() => {
  if (!useCookie("session").value) return navigateTo("/login");
});
```

ফোল্ডারে একটি `middleware.py` সার্ভারে চলে, পৃষ্ঠা বা হ্যান্ডলারের আগে:

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

## `useHead` এবং `useSeoMeta`

```vue filename="pages/blog.vue"
<script setup lang="ts">
useSeoMeta({ title: "Blog", description: "Posts about Nexy" });
</script>
```

Nexy-এ একটি `.vue` পৃষ্ঠার কোনো মেটাডেটা API নেই: ট্যাগগুলিকে রুট লেআউটে রাখুন। সার্ভার মোডে একটি `.nexy` পৃষ্ঠা তাদের সেট করে এবং এর বিন্যাস তাদের `{{ useMetadata().html() }}` দিয়ে লেখে:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## `routeRules` `swr` বা `isr` সহ

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  routeRules: { "/news": { swr: 60 } },
});
```

নিয়মটি সার্ভার মোডে পৃষ্ঠায় চলে যায়:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## Vue সার্ভার পৃষ্ঠাগুলিতে উপাদান

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

সার্ভার মোডে উপাদানটি হল একটি `.nexy` পৃষ্ঠার একটি দ্বীপ, যেমন একটি সার্ভার-রেন্ডার করা Nuxt পৃষ্ঠার একটি `<ClientOnly>` অংশ, এটি কখন হাইড্রেট হয় তার নির্দেশনা সহ:

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

`src/routes/notfound.vue` ক্লায়েন্ট মোডে অজানা URL, সার্ভার মোডে `notfound.nexy` উত্তর দেয় এবং API ক্লায়েন্টরা `{"detail": ...}` পায়।

## `runtimeConfig`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  runtimeConfig: { databaseUrl: process.env.DATABASE_URL },
});
```

সার্ভার সেটিংস হল পরিবেশ ভেরিয়েবল, Python-এ পড়ুন:

```python filename="src/settings.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## চলছে

| নক্সট | নেক্সি |
|---|---|
| `npx nuxi init` | `nx new`, টেমপ্লেট `web-fbr-vue` |
| `nuxt dev` | `nx dev` |
| `nuxt build`, তারপর `node .output/server/index.mjs` | `nx build`, তারপর `nx start` |
| `nuxt generate` | কোন স্ট্যাটিক এক্সপোর্ট: `nx start` পৃষ্ঠাগুলি পরিবেশন করে |
| `public/` | `public/`, `/` এ পরিবেশিত |

## পরবর্তী পদক্ষেপ

- [সার্ভার মোড এবং ক্লায়েন্ট মোড](../routing/fbr/modes.md)
- [Vue নেক্সিতে](../views/vue/differences.md)
- [কর্ম](../guides/actions.md)
- [থেকে Next.js Nexy থেকে](nextjs.md)
