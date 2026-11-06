# From Remix to Nexy

In Nexy a Remix or React Router route keeps its React component, while its `loader` becomes a
Python handler, its `action` a Python action, and nested routes become folders with a `layout.tsx`.

Each section below shows a Remix habit, then the same thing in Nexy. React Router v7 in framework
mode uses the same names.

## Pick the mode

A Remix app navigates on the client, so it maps to client mode:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

A content site that only needs a few interactive parts fits server mode better: `.nexy` pages
with React islands. See [Server mode and client mode](../routing/fbr/modes.md).

## Route files

| Remix (`app/routes/`) | Nexy (`src/routes/`) |
|---|---|
| `_index.tsx` | `index.tsx` |
| `about.tsx` | `about.tsx` |
| `blog.$slug.tsx` | `blog/[slug].tsx` |
| `files.$.tsx` (splat) | `files/[...path].tsx` |
| `_auth.login.tsx` (pathless layout) | `(auth)/login.tsx`, a route group |
| `api.items.$id.ts` (resource route) | `api/items/[id].py` |

Dots become folders, and `$param` becomes `[param]`.

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

## `loader` and `useLoaderData`

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

The loader moves to a Python handler, and the page reads it:

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

In server mode, a `.nexy` page is the loader and the view in one file, and the data is in the first
HTML:

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

## `params` and `request` in a loader

```tsx filename="app/routes/api.orders.$id.ts"
export async function loader({ params, request }: LoaderFunctionArgs) {
  const currency = new URL(request.url).searchParams.get("currency") ?? "EUR";
  if (Number(params.id) > 100) throw new Response("No such order", { status: 404 });
  return json({ id: Number(params.id), currency });
}
```

Path and query values are typed parameters, and an error is raised:

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `action`, `<Form>` and `useActionData`

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

The action is a Python function with a typed client, and `useAction` holds what `useActionData`
and `useNavigation().state` held:

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

`revalidate("/todos")` does what Remix does after every action: the page loads its data again.

## `useFetcher`

```tsx
const fetcher = useFetcher();
fetcher.submit({ title: "Write the docs" }, { method: "post", action: "/todos" });
```

`useAction` is a fetcher bound to one action: call it from as many components as you need, each
with its own `pending` and `data`.

## Progressive enhancement

A Remix `<Form>` works before JavaScript loads. In server mode, a plain form posts to an action the
same way, and the visitor comes back to the page with a `303`:

```nexy filename="src/routes/notes.nexy"
---
from src.actions.todos import add_todo
---
<form method="post" action="{{ __actions_path['add_todo'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
```

## Nested routes and `<Outlet />`

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

The parent route becomes the `layout.tsx` of the folder, and `<Outlet />` becomes `children`:

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

The root `layout.tsx` owns the document. There is no `<Scripts />` or `<Links />` to place: Nexy
adds the client bundle itself.

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

A `.tsx` page has no `meta` export: write the tags in the root layout. In server mode, a `.nexy`
page sets them with `metadata = {...}`, and its layout writes them with
`{{ useMetadata().html() }}`.

## `<Link>`, `<NavLink>` and `useNavigate`

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

`<NavLink>` is a `Link` with `activeClassName`, and `useNavigate()(path)` is `router.push(path)`.

## `redirect` and sessions

```tsx filename="app/routes/dashboard.tsx"
export async function loader({ request }: LoaderFunctionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  if (!session.has("user")) throw redirect("/login");
  return null;
}
```

A `middleware.py` in the folder runs before every route below it, pages included:

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

`createCookieSessionStorage` becomes one field of `nexyconfig.py`, and `request.session` is a dict:

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

## Error boundaries

A route's `ErrorBoundary` export has no Nexy equivalent. A failed loader is a status code: API
clients get `{"detail": ...}`, and an unknown URL renders `src/routes/notfound.tsx`. Errors thrown
while a component renders are caught by a React error boundary of your own, around the part that
can fail.

## `headers` and caching

```tsx filename="app/routes/news.tsx"
export const headers = () => ({ "Cache-Control": "public, s-maxage=60, stale-while-revalidate=60" });
```

In server mode, one line in the frontmatter sends that header and keeps the rendered page:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## Running

| Remix / React Router | Nexy |
|---|---|
| `npx create-react-router` | `nx new`, template `web-fbr-react` |
| `react-router dev` | `nx dev` |
| `react-router build`, then `react-router-serve` | `nx build`, then `nx start` |
| `public/` | `public/`, served at `/` |
| Node at runtime | Python at runtime; Node only builds the client bundles |

## Next steps

- [From Next.js to Nexy](nextjs.md)
- [React in Nexy](../views/react/differences.md)
- [Actions](../guides/actions.md)
- [Server mode and client mode](../routing/fbr/modes.md)
