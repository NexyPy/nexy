# नेक्स्ट से नेक्सी तक

Nexy में एक Nuxt प्रोजेक्ट अपने `.vue` पेज, लेआउट और घटकों को रखता है, जबकि `server/api` हैंडलर, सर्वर मिडलवेयर और डेटा लोडिंग उनके बगल में Python फ़ाइलों में चले जाते हैं।

नीचे दिया गया प्रत्येक अनुभाग एक नक्स्ट आदत दिखाता है, फिर नेक्सी में भी वही चीज़।

## सबसे पहले मोड चुनें

| आपका Nuxt ऐप है | नेक्सी मोड | पन्ने हैं |
|---|---|---|
| क्लाइंट नेविगेशन वाला एक ऐप | क्लाइंट मोड, `useCSR = True` | `.vue` के अंतर्गत फ़ाइलें `src/routes/` |
| अधिकतर सामग्री, कुछ इंटरैक्टिव भाग | सर्वर मोड, डिफ़ॉल्ट | `.nexy` Vue द्वीपों वाले पृष्ठ |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useCSR = True
    useAliases = {"@": "src"}
```

`nuxt.config.ts` यह फ़ाइल बन जाती है। नीचे दिए गए अनुभाग क्लाइंट मोड का उपयोग करते हैं जब तक कि वे अन्यथा न कहें।

## `pages/`

```vue filename="पेज/about.vue"
<template>
  <h1>About</h1>
</template>
```

```vue filename="src/routes/about.vue"
<template>
  <h1>About</h1>
</template>
```

`pages/index.vue` है `src/routes/index.vue`, `pages/blog/index.vue` है `src/routes/blog/index.vue`।

## गतिशील पृष्ठ और `useRoute().params`

```vue filename="पेज/ब्लॉग/[स्लग].व्यू"
<script setup lang="ts">
const route = useRoute();
</script>

<template>
  <h1>{{ route.params.slug }}</h1>
</template>
```

खंड पृष्ठ पर प्रॉप्स के रूप में पहुंचते हैं:

```vue filename="src/routes/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

किसी भी अन्य घटक में, `useParams()` से `@nexy/client` उन्हें एक परिकलित रेफरी के रूप में लौटाता है। `[...slug].vue` एक कैच-ऑल है, जैसा कि नक्स्ट में है।

## `layouts/default.vue` और `app.vue`

```vue filename="लेआउट/डिफ़ॉल्ट.व्यू"
<template>
  <header>My app</header>
  <main><slot /></main>
</template>
```

कोई `<NuxtLayout>` और कोई `app.vue` नहीं है: रूट `layout.vue` दस्तावेज़ का मालिक है और हर पृष्ठ को लपेटता है, और एक `layout.vue` उसके अंदर एक सबफ़ोल्डर में रहता है।

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

एक नामित लेआउट, `definePageMeta({ layout: "admin" })`, अपने स्वयं के `layout.vue` के साथ एक फ़ोल्डर बन जाता है, या एक रूट समूह जैसे `(admin)/layout.vue` बन जाता है।

## `<NuxtLink>` और `navigateTo`

```vue filename="घटक/Nav.vue"
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

घटक स्वतः आयातित नहीं होते हैं: उन्हें वहीं आयात करें जहाँ आप उनका उपयोग करते हैं।

## `server/api`

```ts filename="सर्वर/एपीआई/आइटम/[आईडी].get.ts"
export default defineEventHandler((event) => {
  const id = Number(getRouterParam(event, "id"));
  return { id };
});
```

प्रति यूआरएल एक Python फ़ाइल, प्रति विधि एक फ़ंक्शन, बिना `.get` प्रत्यय के:

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

## `readBody` और सत्यापन

```ts filename="सर्वर/एपीआई/आइटम/index.post.ts"
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

## `getQuery` और `createError`

```ts filename="सर्वर/एपीआई/ऑर्डर/[आईडी].get.ts"
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

## `useFetch` और `useAsyncData`

```vue filename="पेज/उपयोगकर्ता.व्यू"
<script setup lang="ts">
const { data: users } = await useFetch("/api/users");
</script>

