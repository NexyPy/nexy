# From Astro to Nexy

A Nexy `.nexy` page is an Astro page with Python in its `---` frontmatter instead of TypeScript: the
same server-first HTML, the same islands and `client:*` directives, rendered on each request.

Each section below shows an Astro habit, then the same thing in Nexy.

## A page

```astro filename="src/pages/about.astro"
---
const title = "About";
---
<h1>{title}</h1>
```

The frontmatter is Python and the template is Jinja2:

```nexy filename="src/routes/about.nexy"
---
title = "About"
---
<h1>{{ title }}</h1>
```

`src/pages/` is `src/routes/`, and `index.astro` is `index.nexy`.

## Loops and conditions

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
> Astro escapes every `{value}`. `.nexy` templates do not: escape what a visitor typed with
> `{{ value | e }}`.

## Components and `Astro.props`

```astro filename="src/components/Card.astro"
---
const { title, tone = "neutral" } = Astro.props;
---
<article class={`card card-${tone}`}>
  <h2>{title}</h2>
  <slot />
</article>
```

Props are declared with `prop[...]`, a default is a Python default, and `<slot />` is `<Slot />`:

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

`@` is `src/`: `nx new` writes `useAliases = {"@": "src"}` in `nexyconfig.py`.

## Layouts

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

A page does not import its layout: the nearest `layout.nexy` above it wraps it, and the root one
owns the document.

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

## The title and meta tags

The `title` prop of the layout becomes `metadata` in the page, which `useMetadata().html()` writes
in the `<head>` of the layout above:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## Dynamic routes and `getStaticPaths`

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

A dynamic `.nexy` page renders on request, so there is no list of paths: the segment is a prop, and
an unknown one is a `404`.

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

`[...path].astro` is `[...path].nexy`.

## Islands and `client:*`

```astro filename="src/pages/index.astro"
---
import Counter from "../components/Counter.tsx";
---
<h1>Static heading</h1>
<Counter start={3} client:visible />
```

The directive becomes a `directive` attribute, with the same values:

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

| Astro | Nexy |
|---|---|
| `client:load` | `directive="client:load"`, or no directive |
| `client:idle` | `directive="client:idle"` |
| `client:visible` | `directive="client:visible"` |
| `client:media="(min-width: 768px)"` | `directive="client:media" media="(min-width: 768px)"` |
| `client:only="react"` | accepted, but never hydrates: use `client:load` |

The framework is set once in `nexyconfig.py`, and a project uses one:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

## Markdown pages

```md filename="src/pages/changelog.md"
---
layout: ../layouts/Base.astro
---
# Changelog
```

A `.md` file under `src/routes/` is a page, wrapped in the nearest layout with no `layout:` key:

```md filename="src/routes/changelog.md"
# Changelog

Version 2.2 is out.
```

`.mdx` pages work too, with React or Preact as the framework. See
[Markdown and MDX](../views/nexy/markdown.md).

## API endpoints

```ts filename="src/pages/api/items/[id].ts"
export function GET({ params }) {
  return Response.json({ id: Number(params.id) });
}
```

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

A body is a Pydantic model, validated before the function runs:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## `Astro.redirect`, `Astro.cookies` and `Astro.url`

```astro filename="src/pages/account.astro"
---
const theme = Astro.cookies.get("theme")?.value ?? "light";
if (!Astro.cookies.has("session")) return Astro.redirect("/login");
const page = Astro.url.searchParams.get("page") ?? "1";
---
<p>{theme} theme, page {page}</p>
```

The same reads are hooks, and the redirect is a function:

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

## Middleware

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

A `middleware.py` in a subfolder only wraps the routes below it, which replaces the path checks
inside `onRequest`.

## Astro Actions

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

An action is a Python function in `src/actions/`; a form posts to its path:

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

From an island, `useAction(add_note)` in `@nexy/client` calls the same function with typed input.

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

API clients still get `{"detail": "Not Found"}`.

## Static output and on-demand rendering

Astro builds static HTML by default and renders on demand with `output: "server"` or
`export const prerender = false`. Nexy renders every page on request, and caches the ones you
choose per URL:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

There is no static export: `nx start` serves the site. See [Rendering](../rendering/README.md).

## Running

| Astro | Nexy |
|---|---|
| `npm create astro@latest` | `nx new` |
| `astro dev` | `nx dev` |
| `astro build` and `astro preview` | `nx build`, then `nx start` |
| `public/` | `public/`, served at `/` |
| `astro add react` | `nx new` with a framework, or `useFF = react()` |

## Next steps

- [.nexy files](../views/nexy/README.md)
- [Islands](../rendering/islands.md)
- [Markdown and MDX](../views/nexy/markdown.md)
- [From Next.js to Nexy](nextjs.md)
