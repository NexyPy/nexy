# Dari Nuxt hingga Nexy

Di Nexy, proyek Nuxt menyimpan `.vue` halaman, tata letak, dan komponennya, sementara `server/api` penangan, middleware server, dan pemuatan data berpindah ke file Python di sebelahnya.

Setiap bagian di bawah ini menunjukkan kebiasaan Nuxt, lalu hal yang sama di Nexy.

## Pilih modenya terlebih dahulu

| Aplikasi Nuxt Anda adalah | Modus Nexy | Halaman adalah |
|---|---|---|
| sebuah aplikasi dengan navigasi klien | mode klien, `useCSR = True` | `.vue` file di bawah `src/routes/` |
| sebagian besar konten, beberapa bagian interaktif | mode server, default | `.nexy` halaman dengan Vue pulau |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useCSR = True
    useAliases = {"@": "src"}
```

`nuxt.config.ts` menjadi file ini. Bagian di bawah ini menggunakan mode klien kecuali dinyatakan lain.

## `pages/`

```vue filename="halaman/tentang.vue"
<template>
  <h1>About</h1>
</template>
```

```vue filename="src/rute/tentang.vue"
<template>
  <h1>About</h1>
</template>
```

`pages/index.vue` adalah `src/routes/index.vue`, `pages/blog/index.vue` adalah `src/routes/blog/index.vue`.

## Halaman dinamis dan `useRoute().params`

```vue filename="halaman/blog/[siput].vue"
<script setup lang="ts">
const route = useRoute();
</script>

<template>
  <h1>{{ route.params.slug }}</h1>
</template>
```

Segmen mencapai halaman sebagai alat peraga:

```vue filename="src/rute/blog/[siput].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

Di komponen lainnya, `useParams()` dari `@nexy/client` mengembalikannya sebagai referensi yang dihitung. `[...slug].vue` bersifat universal, seperti di Nuxt.

## `layouts/default.vue` dan `app.vue`

```vue filename="tata letak/default.vue"
<template>
  <header>My app</header>
  <main><slot /></main>
</template>
```

Tidak ada `<NuxtLayout>` dan tidak ada `app.vue`: root `layout.vue` memiliki dokumen dan membungkus setiap halaman, dan `layout.vue` dalam subfolder bersarang di dalamnya.

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

Tata letak bernama, `definePageMeta({ layout: "admin" })`, menjadi folder dengan `layout.vue` miliknya sendiri, atau grup rute seperti `(admin)/layout.vue`.

## `<NuxtLink>` dan `navigateTo`

```vue filename="komponen/Nav.vue"
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

Komponen tidak diimpor secara otomatis: imporlah komponen tersebut ke tempat Anda menggunakannya.

## `server/api`

```ts filename="server/api/item/[id].get.ts"
export default defineEventHandler((event) => {
  const id = Number(getRouterParam(event, "id"));
  return { id };
});
```

Satu file Python per URL, satu fungsi per metode, tanpa akhiran `.get`:

```python filename="src/routes/api/item/[id].py"
async def GET(id: int):
    return {"id": id}
```

## `readBody` dan validasi

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

## `getQuery` dan `createError`

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

## `useFetch` dan `useAsyncData`

```vue filename="halaman/pengguna.vue"
<script setup lang="ts">
const { data: users } = await useFetch("/api/users");
</script>

<template>
  <ul>
    <li v-for="user in users" :key="user.id">{{ user.name }}</li>
  </ul>
</template>
```

Dalam mode klien, halaman memanggil pengendali dari browser:

```python filename="src/routes/api/users.py"
async def GET():
    return [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
```

```vue filename="src/rute/pengguna.vue"
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

Dalam mode server, frontmatter halaman `.nexy` memuat data saat server merendernya:

```nexy filename="src/rute/orang.nexy"
---
users = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Mutasi: `$fetch` ke rute server

```vue filename="komponen/AddTodo.vue"
<script setup lang="ts">
const title = ref("");
const add = () => $fetch("/api/todos", { method: "POST", body: { title: title.value } });
</script>
```

Suatu tindakan melewatkan URL: Nexy menghasilkan klien yang diketik dari fungsi Python.

```python filename="src/aksi/todos.py"
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

## Perangkat tengah server

```ts filename="server/middleware/app-header.ts"
export default defineEventHandler((event) => {
  setResponseHeader(event, "x-app", "demo");
});
```

```python filename="src/rute/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Middleware rute

```ts filename="middleware/auth.ts"
export default defineNuxtRouteMiddleware(() => {
  if (!useCookie("session").value) return navigateTo("/login");
});
```

A `middleware.py` dalam folder berjalan di server, sebelum halaman atau pengendali:

```python filename="src/routes/dashboard/middleware.py"
from nexy.http import RedirectResponse, Request


async def middleware(request: Request, call_next):
    if "session" not in request.cookies:
        return RedirectResponse("/login", status_code=307)
    return await call_next(request)
```

```python filename="src/route/dashboard/stats.py"
async def GET():
    return {"visits": 12}
```

## `useHead` dan `useSeoMeta`

```vue filename="halaman/blog.vue"
<script setup lang="ts">
useSeoMeta({ title: "Blog", description: "Posts about Nexy" });
</script>
```

Halaman `.vue` tidak memiliki API metadata di Nexy: letakkan tag di tata letak root. Dalam mode server, halaman `.nexy` mengaturnya, dan tata letaknya menuliskannya dengan `{{ useMetadata().html() }}`:

```nexy filename="src/rute/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## `routeRules` dengan `swr` atau `isr`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  routeRules: { "/news": { swr: 60 } },
});
```

Aturan berpindah ke halaman, dalam mode server:

```nexy filename="src/rute/berita.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## Vue komponen di halaman server

```vue filename="komponen/Counter.vue"
<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{ start?: number }>();
const count = ref(props.start ?? 0);
</script>

<template>
  <button @click="count++">{{ count }}</button>
</template>
```

Dalam mode server, komponennya adalah sebuah pulau dari halaman `.nexy`, seperti bagian `<ClientOnly>` dari halaman Nuxt yang dirender oleh server, dengan arahan kapan komponen tersebut terhidrasi:

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

`src/routes/notfound.vue` menjawab URL yang tidak diketahui dalam mode klien, `notfound.nexy` dalam mode server, dan klien API mendapatkan `{"detail": ...}`.

## `runtimeConfig`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  runtimeConfig: { databaseUrl: process.env.DATABASE_URL },
});
```

Pengaturan server adalah variabel lingkungan, baca di Python:

```python filename="src/pengaturan.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## Berlari

| Selanjutnya | Nexy |
|---|---|
| `npx nuxi init` | `nx new`, templat `web-fbr-vue` |
| `nuxt dev` | `nx dev` |
| `nuxt build`, lalu `node .output/server/index.mjs` | `nx build`, lalu `nx start` |
| `nuxt generate` | tidak ada ekspor statis: `nx start` menyajikan halaman |
| `public/` | `public/`, bertugas di `/` |

## Langkah selanjutnya

- [Mode server dan mode klien](../routing/fbr/modes.md)
- [Vue di Nexy](../views/vue/differences.md)
- [Tindakan](../guides/actions.md)
- [Dari Next.js hingga Nexy](nextjs.md)
