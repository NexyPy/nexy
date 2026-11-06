# SvelteKit से Nexy तक

नेक्सी में एक SvelteKit प्रोजेक्ट अपने Svelte पृष्ठों और लेआउट को सादे `.svelte` फ़ाइलों के रूप में रखता है, जबकि `+server.ts`, `+page.server.ts` लोड होता है, क्रियाएँ बनाता है और हुक उनके बगल में Python फ़ाइलों में चले जाते हैं।

नीचे दिया गया प्रत्येक अनुभाग SvelteKit आदत दिखाता है, फिर Nexy में भी यही चीज़ दिखाई देती है।

## सबसे पहले मोड चुनें

| आपका SvelteKit ऐप है | नेक्सी मोड | पन्ने हैं |
|---|---|---|
| क्लाइंट नेविगेशन वाला एक ऐप | क्लाइंट मोड, `useCSR = True` | `.svelte` `src/routes/` के अंतर्गत फ़ाइलें |
| अधिकतर सामग्री, कुछ इंटरैक्टिव भाग | सर्वर मोड, डिफ़ॉल्ट | `.nexy` Svelte द्वीपों वाले पृष्ठ |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useCSR = True
    useAliases = {"@": "src"}
```

नीचे दिए गए अनुभाग क्लाइंट मोड का उपयोग करते हैं जब तक कि वे अन्यथा न कहें।

## `+page.svelte`

```svelte filename="src/routes/about/+page.svelte"
<h1>About</h1>
```

पेज फ़ाइल ही है, जिसका नाम उसके URL के नाम पर रखा गया है:

```svelte filename="src/routes/about.svelte"
<h1>About</h1>
```

`src/routes/+page.svelte` `src/routes/index.svelte` है।

## गतिशील मार्ग और `params`

```svelte filename="src/routes/blog/[slug]/+page.svelte"
<script lang="ts">
  import { page } from "$app/state";
</script>

<h1>{page.params.slug}</h1>
```

खंड पृष्ठ पर प्रॉप्स के रूप में पहुंचते हैं:

```svelte filename="src/routes/blog/[slug].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

किसी भी अन्य घटक में, `@nexy/client` का `params` स्टोर उन्हें रखता है: `$params.slug`। `[...rest]` और `(group)` फ़ोल्डर SvelteKit की तरह काम करते हैं।

## `+layout.svelte`

```svelte filename="src/routes/+layout.svelte"
<script lang="ts">
  let { children } = $props();
</script>

<header>My app</header>
<main>{@render children()}</main>
```

कोई `app.html` नहीं है: मूल `layout.svelte` दस्तावेज़ का स्वामी है।

```svelte filename="src/routes/layout.svelte"
<script lang="ts">
  import type { Snippet } from "svelte";
  let { children }: { children?: Snippet } = $props();
</script>

<html>
  <body>
    <header>My app</header>
    <main>{@render children?.()}</main>
  </body>
</html>
```

## `+server.ts`

```ts filename="src/routes/api/items/[id]/+server.ts"
import { json } from "@sveltejs/kit";

export function GET({ params }) {
  return json({ id: Number(params.id) });
}
```

वही `GET` निर्यात, Python में:

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
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

## `error()`

```ts filename="src/routes/api/orders/[id]/+server.ts"
import { error, json } from "@sveltejs/kit";

export function GET({ params, url }) {
  if (Number(params.id) > 100) error(404, "No such order");
  return json({ id: Number(params.id), currency: url.searchParams.get("currency") ?? "EUR" });
}
```

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `load` में `+page.server.ts`

```ts filename="src/routes/users/+page.server.ts"
export async function load() {
  return { users: await db.user.findMany() };
}
```

```svelte filename="src/routes/users/+page.svelte"
<script lang="ts">
  let { data } = $props();
</script>

<ul>
  {#each data.users as user (user.id)}
    <li>{user.name}</li>
  {/each}
</ul>
```

क्लाइंट मोड में पेज हैंडलर से उसका डेटा मांगता है:

```python filename="src/routes/api/users.py"
async def GET():
    return [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
```

```svelte filename="src/routes/users.svelte"
<script lang="ts">
  let users = $state<{ id: number; name: string }[]>([]);

  $effect(() => {
    fetch("/api/users").then((response) => response.json()).then((list) => (users = list));
  });
</script>

<ul>
  {#each users as user (user.id)}
    <li>{user.name}</li>
  {/each}
</ul>
```

सर्वर मोड में `.nexy` पेज का फ्रंटमैटर `load` फ़ंक्शन होता है, और यह तब चलता है जब सर्वर प्रस्तुत करता है:

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

## फॉर्म क्रियाएं और `use:enhance`

```ts filename="src/routes/todos/+page.server.ts"
export const actions = {
  default: async ({ request }) => {
    const data = await request.formData();
    await db.todo.create({ title: data.get("title") });
  },
};
```

