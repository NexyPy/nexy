# De Next.js a Nexy

En Nexy, un proyecto de App Router Next.js mantiene sus rutas de archivos, diseños y React componentes, mientras que el código del servidor, los controladores de ruta y las acciones del servidor se mueven a los archivos Python junto a ellos.

Cada sección a continuación muestra un hábito Next.js, luego lo mismo en Nexy.

## Elige el modo primero

Una aplicación Next.js combina componentes de servidor y cliente en un solo árbol. Un proyecto Nexy elige una de dos formas en `nexyconfig.py`:

| Tu aplicación Next.js es | Modo Nexy | Las páginas son |
|---|---|---|
| Navegación del cliente principalmente interactiva. | modo cliente, `useCSR = True` | `.tsx` archivos, como en `app/` |
| principalmente contenido, algunas partes interactivas | modo servidor, el predeterminado | `.nexy` páginas con React islas |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

Las secciones siguientes utilizan el modo cliente a menos que indiquen lo contrario. Consulte [Modo servidor y modo cliente](../routing/fbr/modes.md).

## `page.tsx`

```tsx filename="aplicación/acerca de/página.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

Una página es el archivo en sí, no un `page.tsx` dentro de una carpeta:

```tsx filename="src/rutas/about.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

`app/page.tsx` es `src/routes/index.tsx` y `app/blog/page.tsx` es `src/routes/blog/index.tsx`.

## Segmentos dinámicos y `params`

```tsx filename="aplicación/blog/[slug]/page.tsx"
export default async function Post({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return <h1>{slug}</h1>;
}
```

```tsx filename="src/rutas/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

`[...slug]` y grupos de rutas como `(marketing)` funcionan como en Next.js.

## `generateStaticParams`

```tsx filename="aplicación/blog/[slug]/page.tsx"
export async function generateStaticParams() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

La misma exportación, bajo este nombre o `getStaticParams`, proporciona un documento pre-renderizado por valor. Nexy lo llama sin `await`, así que devuelve la matriz misma:

```tsx filename="src/rutas/blog/[slug].tsx"
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

```tsx filename="aplicación/diseño.tsx"
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

El mismo archivo, una carpeta arriba: el diseño raíz posee `<html>`, y un `layout.tsx` en una subcarpeta se anida dentro de él.

```tsx filename="src/rutas/layout.tsx"
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

```tsx filename="aplicación/blog/page.tsx"
export const metadata = { title: "Blog", description: "Posts about Nexy" };
```

Una página `.tsx` no tiene `metadata` exportación: escriba las etiquetas en el diseño raíz. En modo servidor, una página `.nexy` los establece por página:

```nexy filename="src/rutas/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

La raíz `layout.nexy` escribe las etiquetas donde lo haría Next.js, en el `<head>`:

```nexy filename="src/rutas/layout.nexy"
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

## `next/link` y `next/navigation`

```tsx filename="aplicación/nav.tsx"
"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
```

Los mismos nombres, de `@nexy/client`:

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

## Controladores de ruta

```ts filename="aplicación/api/items/[id]/ruta.ts"
export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return Response.json({ id: Number(id) });
}
```

La misma exportación `GET`, en Python, sin `/route`:

```python filename="src/rutas/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

Un cuerpo es un modelo Pydantic y `/docs` enumera todos los controladores:

```python filename="src/rutas/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## Acciones del servidor y `revalidatePath`

```ts filename="aplicación/acciones.ts"
"use server";
import { revalidatePath } from "next/cache";

export async function addTodo(title: string) {
  await db.todo.create({ data: { title } });
  revalidatePath("/todos");
}
```

Una acción es una función Python. Nexy genera su cliente escrito en `@nexy/actions`:

```python filename="src/acciones/todos.py"
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

```tsx filename="src/rutas/todos.tsx"
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

`useActionState` y `useFormStatus` se asignan a `pending`, `error` y `data` de `useAction`.

## Componentes del servidor que leen datos.

```tsx filename="aplicación/usuarios/página.tsx"
export default async function Users() {
  const users = await db.user.findMany();
  return <ul>{users.map((user) => <li key={user.id}>{user.name}</li>)}</ul>;
}
```

En modo cliente, una página no puede leer la base de datos mientras se representa: llama a un controlador o una acción.

```python filename="src/rutas/api/usuarios.py"
async def GET():
    return [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
```

```tsx filename="src/rutas/usuarios.tsx"
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

En modo servidor, eso es lo que hace una página `.nexy`: su contenido frontal es el componente del servidor asíncrono.

```nexy filename="src/rutas/personas.nexy"
---
users = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## `"use client"` componentes dentro de las páginas del servidor

```tsx filename="aplicación/página.tsx"
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

En modo servidor, el componente cliente es una isla, y su directiva dice cuando se hidrata:

```nexy filename="src/rutas/home.nexy"
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

Véase [Islas](../rendering/islands.md) para `client:load`, `client:idle`, `client:visible` y `client:media`.

## ISR con `revalidate`

```tsx filename="aplicación/noticias/page.tsx"
export const revalidate = 60;
```

La misma línea, en la portada de una página en modo servidor:

```nexy filename="src/rutas/noticias.nexy"
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

El `matcher` es la carpeta: un `middleware.py` en `dashboard/` envuelve todas las rutas debajo de él.

```python filename="src/rutas/dashboard/middleware.py"
from nexy.http import RedirectResponse, Request


async def middleware(request: Request, call_next):
    if "session" not in request.cookies:
        return RedirectResponse("/login", status_code=307)
    return await call_next(request)
```

```python filename="src/rutas/dashboard/stats.py"
async def GET():
    return {"visits": 12}
```

## `notFound()` y `not-found.tsx`

```tsx filename="aplicación/blog/[slug]/page.tsx"
import { notFound } from "next/navigation";

if (!post) notFound();
```

En un manejador, sube; en una página en modo servidor, llame a `notFound()`:

```python filename="src/routes/api/posts/[slug].py"
from nexy.http import HTTPException

POSTS = {"hello": "Hello, world"}


async def GET(slug: str):
    if slug not in POSTS:
        raise HTTPException(status_code=404, detail="No such post")
    return {"title": POSTS[slug]}
```

`app/not-found.tsx` es `src/routes/notfound.tsx` en modo cliente y `notfound.nexy` en modo servidor.

## `next/image`

```tsx
import Image from "next/image";

<Image src="/logo.png" alt="Logo" width={128} height={32} />
```

En una página `.nexy`, el componente `Image` de `nexy`:

```nexy filename="src/rutas/marca.nexy"
---
from nexy import Image
---
<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

## corriendo

| Next.js | nexy |
|---|---|
| `npx create-next-app` | `nx new`, plantilla `web-fbr-react` |
| `next dev` | `nx dev` |
| `next build && next start` | `nx build`, luego `nx start` |
| `public/` | `public/`, servido en `/` |
| Nodo en tiempo de ejecución | Python en tiempo de ejecución; Node solo crea los paquetes de clientes |

## Próximos pasos

- [Modo servidor y modo cliente](../routing/fbr/modes.md)
- [React en Nexy](../views/react/differences.md)
- [Acciones](../guides/actions.md)
- [Islas](../rendering/islands.md)