<template>
  <ul>
    <li v-for="user in users" :key="user.id">{{ user.name }}</li>
  </ul>
</template>
```

क्लाइंट मोड में पेज ब्राउज़र से हैंडलर को कॉल करता है:

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

सर्वर मोड में, `.nexy` पेज का फ्रंटमैटर डेटा लोड करता है जबकि सर्वर इसे प्रस्तुत करता है:

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

## उत्परिवर्तन: `$fetch` एक सर्वर रूट के लिए

```vue filename="घटक/AddTodo.vue"
<script setup lang="ts">
const title = ref("");
const add = () => $fetch("/api/todos", { method: "POST", body: { title: title.value } });
</script>
```

एक क्रिया यूआरएल को छोड़ देती है: नेक्सी Python फ़ंक्शन से एक टाइप किया हुआ क्लाइंट उत्पन्न करता है।

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

## सर्वर मिडलवेयर

```ts filename="सर्वर/मिडलवेयर/ऐप-हेडर.ts"
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

## रूट मिडलवेयर

```ts filename="मिडलवेयर/auth.ts"
export default defineNuxtRouteMiddleware(() => {
  if (!useCookie("session").value) return navigateTo("/login");
});
```

फ़ोल्डर में एक `middleware.py` पेज या हैंडलर से पहले सर्वर पर चलता है:

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

## `useHead` और `useSeoMeta`

```vue filename="पेज/ब्लॉग.व्यू"
<script setup lang="ts">
useSeoMeta({ title: "Blog", description: "Posts about Nexy" });
</script>
```

एक `.vue` पेज में नेक्सी में कोई मेटाडेटा एपीआई नहीं है: टैग को रूट लेआउट में रखें। सर्वर मोड में एक `.nexy` पेज उन्हें सेट करता है, और इसका लेआउट उन्हें `{{ useMetadata().html() }}` के साथ लिखता है:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## `routeRules` के साथ `swr` या `isr`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  routeRules: { "/news": { swr: 60 } },
});
```

नियम सर्वर मोड में पेज में चला जाता है:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## Vue सर्वर पेजों में घटक

```vue filename="घटक/काउंटर.व्यू"
<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{ start?: number }>();
const count = ref(props.start ?? 0);
</script>

<template>
  <button @click="count++">{{ count }}</button>
</template>
```

सर्वर मोड में घटक एक `.nexy` पेज का एक द्वीप है, जैसे सर्वर-रेंडर किए गए नेक्स्ट पेज का एक `<ClientOnly>` भाग, जब यह हाइड्रेट होता है तो एक निर्देश के साथ:

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.vue" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

## `error.vue`

```vue filename="त्रुटि.व्यू"
<script setup lang="ts">
defineProps<{ error: { statusCode: number } }>();
</script>

<template>
  <h1>{{ error.statusCode }}</h1>
</template>
```

`src/routes/notfound.vue` क्लाइंट मोड में अज्ञात यूआरएल का उत्तर देता है, `notfound.nexy` सर्वर मोड में, और एपीआई क्लाइंट को `{"detail": ...}` मिलता है।

## `runtimeConfig`

```ts filename="nuxt.config.ts"
export default defineNuxtConfig({
  runtimeConfig: { databaseUrl: process.env.DATABASE_URL },
});
```

सर्वर सेटिंग्स पर्यावरण चर हैं, Python में पढ़ें:

```python filename="src/settings.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## चल रहा है

| अगला | नेक्सी |
|---|---|
| `npx nuxi init` | `nx new`, टेम्पलेट `web-fbr-vue` |
| `nuxt dev` | `nx dev` |
| `nuxt build`, फिर `node .output/server/index.mjs` | `nx build`, फिर `nx start` |
| `nuxt generate` | कोई स्थिर निर्यात नहीं: `nx start` पृष्ठों पर काम करता है |
| `public/` | `public/`, `/` में सेवा दी गई |

## अगले चरण

- [सर्वर मोड और क्लाइंट मोड](../routing/fbr/modes.md)
- [Vue नेक्सी में](../views/vue/differences.md)
- [क्रियाएँ](../guides/actions.md)
- [से Next.js से नेक्सी](nextjs.md)
