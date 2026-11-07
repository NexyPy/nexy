# From Next.js to Nexy

In Nexy a Next.js App Router project keeps its file routes, layouts and React components, while
server code, route handlers and Server Actions move to Python files next to them.

Each section below shows a Next.js habit, then the same thing in Nexy.

## Pick the mode first

A Next.js app mixes server and client components in one tree. A Nexy project picks one of two
shapes in `nexyconfig.py`:

| Your Next.js app is | Nexy mode | Pages are |
|---|---|---|
| mostly interactive, client navigation | client mode, `useCSR = True` | `.tsx` files, as in `app/` |
| mostly content, a few interactive parts | server mode, the default | `.nexy` pages with React islands |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

The sections below use client mode unless they say otherwise. See
[Server mode and client mode](../routing/fbr/modes.md).

## `page.tsx`

```tsx filename="app/about/page.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

A page is the file itself, not a `page.tsx` inside a folder:

```tsx filename="src/routes/about.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

`app/page.tsx` is `src/routes/index.tsx`, and `app/blog/page.tsx` is `src/routes/blog/index.tsx`.

## Route files, App Router and Pages Router

Both routers of Next.js map to `src/routes/`. A file of the Pages Router keeps its path; a
`page.tsx` of the App Router becomes `index.tsx`, or a file named after its folder:

| Next.js | Nexy |
|---|---|
| `pages/about.tsx` | `src/routes/about.tsx` |
| `pages/blog/[slug].tsx` | `src/routes/blog/[slug].tsx` |
| `app/about/page.tsx` | `src/routes/about/index.tsx`, or `src/routes/about.tsx` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug]/index.tsx`, or `src/routes/blog/[slug].tsx` |
| `app/docs/[...slug]/page.tsx` | `src/routes/docs/[...slug].tsx` |
| `app/(marketing)/pricing/page.tsx` | `src/routes/(marketing)/pricing.tsx` |
| `pages/api/items/[id].ts` | `src/routes/api/items/[id].py` |
| `app/api/items/[id]/route.ts` | `src/routes/api/items/[id].py`, or `src/routes/api/items/[id]/index.py` |

A `.tsx` file is a page and a `.py` file is a handler: the extension says which, so a route handler
loses its `/route` folder.

## Dynamic segments and `params`

```tsx filename="app/blog/[slug]/page.tsx"
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

`[...slug]` and route groups such as `(marketing)` work as in Next.js.

## `generateStaticParams`

```tsx filename="app/blog/[slug]/page.tsx"
export async function generateStaticParams() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

The same export, under this name or `getStaticParams`, gives one pre-rendered document per value.
Nexy calls it without `await`, so return the array itself:

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

```tsx filename="app/layout.tsx"
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

The same file, one folder up: the root layout owns `<html>`, and a `layout.tsx` in a subfolder
nests inside it.

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

## `metadata`

```tsx filename="app/blog/page.tsx"
export const metadata = { title: "Blog", description: "Posts about Nexy" };
```

A `.tsx` page has no `metadata` export: write the tags in the root layout. In server mode, a
`.nexy` page sets them per page:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

The root `layout.nexy` writes the tags where Next.js would, in the `<head>`:

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

## `next/link` and `next/navigation`

```tsx filename="app/nav.tsx"
"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
```

The same names, from `@nexy/client`:

```tsx filename="src/components/Nav.tsx"
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

## Route handlers

```ts filename="app/api/items/[id]/route.ts"
export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return Response.json({ id: Number(id) });
}
```

The same `GET` export, in Python, without `/route`:

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

A body is a Pydantic model, and `/docs` lists every handler:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## Server Actions and `revalidatePath`

```ts filename="app/actions.ts"
"use server";
import { revalidatePath } from "next/cache";

export async function addTodo(title: string) {
  await db.todo.create({ data: { title } });
  revalidatePath("/todos");
}
```

An action is a Python function. Nexy generates its typed client in `@nexy/actions`:

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

`useActionState` and `useFormStatus` map to the `pending`, `error` and `data` of `useAction`.

## Server components are `.nexy` pages

```tsx filename="app/users/page.tsx"
export default async function Users() {
  const users = await db.user.findMany();
  return <ul>{users.map((user) => <li key={user.id}>{user.name}</li>)}</ul>;
}
```

A Next.js server component runs on the server, reads data and sends HTML. A `.nexy` page is the
same thing in server mode: its frontmatter is the body of the async component, in Python, and the
template is what it returns.

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

| Next.js server component | `.nexy` page |
|---|---|
| `app/users/page.tsx`, no `"use client"` | `src/routes/users.nexy` |
| `await db.user.findMany()` in the component | a query in the frontmatter |
| `{params}` and `{searchParams}` | `slug: prop[str]` and `useSearchParams()` |
| `cookies()` and `headers()` from `next/headers` | `useCookies()` and `useHeaders()` |
| `export const revalidate = 60` | `revalidate = 60` |
| a `"use client"` component inside it | an island: `<Counter directive="client:load" />` |

In client mode, a `.tsx` page runs in the browser, so it reads the data from a handler:

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

## `"use client"` components inside server pages

```tsx filename="app/page.tsx"
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

In server mode, the client component is an island, and its directive says when it hydrates:

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

```tsx filename="src/components/Counter.tsx"
import { useState } from "react";

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

See [Islands](../rendering/islands.md) for `client:load`, `client:idle`, `client:visible` and
`client:media`.

## ISR with `revalidate`

```tsx filename="app/news/page.tsx"
export const revalidate = 60;
```

The same line, in the frontmatter of a server-mode page:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## `middleware.ts`

```ts filename="middleware.ts"
import { NextResponse, type NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  if (!request.cookies.get("session")) return NextResponse.redirect(new URL("/login", request.url));
}

export const config = { matcher: "/dashboard/:path*" };
```

The `matcher` is the folder: a `middleware.py` in `dashboard/` wraps every route below it.

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

## `notFound()` and `not-found.tsx`

```tsx filename="app/blog/[slug]/page.tsx"
import { notFound } from "next/navigation";

if (!post) notFound();
```

In a handler, raise; in a server-mode page, call `notFound()`:

```python filename="src/routes/api/posts/[slug].py"
from nexy.http import HTTPException

POSTS = {"hello": "Hello, world"}


async def GET(slug: str):
    if slug not in POSTS:
        raise HTTPException(status_code=404, detail="No such post")
    return {"title": POSTS[slug]}
```

`app/not-found.tsx` is `src/routes/notfound.tsx` in client mode, and `notfound.nexy` in server mode.

## `next/image`

```tsx
import Image from "next/image";

<Image src="/logo.png" alt="Logo" width={128} height={32} />
```

In a `.nexy` page, the `Image` component of `nexy`:

```nexy filename="src/routes/brand.nexy"
---
from nexy import Image
---
<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

## Running

| Next.js | Nexy |
|---|---|
| `npx create-next-app` | `nx new`, template `web-fbr-react` |
| `next dev` | `nx dev` |
| `next build && next start` | `nx build`, then `nx start` |
| `public/` | `public/`, served at `/` |
| Node at runtime | Python at runtime; Node only builds the client bundles |

## Next steps

- [Server mode and client mode](../routing/fbr/modes.md)
- [React in Nexy](../views/react/differences.md)
- [Actions](../guides/actions.md)
- [Islands](../rendering/islands.md)
