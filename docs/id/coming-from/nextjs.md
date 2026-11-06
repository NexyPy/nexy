# Dari Next.js hingga Nexy

Di Nexy, proyek Next.js App Router menyimpan rute file, tata letak, dan komponen React, sementara kode server, penangan rute, dan Tindakan Server dipindahkan ke file Python di sebelahnya.

Setiap bagian di bawah menunjukkan kebiasaan Next.js, lalu hal yang sama di Nexy.

## Pilih modenya terlebih dahulu

Aplikasi Next.js menggabungkan komponen server dan klien dalam satu pohon. Proyek Nexy memilih salah satu dari dua bentuk di `nexyconfig.py`:

| Aplikasi Next.js Anda adalah | Modus Nexy | Halaman adalah |
|---|---|---|
| sebagian besar interaktif, navigasi klien | mode klien, `useCSR = True` | `.tsx` file, seperti pada `app/` |
| sebagian besar konten, beberapa bagian interaktif | mode server, default | `.nexy` halaman dengan React pulau |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

Bagian di bawah ini menggunakan mode klien kecuali dinyatakan lain. Lihat [Mode server dan mode klien](../routing/fbr/modes.md).

## `page.tsx`

```tsx filename="aplikasi/tentang/halaman.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

Halaman adalah file itu sendiri, bukan `page.tsx` di dalam folder:

```tsx filename="src/rute/tentang.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

`app/page.tsx` adalah `src/routes/index.tsx`, dan `app/blog/page.tsx` adalah `src/routes/blog/index.tsx`.

## Segmen dinamis dan `params`

```tsx filename="aplikasi/blog/[siput]/halaman.tsx"
export default async function Post({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return <h1>{slug}</h1>;
}
```

```tsx filename="src/rute/blog/[siput].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

`[...slug]` dan grup rute seperti `(marketing)` berfungsi seperti pada Next.js.

## `generateStaticParams`

```tsx filename="aplikasi/blog/[siput]/halaman.tsx"
export async function generateStaticParams() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

Ekspor yang sama, dengan nama ini atau `getStaticParams`, memberikan satu dokumen pra-render per nilai. Nexy memanggilnya tanpa `await`, jadi kembalikan array itu sendiri:

```tsx filename="src/rute/blog/[siput].tsx"
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

```tsx filename="aplikasi/tata letak.tsx"
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

File yang sama, satu folder ke atas: tata letak root memiliki `<html>`, dan `layout.tsx` dalam subfolder bersarang di dalamnya.

```tsx filename="src/route/layout.tsx"
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

```tsx filename="aplikasi/blog/halaman.tsx"
export const metadata = { title: "Blog", description: "Posts about Nexy" };
```

Halaman `.tsx` tidak memiliki ekspor `metadata`: tulis tag di tata letak root. Dalam mode server, halaman `.nexy` mengaturnya per halaman:

```nexy filename="src/rute/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

Root `layout.nexy` menulis tag di mana Next.js akan, di `<head>`:

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

## `next/link` dan `next/navigation`

```tsx filename="app/nav.tsx"
"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
```

Nama yang sama, dari `@nexy/client`:

```tsx filename="src/komponen/Nav.tsx"
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

## Pengendali rute

```ts filename="app/api/items/[id]/route.ts"
export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return Response.json({ id: Number(id) });
}
```

Ekspor `GET` yang sama, di Python, tanpa `/route`:

```python filename="src/routes/api/item/[id].py"
async def GET(id: int):
    return {"id": id}
```

Tubuh adalah model Pydantic, dan `/docs` mencantumkan setiap penangan:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## Tindakan Server dan `revalidatePath`

```ts filename="aplikasi/tindakan.ts"
"use server";
import { revalidatePath } from "next/cache";

export async function addTodo(title: string) {
  await db.todo.create({ data: { title } });
  revalidatePath("/todos");
}
```

Suatu tindakan adalah fungsi Python. Nexy menghasilkan klien yang diketiknya di `@nexy/actions`:

```python filename="src/aksi/todos.py"
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

```tsx filename="src/rute/todos.tsx"
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

`useActionState` dan `useFormStatus` dipetakan ke `pending`, `error` dan `data` dari `useAction`.

## Komponen server yang membaca data

```tsx filename="aplikasi/pengguna/halaman.tsx"
export default async function Users() {
  const users = await db.user.findMany();
  return <ul>{users.map((user) => <li key={user.id}>{user.name}</li>)}</ul>;
}
```

Dalam mode klien, halaman tidak dapat membaca database saat sedang dirender: halaman memanggil pengendali atau tindakan.

```python filename="src/routes/api/users.py"
async def GET():
    return [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
```

```tsx filename="src/rute/pengguna.tsx"
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

Dalam mode server, itulah yang dilakukan halaman `.nexy`: materi depannya adalah komponen server asinkron.

```nexy filename="src/rute/orang.nexy"
---
users = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## `"use client"` komponen di dalam halaman server

```tsx filename="aplikasi/halaman.tsx"
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

Dalam mode server, komponen klien adalah sebuah pulau, dan arahannya menyatakan kapan terhidrasi:

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

Lihat [Pulau](../rendering/islands.md) untuk `client:load`, `client:idle`, `client:visible` dan `client:media`.

## ISR dengan `revalidate`

```tsx filename="aplikasi/berita/halaman.tsx"
export const revalidate = 60;
```

Baris yang sama, di bagian depan halaman mode server:

```nexy filename="src/rute/berita.nexy"
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

`matcher` adalah foldernya: `middleware.py` di `dashboard/` membungkus setiap rute di bawahnya.

```python filename="src/routes/dashboard/middleware.py"
from nexy.http import RedirectResponse, Request


async def middleware(request: Request, call_next):
    if "session" not in request.cookies:
        return RedirectResponse("/login", status_code=307)
    return await call_next(request)
```

```python filename="src/route/dashboard/stats.py"
async def GET():
    return {"visits": 12}
```

## `notFound()` dan `not-found.tsx`

```tsx filename="aplikasi/blog/[siput]/halaman.tsx"
import { notFound } from "next/navigation";

if (!post) notFound();
```

Di pawang, angkat; di halaman mode server, panggil `notFound()`:

```python filename="src/routes/api/posts/[siput].py"
from nexy.http import HTTPException

POSTS = {"hello": "Hello, world"}


async def GET(slug: str):
    if slug not in POSTS:
        raise HTTPException(status_code=404, detail="No such post")
    return {"title": POSTS[slug]}
```

`app/not-found.tsx` adalah `src/routes/notfound.tsx` dalam mode klien, dan `notfound.nexy` dalam mode server.

## `next/image`

```tsx
import Image from "next/image";

<Image src="/logo.png" alt="Logo" width={128} height={32} />
```

Di halaman `.nexy`, komponen `Image` dari `nexy`:

```nexy filename="src/rute/merek.nexy"
---
from nexy import Image
---
<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

## Berlari

| Next.js | Nexy |
|---|---|
| `npx create-next-app` | `nx new`, templat `web-fbr-react` |
| `next dev` | `nx dev` |
| `next build && next start` | `nx build`, lalu `nx start` |
| `public/` | `public/`, bertugas di `/` |
| Node saat runtime | Python pada saat runtime; Node hanya membuat bundel klien |

## Langkah selanjutnya

- [Mode server dan mode klien](../routing/fbr/modes.md)
- [React di Nexy](../views/react/differences.md)
- [Tindakan](../guides/actions.md)
- [Kepulauan](../rendering/islands.md)
