# De Nuxt à Nexy

Dans Nexy, un projet Nuxt conserve ses `.vue` pages, mises en page et composants, tandis que les gestionnaires `server/api`, le middleware du serveur et le chargement des données se déplacent vers les Python fichiers à côté d'eux.

Chaque section ci-dessous montre une habitude Nuxt, puis la même chose dans Nexy.

## Choisissez d'abord le mode

| Votre application Nuxt est | Mode Nexy | Les pages sont |
|---|---|---|
| une application avec navigation client | mode client, `useCSR = True` | `.vue` fichiers sous `src/routes/` |
| principalement du contenu, quelques parties interactives | mode serveur, la valeur par défaut | `.nexy` pages avec Vue îles |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useCSR = True
    useAliases = {"@": "src"}
```

`nuxt.config.ts` devient ce fichier. Les sections ci-dessous utilisent le mode client, sauf indication contraire.

## `pages/`

```vue filename="pages/à propos.vue"
<template>
  <h1>About</h1>
</template>
```

```vue filename="src/routes/about.vue"
<template>
  <h1>About</h1>
</template>
```

`pages/index.vue` est `src/routes/index.vue`, `pages/blog/index.vue` est `src/routes/blog/index.vue`.

## Pages dynamiques et `useRoute().params`

```vue filename="pages/blog/[slug].vue"
<script setup lang="ts">
const route = useRoute();
</script>

<template>
  <h1>{{ route.params.slug }}</h1>
</template>
```

Les segments atteignent la page en tant qu'accessoires :

```vue filename="src/routes/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

Dans tout autre composant, `useParams()` de `@nexy/client` les renvoie sous forme de référence calculée. `[...slug].vue` est un fourre-tout, comme dans Nuxt.

## `layouts/default.vue` et `app.vue`

```vue filename="mises en page/par défaut.vue"
<template>
  <header>My app</header>
  <main><slot /></main>
</template>
```

Il n'y a ni `<NuxtLayout>` ni `app.vue` : la racine `layout.vue` est propriétaire du document et enveloppe chaque page, et un `layout.vue` dans un sous-dossier s'y niche.

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

Une disposition nommée, `definePageMeta({ layout: "admin" })`, devient un dossier avec son propre `layout.vue`, ou un groupe de routage tel que `(admin)/layout.vue`.

## `<NuxtLink>` et `navigateTo`

```vue filename="composants/Nav.vue"
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

Les composants ne sont pas importés automatiquement : importez-les là où vous les utilisez.

## `server/api`

```ts filename="serveur/api/items/[id].get.ts"
export default defineEventHandler((event) => {
  const id = Number(getRouterParam(event, "id"));
  return { id };
});
```

Un fichier Python par URL, une fonction par méthode, sans le suffixe `.get` :

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

## `readBody` et validation

```ts filename="serveur/api/items/index.post.ts"
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

## `getQuery` et `createError`

```ts filename="serveur/api/commandes/[id].get.ts"
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

## `useFetch` et `useAsyncData`

```vue filename="pages/utilisateurs.vue"
<script setup lang="ts">
const { data: users } = await useFetch("/api/users");
</script>

<template>
  <ul>
    <li v-for="user in users" :key="user.id">{{ user.name }}</li>
  </ul>
</template>
```

En mode client, la page appelle le gestionnaire depuis le navigateur :

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

En mode serveur, le frontmatter d'une page `.nexy` charge les données pendant que le serveur les restitue :

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

## Mutations : `$fetch` vers une route de serveur

```vue filename="composants/AddTodo.vue"
<script setup lang="ts">
const title = ref("");
const add = () => $fetch("/api/todos", { method: "POST", body: { title: title.value } });
</script>
```

Une action saute l'URL : Nexy génère un client typé à partir de la fonction Python.

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

## Intergiciel serveur

```ts filename="serveur/middleware/app-header.ts"
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

## Middleware de routage

```ts filename="middleware/auth.ts"
export default defineNuxtRouteMiddleware(() => {
  if (!useCookie("session").value) return navigateTo("/login");
});
```

Un `middleware.py` dans le dossier s'exécute sur le serveur, avant la page ou le gestionnaire :

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

## `useHead` et `useSeoMeta`

```vue filename="pages/blog.vue"
<script setup lang="ts">
useSeoMeta({ title: "Blog", description: "Posts about Nexy" });
</script>
```

Une page `.vue` n'a pas d'API de métadonnées dans Nexy : placez les balises dans la mise en page racine. En mode serveur, une page `.nexy` les définit, et sa mise en page les écrit avec `{{ useMetadata().html() }}` :

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## `routeRules` avec `swr` ou `isr`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  routeRules: { "/news": { swr: 60 } },
});
```

La règle se déplace dans la page, en mode serveur :

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## Vue composants dans les pages du serveur

```vue filename="composants/Compteur.vue"
<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{ start?: number }>();
const count = ref(props.start ?? 0);
</script>

<template>
  <button @click="count++">{{ count }}</button>
</template>
```

En mode serveur, le composant est un îlot d'une page `.nexy`, comme une partie `<ClientOnly>` d'une page Nuxt rendue par le serveur, avec une directive indiquant quand il s'hydrate :

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.vue" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

## `error.vue`

```vue filename="erreur.vue"
<script setup lang="ts">
defineProps<{ error: { statusCode: number } }>();
</script>

<template>
  <h1>{{ error.statusCode }}</h1>
</template>
```

`src/routes/notfound.vue` répond aux URL inconnues en mode client, `notfound.nexy` en mode serveur et les clients API obtiennent `{"detail": ...}`.

## `runtimeConfig`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  runtimeConfig: { databaseUrl: process.env.DATABASE_URL },
});
```

Les paramètres du serveur sont des variables d'environnement, lues dans Python :

```python filename="src/settings.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## Courir

| Nuxt | Nexy |
|---|---|
| `npx nuxi init` | `nx new`, modèle `web-fbr-vue` |
| `nuxt dev` | `nx dev` |
| `nuxt build`, puis `node .output/server/index.mjs` | `nx build`, puis `nx start` |
| `nuxt generate` | pas d'export statique : `nx start` sert les pages |
| `public/` | `public/`, servi à `/` |

## Prochaines étapes

- [Mode serveur et mode client](../routing/fbr/modes.md)
- [Vue à Nexy](../views/vue/differences.md)
- [Actions](../guides/actions.md)
- [De Next.js à Nexy](nextjs.md)
