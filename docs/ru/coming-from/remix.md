# От Remix до Некси

В Nexy маршрут маршрутизатора Remix или React сохраняет свой компонент React, тогда как его `loader` становится обработчиком Python, его действие `action` - Python, а вложенные маршруты становятся папками с `layout.tsx`.

В каждом разделе ниже показана Remix привычка, затем то же самое в Nexy. React Маршрутизатор v7 в режиме framework использует те же имена.

## Выберите режим

Приложение Remix перемещается по клиенту, поэтому оно отображается в клиентский режим:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

Контентный сайт, которому требуется всего несколько интерактивных частей, лучше подходит для серверного режима: `.nexy` страниц с React островами. См. [Режим сервера и режим клиента](../routing/fbr/modes.md).

## Файлы маршрутов

| Remix (`app/routes/`) | Некси (`src/routes/`) |
|---|---|
| `_index.tsx` | `index.tsx` |
| `about.tsx` | `about.tsx` |
| `blog.$slug.tsx` | `blog/[slug].tsx` |
| `files.$.tsx` (знак) | `files/[...path].tsx` |
| `_auth.login.tsx` (бесконечный макет) | `(auth)/login.tsx`, группа маршрутов |
| `api.items.$id.ts` (маршрут ресурса) | `api/items/[id].py` |

Точки становятся папками, а `$param` становится `[param]`.

## `useParams`

```tsx filename="приложение/маршруты/блог.$slug.tsx"
import { useParams } from "@remix-run/react";

export default function Post() {
  const { slug } = useParams();
  return <h1>{slug}</h1>;
}
```

```tsx filename="src/маршруты/блог/[слизень].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

## `loader` и `useLoaderData`

```tsx filename="приложение/маршруты/users.tsx"
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

Загрузчик переходит к обработчику Python, и страница считывает его:

```python filename="src/routes/api/users.py"
async def GET():
    return [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
```

```tsx filename="src/маршруты/users.tsx"
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

В режиме сервера страница `.nexy` - это загрузчик и представление в одном файле, а данные находятся в первом HTML:

```nexy filename="src/маршруты/people.nexy"
---
users = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## `params` и `request` в загрузчике

```tsx filename="приложение/маршруты/api.orders.$id.ts"
export async function loader({ params, request }: LoaderFunctionArgs) {
  const currency = new URL(request.url).searchParams.get("currency") ?? "EUR";
  if (Number(params.id) > 100) throw new Response("No such order", { status: 404 });
  return json({ id: Number(params.id), currency });
}
```

Значения пути и запроса являются типизированными параметрами, и возникает ошибка:

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `action`, `<Form>` и `useActionData`

```tsx filename="приложение/маршруты/todos.tsx"
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

Действие представляет собой функцию Python с типизированным клиентом, а `useAction` содержит то же, что `useActionData` и `useNavigation().state`:

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

```tsx filename="src/маршруты/todos.tsx"
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

`revalidate("/todos")` делает то же, что Remix после каждого действия: страница снова загружает свои данные.

## `useFetcher`

```tsx
const fetcher = useFetcher();
fetcher.submit({ title: "Write the docs" }, { method: "post", action: "/todos" });
```

`useAction` - это сборщик, привязанный к одному действию: вызывайте его из любого количества компонентов, каждый из которых имеет свои собственные `pending` и `data`.

## Прогрессивное улучшение

Remix `<Form>` работает до загрузки JavaScript. В режиме сервера простая форма отправляет действие таким же образом, и посетитель возвращается на страницу с `303`:

```nexy filename="src/маршруты/notes.nexy"
---
from src.actions.todos import add_todo
---
<form method="post" action="{{ __actions_path['add_todo'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
```

## Вложенные маршруты и `<Outlet />`

```tsx filename="приложение/маршруты/dashboard.tsx"
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

Родительский маршрут становится `layout.tsx` папки, а `<Outlet />` становится `children`:

```tsx filename="src/маршруты/панель мониторинга/layout.tsx"
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

```tsx filename="приложение/root.tsx"
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

Корень `layout.tsx` владеет документом. Нет `<Scripts />` или `<Links />` для размещения: Nexy добавляет сам пакет клиента.

```tsx filename="src/маршруты/layout.tsx"
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

```tsx filename="приложение/маршруты/blog.tsx"
export const meta = () => [{ title: "Blog" }, { name: "description", content: "Posts" }];
```

Страница `.tsx` не имеет экспорта `meta`: запишите теги в корневом макете. В режиме сервера страница `.nexy` устанавливает их с помощью `metadata = {...}`, а ее макет записывает их с помощью `{{ useMetadata().html() }}`.

## `<Link>`, `<NavLink>` и `useNavigate`

```tsx filename="приложение/компоненты/Nav.tsx"
import { Link, NavLink, useNavigate } from "@remix-run/react";
```

```tsx filename="src/компоненты/Nav.tsx"
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

`<NavLink>` - это `Link` с `activeClassName`, а `useNavigate()(path)` - это `router.push(path)`.

## `redirect` и сеансы

```tsx filename="приложение/маршруты/dashboard.tsx"
export async function loader({ request }: LoaderFunctionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  if (!session.has("user")) throw redirect("/login");
  return null;
}
```

`middleware.py` в папке выполняется перед каждым маршрутом ниже нее, включая страницы:

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

`createCookieSessionStorage` становится одним полем `nexyconfig.py`, а `request.session` - это словарь:

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

## Границы ошибок

Экспорт маршрута `ErrorBoundary` не имеет эквивалента в Nexy. Сбой загрузчика - это код состояния: клиенты API получают `{"detail": ...}`, а неизвестный URL-адрес отображает `src/routes/notfound.tsx`. Ошибки, возникающие во время рендеринга компонента, перехватываются вашей собственной границей ошибок React вокруг части, которая может выйти из строя.

## `headers` и кеширование

```tsx filename="приложение/маршруты/news.tsx"
export const headers = () => ({ "Cache-Control": "public, s-maxage=60, stale-while-revalidate=60" });
```

В режиме сервера одна строка заголовка отправляет этот заголовок и сохраняет отображаемую страницу:

```nexy filename="src/маршруты/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## Бег

| Remix / React Маршрутизатор | Некси |
|---|---|
| `npx create-react-router` | `nx new`, шаблон `web-fbr-react` |
| `react-router dev` | `nx dev` |
| `react-router build`, затем `react-router-serve` | `nx build`, затем `nx start` |
| `public/` | `public/`, служил в `/` |
| Узел во время выполнения | Python во время выполнения; Node собирает только клиентские пакеты |

## Следующие шаги

- [От Next.js до Некси](nextjs.md)
- [React в Некси](../views/react/differences.md)
- [Действия](../guides/actions.md)
- [Режим сервера и режим клиента](../routing/fbr/modes.md)
