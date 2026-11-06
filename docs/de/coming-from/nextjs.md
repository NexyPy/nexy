# Von Next.js zu Nexy

In Nexy behält ein Next.js App Router-Projekt seine Dateirouten, Layouts und React Komponenten, während Servercode, Routenhandler und Serveraktionen in Python Dateien daneben verschoben werden.

Jeder Abschnitt unten zeigt eine Next.js-Gewohnheit, dann dasselbe in Nexy.

## Wählen Sie zuerst den Modus aus

Eine Next.js-App mischt Server- und Clientkomponenten in einem Baum. Ein Nexy-Projekt wählt eine von zwei Formen in `nexyconfig.py`:

| Ihre Next.js-App ist | Nexy-Modus | Seiten sind |
|---|---|---|
| überwiegend interaktiv, Client-Navigation | Client-Modus, `useCSR = True` | `.tsx` Dateien, wie in `app/` |
| größtenteils Inhalt, ein paar interaktive Teile | Servermodus, die Standardeinstellung | `.nexy` Seiten mit React Inseln |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

In den folgenden Abschnitten wird der Client-Modus verwendet, sofern nicht anders angegeben. Siehe [Servermodus und Clientmodus](../routing/fbr/modes.md).

## `page.tsx`

```tsx filename="app/about/page.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

Eine Seite ist die Datei selbst, kein `page.tsx` in einem Ordner:

```tsx filename="src/routes/about.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

`app/page.tsx` ist `src/routes/index.tsx` und `app/blog/page.tsx` ist `src/routes/blog/index.tsx`.

## Dynamische Segmente und `params`

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

`[...slug]` und Routengruppen wie `(marketing)` funktionieren wie in Next.js.

## `generateStaticParams`

```tsx filename="app/blog/[slug]/page.tsx"
export async function generateStaticParams() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

Der gleiche Export unter diesem Namen oder `getStaticParams` liefert ein vorgerendertes Dokument pro Wert. Nexy ruft es ohne `await` auf, also gibt das Array selbst zurück:

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

Dieselbe Datei, einen Ordner höher: Das Stammlayout besitzt `<html>`, und ein `layout.tsx` in einem Unterordner ist darin verschachtelt.

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

Eine `.tsx`-Seite hat keinen `metadata`-Export: Schreiben Sie die Tags in das Root-Layout. Im Servermodus legt eine `.nexy`-Seite sie pro Seite fest:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

Die Wurzel `layout.nexy` schreibt die Tags, wo Next.js würde, im `<head>`:

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

## `next/link` und `next/navigation`

```tsx filename="app/nav.tsx"
"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
```

Die gleichen Namen, aus `@nexy/client`:

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

## Routenhandler

```ts filename="app/api/items/[id]/route.ts"
export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return Response.json({ id: Number(id) });
}
```

Derselbe `GET`-Export, in Python, ohne `/route`:

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

Ein Körper ist ein Pydantic-Modell und `/docs` listet jeden Handler auf:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## Serveraktionen und `revalidatePath`

```ts filename="app/actions.ts"
"use server";
import { revalidatePath } from "next/cache";

export async function addTodo(title: string) {
  await db.todo.create({ data: { title } });
  revalidatePath("/todos");
}
```

Eine Aktion ist eine Python Funktion. Nexy generiert seinen typisierten Client in `@nexy/actions`:

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

`useActionState` und `useFormStatus` werden den `pending`, `error` und `data` von `useAction` zugeordnet.

## Serverkomponenten, die Daten lesen

```tsx filename="app/users/page.tsx"
export default async function Users() {
  const users = await db.user.findMany();
  return <ul>{users.map((user) => <li key={user.id}>{user.name}</li>)}</ul>;
}
```

Im Clientmodus kann eine Seite die Datenbank beim Rendern nicht lesen: Sie ruft einen Handler oder eine Aktion auf.

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

Im Servermodus ist es genau das, was eine `.nexy`-Seite tut: Ihr Hauptbestandteil ist die asynchrone Serverkomponente.

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

## `"use client"` Komponenten innerhalb von Serverseiten

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

Im Servermodus ist die Client-Komponente eine Insel und ihre Anweisung besagt, wann sie hydratisiert wird:

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

Siehe [Inseln](../rendering/islands.md) für `client:load`, `client:idle`, `client:visible` und `client:media`.

## ISR mit `revalidate`

```tsx filename="app/news/page.tsx"
export const revalidate = 60;
```

Dieselbe Zeile im Titelblatt einer Servermodus-Seite:

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

Der `matcher` ist der Ordner: ein `middleware.py` in `dashboard/` umschließt jede Route darunter.

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

## `notFound()` und `not-found.tsx`

```tsx filename="app/blog/[slug]/page.tsx"
import { notFound } from "next/navigation";

if (!post) notFound();
```

Erhöhen Sie in einem Handler; Rufen Sie auf einer Seite im Servermodus `notFound()` auf:

```python filename="src/routes/api/posts/[slug].py"
from nexy.http import HTTPException

POSTS = {"hello": "Hello, world"}


async def GET(slug: str):
    if slug not in POSTS:
        raise HTTPException(status_code=404, detail="No such post")
    return {"title": POSTS[slug]}
```

`app/not-found.tsx` ist im Client-Modus `src/routes/notfound.tsx` und im Server-Modus `notfound.nexy`.

## `next/image`

```tsx
import Image from "next/image";

<Image src="/logo.png" alt="Logo" width={128} height={32} />
```

Auf einer `.nexy`-Seite ist die `Image`-Komponente von `nexy`:

```nexy filename="src/routes/brand.nexy"
---
from nexy import Image
---
<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

## Laufen

| Next.js | Nexy |
|---|---|
| `npx create-next-app` | `nx new`, Vorlage `web-fbr-react` |
| `next dev` | `nx dev` |
| `next build && next start` | `nx build`, dann `nx start` |
| `public/` | `public/`, zugestellt in `/` |
| Knoten zur Laufzeit | Python zur Laufzeit; Der Knoten erstellt nur die Client-Bundles |

## Nächste Schritte

- [Servermodus und Clientmodus](../routing/fbr/modes.md)
- [React in Nexy](../views/react/differences.md)
- [Aktionen](../guides/actions.md)
- [Inseln](../rendering/islands.md)
