# De Remix a Nexy

En Nexy, una ruta de enrutador Remix o React mantiene su componente React, mientras que su `loader` se convierte en un controlador Python, su `action` una acción Python y las rutas anidadas se convierten en carpetas con un `layout.tsx`.

Cada sección a continuación muestra un hábito Remix, luego lo mismo en Nexy. React El enrutador v7 en modo marco usa los mismos nombres.

## Elige el modo

Una aplicación Remix navega en el cliente, por lo que se asigna al modo cliente:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

Un sitio de contenido que sólo necesita unas pocas partes interactivas se adapta mejor al modo servidor: `.nexy` páginas con React islas. Consulte [Modo servidor y modo cliente](../routing/fbr/modes.md).

## Archivos de ruta

| Remix (`app/routes/`) | Nexi (`src/routes/`) |
|---|---|
| `_index.tsx` | `index.tsx` |
| `about.tsx` | `about.tsx` |
| `blog.$slug.tsx` | `blog/[slug].tsx` |
| `files.$.tsx` (salpicar) | `files/[...path].tsx` |
| `_auth.login.tsx` (diseño sin camino) | `(auth)/login.tsx`, un grupo de rutas |
| `api.items.$id.ts` (ruta de recursos) | `api/items/[id].py` |

Los puntos se convierten en carpetas y `$param` se convierte en `[param]`.

## `useParams`

```tsx filename="aplicación/rutas/blog.$slug.tsx"
import { useParams } from "@remix-run/react";

export default function Post() {
  const { slug } = useParams();
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

## `loader` y `useLoaderData`

```tsx filename="aplicación/rutas/usuarios.tsx"
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

El cargador se mueve a un controlador Python y la página lo lee:

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

En modo servidor, una página `.nexy` es el cargador y la vista en un archivo, y los datos están en el primer HTML:

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

## `params` y `request` en un cargador

```tsx filename="aplicación/rutas/api.orders.$id.ts"
export async function loader({ params, request }: LoaderFunctionArgs) {
  const currency = new URL(request.url).searchParams.get("currency") ?? "EUR";
  if (Number(params.id) > 100) throw new Response("No such order", { status: 404 });
  return json({ id: Number(params.id), currency });
}
```

Los valores de ruta y consulta son parámetros escritos y se genera un error:

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `action`, `<Form>` y `useActionData`

```tsx filename="aplicación/rutas/todos.tsx"
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

La acción es una función Python con un cliente escrito, y `useAction` contiene lo que `useActionData` y `useNavigation().state` contienen:

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

`revalidate("/todos")` hace lo que Remix hace después de cada acción: la página carga sus datos nuevamente.

## `useFetcher`

```tsx
const fetcher = useFetcher();
fetcher.submit({ title: "Write the docs" }, { method: "post", action: "/todos" });
```

`useAction` es un buscador vinculado a una acción: llámalo desde tantos componentes como necesites, cada uno con sus propios `pending` y `data`.

## Mejora progresiva

Un Remix `<Form>` funciona antes de que se cargue JavaScript. En el modo servidor, un formulario simple publica una acción de la misma manera y el visitante regresa a la página con un `303`:

```nexy filename="src/rutas/notas.nexy"
---
from src.actions.todos import add_todo
---
<form method="post" action="{{ __actions_path['add_todo'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
```

## Rutas anidadas y `<Outlet />`

```tsx filename="aplicación/rutas/dashboard.tsx"
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

La ruta principal se convierte en la `layout.tsx` de la carpeta y `<Outlet />` se convierte en `children`:

```tsx filename="src/rutas/dashboard/layout.tsx"
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

```tsx filename="aplicación/root.tsx"
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

La raíz `layout.tsx` es propietaria del documento. No hay `<Scripts />` o `<Links />` para colocar: Nexy agrega el paquete del cliente.

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

## `meta`

```tsx filename="aplicación/rutas/blog.tsx"
export const meta = () => [{ title: "Blog" }, { name: "description", content: "Posts" }];
```

Una página `.tsx` no tiene `meta` exportación: escriba las etiquetas en el diseño raíz. En modo servidor, una página `.nexy` los establece con `metadata = {...}`, y su diseño los escribe con `{{ useMetadata().html() }}`.

## `<Link>`, `<NavLink>` y `useNavigate`

```tsx filename="aplicación/componentes/Nav.tsx"
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

`<NavLink>` es un `Link` con `activeClassName`, y `useNavigate()(path)` es `router.push(path)`.

## `redirect` y sesiones

```tsx filename="aplicación/rutas/dashboard.tsx"
export async function loader({ request }: LoaderFunctionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  if (!session.has("user")) throw redirect("/login");
  return null;
}
```

Un `middleware.py` en la carpeta se ejecuta antes de cada ruta debajo de ella, incluidas las páginas:

```python filename="src/rutas/dashboard/middleware.py"
from nexy.http import RedirectResponse, Request


async def middleware(request: Request, call_next):
    if "user" not in request.session:
        return RedirectResponse("/login", status_code=307)
    return await call_next(request)
```

```python filename="src/rutas/dashboard/stats.py"
async def GET():
    return {"visits": 12}
```

`createCookieSessionStorage` se convierte en un campo de `nexyconfig.py`, y `request.session` es un dict:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me"}
```

```python filename="src/rutas/api/login.py"
from pydantic import BaseModel

from nexy.http import Request


class Login(BaseModel):
    name: str


async def POST(request: Request, body: Login):
    request.session["user"] = body.name
    return {"user": body.name}
```

## Límites de error

La exportación `ErrorBoundary` de una ruta no tiene equivalente Nexy. Un cargador fallido es un código de estado: los clientes API obtienen `{"detail": ...}` y una URL desconocida muestra `src/routes/notfound.tsx`. Los errores generados mientras se procesa un componente son detectados por un React límite de error propio, alrededor de la parte que puede fallar.

## `headers` y almacenamiento en caché

```tsx filename="aplicación/rutas/news.tsx"
export const headers = () => ({ "Cache-Control": "public, s-maxage=60, stale-while-revalidate=60" });
```

En modo servidor, una línea en el frontmatter envía ese encabezado y mantiene la página renderizada:

```nexy filename="src/rutas/noticias.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## corriendo

| Remix / React Enrutador | nexy |
|---|---|
| `npx create-react-router` | `nx new`, plantilla `web-fbr-react` |
| `react-router dev` | `nx dev` |
| `react-router build`, luego `react-router-serve` | `nx build`, luego `nx start` |
| `public/` | `public/`, servido en `/` |
| Nodo en tiempo de ejecución | Python en tiempo de ejecución; Node solo crea los paquetes de clientes |

## Próximos pasos

- [De Next.js a Nexy](nextjs.md)
- [React en Nexy](../views/react/differences.md)
- [Acciones](../guides/actions.md)
- [Modo servidor y modo cliente](../routing/fbr/modes.md)
