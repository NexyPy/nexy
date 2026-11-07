# من Nuxt إلى Nexy

في Nexy، يحتفظ مشروع Nuxt بصفحاته `.vue` وتخطيطاته ومكوناته، بينما تنتقل معالجات `server/api` والبرمجيات الوسيطة للخادم وتحميل البيانات إلى الملفات Python المجاورة لها.

يعرض كل قسم أدناه عادة Nuxt، ثم نفس الشيء في Nexy.

## اختر الوضع أولاً

| تطبيق Nuxt الخاص بك هو | وضع نكسي | الصفحات هي |
|---|---|---|
| التطبيق مع الملاحة العميل | وضع العميل، `useCSR = True` | `.vue` الملفات ضمن `src/routes/` |
| في الغالب المحتوى، وبعض الأجزاء التفاعلية | وضع الخادم، الافتراضي | `.nexy` صفحة تحتوي على Vue جزيرة |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useCSR = True
    useAliases = {"@": "src"}
```

`nuxt.config.ts` يصبح هذا الملف. تستخدم الأقسام أدناه وضع العميل ما لم تنص على خلاف ذلك.

## `pages/`

```vue filename="الصفحات/about.vue"
<template>
  <h1>About</h1>
</template>
```

```vue filename="src/routes/about.vue"
<template>
  <h1>About</h1>
</template>
```

`pages/index.vue` هو `src/routes/index.vue`، `pages/blog/index.vue` هو `src/routes/blog/index.vue`.

## الصفحات الديناميكية و `useRoute().params`

```vue filename="الصفحات/المدونة/[slug].vue"
<script setup lang="ts">
const route = useRoute();
</script>

<template>
  <h1>{{ route.params.slug }}</h1>
</template>
```

تصل المقاطع إلى الصفحة كدعائم:

```vue filename="src/routes/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

في أي مكون آخر، `useParams()` من `@nexy/client` يُرجعها كمرجع محسوب. `[...slug].vue` هو ملف شامل، كما هو الحال في Nuxt.

## `layouts/default.vue` و `app.vue`

```vue filename="تخطيطات/default.vue"
<template>
  <header>My app</header>
  <main><slot /></main>
</template>
```

لا يوجد `<NuxtLayout>` ولا `app.vue`: الجذر `layout.vue` يملك الوثيقة ويغلف كل صفحة، و `layout.vue` في مجلد فرعي يعشش بداخلها.

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

يصبح التخطيط المسمى، `definePageMeta({ layout: "admin" })`، مجلدًا به `layout.vue` خاص به، أو مجموعة توجيه مثل `(admin)/layout.vue`.

## `<NuxtLink>` و `navigateTo`

```vue filename="المكونات/Nav.vue"
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

لا يتم استيراد المكونات تلقائيًا: قم باستيرادها حيث تستخدمها.

## `server/api`

```ts filename="الخادم/api/items/[id].get.ts"
export default defineEventHandler((event) => {
  const id = Number(getRouterParam(event, "id"));
  return { id };
});
```

ملف Python واحد لكل عنوان URL، ووظيفة واحدة لكل طريقة، بدون اللاحقة `.get`:

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

## `readBody` والتصديق

```ts filename="الخادم/api/items/index.post.ts"
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

## `getQuery` و `createError`

```ts filename="الخادم/api/orders/[id].get.ts"
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

## `useFetch` و `useAsyncData`

```vue filename="الصفحات/users.vue"
<script setup lang="ts">
const { data: users } = await useFetch("/api/users");
</script>

<template>
  <ul>
    <li v-for="user in users" :key="user.id">{{ user.name }}</li>
  </ul>
</template>
```

في وضع العميل، تستدعي الصفحة المعالج من المتصفح:

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

في وضع الخادم، يقوم الجزء الأمامي من صفحة `.nexy` بتحميل البيانات بينما يعرضها الخادم:

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

## الطفرات: `$fetch` إلى طريق الخادم

```vue filename="المكونات/AddTodo.vue"
<script setup lang="ts">
const title = ref("");
const add = () => $fetch("/api/todos", { method: "POST", body: { title: title.value } });
</script>
```

يتخطى الإجراء عنوان URL: يقوم Nexy بإنشاء عميل مكتوب من الدالة Python.

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

## الوسيطة الخادم

```ts filename="الخادم/الوسيطة/app-header.ts"
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

## طريق الوسيطة

```ts filename="الوسيطة/auth.ts"
export default defineNuxtRouteMiddleware(() => {
  if (!useCookie("session").value) return navigateTo("/login");
});
```

يتم تشغيل `middleware.py` الموجود في المجلد على الخادم، قبل الصفحة أو المعالج:

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

## `useHead` و `useSeoMeta`

```vue filename="الصفحات/blog.vue"
<script setup lang="ts">
useSeoMeta({ title: "Blog", description: "Posts about Nexy" });
</script>
```

لا تحتوي الصفحة `.vue` على واجهة برمجة تطبيقات للبيانات الوصفية في Nexy: ضع العلامات في تخطيط الجذر. في وضع الخادم، تقوم صفحة `.nexy` بتعيينها، ويكتبها تخطيطها بـ `{{ useMetadata().html() }}`:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## `routeRules` مع `swr` أو `isr`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  routeRules: { "/news": { swr: 60 } },
});
```

تنتقل القاعدة إلى الصفحة، في وضع الخادم:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## Vue المكونات الموجودة في صفحات الخادم

```vue filename="المكونات/Counter.vue"
<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{ start?: number }>();
const count = ref(props.start ?? 0);
</script>

<template>
  <button @click="count++">{{ count }}</button>
</template>
```

في وضع الخادم، يكون المكون عبارة عن جزيرة من صفحة `.nexy`، مثل جزء `<ClientOnly>` من صفحة Nuxt التي يعرضها الخادم، مع توجيه لوقت الترطيب:

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

`src/routes/notfound.vue` يجيب على عناوين URL غير المعروفة في وضع العميل، `notfound.nexy` في وضع الخادم، ويحصل عملاء API على `{"detail": ...}`.

## `runtimeConfig`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  runtimeConfig: { databaseUrl: process.env.DATABASE_URL },
});
```

إعدادات الخادم هي متغيرات البيئة، اقرأ في Python:

```python filename="src/settings.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## الجري

| نوكست | نكسي |
|---|---|
| `npx nuxi init` | `nx new`، القالب `web-fbr-vue` |
| `nuxt dev` | `nx dev` |
| `nuxt build`، ثم `node .output/server/index.mjs` | `nx build`، ثم `nx start` |
| `nuxt generate` | لا يوجد تصدير ثابت: `nx start` يخدم الصفحات |
| `public/` | `public/`، خدم في `/` |

## الخطوات التالية

- [وضع الخادم ووضع العميل](../routing/fbr/modes.md)
- [Vue في نكسي](../views/vue/differences.md)
- [الإجراءات](../guides/actions.md)
- [من Next.js إلى نكسي](nextjs.md)
