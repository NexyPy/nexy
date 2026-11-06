# De Next.js para Nexy

No Nexy, um projeto Next.js App Router mantém suas rotas de arquivos, layouts e React componentes, enquanto o código do servidor, manipuladores de rotas e ações do servidor são movidos para Python arquivos próximos a eles.

Cada seção abaixo mostra um hábito Next.js, então a mesma coisa no Nexy.

## Escolha o modo primeiro

Um aplicativo Next.js mistura componentes de servidor e cliente em uma árvore. Um projeto Nexy escolhe uma das duas formas em `nexyconfig.py`:

| Seu Next.js aplicativo é | Modo Nexy | As páginas são |
|---|---|---|
| principalmente interativo, navegação do cliente | modo cliente, `useCSR = True` | `.tsx` arquivos, como em `app/` |
| principalmente conteúdo, algumas partes interativas | modo de servidor, o padrão | `.nexy` páginas com React ilhas |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

As seções abaixo usam o modo cliente, a menos que seja indicado o contrário. Consulte [Modo servidor e modo cliente](../routing/fbr/modes.md).

## `page.tsx`

```tsx filename="app/sobre/page.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

Uma página é o arquivo em si, não um `page.tsx` dentro de uma pasta:

```tsx filename="src/rotas/about.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

`app/page.tsx` é `src/routes/index.tsx` e `app/blog/page.tsx` é `src/routes/blog/index.tsx`.

## Arquivos de rota, roteador de aplicativos e roteador de páginas

Ambos os roteadores de Next.js mapeiam para `src/routes/`. Um arquivo do Pages Router mantém seu caminho; um `page.tsx` do App Router se torna `index.tsx`, ou um arquivo com o nome de sua pasta:

