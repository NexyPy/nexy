# De Next.js à Nexy

Dans Nexy, un projet Next.js App Router conserve ses routes de fichiers, ses mises en page et ses composants React, tandis que le code du serveur, les gestionnaires de routes et les actions du serveur se déplacent vers les fichiers Python à côté d'eux.

Chaque section ci-dessous montre une habitude Next.js, puis la même chose dans Nexy.

## Choisissez d'abord le mode

Une application Next.js mélange les composants serveur et client dans une seule arborescence. Un projet Nexy sélectionne l'une des deux formes dans `nexyconfig.py` :

| Votre application Next.js est | Mode Nexy | Les pages sont |
|---|---|---|
| navigation client principalement interactive | mode client, `useCSR = True` | `.tsx` fichiers, comme dans `app/` |
| principalement du contenu, quelques parties interactives | mode serveur, la valeur par défaut | `.nexy` pages avec React îles |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

Les sections ci-dessous utilisent le mode client, sauf indication contraire. Voir [Mode serveur et mode client](../routing/fbr/modes.md).

## `page.tsx`

```tsx filename="app/about/page.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

Une page est le fichier lui-même, pas un `page.tsx` dans un dossier :

```tsx filename="src/routes/about.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

`app/page.tsx` est `src/routes/index.tsx` et `app/blog/page.tsx` est `src/routes/blog/index.tsx`.

## Acheminer les fichiers, le routeur d'applications et le routeur de pages

Les deux routeurs de Next.js sont mappés à `src/routes/`. Un fichier du Pages Router garde son chemin ; un `page.tsx` de l'App Router devient `index.tsx`, ou un fichier nommé d'après son dossier :

| Next.js | Nexy |
|---|---|
| `pages/about.tsx` | `src/routes/about.tsx` |
| `pages/blog/[slug].tsx` | `src/routes/blog/[slug].tsx` |
| `app/about/page.tsx` | `src/routes/about/index.tsx`, ou `src/routes/about.tsx` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug]/index.tsx`, ou `src/routes/blog/[slug].tsx` |
| `app/docs/[...slug]/page.tsx` | `src/routes/docs/[...slug].tsx` |
| `app/(marketing)/pricing/page.tsx` | `src/routes/(marketing)/pricing.tsx` |
| `pages/api/items/[id].ts` | `src/routes/api/items/[id].py` |
| `app/api/items/[id]/route.ts` | `src/routes/api/items/[id].py`, ou `src/routes/api/items/[id]/index.py` |

Un fichier `.tsx` est une page et un fichier `.py` est un gestionnaire : l'extension indique lequel, donc un gestionnaire de route perd son dossier `/route`.

## Segments dynamiques et `params`

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

`[...slug]` et les groupes de routes tels que `(marketing)` fonctionnent comme dans Next.js.

## `generateStaticParams`

```tsx filename="app/blog/[slug]/page.tsx"
export async function generateStaticParams() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

Le même export, sous ce nom ou `getStaticParams`, donne un document pré-rendu par valeur. Nexy l'appelle sans `await`, donc renvoie le tableau lui-même :

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

Le même fichier, un dossier plus haut : la mise en page racine possède `<html>`, et un `layout.tsx` dans un sous-dossier s'y niche.

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

Une page `.tsx` n'a pas d'export `metadata` : écrivez les balises dans la mise en page racine. En mode serveur, une page `.nexy` les définit par page :

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

La racine `layout.nexy` écrit les balises là où Next.js le ferait, dans le `<head>` :

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

## `next/link` et `next/navigation`

```tsx filename="app/nav.tsx"
"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
```

Les mêmes noms, de `@nexy/client` :

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

## Gestionnaires de routes

```ts filename="app/api/items/[id]/route.ts"
export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return Response.json({ id: Number(id) });
}
```

Le même export `GET`, dans Python, sans `/route` :

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

