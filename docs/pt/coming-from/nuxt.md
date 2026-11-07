# De Nuxt a Nexy

No Nexy, um projeto Nuxt mantém suas `.vue` páginas, layouts e componentes, enquanto `server/api` manipuladores, middleware de servidor e carregamento de dados são movidos para Python arquivos próximos a eles.

Cada seção abaixo mostra um hábito do Nuxt e a mesma coisa no Nexy.

## Escolha o modo primeiro

| Seu aplicativo Nuxt é | Modo Nexy | As páginas são |
|---|---|---|
| um aplicativo com navegação do cliente | modo cliente, `useCSR = True` | `.vue` arquivos em `src/routes/` |
| principalmente conteúdo, algumas partes interativas | modo de servidor, o padrão | `.nexy` páginas com Vue ilhas |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useCSR = True
    useAliases = {"@": "src"}
```

`nuxt.config.ts` se torna este arquivo. As seções abaixo usam o modo cliente, a menos que seja indicado o contrário.

## `pages/`

```vue filename="páginas/about.vue"
<template>
  <h1>About</h1>
</template>
```

```vue filename="src/rotas/about.vue"
<template>
  <h1>About</h1>
</template>
```

`pages/index.vue` é `src/routes/index.vue`, `pages/blog/index.vue` é `src/routes/blog/index.vue`.

## Páginas dinâmicas e `useRoute().params`

```vue filename="páginas/blog/[slug].vue"
<script setup lang="ts">
const route = useRoute();
</script>

<template>
  <h1>{{ route.params.slug }}</h1>
</template>
```

Os segmentos chegam à página como adereços:

```vue filename="src/rotas/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

Em qualquer outro componente, `useParams()` de `@nexy/client` os retorna como uma referência computada. `[...slug].vue` é abrangente, como em Nuxt.

## `layouts/default.vue` e `app.vue`

```vue filename="layouts/default.vue"
<template>
  <header>My app</header>
  <main><slot /></main>
</template>
```

Não há `<NuxtLayout>` nem `app.vue`: a raiz `layout.vue` possui o documento e agrupa todas as páginas, e um `layout.vue` em uma subpasta se aninha dentro dele.

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

Um layout nomeado, `definePageMeta({ layout: "admin" })`, torna-se uma pasta com seu próprio `layout.vue`, ou um grupo de rotas como `(admin)/layout.vue`.

## `<NuxtLink>` e `navigateTo`

```vue filename="componentes/Nav.vue"
<script setup lang="ts">
const go = () => navigateTo("/dashboard");
</script>

<template>
  <NuxtLink to="/about" active-class="active">About</NuxtLink>
  <button @click="go">Dashboard</button>
</template>
```

```vue filename="src/componentes/Nav.vue"
<script setup lang="ts">
import { Link, useRouter } from "@nexy/client";

const router = useRouter();
</script>

<template>
  <Link href="/about" active-class="active">About</Link>
  <button @click="router.push('/dashboard')">Dashboard</button>
</template>
```

Os componentes não são importados automaticamente: importe-os onde você os utiliza.

## `server/api`

```ts filename="servidor/api/items/[id].get.ts"
export default defineEventHandler((event) => {
  const id = Number(getRouterParam(event, "id"));
  return { id };
});
```

Um arquivo Python por URL, uma função por método, sem o sufixo `.get`:

```python filename="src/rotas/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

## `readBody` e validação

```ts filename="servidor/api/items/index.post.ts"
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

## `getQuery` e `createError`

```ts filename="servidor/api/pedidos/[id].get.ts"
export default defineEventHandler((event) => {
  const id = Number(getRouterParam(event, "id"));
  const { currency = "EUR" } = getQuery(event);
  if (id > 100) throw createError({ statusCode: 404, statusMessage: "No such order" });
  return { id, currency };
});
```

```python filename="src/rotas/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `useFetch` e `useAsyncData`

```vue filename="páginas/usuários.vue"
<script setup lang="ts">
const { data: users } = await useFetch("/api/users");
</script>

<template>
  <ul>
    <li v-for="user in users" :key="user.id">{{ user.name }}</li>
  </ul>
</template>
```

No modo cliente, a página chama o manipulador do navegador:

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

No modo servidor, o frontmatter de uma página `.nexy` carrega os dados enquanto o servidor os renderiza:

```nexy filename="src/rotas/pessoas.nexy"
---
users = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Mutações: `$fetch` para uma rota de servidor

```vue filename="componentes/AddTodo.vue"
<script setup lang="ts">
const title = ref("");
const add = () => $fetch("/api/todos", { method: "POST", body: { title: title.value } });
</script>
```

Uma ação ignora a URL: Nexy gera um cliente digitado a partir da função Python.

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

## Middleware de servidor

```ts filename="servidor/middleware/app-header.ts"
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

## Middleware de rota

```ts filename="middleware/auth.ts"
export default defineNuxtRouteMiddleware(() => {
  if (!useCookie("session").value) return navigateTo("/login");
});
```

Um `middleware.py` na pasta é executado no servidor, antes da página ou do manipulador:

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

## `useHead` e `useSeoMeta`

```vue filename="páginas/blog.vue"
<script setup lang="ts">
useSeoMeta({ title: "Blog", description: "Posts about Nexy" });
</script>
```

Uma página `.vue` não possui API de metadados no Nexy: coloque as tags no layout raiz. No modo servidor, uma página `.nexy` os define, e seu layout os grava com `{{ useMetadata().html() }}`:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## `routeRules` com `swr` ou `isr`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  routeRules: { "/news": { swr: 60 } },
});
```

A regra passa para a página, no modo servidor:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## Vue componentes em páginas do servidor

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

No modo servidor, o componente é uma ilha de uma página `.nexy`, como uma parte `<ClientOnly>` de uma página Nuxt renderizada pelo servidor, com uma diretiva para quando ele hidrata:

```nexy filename="src/rotas/home.nexy"
---
from "@/components/Counter.vue" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

## `error.vue`

```vue filename="erro.vue"
<script setup lang="ts">
defineProps<{ error: { statusCode: number } }>();
</script>

<template>
  <h1>{{ error.statusCode }}</h1>
</template>
```

`src/routes/notfound.vue` responde URLs desconhecidos no modo cliente, `notfound.nexy` no modo servidor e os clientes API obtêm `{"detail": ...}`.

## `runtimeConfig`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  runtimeConfig: { databaseUrl: process.env.DATABASE_URL },
});
```

As configurações do servidor são variáveis de ambiente, leia em Python:

```python filename="src/settings.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## Correndo

| Nuxt | Nexy |
|---|---|
| `npx nuxi init` | `nx new`, modelo `web-fbr-vue` |
| `nuxt dev` | `nx dev` |
| `nuxt build`, então `node .output/server/index.mjs` | `nx build`, então `nx start` |
| `nuxt generate` | sem exportação estática: `nx start` veicula as páginas |
| `public/` | `public/`, servido em `/` |

## Próximas etapas

- [Modo servidor e modo cliente](../routing/fbr/modes.md)
- [Vue em Nexy](../views/vue/differences.md)
- [Ações](../guides/actions.md)
- [De Next.js para Nexy](nextjs.md)
