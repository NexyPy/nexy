# 从 Remix 到 Nexy

在 Nexy 中，Remix 或 React 路由器路由保留其 React 组件，而其 `loader` 成为 Python 处理程序，其 `action` 成为 Python 操作，并且嵌套路由成为带有 `layout.tsx` 的文件夹。

下面的每个部分都显示了一个 Remix 习惯，然后 Nexy 中也显示了相同的内容。 React 框架模式下的路由器 v7 使用相同的名称。

## 选择模式

Remix 应用程序在客户端上导航，因此它映射到客户端模式：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

仅需要一些交互部分的内容站点更适合服务器模式：带有 React 岛屿的 `.nexy` 页面。请参阅[服务器模式和客户端模式](../routing/fbr/modes.md)。

## 路线文件

| Remix（`app/routes/`） | 尼克西 (`src/routes/`) |
|---|---|
| `_index.tsx` | `index.tsx` |
| `about.tsx` | `about.tsx` |
| `blog.$slug.tsx` | `blog/[slug].tsx` |
| `files.$.tsx`（啪） | `files/[...path].tsx` |
| `_auth.login.tsx`（无路径布局） | `(auth)/login.tsx`，路线组 |
| `api.items.$id.ts`（资源路线） | `api/items/[id].py` |

点变成文件夹，`$param` 变成 `[param]`。

## `useParams`

```tsx filename="应用程序/路线/博客.$slug.tsx"
import { useParams } from "@remix-run/react";

export default function Post() {
  const { slug } = useParams();
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

## `loader` 和 `useLoaderData`

```tsx filename="应用程序/路线/users.tsx"
import { json } from "@remix-run/node";
import { useLoaderData } from "@remix-run/react";

export async function loader() {
  return json(await db.user.findMany());
}

export default function Users() {
  const users = useLoaderData<typeof loader>();
  return <ul>{users.map((user) => <li key={user.id}>{user.name}</li>)}</ul>;
}
```

加载器移动到 Python 处理程序，页面读取它：

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

在服务器模式下，`.nexy` 页面是加载器和视图在一个文件中，数据位于第一个 HTML 中：

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

## 加载程序中的 `params` 和 `request`

```tsx filename="应用程序/路线/api.orders.$id.ts"
export async function loader({ params, request }: LoaderFunctionArgs) {
  const currency = new URL(request.url).searchParams.get("currency") ?? "EUR";
  if (Number(params.id) > 100) throw new Response("No such order", { status: 404 });
  return json({ id: Number(params.id), currency });
}
```

路径和查询值是键入参数，并且会引发错误：

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `action`、`<Form>` 和 `useActionData`

```tsx filename="应用程序/路线/todos.tsx"
import { Form, useActionData } from "@remix-run/react";

export async function action({ request }: ActionFunctionArgs) {
  const form = await request.formData();
  return json({ title: String(form.get("title")), done: false });
}

export default function Todos() {
  const todo = useActionData<typeof action>();
  return (
    <Form method="post">
      <input name="title" />
      <button>Add</button>
      {todo && <p>Added {todo.title}</p>}
    </Form>
  );
}
```

该操作是具有类型化客户端的 Python 函数，并且 `useAction` 保存 `useActionData` 和 `useNavigation().state` 所保存的内容：

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
import { useState } from "react";
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export default function Todos() {
  const [title, setTitle] = useState("");
  const { run, pending, error, data } = useAction(add_todo);
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        run({ title });
      }}
    >
      <input value={title} onChange={(event) => setTitle(event.target.value)} />
      <button disabled={pending}>Add</button>
      {error && <p>{error.message}</p>}
      {data && <p>Added {data.title}</p>}
    </form>
  );
}
```

`revalidate("/todos")` 执行 Remix 在每个操作后执行的操作：页面再次加载其数据。

## `useFetcher`

```tsx
const fetcher = useFetcher();
fetcher.submit({ title: "Write the docs" }, { method: "post", action: "/todos" });
```

`useAction` 是一个绑定到一个操作的获取器：根据需要从任意多个组件调用它，每个组件都有自己的 `pending` 和 `data`。

## 渐进增强

Remix `<Form>` 在 JavaScript 加载之前工作。在服务器模式下，普通表单以相同的方式发布到操作，并且访问者返回到页面并显示 `303`：

```nexy filename="src/routes/notes.nexy"
---
from src.actions.todos import add_todo
---
<form method="post" action="{{ __actions_path['add_todo'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
```

