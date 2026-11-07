# Remix سے Nexy تک

Nexy میں ایک Remix یا React راؤٹر روٹ اپنا React جزو رکھتا ہے، جب کہ اس کا `loader` ایک Python ہینڈلر بن جاتا ہے، اس کا `action` ایک Python ایکشن ہوتا ہے، اور نیسٹڈ روٹس `layout.tsx` کے ساتھ فولڈر بن جاتے ہیں۔

ذیل میں ہر سیکشن ایک Remix عادت دکھاتا ہے، پھر Nexy میں وہی چیز۔ React فریم ورک موڈ میں راؤٹر v7 وہی نام استعمال کرتا ہے۔

## موڈ کا انتخاب کریں۔

ایک Remix ایپ کلائنٹ پر نیویگیٹ کرتی ہے، لہذا یہ کلائنٹ موڈ پر نقشہ بناتی ہے:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

ایک مواد کی سائٹ جس کو صرف چند انٹرایکٹو حصوں کی ضرورت ہوتی ہے وہ سرور موڈ میں بہتر طور پر فٹ بیٹھتی ہے: `.nexy` جزائر کے ساتھ React صفحات۔ دیکھیں [سرور موڈ اور کلائنٹ موڈ](../routing/fbr/modes.md)۔

## فائلوں کو روٹ کریں۔

| Remix (`app/routes/`) | Nexy (`src/routes/`) |
|---|---|
| `_index.tsx` | `index.tsx` |
| `about.tsx` | `about.tsx` |
| `blog.$slug.tsx` | `blog/[slug].tsx` |
| `files.$.tsx` | `files/[...path].tsx` |
| `_auth.login.tsx` (بے راہ ترتیب) | `(auth)/login.tsx`، ایک روٹ گروپ |
| `api.items.$id.ts` (وسائل کا راستہ) | `api/items/[id].py` |

نقطے فولڈر بن جاتے ہیں، اور `$param` `[param]` بن جاتے ہیں۔

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

## `loader` اور `useLoaderData`

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

لوڈر ایک Python ہینڈلر کی طرف جاتا ہے، اور صفحہ اسے پڑھتا ہے:

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

سرور موڈ میں، ایک `.nexy` صفحہ ایک فائل میں لوڈر اور منظر ہوتا ہے، اور ڈیٹا پہلے HTML میں ہوتا ہے:

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

## لوڈر میں `params` اور `request`

```tsx filename="app/routes/api.orders.$id.ts"
export async function loader({ params, request }: LoaderFunctionArgs) {
  const currency = new URL(request.url).searchParams.get("currency") ?? "EUR";
  if (Number(params.id) > 100) throw new Response("No such order", { status: 404 });
  return json({ id: Number(params.id), currency });
}
```

پاتھ اور استفسار کی قدریں ٹائپ شدہ پیرامیٹرز ہیں، اور ایک خرابی اٹھائی گئی ہے:

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `action`، `<Form>` اور `useActionData`

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

ایکشن ایک ٹائپ کردہ کلائنٹ کے ساتھ ایک Python فنکشن ہے، اور `useAction` وہ چیز رکھتا ہے جو `useActionData` اور `useNavigation().state` منعقد ہوتا ہے:

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

`revalidate("/todos")` وہ کرتا ہے جو Remix ہر عمل کے بعد کرتا ہے: صفحہ اپنا ڈیٹا دوبارہ لوڈ کرتا ہے۔

## `useFetcher`

```tsx
const fetcher = useFetcher();
fetcher.submit({ title: "Write the docs" }, { method: "post", action: "/todos" });
```

`useAction` ایک حاصل کرنے والا ایک عمل کا پابند ہے: اسے جتنے بھی اجزاء کی ضرورت ہے، ہر ایک کو اس کے اپنے `pending` اور `data` کے ساتھ کال کریں۔

## ترقی پسند اضافہ

