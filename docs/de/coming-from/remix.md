# Von Remix zu Nexy

In Nexy behält eine Remix- oder React-Router-Route ihre React-Komponente, während ihr `loader` zu einem Python-Handler wird, ihre `action` zu einer Python-Aktion und verschachtelte Routen zu Ordnern mit einem `layout.tsx`.

Jeder Abschnitt unten zeigt eine Remix-Gewohnheit, dann dasselbe in Nexy. React Router v7 im Framework-Modus verwendet dieselben Namen.

## Wählen Sie den Modus

Eine Remix-App navigiert auf dem Client und wird daher dem Client-Modus zugeordnet:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

Eine Content-Site, die nur wenige interaktive Teile benötigt, passt besser zum Servermodus: `.nexy` Seiten mit React Inseln. Siehe [Servermodus und Clientmodus](../routing/fbr/modes.md).

## Dateien weiterleiten

| Remix (`app/routes/`) | Nexy (`src/routes/`) |
|---|---|
| `_index.tsx` | `index.tsx` |
| `about.tsx` | `about.tsx` |
| `blog.$slug.tsx` | `blog/[slug].tsx` |
| `files.$.tsx` (Spritzer) | `files/[...path].tsx` |
| `_auth.login.tsx` (wegloses Layout) | `(auth)/login.tsx`, eine Routengruppe |
| `api.items.$id.ts` (Ressourcenroute) | `api/items/[id].py` |

Punkte werden zu Ordnern und `$param` wird zu `[param]`.

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

## `loader` und `useLoaderData`

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

Der Loader wechselt zu einem Python-Handler und die Seite liest ihn:

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

Im Servermodus ist eine `.nexy`-Seite der Loader und die Ansicht in einer Datei, und die Daten befinden sich im ersten HTML:

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

## `params` und `request` in einem Lader

```tsx filename="app/routes/api.orders.$id.ts"
export async function loader({ params, request }: LoaderFunctionArgs) {
  const currency = new URL(request.url).searchParams.get("currency") ?? "EUR";
  if (Number(params.id) > 100) throw new Response("No such order", { status: 404 });
  return json({ id: Number(params.id), currency });
}
```

Pfad- und Abfragewerte sind typisierte Parameter und es wird ein Fehler ausgegeben:

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `action`, `<Form>` und `useActionData`

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

Die Aktion ist eine Python-Funktion mit einem typisierten Client, und `useAction` enthält, was `useActionData` und `useNavigation().state` enthalten:

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

`revalidate("/todos")` macht das, was Remix nach jeder Aktion macht: Die Seite lädt ihre Daten erneut.

## `useFetcher`

```tsx
const fetcher = useFetcher();
fetcher.submit({ title: "Write the docs" }, { method: "post", action: "/todos" });
```

`useAction` ist ein Fetcher, der an eine Aktion gebunden ist: Rufen Sie ihn von so vielen Komponenten auf, wie Sie benötigen, jede mit ihrem eigenen `pending` und `data`.

## Progressive Verbesserung

Ein Remix `<Form>` funktioniert, bevor JavaScript geladen wird. Im Servermodus postet ein einfaches Formular auf die gleiche Weise an eine Aktion, und der Besucher kehrt mit einem `303` zur Seite zurück:

```nexy filename="src/routes/notes.nexy"
---
from src.actions.todos import add_todo
---
<form method="post" action="{{ __actions_path['add_todo'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
```

## Verschachtelte Routen und `<Outlet />`

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

Die übergeordnete Route wird zur `layout.tsx` des Ordners und `<Outlet />` wird zu `children`:

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

Der Root `layout.tsx` ist Eigentümer des Dokuments. Es gibt kein `<Scripts />` oder `<Links />` zum Platzieren: Nexy fügt das Client-Bundle selbst hinzu.

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

Eine `.tsx`-Seite hat keinen `meta`-Export: Schreiben Sie die Tags in das Root-Layout. Im Servermodus setzt eine `.nexy`-Seite sie mit `metadata = {...}` und ihr Layout schreibt sie mit `{{ useMetadata().html() }}`.

## `<Link>`, `<NavLink>` und `useNavigate`

```tsx filename="app/components/Nav.tsx"
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

`<NavLink>` ist ein `Link` mit `activeClassName` und `useNavigate()(path)` ist `router.push(path)`.

## `redirect` und Sitzungen

```tsx filename="app/routes/dashboard.tsx"
export async function loader({ request }: LoaderFunctionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  if (!session.has("user")) throw redirect("/login");
  return null;
}
```

Ein `middleware.py` im Ordner läuft vor jeder Route darunter, einschließlich Seiten:

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

`createCookieSessionStorage` wird zu einem Feld von `nexyconfig.py` und `request.session` ist ein Diktat:

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

## Fehlergrenzen

Der `ErrorBoundary`-Export einer Route hat kein Nexy-Äquivalent. Ein fehlgeschlagener Lader ist ein Statuscode: API-Clients erhalten `{"detail": ...}` und eine unbekannte URL rendert `src/routes/notfound.tsx`. Fehler, die beim Rendern einer Komponente ausgelöst werden, werden von einer eigenen React Fehlergrenze um den Teil abgefangen, der fehlschlagen kann.

## `headers` und Caching

```tsx filename="app/routes/news.tsx"
export const headers = () => ({ "Cache-Control": "public, s-maxage=60, stale-while-revalidate=60" });
```

Im Servermodus sendet eine Zeile im Frontmatter diesen Header und behält die gerenderte Seite:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## Laufen

| Remix / React Router | Nexy |
|---|---|
| `npx create-react-router` | `nx new`, Vorlage `web-fbr-react` |
| `react-router dev` | `nx dev` |
| `react-router build`, dann `react-router-serve` | `nx build`, dann `nx start` |
| `public/` | `public/`, zugestellt in `/` |
| Knoten zur Laufzeit | Python zur Laufzeit; Der Knoten erstellt nur die Client-Bundles |

## Nächste Schritte

- [Von Next.js zu Nexy](nextjs.md)
- [React in Nexy](../views/react/differences.md)
- [Aktionen](../guides/actions.md)
- [Servermodus und Clientmodus](../routing/fbr/modes.md)