## 嵌套路由和 `<Outlet />`

```tsx filename="应用程序/路线/dashboard.tsx"
import { Outlet } from "@remix-run/react";

export default function Dashboard() {
  return (
    <div className="dashboard">
      <nav>Dashboard</nav>
      <Outlet />
    </div>
  );
}
```

父路由变为文件夹的 `layout.tsx`，`<Outlet />` 变为 `children`：

```tsx filename="src/routes/dashboard/layout.tsx"
import type { ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="dashboard">
      <nav>Dashboard</nav>
      <main>{children}</main>
    </div>
  );
}
```

## `root.tsx`

```tsx filename="应用程序/root.tsx"
import { Links, Meta, Outlet, Scripts } from "@remix-run/react";

export default function App() {
  return (
    <html lang="en">
      <head>
        <Meta />
        <Links />
      </head>
      <body>
        <Outlet />
        <Scripts />
      </body>
    </html>
  );
}
```

根 `layout.tsx` 拥有该文档。没有要放置的 `<Scripts />` 或 `<Links />`：Nexy 添加客户端捆绑包本身。

```tsx filename="src/routes/layout.tsx"
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

## `meta`

```tsx filename="应用程序/路线/blog.tsx"
export const meta = () => [{ title: "Blog" }, { name: "description", content: "Posts" }];
```

`.tsx` 页面没有 `meta` 导出：在根布局中写入标签。在服务器模式下，`.nexy` 页面将它们设置为 `metadata = {...}`，其布局将它们写入 `{{ useMetadata().html() }}`。

## `<Link>`、`<NavLink>` 和 `useNavigate`

```tsx filename="应用程序/组件/Nav.tsx"
import { Link, NavLink, useNavigate } from "@remix-run/react";
```

```tsx filename="src/组件/Nav.tsx"
import { Link, useRouter } from "@nexy/client";

export function Nav() {
  const router = useRouter();
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about" activeClassName="active">About</Link>
      <button onClick={() => router.push("/dashboard")}>Dashboard</button>
    </nav>
  );
}
```

`<NavLink>` 是 `Link` 和 `activeClassName`，`useNavigate()(path)` 是 `router.push(path)`。

## `redirect` 和会议

```tsx filename="应用程序/路线/dashboard.tsx"
export async function loader({ request }: LoaderFunctionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  if (!session.has("user")) throw redirect("/login");
  return null;
}
```

文件夹中的 `middleware.py` 在其下面的每个路由之前运行，包括页面：

```python filename="src/routes/dashboard/middleware.py"
from nexy.http import RedirectResponse, Request


async def middleware(request: Request, call_next):
    if "user" not in request.session:
        return RedirectResponse("/login", status_code=307)
    return await call_next(request)
```

```python filename="src/routes/dashboard/stats.py"
async def GET():
    return {"visits": 12}
```

`createCookieSessionStorage` 成为 `nexyconfig.py` 的一个字段，`request.session` 是一个字典：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me"}
```

```python filename="src/routes/api/login.py"
from pydantic import BaseModel

from nexy.http import Request


class Login(BaseModel):
    name: str


async def POST(request: Request, body: Login):
    request.session["user"] = body.name
    return {"user": body.name}
```

## 误差边界

路由的 `ErrorBoundary` 导出没有 Nexy 等效项。失败的加载程序是一个状态代码：API 客户端获取 `{"detail": ...}`，未知 URL 呈现 `src/routes/notfound.tsx`。组件渲染时抛出的错误由您自己的 React 错误边界捕获，围绕可能失败的部分。

## `headers` 和缓存

```tsx filename="应用程序/路线/news.tsx"
export const headers = () => ({ "Cache-Control": "public, s-maxage=60, stale-while-revalidate=60" });
```

在服务器模式下，frontmatter 中的一行发送该标头并保留呈现的页面：

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## 跑步

| Remix / React 路由器 | 内克西 |
|---|---|
| `npx create-react-router` | `nx new`，模板 `web-fbr-react` |
| `react-router dev` | `nx dev` |
| `react-router build`，然后 `react-router-serve` | `nx build`，然后 `nx start` |
| `public/` | `public/`，服务于 `/` |
| 运行时的节点 | Python 在运行时； Node 仅构建客户端包 |

## 后续步骤

- [从 Next.js 到 Nexy](nextjs.md)
- [React 在 Nexy](../views/react/differences.md)
- [行动](../guides/actions.md)
- [服务器模式和客户端模式](../routing/fbr/modes.md)
