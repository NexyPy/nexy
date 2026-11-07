# من Astro إلى النكسي

صفحة Nexy `.nexy` هي صفحة Astro تحتوي على Python في الجزء الأمامي `---` بدلاً من TypeScript: نفس HTML الخاص بالخادم الأول، ونفس الجزر وتوجيهات `client:*`، التي يتم تقديمها عند كل طلب.

كل قسم أدناه يوضح عادة Astro، ثم نفس الشيء في Nexy.

## صفحة

```astro filename="src/pages/about.astro"
---
const title = "About";
---
<h1>{title}</h1>
```

الواجهة هي Python والقالب هو Jinja2:

```nexy filename="src/routes/about.nexy"
---
title = "About"
---
<h1>{{ title }}</h1>
```

`src/pages/` هو `src/routes/`، و `index.astro` هو `index.nexy`.

## الحلقات والشروط

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
> Astro يهرب من كل `{value}`. `.nexy` القوالب لا: تهرب مما كتبه الزائر بـ `{{ value | e }}`.

## المكونات و `Astro.props`

```astro filename="src/components/Card.astro"
---
const { title, tone = "neutral" } = Astro.props;
---
<article class={`card card-${tone}`}>
  <h2>{title}</h2>
  <slot />
</article>
```

يتم الإعلان عن الخاصيات باستخدام `prop[...]`، والافتراضي هو Python الافتراضي، و `<slot />` هو `<Slot />`:

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

`@` هو `src/`: `nx new` يكتب `useAliases = {"@": "src"}` في `nexyconfig.py`.

## التخطيطات

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

الصفحة لا تستورد تخطيطها: أقرب `layout.nexy` فوقها يغلفها، والجذر يملك الوثيقة.

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

## العنوان والعلامات الوصفية

تصبح الدعامة `title` للتخطيط `metadata` في الصفحة، والتي يكتبها `useMetadata().html()` في `<head>` للتخطيط أعلاه:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## المسارات الديناميكية و `getStaticPaths`

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

يتم عرض صفحة `.nexy` ديناميكية عند الطلب، لذلك لا توجد قائمة بالمسارات: المقطع هو دعامة، والجزء غير المعروف هو `404`.

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

`[...path].astro` هو `[...path].nexy`.

## الجزر و `client:*`

```astro filename="src/pages/index.astro"
---
import Counter from "../components/Counter.tsx";
---
<h1>Static heading</h1>
<Counter start={3} client:visible />
```

يصبح التوجيه سمة `directive` بنفس القيم:

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

| Astro | نكسي |
|---|---|
| `client:load` | `directive="client:load"`، أو بدون توجيه |
| `client:idle` | `directive="client:idle"` |
| `client:visible` | `directive="client:visible"` |
| `client:media="(min-width: 768px)"` | `directive="client:media" media="(min-width: 768px)"` |
| `client:only="react"` | مقبول، ولكن لا يرطب أبدًا: استخدم `client:load` |

يتم تعيين إطار العمل مرة واحدة في `nexyconfig.py`، ويستخدم المشروع واحدًا:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

## Markdown صفحة

```md filename="src/pages/changelog.md"
---
layout: ../layouts/Base.astro
---
# Changelog
```

الملف `.md` ضمن `src/routes/` هو صفحة ملفوفة بأقرب تخطيط بدون مفتاح `layout:`:

```md filename="src/routes/changelog.md"
# Changelog

Version 2.2 is out.
```

`.mdx` تعمل الصفحات أيضًا، مع React أو Preact كإطار عمل. انظر [Markdown و MDX](../views/nexy/markdown.md).

## نقاط نهاية API

```ts filename="src/pages/api/items/[id].ts"
export function GET({ params }) {
  return Response.json({ id: Number(params.id) });
}
```

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

الجسم هو نموذج Pydantic، يتم التحقق من صحته قبل تشغيل الوظيفة:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## `Astro.redirect` و `Astro.cookies` و `Astro.url`

```astro filename="src/pages/account.astro"
---
const theme = Astro.cookies.get("theme")?.value ?? "light";
if (!Astro.cookies.has("session")) return Astro.redirect("/login");
const page = Astro.url.searchParams.get("page") ?? "1";
---
<p>{theme} theme, page {page}</p>
```

نفس القراءات عبارة عن خطافات، وإعادة التوجيه هي وظيفة:

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

## الوسيطة

```ts filename="src/middleware.ts"
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

يقوم `middleware.py` الموجود في المجلد الفرعي بتغليف المسارات الموجودة أسفله فقط، مما يحل محل عمليات التحقق من المسار داخل `onRequest`.

## Astro الأفعال

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

الفعل هو دالة Python في `src/actions/`؛ نموذج ينشر في مساره:

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

من جزيرة، `useAction(add_note)` في `@nexy/client` يستدعي نفس الوظيفة مع الإدخال المكتوب.

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

لا يزال عملاء API يحصلون على `{"detail": "Not Found"}`.

## الإخراج الثابت والعرض عند الطلب

Astro ينشئ HTML ثابتًا بشكل افتراضي ويتم عرضه عند الطلب باستخدام `output: "server"` أو `export const prerender = false`. يعرض Nexy كل صفحة عند الطلب، ويخزن مؤقتًا الصفحات التي تختارها لكل عنوان URL:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

لا يوجد تصدير ثابت: `nx start` يخدم الموقع. انظر [التقديم](../rendering/README.md).

## الجري

| Astro | نكسي |
|---|---|
| `npm create astro@latest` | `nx new` |
| `astro dev` | `nx dev` |
| `astro build` و `astro preview` | `nx build`، ثم `nx start` |
| `public/` | `public/`، خدم في `/` |
| `astro add react` | `nx new` مع إطار، أو `useFF = react()` |

## الخطوات التالية

- [ملفات .nexy](../views/nexy/README.md)
- [الجزر](../rendering/islands.md)
- [Markdown و MDX](../views/nexy/markdown.md)
- [من Next.js إلى نكسي](nextjs.md)
