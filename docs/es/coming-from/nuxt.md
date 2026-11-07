# De Nuxt a Nexy

En Nexy, un proyecto de Nuxt mantiene sus `.vue` páginas, diseños y componentes, mientras que `server/api` controladores, middleware de servidor y carga de datos se mueven a Python archivos junto a ellos.

Cada sección a continuación muestra un hábito de Nuxt y luego lo mismo en Nexy.

## Elige el modo primero

| Tu aplicación Nuxt es | Modo Nexy | Las páginas son |
|---|---|---|
| una aplicación con navegación del cliente | modo cliente, `useCSR = True` | `.vue` archivos en `src/routes/` |
| principalmente contenido, algunas partes interactivas | modo servidor, el predeterminado | `.nexy` páginas con Vue islas |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useCSR = True
    useAliases = {"@": "src"}
```

`nuxt.config.ts` se convierte en este archivo. Las secciones siguientes utilizan el modo cliente a menos que indiquen lo contrario.

## `pages/`

```vue filename="páginas/acerca de.vue"
<template>
  <h1>About</h1>
</template>
```

```vue filename="src/rutas/about.vue"
<template>
  <h1>About</h1>
</template>
```

`pages/index.vue` es `src/routes/index.vue`, `pages/blog/index.vue` es `src/routes/blog/index.vue`.

## Páginas dinámicas y `useRoute().params`

```vue filename="páginas/blog/[slug].vue"
<script setup lang="ts">
const route = useRoute();
</script>

<template>
  <h1>{{ route.params.slug }}</h1>
</template>
```

Los segmentos llegan a la página como accesorios:

```vue filename="src/rutas/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

En cualquier otro componente, `useParams()` de `@nexy/client` los devuelve como una referencia calculada. `[...slug].vue` es un comodín, como en Nuxt.

## `layouts/default.vue` y `app.vue`

```vue filename="diseños/default.vue"
<template>
  <header>My app</header>
  <main><slot /></main>
</template>
```

No hay `<NuxtLayout>` ni `app.vue`: la raíz `layout.vue` posee el documento y envuelve cada página, y un `layout.vue` en una subcarpeta se anida dentro de él.

```vue filename="src/rutas/layout.vue"
<template>
  <html>
    <body>
      <header>My app</header>
      <main><slot /></main>
    </body>
  </html>
</template>
```

Un diseño con nombre, `definePageMeta({ layout: "admin" })`, se convierte en una carpeta con su propio `layout.vue`, o un grupo de rutas como `(admin)/layout.vue`.

## `<NuxtLink>` y `navigateTo`

```vue filename="componentes/Nav.vue"
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

Los componentes no se importan automáticamente: impórtelos donde los utilice.

## `server/api`

```ts filename="servidor/api/items/[id].get.ts"
export default defineEventHandler((event) => {
  const id = Number(getRouterParam(event, "id"));
  return { id };
});
```

Un archivo Python por URL, una función por método, sin el sufijo `.get`:

```python filename="src/rutas/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

## `readBody` y validación

```ts filename="servidor/api/items/index.post.ts"
import { z } from "zod";

const NewItem = z.object({ name: z.string(), price: z.number().positive() });

export default defineEventHandler(async (event) => {
  const item = await readValidatedBody(event, NewItem.parse);
  setResponseStatus(event, 201);
  return item;
});
```

```python filename="src/rutas/api/items/index.py"
from pydantic import BaseModel, Field

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str
    price: float = Field(gt=0)


async def POST(item: NewItem):
    return JSONResponse(item.model_dump(), status_code=201)
```

## `getQuery` y `createError`

```ts filename="servidor/api/pedidos/[id].get.ts"
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

## `useFetch` y `useAsyncData`

```vue filename="páginas/usuarios.vue"
<script setup lang="ts">
const { data: users } = await useFetch("/api/users");
</script>

