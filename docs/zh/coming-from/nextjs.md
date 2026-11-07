# 从 Next.js 到 Nexy

在 Nexy 中，Next.js App Router 项目保留其文件路由、布局和 React 组件，而服务器代码、路由处理程序和服务器操作则移动到它们旁边的 Python 文件。

下面的每个部分都显示了一个 Next.js 习惯，然后 Nexy 中也显示了相同的内容。

## 首先选择模式

Next.js 应用程序将服务器和客户端组件混合在一棵树中。 Nexy 项目选择 `nexyconfig.py` 中的两种形状之一：

| 您的 Next.js 应用程序是 | 邻接模式 | 页面是 |
|---|---|---|
| 主要是交互式、客户端导航 | 客户端模式，`useCSR = True` | `.tsx` 文件，如 `app/` |
| 主要内容，一些互动部分 | 服务器模式，默认 | `.nexy` 页面包含 React 岛屿 |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

除非另有说明，以下部分均使用客户端模式。请参阅[服务器模式和客户端模式](../routing/fbr/modes.md)。

## `page.tsx`

```tsx filename="应用程序/关于/page.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

页面是文件本身，而不是文件夹内的 `page.tsx`：

```tsx filename="src/routes/about.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

`app/page.tsx` 是 `src/routes/index.tsx`，`app/blog/page.tsx` 是 `src/routes/blog/index.tsx`。

## 路由文件、App Router 和 Pages Router

Next.js 的两个路由器都映射到 `src/routes/`。 Pages Router 的文件保留其路径； App Router 的 `page.tsx` 变为 `index.tsx`，或以其文件夹命名的文件：

| Next.js | 内克西 |
|---|---|
| `pages/about.tsx` | `src/routes/about.tsx` |
| `pages/blog/[slug].tsx` | `src/routes/blog/[slug].tsx` |
| `app/about/page.tsx` | `src/routes/about/index.tsx` 或 `src/routes/about.tsx` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug]/index.tsx` 或 `src/routes/blog/[slug].tsx` |
| `app/docs/[...slug]/page.tsx` | `src/routes/docs/[...slug].tsx` |
| `app/(marketing)/pricing/page.tsx` | `src/routes/(marketing)/pricing.tsx` |
| `pages/api/items/[id].ts` | `src/routes/api/items/[id].py` |
| `app/api/items/[id]/route.ts` | `src/routes/api/items/[id].py` 或 `src/routes/api/items/[id]/index.py` |

`.tsx` 文件是一个页面，`.py` 文件是一个处理程序：扩展名说明了哪个文件，因此路由处理程序会丢失其 `/route` 文件夹。

## 动态段和 `params`

```tsx filename="应用程序/博客/[slug]/page.tsx"
export default async function Post({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return <h1>{slug}</h1>;
}
```

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

`[...slug]` 和路由组（例如 `(marketing)`）的工作方式与 Next.js 中相同。

## `generateStaticParams`

```tsx filename="应用程序/博客/[slug]/page.tsx"
export async function generateStaticParams() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

同一导出，在此名称或 `getStaticParams` 下，为每个值提供一个预渲染文档。 Nexy 在没有 `await` 的情况下调用它，因此返回数组本身：

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export function getStaticParams() {
  return [{ slug: "hello" }, { slug: "world" }];
}

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

## `layout.tsx`

```tsx filename="应用程序/布局.tsx"
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

同一个文件，上一个文件夹：根布局拥有 `<html>`，子文件夹中的 `layout.tsx` 嵌套在其中。

```tsx filename=""
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <title>My app</title>
      </head>
      <body>{children}</body>
    </html>
  );
}
```

## `metadata`

```tsx filename="应用程序/博客/page.tsx"
export const metadata = { title: "Blog", description: "Posts about Nexy" };
```

`.tsx` 页面没有 `metadata` 导出：在根布局中写入标签。在服务器模式下，`.nexy` 页面每页设置它们：

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

根 `layout.nexy` 在 Next.js 中写入标签，在 `<head>` 中：

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

## `next/link` 和 `next/navigation`

```tsx filename="应用程序/nav.tsx"
"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
```

相同的名字，来自 `@nexy/client`：

```tsx filename="src/组件/Nav.tsx"
import { Link, usePathname, useRouter } from "@nexy/client";

export function Nav() {
  const pathname = usePathname();
  const router = useRouter();
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about" activeClassName="active">About</Link>
      <span>{pathname}</span>
      <button onClick={() => router.push("/dashboard")}>Dashboard</button>
    </nav>
  );
}
```

## 路线处理程序

```ts filename="应用程序/api/items/[id]/route.ts"
export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return Response.json({ id: Number(id) });
}
```

相同的 `GET` 导出，在 Python 中，没有 `/route`：

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

主体是 Pydantic 模型，`/docs` 列出每个处理程序：

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## 服务器操作和 `revalidatePath`

```ts filename="应用程序/actions.ts"
"use server";
import { revalidatePath } from "next/cache";

