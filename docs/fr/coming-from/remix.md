# De Remix à Nexy

Dans Nexy, une route de routeur Remix ou React conserve son composant React, tandis que son `loader` devient un gestionnaire Python, son `action` une action Python et les routes imbriquées deviennent des dossiers avec un `layout.tsx`.

Chaque section ci-dessous montre une habitude Remix, puis la même chose dans Nexy. React Le routeur v7 en mode framework utilise les mêmes noms.

## Choisissez le mode

Une application Remix navigue sur le client, elle est donc mappée en mode client :

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

Un site de contenu qui n'a besoin que de quelques parties interactives s'adapte mieux au mode serveur : `.nexy` pages avec React îlots. Voir [Mode serveur et mode client](../routing/fbr/modes.md).

## Fichiers d'itinéraire

| Remix (`app/routes/`) | Nexy (`src/routes/`) |
|---|---|
| `_index.tsx` | `index.tsx` |
| `about.tsx` | `about.tsx` |
| `blog.$slug.tsx` | `blog/[slug].tsx` |
| `files.$.tsx` (éclaboussure) | `files/[...path].tsx` |
| `_auth.login.tsx` (mise en page sans chemin) | `(auth)/login.tsx`, un groupe de routes |
| `api.items.$id.ts` (itinéraire de ressources) | `api/items/[id].py` |

Les points deviennent des dossiers et `$param` devient `[param]`.

## `useParams`

```tsx filename="app/routes/blog.$slug.tsx"
import { useParams } from "@remix-run/react";

export default function Post() {
  const { slug } = useParams();
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

## `loader` et `useLoaderData`

```tsx filename="app/routes/users.tsx"
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

Le chargeur se déplace vers un gestionnaire Python et la page le lit :

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

En mode serveur, une page `.nexy` est le chargeur et la vue dans un seul fichier, et les données sont dans le premier HTML :

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

## `params` et `request` dans un chargeur

```tsx filename="app/routes/api.orders.$id.ts"
export async function loader({ params, request }: LoaderFunctionArgs) {
  const currency = new URL(request.url).searchParams.get("currency") ?? "EUR";
  if (Number(params.id) > 100) throw new Response("No such order", { status: 404 });
  return json({ id: Number(params.id), currency });
}
```

Les valeurs de chemin et de requête sont des paramètres saisis et une erreur est générée :

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `action`, `<Form>` et `useActionData`

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

L'action est une fonction Python avec un client typé, et `useAction` contient ce que `useActionData` et `useNavigation().state` détenaient :

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

`revalidate("/todos")` fait ce que Remix fait après chaque action : la page charge à nouveau ses données.

## `useFetcher`

```tsx
const fetcher = useFetcher();
fetcher.submit({ title: "Write the docs" }, { method: "post", action: "/todos" });
```

`useAction` est un outil de récupération lié à une seule action : appelez-le à partir d'autant de composants que nécessaire, chacun avec ses propres `pending` et `data`.

## Amélioration progressive

Un Remix `<Form>` fonctionne avant le chargement de JavaScript. En mode serveur, un formulaire simple publie une action de la même manière, et le visiteur revient à la page avec un `303` :

```nexy filename="src/routes/notes.nexy"
---
from src.actions.todos import add_todo
---
<form method="post" action="{{ __actions_path['add_todo'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
```

## Itinéraires imbriqués et `<Outlet />`

```tsx filename="app/routes/dashboard.tsx"
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

La route parent devient la `layout.tsx` du dossier, et `<Outlet />` devient `children` :

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

La racine `layout.tsx` est propriétaire du document. Il n'y a pas de `<Scripts />` ou de `<Links />` à placer : Nexy ajoute lui-même le bundle client.

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

```tsx filename="app/routes/blog.tsx"
export const meta = () => [{ title: "Blog" }, { name: "description", content: "Posts" }];
```

Une page `.tsx` n'a pas d'export `meta` : écrivez les balises dans la mise en page racine. En mode serveur, une page `.nexy` les définit avec `metadata = {...}`, et sa mise en page les écrit avec `{{ useMetadata().html() }}`.

## `<Link>`, `<NavLink>` et `useNavigate`

```tsx filename="application/composants/Nav.tsx"
import { Link, NavLink, useNavigate } from "@remix-run/react";
```

```tsx filename="src/components/Nav.tsx"
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

`<NavLink>` est un `Link` avec `activeClassName`, et `useNavigate()(path)` est `router.push(path)`.

## `redirect` et séances

```tsx filename="app/routes/dashboard.tsx"
export async function loader({ request }: LoaderFunctionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  if (!session.has("user")) throw redirect("/login");
  return null;
}
```

Un `middleware.py` dans le dossier s'exécute avant chaque itinéraire en dessous, pages incluses :

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

`createCookieSessionStorage` devient un champ de `nexyconfig.py`, et `request.session` est un dict :

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

## Limites d'erreur

L'export `ErrorBoundary` d'une route n'a pas d'équivalent Nexy. Un chargeur défaillant est un code d'état : les clients API obtiennent `{"detail": ...}` et une URL inconnue affiche `src/routes/notfound.tsx`. Les erreurs générées lors du rendu d'un composant sont détectées par votre propre limite d'erreur React, autour de la partie qui peut échouer.

## `headers` et mise en cache

```tsx filename="app/routes/news.tsx"
export const headers = () => ({ "Cache-Control": "public, s-maxage=60, stale-while-revalidate=60" });
```

En mode serveur, une ligne du frontmatter envoie cet en-tête et conserve la page rendue :

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## Courir

| Remix / React Routeur | Nexy |
|---|---|
| `npx create-react-router` | `nx new`, modèle `web-fbr-react` |
| `react-router dev` | `nx dev` |
| `react-router build`, puis `react-router-serve` | `nx build`, puis `nx start` |
| `public/` | `public/`, servi à `/` |
| Nœud au moment de l'exécution | Python au moment de l'exécution ; Node construit uniquement les bundles clients |

## Prochaines étapes

- [De Next.js à Nexy](nextjs.md)
- [React à Nexy](../views/react/differences.md)
- [Actions](../guides/actions.md)
- [Mode serveur et mode client](../routing/fbr/modes.md)