Un corps est un modèle Pydantic, et `/docs` répertorie tous les gestionnaires :

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## Actions du serveur et `revalidatePath`

```ts filename="app/actions.ts"
"use server";
import { revalidatePath } from "next/cache";

export async function addTodo(title: string) {
  await db.todo.create({ data: { title } });
  revalidatePath("/todos");
}
```

Une action est une fonction Python. Nexy génère son client typé en `@nexy/actions` :

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

`useActionState` et `useFormStatus` correspondent aux `pending`, `error` et `data` de `useAction`.

## Les composants du serveur sont des `.nexy` pages

```tsx filename="app/utilisateurs/page.tsx"
export default async function Users() {
  const users = await db.user.findMany();
  return <ul>{users.map((user) => <li key={user.id}>{user.name}</li>)}</ul>;
}
```

Un composant serveur Next.js s'exécute sur le serveur, lit les données et envoie du HTML. Une page `.nexy` est la même chose en mode serveur : son frontmatter est le corps du composant asynchrone, dans Python, et le modèle est ce qu'il renvoie.

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

| Next.js composant serveur | `.nexy` page |
|---|---|
| `app/users/page.tsx`, non `"use client"` | `src/routes/users.nexy` |
| `await db.user.findMany()` dans le composant | une requête en première ligne |
| `{params}` et `{searchParams}` | `slug: prop[str]` et `useSearchParams()` |
| `cookies()` et `headers()` de `next/headers` | `useCookies()` et `useHeaders()` |
| `export const revalidate = 60` | `revalidate = 60` |
| un composant `"use client"` à l'intérieur | une île : `<Counter directive="client:load" />` |

En mode client, une page `.tsx` s'exécute dans le navigateur, elle lit donc les données d'un gestionnaire :

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

## `"use client"` composants dans les pages du serveur

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

En mode serveur, le composant client est un îlot, et sa directive dit lorsqu'il s'hydrate :

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

Voir [Îles](../rendering/islands.md) pour `client:load`, `client:idle`, `client:visible` et `client:media`.

## ISR avec `revalidate`

```tsx filename="app/news/page.tsx"
export const revalidate = 60;
```

La même ligne, au début d'une page en mode serveur :

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

Le `matcher` est le dossier : un `middleware.py` dans `dashboard/` enveloppe chaque route en dessous.

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

## `notFound()` et `not-found.tsx`

```tsx filename="app/blog/[slug]/page.tsx"
import { notFound } from "next/navigation";

if (!post) notFound();
```

Dans un handler, relancez ; dans une page en mode serveur, appelez `notFound()` :

```python filename="src/routes/api/posts/[slug].py"
from nexy.http import HTTPException

POSTS = {"hello": "Hello, world"}


async def GET(slug: str):
    if slug not in POSTS:
        raise HTTPException(status_code=404, detail="No such post")
    return {"title": POSTS[slug]}
```

`app/not-found.tsx` est `src/routes/notfound.tsx` en mode client et `notfound.nexy` en mode serveur.

## `next/image`

```tsx
import Image from "next/image";

<Image src="/logo.png" alt="Logo" width={128} height={32} />
```

Dans une page `.nexy`, le composant `Image` de `nexy` :

```nexy filename="src/routes/brand.nexy"
---
from nexy import Image
---
<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

## Courir

| Next.js | Nexy |
|---|---|
| `npx create-next-app` | `nx new`, modèle `web-fbr-react` |
| `next dev` | `nx dev` |
| `next build && next start` | `nx build`, puis `nx start` |
| `public/` | `public/`, servi à `/` |
| Nœud au moment de l'exécution | Python au moment de l'exécution ; Node construit uniquement les bundles clients |

## Prochaines étapes

- [Mode serveur et mode client](../routing/fbr/modes.md)
- [React à Nexy](../views/react/differences.md)
- [Actions](../guides/actions.md)
- [Îles](../rendering/islands.md)
