# Astro سے Nexy تک

ایک Nexy `.nexy` صفحہ ایک Astro صفحہ ہوتا ہے جس کے Python کے `---` فرنٹ میٹر میں TypeScript کی بجائے: وہی سرور-پہلا ایچ ٹی ایم ایل، وہی جزیرے اور `client:*` ہدایات، ہر درخواست پر پیش کی جاتی ہیں۔

ذیل میں ہر سیکشن ایک Astro عادت دکھاتا ہے، پھر Nexy میں وہی چیز۔

## ایک صفحہ

```astro filename="src/pages/about.astro"
---
const title = "About";
---
<h1>{title}</h1>
```

فرنٹ میٹر ہے Python اور سانچہ ہے Jinja2:

```nexy filename="src/routes/about.nexy"
---
title = "About"
---
<h1>{{ title }}</h1>
```

`src/pages/` ہے `src/routes/`، اور `index.astro` ہے `index.nexy`۔

## لوپس اور حالات

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
> Astro ہر `{value}` سے بچ جاتا ہے۔ `.nexy` ٹیمپلیٹس ایسا نہیں کرتے: ایک وزیٹر `{{ value | e }}` کے ساتھ جو ٹائپ کرتا ہے اس سے بچ جاتا ہے۔

## اجزاء اور `Astro.props`

```astro filename="src/components/Card.astro"
---
const { title, tone = "neutral" } = Astro.props;
---
<article class={`card card-${tone}`}>
  <h2>{title}</h2>
  <slot />
</article>
```

پرپس کا اعلان `prop[...]` کے ساتھ کیا جاتا ہے، ڈیفالٹ ایک Python ڈیفالٹ ہوتا ہے، اور `<slot />` ہوتا ہے `<Slot />`:

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

`@` ہے `src/`: `nx new` `nexyconfig.py` میں `useAliases = {"@": "src"}` لکھتے ہیں۔

## لے آؤٹ

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

ایک صفحہ اپنی ترتیب کو درآمد نہیں کرتا: اس کے اوپر قریب ترین `layout.nexy` اسے لپیٹ دیتا ہے، اور جڑ والا دستاویز کا مالک ہوتا ہے۔

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

## عنوان اور میٹا ٹیگز

صفحہ میں ترتیب کا `title` پروپ `metadata` بن جاتا ہے، جسے `useMetadata().html()` اوپر کی ترتیب کے `<head>` میں لکھتا ہے:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## متحرک راستے اور `getStaticPaths`

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

ایک متحرک `.nexy` صفحہ درخواست پر پیش کرتا ہے، اس لیے راستوں کی کوئی فہرست نہیں ہے: سیگمنٹ ایک سہارا ہے، اور ایک نامعلوم ایک `404` ہے۔

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

`[...path].astro` ہے `[...path].nexy`۔

## جزائر اور `client:*`

```astro filename="src/pages/index.astro"
---
import Counter from "../components/Counter.tsx";
---
<h1>Static heading</h1>
<Counter start={3} client:visible />
```

ہدایت ایک `directive` وصف بن جاتی ہے، اسی قدروں کے ساتھ:

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

| Astro | نیکسی |
|---|---|
| `client:load` | `directive="client:load"`، یا کوئی ہدایت نہیں۔ |
| `client:idle` | `directive="client:idle"` |
| `client:visible` | `directive="client:visible"` |
| `client:media="(min-width: 768px)"` | `directive="client:media" media="(min-width: 768px)"` |
| `client:only="react"` | قبول کیا جاتا ہے، لیکن کبھی ہائیڈریٹ نہیں ہوتا: استعمال کریں `client:load` |

فریم ورک `nexyconfig.py` میں ایک بار ترتیب دیا گیا ہے، اور ایک پروجیکٹ ایک استعمال کرتا ہے:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

## Markdown صفحات

```md filename="src/pages/changelog.md"
---
layout: ../layouts/Base.astro
---
# Changelog
```

`.md` فائل `src/routes/` کے نیچے ایک صفحہ ہے، جسے بغیر `layout:` کلید کے قریب ترین لے آؤٹ میں لپیٹا گیا ہے:

```md filename="src/routes/changelog.md"
# Changelog

Version 2.2 is out.
```

`.mdx` صفحات بھی کام کرتے ہیں، فریم ورک کے طور پر React یا Preact کے ساتھ۔ دیکھیں [Markdown اور MDX](../views/nexy/markdown.md)۔

## API اختتامی پوائنٹس

```ts filename="src/pages/api/items/[id].ts"
export function GET({ params }) {
  return Response.json({ id: Number(params.id) });
}
```

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

باڈی ایک Pydantic ماڈل ہے، جس کی توثیق فنکشن کے چلنے سے پہلے کی جاتی ہے:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## `Astro.redirect`، `Astro.cookies` اور `Astro.url`

```astro filename="src/pages/account.astro"
---
const theme = Astro.cookies.get("theme")?.value ?? "light";
if (!Astro.cookies.has("session")) return Astro.redirect("/login");
const page = Astro.url.searchParams.get("page") ?? "1";
---
<p>{theme} theme, page {page}</p>
```

وہی ریڈز ہکس ہیں، اور ری ڈائریکٹ ایک فنکشن ہے:

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

## مڈل ویئر

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

ذیلی فولڈر میں ایک `middleware.py` صرف اس کے نیچے کے راستوں کو لپیٹتا ہے، جو `onRequest` کے اندر راستے کی جانچ پڑتال کی جگہ لے لیتا ہے۔

## Astro اعمال

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

ایک عمل ایک Python فعل ہے `src/actions/` میں؛ ایک فارم اس کے راستے پر پوسٹ کرتا ہے:

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

ایک جزیرے سے، `useAction(add_note)` میں `@nexy/client` ٹائپ شدہ ان پٹ کے ساتھ ایک ہی فنکشن کو کال کرتا ہے۔

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

API کلائنٹس کو اب بھی `{"detail": "Not Found"}` ملتا ہے۔

## جامد آؤٹ پٹ اور آن ڈیمانڈ رینڈرنگ

Astro پہلے سے طے شدہ طور پر جامد HTML بناتا ہے اور `output: "server"` یا `export const prerender = false` کے ساتھ ڈیمانڈ پر پیش کرتا ہے۔ Nexy درخواست پر ہر صفحہ کو رینڈر کرتا ہے، اور آپ کے فی یو آر ایل کے منتخب کردہ کو کیش کرتا ہے:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

کوئی جامد برآمد نہیں ہے: `nx start` سائٹ کی خدمت کرتا ہے۔ دیکھیں [ترجمہ ](../rendering/README.md)۔

## چل رہا ہے۔

| Astro | نیکسی |
|---|---|
| `npm create astro@latest` | `nx new` |
| `astro dev` | `nx dev` |
| `astro build` اور `astro preview` | `nx build`، پھر `nx start` |
| `public/` | `public/`، `/` میں خدمت کی |
| `astro add react` | `nx new` ایک فریم ورک کے ساتھ، یا `useFF = react()` |

## اگلے اقدامات

- [.nexy فائلیں](../views/nexy/README.md)
- [جزائر](../rendering/islands.md)
- [Markdown اور MDX](../views/nexy/markdown.md)
- [سے Next.js سے Nexy](nextjs.md)
