# Astro से नेक्सी तक

एक नेक्सी `.nexy` पृष्ठ एक Astro पृष्ठ है जिसके TypeScript के बजाय `---` फ्रंटमैटर में Python है: समान सर्वर-प्रथम HTML, समान द्वीप और `client:*` निर्देश, प्रत्येक अनुरोध पर प्रस्तुत किए गए।

नीचे प्रत्येक अनुभाग एक Astro आदत दिखाता है, फिर नेक्सी में भी वही चीज़।

## एक पन्ना

```astro filename="src/pages/about.astro"
---
const title = "About";
---
<h1>{title}</h1>
```

फ्रंटमैटर Python है और टेम्पलेट Jinja2 है:

```nexy filename="src/routes/about.nexy"
---
title = "About"
---
<h1>{{ title }}</h1>
```

`src/pages/` है `src/routes/`, और `index.astro` है `index.nexy`।

## लूप और शर्तें

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
> Astro हर `{value}` से बच जाता है। `.nexy` टेम्प्लेट किसी विज़िटर द्वारा `{{ value | e }}` से टाइप किए जाने से बच नहीं सकते।

## घटक और `Astro.props`

```astro filename="src/components/Card.astro"
---
const { title, tone = "neutral" } = Astro.props;
---
<article class={`card card-${tone}`}>
  <h2>{title}</h2>
  <slot />
</article>
```

प्रॉप्स को `prop[...]` के साथ घोषित किया जाता है, डिफॉल्ट को Python डिफॉल्ट के साथ घोषित किया जाता है, और `<slot />` को `<Slot />` के साथ घोषित किया जाता है:

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

`@` है `src/`: `nx new` `nexyconfig.py` में `useAliases = {"@": "src"}` लिखता है।

## लेआउट

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

एक पृष्ठ अपना लेआउट आयात नहीं करता है: इसके ऊपर निकटतम `layout.nexy` इसे लपेटता है, और मूल दस्तावेज़ का स्वामी होता है।

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

## शीर्षक और मेटा टैग

पृष्ठ में लेआउट का `title` प्रोप `metadata` बन जाता है, जिसे `useMetadata().html()` उपरोक्त लेआउट के `<head>` में लिखता है:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## गतिशील मार्ग और `getStaticPaths`

```astro filename="src/पेज/पोस्ट/[स्लग].एस्ट्रो"
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

एक गतिशील `.nexy` पृष्ठ अनुरोध पर प्रस्तुत होता है, इसलिए पथों की कोई सूची नहीं है: खंड एक प्रोप है, और एक अज्ञात एक `404` है।

```nexy filename="src/routes/posts/[स्लग].nexy"
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

`[...path].astro` `[...path].nexy` है।

## द्वीप और `client:*`

```astro filename="src/pages/index.astro"
---
import Counter from "../components/Counter.tsx";
---
<h1>Static heading</h1>
<Counter start={3} client:visible />
```

समान मानों के साथ निर्देश एक `directive` विशेषता बन जाता है:

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

| Astro | नेक्सी |
|---|---|
| `client:load` | `directive="client:load"`, या कोई निर्देश नहीं |
| `client:idle` | `directive="client:idle"` |
| `client:visible` | `directive="client:visible"` |
| `client:media="(min-width: 768px)"` | `directive="client:media" media="(min-width: 768px)"` |
| `client:only="react"` | स्वीकार किया जाता है, लेकिन कभी हाइड्रेट नहीं करता: उपयोग करें `client:load` |

फ़्रेमवर्क को `nexyconfig.py` में एक बार सेट किया जाता है, और एक प्रोजेक्ट इसका उपयोग करता है:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

## Markdown पेज

```md filename="src/pages/changelog.md"
---
layout: ../layouts/Base.astro
---
# Changelog
```

`src/routes/` के अंतर्गत एक `.md` फ़ाइल एक पृष्ठ है, जो बिना `layout:` कुंजी के निकटतम लेआउट में लपेटा गया है:

```md filename="src/routes/changelog.md"
# Changelog

Version 2.2 is out.
```

`.mdx` पृष्ठ, React या Preact की रूपरेखा के साथ भी काम करते हैं। [Markdown और MDX](../views/nexy/markdown.md) देखें।

## एपीआई समापनबिंदु

```ts filename="src/pages/api/items/[id].ts"
export function GET({ params }) {
  return Response.json({ id: Number(params.id) });
}
```

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

बॉडी एक Pydantic मॉडल है, जिसे फ़ंक्शन चलने से पहले मान्य किया जाता है:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## `Astro.redirect`, `Astro.cookies` और `Astro.url`

```astro filename="src/pages/account.astro"
---
const theme = Astro.cookies.get("theme")?.value ?? "light";
if (!Astro.cookies.has("session")) return Astro.redirect("/login");
const page = Astro.url.searchParams.get("page") ?? "1";
---
<p>{theme} theme, page {page}</p>
```

वही रीड्स हुक हैं, और रीडायरेक्ट एक फ़ंक्शन है:

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

## मिडलवेयर

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

एक सबफ़ोल्डर में एक `middleware.py` केवल उसके नीचे के मार्गों को लपेटता है, जो `onRequest` के अंदर पथ जांच को प्रतिस्थापित करता है।

## Astro क्रियाएँ

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

`src/actions/` में एक क्रिया एक Python फ़ंक्शन है; एक प्रपत्र अपने पथ पर पोस्ट करता है:

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

एक द्वीप से, `useAction(add_note)` में `@nexy/client` टाइप किए गए इनपुट के साथ समान फ़ंक्शन को कॉल करता है।

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

एपीआई क्लाइंट को अभी भी `{"detail": "Not Found"}` मिलता है।

## स्टेटिक आउटपुट और ऑन-डिमांड रेंडरिंग

Astro डिफ़ॉल्ट रूप से स्थिर HTML बनाता है और `output: "server"` या `export const prerender = false` के साथ मांग पर प्रस्तुत करता है। नेक्सी अनुरोध पर प्रत्येक पेज को प्रस्तुत करता है, और आपके द्वारा प्रति यूआरएल के अनुसार चुने गए पेज को कैश करता है:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

कोई स्थिर निर्यात नहीं है: `nx start` साइट पर कार्य करता है। [रेंडरिंग](../rendering/README.md) देखें।

## चल रहा है

| Astro | नेक्सी |
|---|---|
| `npm create astro@latest` | `nx new` |
| `astro dev` | `nx dev` |
| `astro build` और `astro preview` | `nx build`, फिर `nx start` |
| `public/` | `public/`, `/` में सेवा दी गई |
| `astro add react` | `nx new` एक रूपरेखा के साथ, या `useFF = react()` |

## अगले चरण

- [.nexy फ़ाइलें](../views/nexy/README.md)
- [द्वीप](../rendering/islands.md)
- [Markdown और MDX](../views/nexy/markdown.md)
- [से Next.js से नेक्सी](nextjs.md)