export async function addTodo(title: string) {
  await db.todo.create({ data: { title } });
  revalidatePath("/todos");
}
```

一个动作是一个 Python 函数。 Nexy 在 `@nexy/actions` 中生成其类型化客户端：

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

```tsx filename="src/routes/todos.tsx"
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export default function Todos() {
  const { run, pending, error, data } = useAction(add_todo);
  return (
    <button disabled={pending} onClick={() => run({ title: "Write the docs" })}>
      {error ? error.message : data ? `Added ${data.title}` : "Add"}
    </button>
  );
}
```

`useActionState` 和 `useFormStatus` 映射到 `useAction` 的 `pending`、`error` 和 `data`。

## 服务器组件是 `.nexy` 页面

```tsx filename="应用程序/用户/page.tsx"
export default async function Users() {
  const users = await db.user.findMany();
  return <ul>{users.map((user) => <li key={user.id}>{user.name}</li>)}</ul>;
}
```

Next.js 服务器组件在服务器上运行，读取数据并发送 HTML。 `.nexy` 页面在服务器模式下是相同的：它的 frontmatter 是异步组件的主体，在 Python 中，模板是它返回的内容。

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

| Next.js 服务器组件 | `.nexy` 页 |
|---|---|
| `app/users/page.tsx`，无 `"use client"` | `src/routes/users.nexy` |
| 组件中的 `await db.user.findMany()` | frontmatter 中的查询 |
| `{params}` 和 `{searchParams}` | `slug: prop[str]` 和 `useSearchParams()` |
| `cookies()` 和 `headers()` 来自 `next/headers` | `useCookies()` 和 `useHeaders()` |
| `export const revalidate = 60` | `revalidate = 60` |
| 里面有一个 `"use client"` 组件 | 一座岛屿：`<Counter directive="client:load" />` |

在客户端模式下，`.tsx` 页面在浏览器中运行，因此它从处理程序读取数据：

```python filename="src/routes/api/users.py"
async def GET():
    return [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
```

```tsx filename="src/routes/users.tsx"
import { useEffect, useState } from "react";

type User = { id: number; name: string };

export default function Users() {
  const [users, setUsers] = useState<User[]>([]);
  useEffect(() => {
    fetch("/api/users").then((response) => response.json()).then(setUsers);
  }, []);
  return <ul>{users.map((user) => <li key={user.id}>{user.name}</li>)}</ul>;
}
```

## `"use client"` 服务器页面内的组件

```tsx filename="应用程序/page.tsx"
import Counter from "./counter"; // "use client"

export default function Home() {
  return (
    <>
      <h1>Static heading</h1>
      <Counter />
    </>
  );
}
```

在服务器模式下，客户端组件是一个孤岛，其指令表示何时水合：

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

```tsx filename="src/组件/Counter.tsx"
import { useState } from "react";

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

请参阅[岛屿](../rendering/islands.md) 了解 `client:load`、`client:idle`、`client:visible` 和 `client:media`。

## ISR 与 `revalidate`

```tsx filename="应用程序/新闻/page.tsx"
export const revalidate = 60;
```

同一行，在服务器模式页面的 frontmatter 中：

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## `middleware.ts`

```ts filename="中间件.ts"
import { NextResponse, type NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  if (!request.cookies.get("session")) return NextResponse.redirect(new URL("/login", request.url));
}

export const config = { matcher: "/dashboard/:path*" };
```

`matcher` 是文件夹：`dashboard/` 中的 `middleware.py` 包含其下面的每个路由。

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

## `notFound()` 和 `not-found.tsx`

```tsx filename="应用程序/博客/[slug]/page.tsx"
import { notFound } from "next/navigation";

if (!post) notFound();
```

在处理程序中，加注；在服务器模式页面中，调用 `notFound()`：

```python filename="src/routes/api/posts/[slug].py"
from nexy.http import HTTPException

POSTS = {"hello": "Hello, world"}


async def GET(slug: str):
    if slug not in POSTS:
        raise HTTPException(status_code=404, detail="No such post")
    return {"title": POSTS[slug]}
```

`app/not-found.tsx` 在客户端模式下为 `src/routes/notfound.tsx`，在服务器模式下为 `notfound.nexy`。

## `next/image`

```tsx
import Image from "next/image";

<Image src="/logo.png" alt="Logo" width={128} height={32} />
```

在 `.nexy` 页面中，`nexy` 的 `Image` 组件：

```nexy filename="src/routes/brand.nexy"
---
from nexy import Image
---
<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

## 跑步

| Next.js | 内克西 |
|---|---|
| `npx create-next-app` | `nx new`，模板 `web-fbr-react` |
| `next dev` | `nx dev` |
| `next build && next start` | `nx build`，然后 `nx start` |
| `public/` | `public/`，服务于 `/` |
| 运行时的节点 | Python 在运行时； Node 仅构建客户端包 |

## 后续步骤

- [服务器模式和客户端模式](../routing/fbr/modes.md)
- [React 在 Nexy](../views/react/differences.md)
- [行动](../guides/actions.md)
- [岛屿](../rendering/islands.md)
