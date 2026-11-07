# Astro থেকে নেক্সি পর্যন্ত

একটি Nexy `.nexy` পৃষ্ঠা হল একটি Astro পৃষ্ঠা যার Python `---` ফ্রন্টম্যাটারে TypeScript এর পরিবর্তে: একই সার্ভার-প্রথম এইচটিএমএল, একই দ্বীপ এবং `client:*` নির্দেশাবলী, প্রতিটি অনুরোধে রেন্ডার করা হয়।

নীচের প্রতিটি বিভাগ একটি Astro অভ্যাস দেখায়, তারপর Nexy তে একই জিনিস।

## একটি পাতা

```astro filename="src/pages/about.astro"
---
const title = "About";
---
<h1>{title}</h1>
```

ফ্রন্ট ম্যাটার হল Python এবং টেমপ্লেট হল Jinja2:

```nexy filename="src/routes/about.nexy"
---
title = "About"
---
<h1>{{ title }}</h1>
```

`src/pages/` হল `src/routes/`, এবং `index.astro` হল `index.nexy`।

## লুপ এবং শর্ত

```astro filename="src/pages/users.astro"
---
const users = [{ name: "Ada", admin: true }, { name: "Alan", admin: false }];
---
<ul>
  {users.map((user) => <li>{user.name}{user.admin && <strong> admin</strong>}</li>)}
</ul>
```

```nexy filename="src/routes/users.nexy"
---
users = [{"name": "Ada", "admin": True}, {"name": "Alan", "admin": False}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}{% if user.admin %}<strong> admin</strong>{% endif %}</li>
  {% endfor %}
</ul>
```

> [!WARNING]
> Astro প্রতি `{value}` থেকে পালিয়ে যায়। `.nexy` টেমপ্লেটগুলি করে না: একজন দর্শক `{{ value | e }}` দিয়ে যা টাইপ করেছেন তা এড়িয়ে যান।

## উপাদান এবং `Astro.props`

```astro filename="src/components/Card.astro"
---
const { title, tone = "neutral" } = Astro.props;
---
<article class={`card card-${tone}`}>
  <h2>{title}</h2>
  <slot />
</article>
```

প্রপস `prop[...]` দিয়ে ঘোষণা করা হয়, একটি ডিফল্ট একটি Python ডিফল্ট, এবং `<slot />` হল `<Slot />`:

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
tone: prop[str] = "neutral"
---
<article class="card card-{{ tone }}">
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/routes/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest" tone="warm">
  <p>This week</p>
</Card>
```

`@` হল `src/`: `nx new` লিখেছেন `useAliases = {"@": "src"}` `nexyconfig.py`।

## বিন্যাস

```astro filename="src/layouts/Base.astro"
---
const { title } = Astro.props;
---
<html>
  <head><title>{title}</title></head>
  <body><slot /></body>
</html>
```

```astro filename="src/pages/about.astro"
---
import Base from "../layouts/Base.astro";
---
<Base title="About"><h1>About</h1></Base>
```

একটি পৃষ্ঠা তার বিন্যাস আমদানি করে না: এটির উপরে নিকটতম `layout.nexy` এটিকে মোড়ানো, এবং মূলটি নথিটির মালিক।

```nexy filename="src/routes/layout.nexy"
---
from nexy import useMetadata

children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <head>{{ useMetadata().html() }}</head>
  <body>{{ children | safe }}</body>
</html>
```

## শিরোনাম এবং মেটা ট্যাগ

লেআউটের `title` প্রপটি পৃষ্ঠায় `metadata` হয়ে যায়, যা `useMetadata().html()` উপরের লেআউটের `<head>`-এ লিখেছেন:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## গতিশীল রুট এবং `getStaticPaths`

```astro filename="src/pages/posts/[slug].astro"
---
export function getStaticPaths() {
  return [
    { params: { slug: "hello" }, props: { title: "Hello" } },
    { params: { slug: "world" }, props: { title: "World" } },
  ];
}
const { title } = Astro.props;
---
<h1>{title}</h1>
```

একটি গতিশীল `.nexy` পৃষ্ঠা অনুরোধে রেন্ডার হয়, তাই পাথের কোনো তালিকা নেই: সেগমেন্টটি একটি প্রপ, এবং একটি অজানা একটি `404`।

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello", "world": "World"}

slug: prop[str]
if slug not in POSTS:
    notFound()
title = POSTS[slug]
---
<h1>{{ title }}</h1>
```

`[...path].astro` হল `[...path].nexy`।

## দ্বীপপুঞ্জ এবং `client:*`

```astro filename="src/pages/index.astro"
---
import Counter from "../components/Counter.tsx";
---
<h1>Static heading</h1>
<Counter start={3} client:visible />
```

নির্দেশিকাটি একই মান সহ একটি `directive` বৈশিষ্ট্য হয়ে যায়:

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

| Astro | নেক্সি |
|---|---|
| `client:load` | `directive="client:load"`, বা কোন নির্দেশনা নেই |
| `client:idle` | `directive="client:idle"` |
| `client:visible` | `directive="client:visible"` |
| `client:media="(min-width: 768px)"` | `directive="client:media" media="(min-width: 768px)"` |
| `client:only="react"` | গৃহীত, কিন্তু কখনই হাইড্রেট হয় না: ব্যবহার `client:load` |