| Next.js | Nexy |
|---|---|
| `pages/about.tsx` | `src/routes/about.tsx` |
| `pages/blog/[slug].tsx` | `src/routes/blog/[slug].tsx` |
| `app/about/page.tsx` | `src/routes/about/index.tsx` ou `src/routes/about.tsx` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug]/index.tsx` ou `src/routes/blog/[slug].tsx` |
| `app/docs/[...slug]/page.tsx` | `src/routes/docs/[...slug].tsx` |
| `app/(marketing)/pricing/page.tsx` | `src/routes/(marketing)/pricing.tsx` |
| `pages/api/items/[id].ts` | `src/routes/api/items/[id].py` |
| `app/api/items/[id]/route.ts` | `src/routes/api/items/[id].py` ou `src/routes/api/items/[id]/index.py` |

Um arquivo `.tsx` é uma página e um arquivo `.py` é um manipulador: a extensão diz qual, então um manipulador de rota perde sua pasta `/route`.

## Segmentos dinâmicos e `params`

```tsx filename="app/blog/[slug]/page.tsx"
export default async function Post({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return <h1>{slug}</h1>;
}
```

```tsx filename="src/rotas/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

`[...slug]` e grupos de rotas como `(marketing)` funcionam como em Next.js.

## `generateStaticParams`

```tsx filename="app/blog/[slug]/page.tsx"
export async function generateStaticParams() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

A mesma exportação, com este nome ou `getStaticParams`, fornece um documento pré-renderizado por valor. Nexy o chama sem `await`, então retorne o próprio array:

```tsx filename="src/rotas/blog/[slug].tsx"
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

O mesmo arquivo, uma pasta acima: o layout raiz possui `<html>`, e um `layout.tsx` em uma subpasta está aninhado dentro dele.

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

Uma página `.tsx` não tem exportação `metadata`: escreva as tags no layout raiz. No modo servidor, uma página `.nexy` os define por página:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

A raiz `layout.nexy` escreve as tags onde Next.js escreveria, no `<head>`:

```nexy filename="src/rotas/layout.nexy"
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

## `next/link` e `next/navigation`

```tsx filename="app/nav.tsx"
"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
```

Os mesmos nomes, de `@nexy/client`:

```tsx filename="src/componentes/Nav.tsx"
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

## Manipuladores de rota

```ts filename="app/api/items/[id]/route.ts"
export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return Response.json({ id: Number(id) });
}
```

A mesma exportação `GET`, em Python, sem `/route`:

```python filename="src/rotas/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

Um corpo é um modelo Pydantic e `/docs` lista todos os manipuladores:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## Ações do servidor e `revalidatePath`

```ts filename="app/actions.ts"
"use server";
import { revalidatePath } from "next/cache";

export async function addTodo(title: string) {
  await db.todo.create({ data: { title } });
  revalidatePath("/todos");
}
```

Uma ação é uma função Python. Nexy gera seu cliente digitado em `@nexy/actions`:

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

`useActionState` e `useFormStatus` mapeiam para `pending`, `error` e `data` de `useAction`.

## Os componentes do servidor são `.nexy` páginas

```tsx filename="app/usuários/page.tsx"
export default async function Users() {
  const users = await db.user.findMany();
  return <ul>{users.map((user) => <li key={user.id}>{user.name}</li>)}</ul>;
}
```

Um componente de servidor Next.js é executado no servidor, lê dados e envia HTML. Uma página `.nexy` é a mesma coisa no modo servidor: seu frontmatter é o corpo do componente assíncrono, em Python, e o template é o que ele retorna.

```nexy filename="src/rotas/pessoas.nexy"
---
users = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Alan"}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

| Next.js componente do servidor | `.nexy` página |
|---|---|
| `app/users/page.tsx`, não `"use client"` | `src/routes/users.nexy` |
| `await db.user.findMany()` no componente | uma consulta no frontmatter |
| `{params}` e `{searchParams}` | `slug: prop[str]` e `useSearchParams()` |
| `cookies()` e `headers()` de `next/headers` | `useCookies()` e `useHeaders()` |
| `export const revalidate = 60` | `revalidate = 60` |
| um componente `"use client"` dentro dele | uma ilha: `<Counter directive="client:load" />` |

No modo cliente, uma página `.tsx` é executada no navegador, então ela lê os dados de um manipulador:

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

## `"use client"` componentes dentro das páginas do servidor

```tsx filename="app/página.tsx"
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

No modo servidor, o componente cliente é uma ilha, e sua diretiva diz quando ele hidrata:

```nexy filename="src/rotas/home.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

```tsx filename="src/componentes/Counter.tsx"
import { useState } from "react";

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

Veja [Ilhas](../rendering/islands.md) para `client:load`, `client:idle`, `client:visible` e `client:media`.

## ISR com `revalidate`

```tsx filename="app/notícias/page.tsx"
export const revalidate = 60;
```

A mesma linha, no frontmatter de uma página em modo servidor:

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

O `matcher` é a pasta: um `middleware.py` em `dashboard/` envolve todas as rotas abaixo dele.

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

## `notFound()` e `not-found.tsx`

```tsx filename="app/blog/[slug]/page.tsx"
import { notFound } from "next/navigation";

if (!post) notFound();
```

Em um manipulador, aumente; em uma página em modo servidor, chame `notFound()`:

```python filename="src/routes/api/posts/[slug].py"
from nexy.http import HTTPException

POSTS = {"hello": "Hello, world"}


async def GET(slug: str):
    if slug not in POSTS:
        raise HTTPException(status_code=404, detail="No such post")
    return {"title": POSTS[slug]}
```

`app/not-found.tsx` está `src/routes/notfound.tsx` no modo cliente e `notfound.nexy` no modo servidor.

## `next/image`

```tsx
import Image from "next/image";

<Image src="/logo.png" alt="Logo" width={128} height={32} />
```

Em uma página `.nexy`, o componente `Image` de `nexy`:

```nexy filename="src/routes/brand.nexy"
---
from nexy import Image
---
<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

## Correndo

| Next.js | Nexy |
|---|---|
| `npx create-next-app` | `nx new`, modelo `web-fbr-react` |
| `next dev` | `nx dev` |
| `next build && next start` | `nx build`, então `nx start` |
| `public/` | `public/`, servido em `/` |
| Nó em tempo de execução | Python em tempo de execução; O nó apenas cria os pacotes do cliente |

## Próximas etapas

- [Modo servidor e modo cliente](../routing/fbr/modes.md)
- [React em Nexy](../views/react/differences.md)
- [Ações](../guides/actions.md)
- [Ilhas](../rendering/islands.md)
