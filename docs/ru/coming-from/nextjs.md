# От Next.js до Некси

В Nexy проект Next.js App Router сохраняет свои файловые маршруты, макеты и React компоненты, в то время как серверный код, обработчики маршрутов и действия сервера перемещаются в Python файлы рядом с ними.

В каждом разделе ниже показана привычка Next.js, затем то же самое в Nexy.

## Сначала выберите режим

Приложение Next.js объединяет серверные и клиентские компоненты в одном дереве. Проект Nexy выбирает одну из двух форм в `nexyconfig.py`:

| Ваше Next.js приложение | Некси-режим | Страницы |
|---|---|---|
| в основном интерактивная, клиентская навигация | клиентский режим, `useCSR = True` | `.tsx` файлы, например `app/` |
| в основном контент, несколько интерактивных частей | режим сервера, по умолчанию | `.nexy` страниц с React островами |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

В разделах ниже используется клиентский режим, если не указано иное. См. [Режим сервера и режим клиента](../routing/fbr/modes.md).

## `page.tsx`

```tsx filename="приложение/о/page.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

Страница — это сам файл, а не `page.tsx` внутри папки:

```tsx filename="src/маршруты/about.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

`app/page.tsx` — это `src/routes/index.tsx`, а `app/blog/page.tsx` — это `src/routes/blog/index.tsx`.

## Маршрутизация файлов, маршрутизатор приложений и маршрутизатор страниц

Оба маршрутизатора Next.js отображаются на `src/routes/`. Файл Pages Router сохраняет свой путь; `page.tsx` App Router становится `index.tsx` или файлом, названным в честь его папки:

