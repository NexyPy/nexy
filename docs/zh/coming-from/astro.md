# 从 Astro 到 Nexy

Nexy `.nexy` 页面是一个 Astro 页面，其 `---` frontmatter 中包含 Python 而不是 TypeScript：相同的服务器优先 HTML、相同的岛屿和 `client:*` 指令，在每个请求上呈现。

下面的每个部分都显示了一个 Astro 习惯，然后 Nexy 中也显示了相同的内容。

## 一页

```astro filename="src/pages/about.astro"
---
const title = "About";
---
<h1>{title}</h1>
```

frontmatter 是 Python，模板是 Jinja2：

```nexy filename="src/routes/about.nexy"
---
title = "About"
---
<h1>{{ title }}</h1>
```

`src/pages/` 是 `src/routes/`，`index.astro` 是 `index.nexy`。

## 循环和条件

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
> Astro 每个 `{value}` 都会转义。 `.nexy` 模板不会：转义访问者使用 `{{ value | e }}` 键入的内容。

## 组件和 `Astro.props`

```astro filename="src/components/Card.astro"
---
const { title, tone = "neutral" } = Astro.props;
---
<article class={`card card-${tone}`}>
  <h2>{title}</h2>
  <slot />
</article>
```

props 使用 `prop[...]` 声明，默认值是 Python 默认值，`<slot />` 是 `<Slot />`：

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

`@` 是 `src/`：`nx new` 在 `nexyconfig.py` 中写入 `useAliases = {"@": "src"}`。

## 布局

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

页面不导入其布局：其上方最近的 `layout.nexy` 将其包裹，根页面拥有该文档。

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

## 标题和元标签

布局的 `title` 属性在页面中变为 `metadata`，`useMetadata().html()` 写入上面布局的 `<head>` 中：

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## 动态路线和 `getStaticPaths`

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

动态 `.nexy` 页面根据请求呈现，因此没有路径列表：该段是一个 prop，未知的一个是 `404`。

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

`[...path].astro` 是 `[...path].nexy`。

## 岛屿和 `client:*`

```astro filename="src/pages/index.astro"
---
import Counter from "../components/Counter.tsx";
---
<h1>Static heading</h1>
<Counter start={3} client:visible />
```

该指令成为 `directive` 属性，具有相同的值：

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

| Astro | 内克西 |
|---|---|
| `client:load` | `directive="client:load"`，或无指令 |
| `client:idle` | `directive="client:idle"` |
| `client:visible` | `directive="client:visible"` |
| `client:media="(min-width: 768px)"` | `directive="client:media" media="(min-width: 768px)"` |
| `client:only="react"` | 已接受，但从不水合：使用 `client:load` |

该框架在 `nexyconfig.py`中设置一次，项目使用一个：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

## Markdown 页

```md filename="src/pages/changelog.md"
---
layout: ../layouts/Base.astro
---
# Changelog
```

`src/routes/` 下的 `.md` 文件是一个页面，包裹在最接近的布局中，没有 `layout:` 键：

```md filename="src/routes/changelog.md"
# Changelog

Version 2.2 is out.
```

`.mdx` 页面也可以使用 React 或 Preact 作为框架。请参阅[Markdown 和 MDX](../views/nexy/markdown.md)。

## API端点

```ts filename="src/pages/api/items/[id].ts"
export function GET({ params }) {
  return Response.json({ id: Number(params.id) });
}
```

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

主体是一个 Pydantic 模型，在函数运行之前进行验证：

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## `Astro.redirect`、`Astro.cookies` 和 `Astro.url`

```astro filename="src/pages/account.astro"
---
const theme = Astro.cookies.get("theme")?.value ?? "light";
if (!Astro.cookies.has("session")) return Astro.redirect("/login");
const page = Astro.url.searchParams.get("page") ?? "1";
---
<p>{theme} theme, page {page}</p>
```

相同的读取是钩子，重定向是一个函数：

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

## 中间件

```ts filename=""
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

子文件夹中的 `middleware.py` 仅包含其下方的路由，这取代了 `onRequest` 内的路径检查。

## Astro 行动

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

动作是 `src/actions/` 中的 Python 函数；表单发布到其路径：

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

在一座岛上，`@nexy/client` 中的 `useAction(add_note)` 使用键入的输入调用相同的函数。

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

API 客户端仍然可以获得 `{"detail": "Not Found"}`。

## 静态输出和按需渲染

Astro 默认构建静态 HTML，并根据需要使用 `output: "server"` 或 `export const prerender = false` 进行渲染。 Nexy 根据请求呈现每个页面，并缓存您根据 URL 选择的页面：

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

没有静态导出：`nx start` 为站点提供服务。请参阅[渲染](../rendering/README.md)。

## 跑步

| Astro | 内克西 |
|---|---|
| `npm create astro@latest` | `nx new` |
| `astro dev` | `nx dev` |
| `astro build` 和 `astro preview` | `nx build`，然后 `nx start` |
| `public/` | `public/`，服务于 `/` |
| `astro add react` | `nx new` 带有框架，或 `useFF = react()` |

## 后续步骤

- [.nexy 文件](../views/nexy/README.md)
- [岛屿](../rendering/islands.md)
- [Markdown 和 MDX](../views/nexy/markdown.md)
- [从 Next.js 到 Nexy](nextjs.md)
