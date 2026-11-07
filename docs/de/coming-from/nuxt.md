# Von Nuxt bis Nexy

In Nexy behält ein Nuxt-Projekt seine `.vue` Seiten, Layouts und Komponenten, während `server/api` Handler, Server-Middleware und Datenladevorgänge in Python Dateien daneben verschoben werden.

Jeder Abschnitt unten zeigt eine Nuxt-Gewohnheit, dann dasselbe in Nexy.

## Wählen Sie zuerst den Modus aus

| Ihre Nuxt-App ist | Nexy-Modus | Seiten sind |
|---|---|---|
| eine App mit Client-Navigation | Client-Modus, `useCSR = True` | `.vue` Dateien unter `src/routes/` |
| größtenteils Inhalt, ein paar interaktive Teile | Servermodus, die Standardeinstellung | `.nexy` Seiten mit Vue Inseln |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useCSR = True
    useAliases = {"@": "src"}
```

`nuxt.config.ts` wird zu dieser Datei. In den folgenden Abschnitten wird der Client-Modus verwendet, sofern nicht anders angegeben.

## `pages/`

```vue filename="Seiten/about.vue"
<template>
  <h1>About</h1>
</template>
```

```vue filename="src/routes/about.vue"
<template>
  <h1>About</h1>
</template>
```

`pages/index.vue` ist `src/routes/index.vue`, `pages/blog/index.vue` ist `src/routes/blog/index.vue`.

## Dynamische Seiten und `useRoute().params`

```vue filename="seiten/blog/[slug].vue"
<script setup lang="ts">
const route = useRoute();
</script>

<template>
  <h1>{{ route.params.slug }}</h1>
</template>
```

Die Segmente gelangen als Requisiten auf die Seite:

```vue filename="src/routes/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

In jeder anderen Komponente gibt `useParams()` von `@nexy/client` sie als berechnete Referenz zurück. `[...slug].vue` ist ein Allheilmittel, wie in Nuxt.

## `layouts/default.vue` und `app.vue`

```vue filename="layouts/default.vue"
<template>
  <header>My app</header>
  <main><slot /></main>
</template>
```

Es gibt kein `<NuxtLayout>` und kein `app.vue`: Der Stamm `layout.vue` ist Eigentümer des Dokuments und umschließt jede Seite, und ein `layout.vue` in einem Unterordner ist darin verschachtelt.

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

Ein benanntes Layout, `definePageMeta({ layout: "admin" })`, wird zu einem Ordner mit seinem eigenen `layout.vue` oder einer Routengruppe wie `(admin)/layout.vue`.

## `<NuxtLink>` und `navigateTo`

```vue filename="Komponenten/Nav.vue"
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

Komponenten werden nicht automatisch importiert: Importieren Sie sie dort, wo Sie sie verwenden.

## `server/api`

```ts filename="server/api/items/[id].get.ts"
export default defineEventHandler((event) => {
  const id = Number(getRouterParam(event, "id"));
  return { id };
});
```

Eine Python-Datei pro URL, eine Funktion pro Methode, ohne das Suffix `.get`:

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

## `readBody` und Validierung

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

## `getQuery` und `createError`

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

## `useFetch` und `useAsyncData`

```vue filename="seiten/users.vue"
<script setup lang="ts">
const { data: users } = await useFetch("/api/users");
</script>

<template>
  <ul>
    <li v-for="user in users" :key="user.id">{{ user.name }}</li>
  </ul>
</template>
```

Im Client-Modus ruft die Seite den Handler vom Browser aus auf:

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

Im Servermodus lädt der Frontmatter einer `.nexy`-Seite die Daten, während der Server sie rendert:

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

## Mutationen: `$fetch` zu einer Serverroute

```vue filename="Komponenten/AddTodo.vue"
<script setup lang="ts">
const title = ref("");
const add = () => $fetch("/api/todos", { method: "POST", body: { title: title.value } });
</script>
```

Eine Aktion überspringt die URL: Nexy generiert einen typisierten Client aus der Funktion Python.

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

## Server-Middleware

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

## Route-Middleware

```ts filename="middleware/auth.ts"
export default defineNuxtRouteMiddleware(() => {
  if (!useCookie("session").value) return navigateTo("/login");
});
```

Ein `middleware.py` im Ordner wird auf dem Server ausgeführt, vor der Seite oder dem Handler:

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

## `useHead` und `useSeoMeta`

```vue filename="seiten/blog.vue"
<script setup lang="ts">
useSeoMeta({ title: "Blog", description: "Posts about Nexy" });
</script>
```

Eine `.vue`-Seite hat in Nexy keine Metadaten-API: Platzieren Sie die Tags im Root-Layout. Im Servermodus werden sie von einer `.nexy`-Seite festgelegt und ihr Layout schreibt sie mit `{{ useMetadata().html() }}`:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## `routeRules` mit `swr` oder `isr`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  routeRules: { "/news": { swr: 60 } },
});
```

Die Regel wird im Servermodus auf die Seite verschoben:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## Vue Komponenten in Serverseiten

```vue filename="Komponenten/Counter.vue"
<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{ start?: number }>();
const count = ref(props.start ?? 0);
</script>

<template>
  <button @click="count++">{{ count }}</button>
</template>
```

Im Servermodus ist die Komponente eine Insel einer `.nexy`-Seite, wie ein `<ClientOnly>`-Teil einer vom Server gerenderten Nuxt-Seite, mit einer Anweisung für den Zeitpunkt der Hydratation:

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

`src/routes/notfound.vue` beantwortet unbekannte URLs im Client-Modus, `notfound.nexy` im Server-Modus und API-Clients erhalten `{"detail": ...}`.

## `runtimeConfig`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  runtimeConfig: { databaseUrl: process.env.DATABASE_URL },
});
```

Servereinstellungen sind Umgebungsvariablen, gelesen in Python:

```python filename="src/settings.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## Laufen

| Nuxt | Nexy |
|---|---|
| `npx nuxi init` | `nx new`, Vorlage `web-fbr-vue` |
| `nuxt dev` | `nx dev` |
| `nuxt build`, dann `node .output/server/index.mjs` | `nx build`, dann `nx start` |
| `nuxt generate` | kein statischer Export: `nx start` stellt die Seiten bereit |
| `public/` | `public/`, zugestellt in `/` |

## Nächste Schritte

- [Servermodus und Clientmodus](../routing/fbr/modes.md)
- [Vue in Nexy](../views/vue/differences.md)
- [Aktionen](../guides/actions.md)
- [Von Next.js zu Nexy](nextjs.md)