কাঠামো `nexyconfig.py`-এ একবার সেট করা হয়, এবং একটি প্রকল্প একটি ব্যবহার করে:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

## Markdown পৃষ্ঠা

```md filename="src/pages/changelog.md"
---
layout: ../layouts/Base.astro
---
# Changelog
```

`src/routes/` এর অধীনে একটি `.md` ফাইল হল একটি পৃষ্ঠা, যা `layout:` কী ছাড়াই নিকটতম লেআউটে মোড়ানো হয়:

```md filename="src/routes/changelog.md"
# Changelog

Version 2.2 is out.
```

`.mdx` পৃষ্ঠাগুলিও কাজ করে, React বা Preact কাঠামো হিসাবে। [Markdown এবং MDX](../views/nexy/markdown.md) দেখুন।

## এপিআই শেষ পয়েন্ট

```ts filename="src/pages/api/items/[id].ts"
export function GET({ params }) {
  return Response.json({ id: Number(params.id) });
}
```

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

একটি বডি একটি Pydantic মডেল, ফাংশন চালানোর আগে যাচাই করা হয়:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## `Astro.redirect`, `Astro.cookies` এবং `Astro.url`

```astro filename="src/pages/account.astro"
---
const theme = Astro.cookies.get("theme")?.value ?? "light";
if (!Astro.cookies.has("session")) return Astro.redirect("/login");
const page = Astro.url.searchParams.get("page") ?? "1";
---
<p>{theme} theme, page {page}</p>
```

একই রিডগুলি হুক, এবং পুনঃনির্দেশ একটি ফাংশন:

```nexy filename="src/routes/account.nexy"
---
from nexy import redirect, useCookies, useSearchParams

cookies = useCookies()
if "session" not in cookies:
    redirect("/login")
theme = cookies.get("theme", "light")
page = useSearchParams().get("page", "1")
---
<p>{{ theme }} theme, page {{ page }}</p>
```

## মিডলওয়্যার

```ts filename="src/midleware.ts"
export function onRequest(context, next) {
  return next().then((response) => {
    response.headers.set("x-app", "demo");
    return response;
  });
}
```

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

একটি সাবফোল্ডারে একটি `middleware.py` শুধুমাত্র এটির নীচের রুটগুলিকে মোড়ানো হয়, যা `onRequest` এর ভিতরে পাথ চেকগুলিকে প্রতিস্থাপন করে।

## Astro কর্ম

```ts filename="src/actions/index.ts"
import { defineAction } from "astro:actions";
import { z } from "astro:schema";

export const server = {
  addNote: defineAction({
    accept: "form",
    input: z.object({ title: z.string() }),
    handler: async ({ title }) => ({ title }),
  }),
};
```

```astro filename="src/pages/notes.astro"
---
import { actions } from "astro:actions";
---
<form method="POST" action={actions.addNote}>
  <input name="title" />
  <button>Add</button>
</form>
```

একটি কর্ম হল একটি Python ফাংশন `src/actions/`; একটি ফর্ম তার পথে পোস্ট করে:

```python filename="src/actions/notes.py"
from nexy.decorators import Action

NOTES: list[str] = []


@Action
async def add_note(title: str) -> None:
    NOTES.append(title)
```

```nexy filename="src/routes/notes.nexy"
---
from src.actions.notes import NOTES
---
<form method="post" action="{{ __actions_path['add_note'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
<ul>
  {% for note in NOTES %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

একটি দ্বীপ থেকে, `useAction(add_note)` in `@nexy/client` টাইপ করা ইনপুট সহ একই ফাংশন কল করে।

## `<Image />`

```astro
---
import { Image } from "astro:assets";
import logo from "../assets/logo.png";
---
<Image src={logo} alt="Logo" width={128} height={32} />
```

```nexy filename="src/routes/brand.nexy"
---
from nexy import Image
---
<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

## `404.astro`

```astro filename="src/pages/404.astro"
<h1>Not found</h1>
```

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

API ক্লায়েন্টরা এখনও `{"detail": "Not Found"}` পান।

## স্ট্যাটিক আউটপুট এবং অন-ডিমান্ড রেন্ডারিং

Astro ডিফল্টরূপে স্ট্যাটিক HTML তৈরি করে এবং `output: "server"` বা `export const prerender = false` এর সাথে চাহিদা অনুযায়ী রেন্ডার করে। Nexy অনুরোধে প্রতিটি পৃষ্ঠা রেন্ডার করে এবং প্রতি ইউআরএলে আপনি যেগুলি বেছে নেন তা ক্যাশ করে:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

কোন স্ট্যাটিক এক্সপোর্ট নেই: `nx start` সাইটে পরিবেশন করে। [রেন্ডারিং](../rendering/README.md) দেখুন।

## চলছে

| Astro | নেক্সি |
|---|---|
| `npm create astro@latest` | `nx new` |
| `astro dev` | `nx dev` |
| `astro build` এবং `astro preview` | `nx build`, তারপর `nx start` |
| `public/` | `public/`, `/` এ পরিবেশিত |
| `astro add react` | `nx new` একটি কাঠামো সহ, বা `useFF = react()` |

## পরবর্তী পদক্ষেপ

- [.nexy ফাইল](../views/nexy/README.md)
- [দ্বীপপুঞ্জ](../rendering/islands.md)
- [Markdown এবং MDX](../views/nexy/markdown.md)
- [থেকে Next.js নেক্সি থেকে](nextjs.md)