| Next.js | Некси |
|---|---|
| `pages/about.tsx` | `src/routes/about.tsx` |
| `pages/blog/[slug].tsx` | `src/routes/blog/[slug].tsx` |
| `app/about/page.tsx` | `src/routes/about/index.tsx` или `src/routes/about.tsx` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug]/index.tsx` или `src/routes/blog/[slug].tsx` |
| `app/docs/[...slug]/page.tsx` | `src/routes/docs/[...slug].tsx` |
| `app/(marketing)/pricing/page.tsx` | `src/routes/(marketing)/pricing.tsx` |
| `pages/api/items/[id].ts` | `src/routes/api/items/[id].py` |
| `app/api/items/[id]/route.ts` | `src/routes/api/items/[id].py` или `src/routes/api/items/[id]/index.py` |

Файл `.tsx` — это страница, а файл `.py` — это обработчик: расширение указывает, что это такое, поэтому обработчик маршрута теряет свою папку `/route`.

## Динамические сегменты и `params`

```tsx filename="приложение/блог/[слаг]/page.tsx"
export default async function Post({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
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

`[...slug]` и группы маршрутов, такие как `(marketing)`, работают так же, как в Next.js.

## `generateStaticParams`

```tsx filename="приложение/блог/[слаг]/page.tsx"
export async function generateStaticParams() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

Тот же экспорт под этим именем или `getStaticParams` дает один предварительно обработанный документ для каждого значения. Nexy вызывает его без `await`, поэтому верните сам массив:

```tsx filename="src/маршруты/блог/[слизень].tsx"
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

```tsx filename="приложение/layout.tsx"
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

Тот же файл, на одну папку выше: корневой макет содержит `<html>`, а `layout.tsx` в подпапке находится внутри него.

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

## `metadata`

```tsx filename="приложение/блог/page.tsx"
export const metadata = { title: "Blog", description: "Posts about Nexy" };
```

Страница `.tsx` не имеет экспорта `metadata`: запишите теги в корневом макете. В режиме сервера страница `.nexy` устанавливает их для каждой страницы:

```nexy filename="src/маршруты/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

Корень `layout.nexy` записывает теги вместо Next.js в `<head>`:

```nexy filename="src/маршруты/layout.nexy"
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

## `next/link` и `next/navigation`

```tsx filename="приложение/nav.tsx"
"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
```

Те же имена из `@nexy/client`:

```tsx filename="src/компоненты/Nav.tsx"
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

## Обработчики маршрутов

```ts filename="приложение/api/items/[id]/route.ts"
export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return Response.json({ id: Number(id) });
}
```

Тот же экспорт `GET` в формате Python без `/route`:

```python filename="src/маршруты/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

Тело — это модель Pydantic, а `/docs` перечисляет все обработчики:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## Действия сервера и `revalidatePath`

```ts filename="приложение/actions.ts"
"use server";
import { revalidatePath } from "next/cache";

export async function addTodo(title: string) {
  await db.todo.create({ data: { title } });
  revalidatePath("/todos");
}
```

Действие — это функция Python. Nexy генерирует типизированного клиента в `@nexy/actions`:

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

`useActionState` и `useFormStatus` отображаются на `pending`, `error` и `data` из `useAction`.

## Компоненты сервера — это `.nexy` страниц.

```tsx filename="приложение/пользователи/page.tsx"
export default async function Users() {
  const users = await db.user.findMany();
  return <ul>{users.map((user) => <li key={user.id}>{user.name}</li>)}</ul>;
}
```

Серверный компонент Next.js запускается на сервере, считывает данные и отправляет HTML. Страница `.nexy` — это то же самое в режиме сервера: ее фронтальная часть — это тело асинхронного компонента в Python, а шаблон — это то, что она возвращает.

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

| Next.js серверный компонент | `.nexy` страница |
|---|---|
| `app/users/page.tsx`, нет `"use client"` | `src/routes/users.nexy` |
| `await db.user.findMany()` в компоненте | запрос в заголовке |
| `{params}` и `{searchParams}` | `slug: prop[str]` и `useSearchParams()` |
| `cookies()` и `headers()` из `next/headers` | `useCookies()` и `useHeaders()` |
| `export const revalidate = 60` | `revalidate = 60` |
| компонент `"use client"` внутри него | остров: `<Counter directive="client:load" />` |

В клиентском режиме страница `.tsx` запускается в браузере, поэтому она считывает данные из обработчика:

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

## `"use client"` компоненты внутри страниц сервера

```tsx filename="приложение/page.tsx"
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

В режиме сервера клиентский компонент представляет собой остров, и его директива гласит, когда он гидратируется:

```nexy filename="src/маршруты/home.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

```tsx filename="src/компоненты/Counter.tsx"
import { useState } from "react";

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

См. [Острова](../rendering/islands.md) для `client:load`, `client:idle`, `client:visible` и `client:media`.

## ISR с `revalidate`

```tsx filename="приложение/новости/page.tsx"
export const revalidate = 60;
```

Та же строка в начале страницы серверного режима:

```nexy filename="src/маршруты/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## `middleware.ts`

```ts filename="промежуточное программное обеспечение.ts"
import { NextResponse, type NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  if (!request.cookies.get("session")) return NextResponse.redirect(new URL("/login", request.url));
}

export const config = { matcher: "/dashboard/:path*" };
```

`matcher` — это папка: `middleware.py` в `dashboard/` оборачивает каждый маршрут ниже нее.

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

## `notFound()` и `not-found.tsx`

```tsx filename="приложение/блог/[слаг]/page.tsx"
import { notFound } from "next/navigation";

if (!post) notFound();
```

В обработчике поднимите; на странице режима сервера вызовите `notFound()`:

```python filename="src/routes/api/posts/[slug].py"
from nexy.http import HTTPException

POSTS = {"hello": "Hello, world"}


async def GET(slug: str):
    if slug not in POSTS:
        raise HTTPException(status_code=404, detail="No such post")
    return {"title": POSTS[slug]}
```

`app/not-found.tsx` — это `src/routes/notfound.tsx` в режиме клиента и `notfound.nexy` в режиме сервера.

## `next/image`

```tsx
import Image from "next/image";

<Image src="/logo.png" alt="Logo" width={128} height={32} />
```

На странице `.nexy` компонент `Image` из `nexy`:

```nexy filename="src/маршруты/brand.nexy"
---
from nexy import Image
---
<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

## Бег

| Next.js | Некси |
|---|---|
| `npx create-next-app` | `nx new`, шаблон `web-fbr-react` |
| `next dev` | `nx dev` |
| `next build && next start` | `nx build`, затем `nx start` |
| `public/` | `public/`, служил в `/` |
| Узел во время выполнения | Python во время выполнения; Node собирает только клиентские пакеты |

## Следующие шаги

- [Режим сервера и режим клиента](../routing/fbr/modes.md)
- [React в Некси](../views/react/differences.md)
- [Действия](../guides/actions.md)
- [Острова](../rendering/islands.md)