ایک Remix `<Form>` سے پہلے کام کرتا ہے۔ JavaScript بوجھ۔ سرور موڈ میں، ایک سادہ شکل میں اسی طرح ایک عمل کو پوسٹ کرتا ہے، اور وزیٹر ایک `303` کے ساتھ صفحہ پر واپس آتا ہے:

```nexy filename="src/routes/notes.nexy"
---
from src.actions.todos import add_todo
---
<form method="post" action="{{ __actions_path['add_todo'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
```

## گھریلو راستے اور `<Outlet />`

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

پیرنٹ روٹ فولڈر کا `layout.tsx` بن جاتا ہے، اور `<Outlet />` بن جاتا ہے `children`:

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

جڑ `layout.tsx` دستاویز کا مالک ہے۔ رکھنے کے لیے کوئی `<Scripts />` یا `<Links />` نہیں ہے: Nexy کلائنٹ بنڈل کو خود شامل کرتا ہے۔

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

ایک `.tsx` صفحہ میں کوئی `meta` برآمد نہیں ہے: روٹ لے آؤٹ میں ٹیگ لکھیں۔ سرور موڈ میں، ایک `.nexy` صفحہ انہیں `metadata = {...}` کے ساتھ سیٹ کرتا ہے، اور اس کی ترتیب انہیں `{{ useMetadata().html() }}` کے ساتھ لکھتی ہے۔

## `<Link>`، `<NavLink>` اور `useNavigate`

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

`<NavLink>` ایک `Link` کے ساتھ `activeClassName` ہے، اور `useNavigate()(path)` `router.push(path)` ہے۔

## `redirect` اور سیشنز

```tsx filename="app/routes/dashboard.tsx"
export async function loader({ request }: LoaderFunctionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  if (!session.has("user")) throw redirect("/login");
  return null;
}
```

فولڈر میں ایک `middleware.py` اس کے نیچے ہر راستے سے پہلے چلتا ہے، صفحات شامل ہیں:

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

`createCookieSessionStorage` `nexyconfig.py` کا ایک فیلڈ بن جاتا ہے، اور `request.session` ایک ڈکٹ ہے:

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

## غلطی کی حدود

ایک روٹ کی `ErrorBoundary` برآمد میں Nexy کے برابر نہیں ہے۔ ایک ناکام لوڈر ایک اسٹیٹس کوڈ ہے: API کلائنٹس کو `{"detail": ...}` ملتا ہے، اور ایک نامعلوم یو آر ایل رینڈر کرتا ہے `src/routes/notfound.tsx`۔ غلطیوں کو پھینک دیا گیا ہے جب ایک جزو رینڈرز a کی طرف سے پکڑے جاتے ہیں React آپ کی اپنی غلطی کی حد، اس حصے کے ارد گرد جو ناکام ہو سکتی ہے۔

## `headers` اور کیشنگ

```tsx filename="app/routes/news.tsx"
export const headers = () => ({ "Cache-Control": "public, s-maxage=60, stale-while-revalidate=60" });
```

سرور موڈ میں، فرنٹ میٹر میں ایک لائن وہ ہیڈر بھیجتی ہے اور پیش کردہ صفحہ کو رکھتی ہے:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## چل رہا ہے۔

| Remix / React راؤٹر | نیکسی |
|---|---|
| `npx create-react-router` | `nx new`، سانچہ `web-fbr-react` |
| `react-router dev` | `nx dev` |
| `react-router build`، پھر `react-router-serve` | `nx build`، پھر `nx start` |
| `public/` | `public/`، `/` میں خدمت کی |
| رن ٹائم پر نوڈ | Python رن ٹائم پر؛ نوڈ صرف کلائنٹ بنڈل بناتا ہے۔ |

## اگلے اقدامات

- [سے Next.js سے Nexy](nextjs.md)
- [React Nexy میں](../views/react/differences.md)
- [اعمال](../guides/actions.md)
- [سرور موڈ اور کلائنٹ موڈ](../routing/fbr/modes.md)