```svelte filename="src/routes/todos/+page.svelte"
<script lang="ts">
  import { enhance } from "$app/forms";
</script>

<form method="POST" use:enhance>
  <input name="title" />
  <button>Add</button>
</form>
```

एक क्रिया एक जेनरेटेड, टाइप किए गए क्लाइंट के साथ एक Python फ़ंक्शन है:

```python filename="src/actions/todos.py"
from pydantic import BaseModel

from nexy.decorators import Action, revalidate


class Todo(BaseModel):
    title: str
    done: bool = False


@Action
async def add_todo(title: str) -> Todo:
    revalidate("/todos")
    return Todo(title=title)
```

```svelte filename="src/routes/todos.svelte"
<script lang="ts">
  import { useAction } from "@nexy/client";
  import { add_todo } from "@nexy/actions";

  let title = $state("");
  const save = useAction(add_todo, { onSuccess: () => (title = "") });
</script>

<form onsubmit={(e) => { e.preventDefault(); save.run({ title }); }}>
  <input bind:value={title} />
  <button disabled={$save.pending}>Add</button>
</form>
```

`revalidate("/todos")` `invalidateAll()` की भूमिका निभाता है: पृष्ठ स्वयं को फिर से प्राप्त करता है।

## `goto`, लिंक और `$app/state`

```svelte filename="src/lib/Nav.svelte"
<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/state";
</script>

<a href="/about">About</a>
<span>{page.url.pathname}</span>
<button onclick={() => goto("/dashboard")}>Dashboard</button>
```

```svelte filename="src/components/Nav.svelte"
<script lang="ts">
  import Link from "@nexy/Link.svelte";
  import { pathname, router } from "@nexy/client";
</script>

<Link href="/about" activeClass="active">About</Link>
<span>{$pathname}</span>
<button onclick={() => router.push("/dashboard")}>Dashboard</button>
```

## `hooks.server.ts`

```ts filename="src/hooks.server.ts"
export async function handle({ event, resolve }) {
  if (event.url.pathname.startsWith("/dashboard") && !event.cookies.get("session")) {
    return new Response(null, { status: 307, headers: { location: "/login" } });
  }
  const response = await resolve(event);
  response.headers.set("x-app", "demo");
  return response;
}
```

पथ परीक्षण फ़ोल्डर है. एक रूट `middleware.py` सब कुछ लपेटता है, एक `dashboard/middleware.py` केवल उसके नीचे के मार्गों को:

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

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

## `prerender` और `entries`

```ts filename="src/routes/blog/[slug]/+page.ts"
export const prerender = true;

export function entries() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

प्रति मान एक पूर्व-प्रदत्त दस्तावेज़ के लिए पृष्ठ से `getStaticParams` निर्यात करें:

```svelte filename="src/routes/posts/[स्लग].svelte"
<script lang="ts" module>
  export function getStaticParams() {
    return [{ slug: "hello" }, { slug: "world" }];
  }
</script>

<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

सर्वर मोड में, `revalidate = 60` एक `.nexy` पेज के फ्रंटमैटर में इसके बजाय इसे प्रति यूआरएल कैश करता है:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## `<svelte:head>`

```svelte filename="src/routes/blog/+page.svelte"
<svelte:head>
  <title>Blog</title>
</svelte:head>
```

क्लाइंट मोड में, टैग को रूट `layout.svelte` में लिखें। सर्वर मोड में एक `.nexy` पेज उन्हें सेट करता है, और इसका लेआउट उन्हें `{{ useMetadata().html() }}` के साथ लिखता है:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## Svelte सर्वर पेजों में घटक

```svelte filename="src/components/Counter.svelte"
<script lang="ts">
  let { start = 0 }: { start?: number } = $props();
  let count = $state(start);
</script>

<button onclick={() => count++}>{count}</button>
```

सर्वर मोड में घटक एक `.nexy` पृष्ठ का एक द्वीप है:

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.svelte" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

## `+error.svelte`

`src/routes/notfound.svelte` क्लाइंट मोड में अज्ञात यूआरएल का उत्तर देता है, `notfound.nexy` सर्वर मोड में, और एपीआई क्लाइंट को `{"detail": ...}` मिलता है।

## `$env/static/private`

```ts filename="src/lib/server/db.ts"
import { DATABASE_URL } from "$env/static/private";
```

```python filename="src/settings.py"
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## चल रहा है

| स्वेलटेकिट | नेक्सी |
|---|---|
| `npx sv create` | `nx new`, टेम्पलेट `web-fbr-svelte` |
| `vite dev` | `nx dev` |
| `vite build` एक एडाप्टर के साथ, फिर `node build` | `nx build`, फिर `nx start` |
| `static/` | `public/`, `/` में सेवा दी गई |
| `src/lib/` और `$lib` | `src/components/` और `@` |

## अगले चरण

- [सर्वर मोड और क्लाइंट मोड](../routing/fbr/modes.md)
- [Svelte नेक्सी में](../views/svelte/differences.md)
- [क्रियाएँ](../guides/actions.md)
- [नेक्सट से नेक्सी तक](nuxt.md)
