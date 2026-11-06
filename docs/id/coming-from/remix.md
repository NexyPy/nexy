# Dari Remix hingga Nexy

Di Nexy, rute Router Remix atau React mempertahankan komponen React-nya, sementara `loader`-nya menjadi penangan Python, `action`-nya menjadi tindakan Python, dan rute bersarang menjadi folder dengan `layout.tsx`.

Setiap bagian di bawah menunjukkan kebiasaan Remix, lalu hal yang sama di Nexy. React Router v7 dalam mode framework menggunakan nama yang sama.

## Pilih modenya

Aplikasi Remix bernavigasi di klien, sehingga dipetakan ke mode klien:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

Situs konten yang hanya memerlukan beberapa bagian interaktif lebih cocok dengan mode server: `.nexy` halaman dengan React pulau. Lihat [Mode server dan mode klien](../routing/fbr/modes.md).

## File rute

| Remix (`app/routes/`) | Nexy (`src/routes/`) |
|---|---|
| `_index.tsx` | `index.tsx` |
| `about.tsx` | `about.tsx` |
| `blog.$slug.tsx` | `blog/[slug].tsx` |
| `files.$.tsx` (percikan) | `files/[...path].tsx` |
| `_auth.login.tsx` (tata letak tanpa jalur) | `(auth)/login.tsx`, grup rute |
| `api.items.$id.ts` (rute sumber daya) | `api/items/[id].py` |

Titik menjadi folder, dan `$param` menjadi `[param]`.

## `useParams`

```tsx filename="aplikasi/rute/blog.$slug.tsx"
import { useParams } from "@remix-run/react";

export default function Post() {
  const { slug } = useParams();
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

## `loader` dan `useLoaderData`

```tsx filename="aplikasi/rute/pengguna.tsx"
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

Pemuat berpindah ke pengendali Python, dan halaman membacanya:

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

Dalam mode server, halaman `.nexy` adalah pemuat dan tampilan dalam satu file, dan datanya ada dalam HTML pertama:

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

## `params` dan `request` di loader

```tsx filename="app/routes/api.orders.$id.ts"
export async function loader({ params, request }: LoaderFunctionArgs) {
  const currency = new URL(request.url).searchParams.get("currency") ?? "EUR";
  if (Number(params.id) > 100) throw new Response("No such order", { status: 404 });
  return json({ id: Number(params.id), currency });
}
```

Nilai jalur dan kueri adalah parameter yang diketik, dan kesalahan muncul:

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `action`, `<Form>` dan `useActionData`

```tsx filename="aplikasi/rute/todos.tsx"
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

Tindakannya adalah fungsi Python dengan klien yang diketik, dan `useAction` menyimpan apa yang dimiliki `useActionData` dan `useNavigation().state`:

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

`revalidate("/todos")` melakukan apa yang dilakukan Remix setelah setiap tindakan: halaman memuat datanya lagi.

## `useFetcher`

```tsx
const fetcher = useFetcher();
fetcher.submit({ title: "Write the docs" }, { method: "post", action: "/todos" });
```

`useAction` adalah pengambil yang terikat pada satu tindakan: panggil dari sebanyak mungkin komponen yang Anda perlukan, masing-masing dengan `pending` dan `data` miliknya sendiri.

## Peningkatan progresif

A Remix `<Form>` berfungsi sebelum JavaScript dimuat. Dalam mode server, formulir biasa memposting tindakan dengan cara yang sama, dan pengunjung kembali ke halaman dengan `303`:

```nexy filename="src/rute/catatan.nexy"
---
from src.actions.todos import add_todo
---
<form method="post" action="{{ __actions_path['add_todo'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
```

## Rute bersarang dan `<Outlet />`

```tsx filename="aplikasi/rute/dashboard.tsx"
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

Rute induk menjadi `layout.tsx` folder, dan `<Outlet />` menjadi `children`:

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

```tsx filename="aplikasi/root.tsx"
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

Root `layout.tsx` memiliki dokumen tersebut. Tidak ada `<Scripts />` atau `<Links />` untuk ditempatkan: Nexy menambahkan bundel klien itu sendiri.

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

## `meta`

```tsx filename="aplikasi/rute/blog.tsx"
export const meta = () => [{ title: "Blog" }, { name: "description", content: "Posts" }];
```

Halaman `.tsx` tidak memiliki ekspor `meta`: tulis tag di tata letak root. Dalam mode server, halaman `.nexy` mengaturnya dengan `metadata = {...}`, dan tata letaknya menuliskannya dengan `{{ useMetadata().html() }}`.

## `<Link>`, `<NavLink>` dan `useNavigate`

```tsx filename="aplikasi/komponen/Nav.tsx"
import { Link, NavLink, useNavigate } from "@remix-run/react";
```

```tsx filename="src/komponen/Nav.tsx"
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

`<NavLink>` adalah `Link` dengan `activeClassName`, dan `useNavigate()(path)` adalah `router.push(path)`.

## `redirect` dan sesi

```tsx filename="aplikasi/rute/dashboard.tsx"
export async function loader({ request }: LoaderFunctionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  if (!session.has("user")) throw redirect("/login");
  return null;
}
```

A `middleware.py` dalam folder dijalankan sebelum setiap rute di bawahnya, termasuk halaman:

```python filename="src/routes/dashboard/middleware.py"
from nexy.http import RedirectResponse, Request


async def middleware(request: Request, call_next):
    if "user" not in request.session:
        return RedirectResponse("/login", status_code=307)
    return await call_next(request)
```

```python filename="src/route/dashboard/stats.py"
async def GET():
    return {"visits": 12}
```

`createCookieSessionStorage` menjadi satu bidang `nexyconfig.py`, dan `request.session` merupakan dikt:

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

## Batasan kesalahan

Ekspor `ErrorBoundary` suatu rute tidak memiliki padanan Nexy. Pemuat yang gagal adalah kode status: klien API mendapatkan `{"detail": ...}`, dan URL yang tidak dikenal dirender `src/routes/notfound.tsx`. Kesalahan terjadi saat komponen dirender ditangkap oleh batas kesalahan React Anda sendiri, di sekitar bagian yang bisa gagal.

## `headers` dan cache

```tsx filename="aplikasi/rute/berita.tsx"
export const headers = () => ({ "Cache-Control": "public, s-maxage=60, stale-while-revalidate=60" });
```

Dalam mode server, satu baris di frontmatter mengirimkan header tersebut dan menyimpan halaman yang dirender:

```nexy filename="src/rute/berita.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## Berlari

| Remix / React Perute | Nexy |
|---|---|
| `npx create-react-router` | `nx new`, templat `web-fbr-react` |
| `react-router dev` | `nx dev` |
| `react-router build`, lalu `react-router-serve` | `nx build`, lalu `nx start` |
| `public/` | `public/`, bertugas di `/` |
| Node saat runtime | Python pada saat runtime; Node hanya membuat bundel klien |

## Langkah selanjutnya

- [Dari Next.js hingga Nexy](nextjs.md)
- [React di Nexy](../views/react/differences.md)
- [Tindakan](../guides/actions.md)
- [Mode server dan mode klien](../routing/fbr/modes.md)
