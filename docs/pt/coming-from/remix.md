# De Remix para Nexy

No Nexy, uma rota Remix ou React Router mantém seu componente React, enquanto seu `loader` se torna um manipulador Python, seu `action` uma ação Python, e rotas aninhadas tornam-se pastas com um `layout.tsx`.

Cada seção abaixo mostra um hábito Remix, então a mesma coisa no Nexy. React O roteador v7 no modo framework usa os mesmos nomes.

## Escolha o modo

Um aplicativo Remix navega no cliente, então mapeia para o modo cliente:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

Um site de conteúdo que precisa apenas de algumas partes interativas se adapta melhor ao modo servidor: `.nexy` páginas com React ilhas. Consulte [Modo servidor e modo cliente](../routing/fbr/modes.md).

## Arquivos de rota

| Remix (`app/routes/`) | Nexy (`src/routes/`) |
|---|---|
| `_index.tsx` | `index.tsx` |
| `about.tsx` | `about.tsx` |
| `blog.$slug.tsx` | `blog/[slug].tsx` |
| `files.$.tsx` (respingo) | `files/[...path].tsx` |
| `_auth.login.tsx` (layout sem caminho) | `(auth)/login.tsx`, um grupo de rotas |
| `api.items.$id.ts` (rota do recurso) | `api/items/[id].py` |

Os pontos tornam-se pastas e `$param` torna-se `[param]`.

## `useParams`

```tsx filename="app/rotas/blog.$slug.tsx"
import { useParams } from "@remix-run/react";

export default function Post() {
  const { slug } = useParams();
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

## `loader` e `useLoaderData`

```tsx filename="app/rotas/usuários.tsx"
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

O carregador move-se para um manipulador Python e a página o lê:

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

No modo servidor, uma página `.nexy` é o carregador e a visualização em um arquivo, e os dados estão no primeiro HTML:

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

## `params` e `request` em um carregador

```tsx filename="app/routes/api.orders.$id.ts"
export async function loader({ params, request }: LoaderFunctionArgs) {
  const currency = new URL(request.url).searchParams.get("currency") ?? "EUR";
  if (Number(params.id) > 100) throw new Response("No such order", { status: 404 });
  return json({ id: Number(params.id), currency });
}
```

Os valores do caminho e da consulta são parâmetros digitados e um erro é gerado:

```python filename="src/rotas/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `action`, `<Form>` e `useActionData`

```tsx filename="app/routes/todos.tsx"
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

A ação é uma função Python com um cliente digitado, e `useAction` contém o que `useActionData` e `useNavigation().state` continham:

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

`revalidate("/todos")` faz o que Remix faz após cada ação: a página carrega seus dados novamente.

## `useFetcher`

```tsx
const fetcher = useFetcher();
fetcher.submit({ title: "Write the docs" }, { method: "post", action: "/todos" });
```

`useAction` é um buscador vinculado a uma ação: chame-o de quantos componentes você precisar, cada um com seu próprio `pending` e `data`.

## Aprimoramento progressivo

Um Remix `<Form>` funciona antes de JavaScript ser carregado. No modo servidor, um formulário simples publica uma ação da mesma maneira, e o visitante volta à página com um `303`:

```nexy filename="src/routes/notes.nexy"
---
from src.actions.todos import add_todo
---
<form method="post" action="{{ __actions_path['add_todo'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
```

## Rotas aninhadas e `<Outlet />`

```tsx filename="app/rotas/dashboard.tsx"
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

A rota pai se torna o `layout.tsx` da pasta e `<Outlet />` se torna `children`:

```tsx filename="src/rotas/dashboard/layout.tsx"
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

```tsx filename="app/root.tsx"
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

A raiz `layout.tsx` possui o documento. Não há `<Scripts />` ou `<Links />` para colocar: Nexy adiciona o próprio pacote do cliente.

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

```tsx filename="app/rotas/blog.tsx"
export const meta = () => [{ title: "Blog" }, { name: "description", content: "Posts" }];
```

Uma página `.tsx` não tem exportação `meta`: escreva as tags no layout raiz. No modo servidor, uma página `.nexy` os define com `metadata = {...}`, e seu layout os grava com `{{ useMetadata().html() }}`.

## `<Link>`, `<NavLink>` e `useNavigate`

```tsx filename="app/componentes/Nav.tsx"
import { Link, NavLink, useNavigate } from "@remix-run/react";
```

```tsx filename="src/componentes/Nav.tsx"
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

`<NavLink>` é um `Link` com `activeClassName` e `useNavigate()(path)` é `router.push(path)`.

## `redirect` e sessões

```tsx filename="app/rotas/dashboard.tsx"
export async function loader({ request }: LoaderFunctionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  if (!session.has("user")) throw redirect("/login");
  return null;
}
```

Um `middleware.py` na pasta é executado antes de cada rota abaixo dela, incluindo páginas:

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

`createCookieSessionStorage` torna-se um campo de `nexyconfig.py` e `request.session` é um ditado:

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

## Limites de erro

A exportação `ErrorBoundary` de uma rota não tem equivalente Nexy. Um carregador com falha é um código de status: os clientes da API obtêm `{"detail": ...}` e um URL desconhecido é renderizado `src/routes/notfound.tsx`. Erros gerados durante a renderização de um componente são capturados por um React limite de erro próprio, em torno da parte que pode falhar.

## `headers` e cache

```tsx filename="app/rotas/news.tsx"
export const headers = () => ({ "Cache-Control": "public, s-maxage=60, stale-while-revalidate=60" });
```

No modo servidor, uma linha no frontmatter envia esse cabeçalho e mantém a página renderizada:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## Correndo

| Remix / React Roteador | Nexy |
|---|---|
| `npx create-react-router` | `nx new`, modelo `web-fbr-react` |
| `react-router dev` | `nx dev` |
| `react-router build`, então `react-router-serve` | `nx build`, então `nx start` |
| `public/` | `public/`, servido em `/` |
| Nó em tempo de execução | Python em tempo de execução; O nó apenas cria os pacotes do cliente |

## Próximas etapas

- [De Next.js para Nexy](nextjs.md)
- [React em Nexy](../views/react/differences.md)
- [Ações](../guides/actions.md)
- [Modo servidor e modo cliente](../routing/fbr/modes.md)