<template>
  <ul>
    <li v-for="user in users" :key="user.id">{{ user.name }}</li>
  </ul>
</template>
```

En modo cliente, la página llama al controlador desde el navegador:

```python filename="src/rutas/api/usuarios.py"
async def GET():
    return [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
```

```vue filename="src/rutas/usuarios.vue"
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

En modo servidor, el front-matter de una página `.nexy` carga los datos mientras el servidor los procesa:

```nexy filename="src/rutas/personas.nexy"
---
users = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Mutaciones: `$fetch` a una ruta de servidor

```vue filename="componentes/AddTodo.vue"
<script setup lang="ts">
const title = ref("");
const add = () => $fetch("/api/todos", { method: "POST", body: { title: title.value } });
</script>
```

Una acción omite la URL: Nexy genera un cliente escrito a partir de la función Python.

```python filename="src/acciones/todos.py"
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

## Middleware de servidor

```ts filename="servidor/middleware/app-header.ts"
export default defineEventHandler((event) => {
  setResponseHeader(event, "x-app", "demo");
});
```

```python filename="src/rutas/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

## Middleware de ruta

```ts filename="middleware/auth.ts"
export default defineNuxtRouteMiddleware(() => {
  if (!useCookie("session").value) return navigateTo("/login");
});
```

Un `middleware.py` en la carpeta se ejecuta en el servidor, antes de la página o el controlador:

```python filename="src/rutas/dashboard/middleware.py"
from nexy.http import RedirectResponse, Request


async def middleware(request: Request, call_next):
    if "session" not in request.cookies:
        return RedirectResponse("/login", status_code=307)
    return await call_next(request)
```

```python filename="src/rutas/dashboard/stats.py"
async def GET():
    return {"visits": 12}
```

## `useHead` y `useSeoMeta`

```vue filename="páginas/blog.vue"
<script setup lang="ts">
useSeoMeta({ title: "Blog", description: "Posts about Nexy" });
</script>
```

Una página `.vue` no tiene API de metadatos en Nexy: coloque las etiquetas en el diseño raíz. En modo servidor una página `.nexy` los configura, y su diseño los escribe con `{{ useMetadata().html() }}`:

```nexy filename="src/rutas/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## `routeRules` con `swr` o `isr`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  routeRules: { "/news": { swr: 60 } },
});
```

La regla pasa a la página, en modo servidor:

```nexy filename="src/rutas/noticias.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## Vue componentes en páginas del servidor

```vue filename="componentes/Counter.vue"
<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{ start?: number }>();
const count = ref(props.start ?? 0);
</script>

<template>
  <button @click="count++">{{ count }}</button>
</template>
```

En modo servidor, el componente es una isla de una página `.nexy`, como una `<ClientOnly>` parte de una página Nuxt renderizada por el servidor, con una directiva para cuando se hidrata:

```nexy filename="src/rutas/home.nexy"
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

`src/routes/notfound.vue` responde URL desconocidas en modo cliente, `notfound.nexy` en modo servidor y los clientes API obtienen `{"detail": ...}`.

## `runtimeConfig`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  runtimeConfig: { databaseUrl: process.env.DATABASE_URL },
});
```

La configuración del servidor son variables de entorno, lea en Python:

```python filename="src/configuración.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## corriendo

| Nuxt | nexy |
|---|---|
| `npx nuxi init` | `nx new`, plantilla `web-fbr-vue` |
| `nuxt dev` | `nx dev` |
| `nuxt build`, luego `node .output/server/index.mjs` | `nx build`, luego `nx start` |
| `nuxt generate` | sin exportación estática: `nx start` sirve las páginas |
| `public/` | `public/`, servido en `/` |

## Próximos pasos

- [Modo servidor y modo cliente](../routing/fbr/modes.md)
- [Vue en Nexy](../views/vue/differences.md)
- [Acciones](../guides/actions.md)
- [De Next.js a Nexy](nextjs.md)
