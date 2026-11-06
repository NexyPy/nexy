# Remix থেকে নেক্সি পর্যন্ত

নেক্সিতে একটি Remix বা React রাউটার রুট তার React উপাদান রাখে, যখন এটি `loader` একটি Python হ্যান্ডলারে পরিণত হয়, এটির `action` একটি Python অ্যাকশন হয় এবং নেস্টেড রুটগুলি `layout.tsx` সহ ফোল্ডার হয়ে যায়।

নীচের প্রতিটি বিভাগ একটি Remix অভ্যাস দেখায়, তারপর Nexy তে একই জিনিস। React ফ্রেমওয়ার্ক মোডে রাউটার v7 একই নাম ব্যবহার করে।

## মোড বাছাই করুন

একটি Remix অ্যাপ ক্লায়েন্টে নেভিগেট করে, তাই এটি ক্লায়েন্ট মোডে ম্যাপ করে:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

একটি বিষয়বস্তু সাইট যেটির জন্য শুধুমাত্র কয়েকটি ইন্টারেক্টিভ অংশের প্রয়োজন সার্ভার মোডকে আরও ভালোভাবে ফিট করে: `.nexy` দ্বীপের সাথে React পৃষ্ঠাগুলি। [সার্ভার মোড এবং ক্লায়েন্ট মোড](../routing/fbr/modes.md) দেখুন।

## রুট ফাইল

| Remix (`app/routes/`) | নেক্সি (`src/routes/`) |
|---|---|
| `_index.tsx` | `index.tsx` |
| `about.tsx` | `about.tsx` |
| `blog.$slug.tsx` | `blog/[slug].tsx` |
| `files.$.tsx` (স্প্ল্যাট) | `files/[...path].tsx` |
| `_auth.login.tsx` (পথহীন বিন্যাস) | `(auth)/login.tsx`, একটি রুট গ্রুপ |
| `api.items.$id.ts` (সম্পদ রুট) | `api/items/[id].py` |

বিন্দু ফোল্ডার হয়ে যায়, এবং `$param` হয়ে যায় `[param]`।

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

## `loader` এবং `useLoaderData`

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

লোডার একটি Python হ্যান্ডলারের কাছে চলে যায় এবং পৃষ্ঠাটি এটি পড়ে:

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

সার্ভার মোডে, একটি `.nexy` পৃষ্ঠা হল একটি ফাইলে লোডার এবং ভিউ, এবং ডেটা প্রথম HTML-এ থাকে:

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

## একটি লোডারে `params` এবং `request`

```tsx filename="app/routes/api.orders.$id.ts"
export async function loader({ params, request }: LoaderFunctionArgs) {
  const currency = new URL(request.url).searchParams.get("currency") ?? "EUR";
  if (Number(params.id) > 100) throw new Response("No such order", { status: 404 });
  return json({ id: Number(params.id), currency });
}
```

পাথ এবং ক্যোয়ারী মান টাইপ করা পরামিতি, এবং একটি ত্রুটি উত্থাপিত হয়:

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `action`, `<Form>` এবং `useActionData`

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

ক্রিয়াটি একটি টাইপ করা ক্লায়েন্ট সহ একটি Python ফাংশন, এবং `useAction` যা `useActionData` এবং `useNavigation().state` ধারণ করে:

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

`revalidate("/todos")` প্রতিটি কর্মের পরে Remix যা করে তা করে: পৃষ্ঠাটি আবার তার ডেটা লোড করে।

## `useFetcher`

```tsx
const fetcher = useFetcher();
fetcher.submit({ title: "Write the docs" }, { method: "post", action: "/todos" });
```

`useAction` হল একটি ক্রিয়াকলাপের সাথে আবদ্ধ একটি আনয়নকারী: আপনার যতগুলি উপাদান প্রয়োজন ততগুলি থেকে এটিকে কল করুন, প্রতিটির নিজস্ব `pending` এবং `data`।

## প্রগতিশীল বর্ধন

একটি Remix `<Form>` JavaScript লোড হওয়ার আগে কাজ করে। সার্ভার মোডে, একটি প্লেইন ফর্ম একইভাবে একটি অ্যাকশন পোস্ট করে এবং ভিজিটর একটি `303` সহ পৃষ্ঠায় ফিরে আসে:

```nexy filename="src/routes/notes.nexy"
---
from src.actions.todos import add_todo
---
<form method="post" action="{{ __actions_path['add_todo'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
```

## নেস্টেড রুট এবং `<Outlet />`

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

মূল রুট ফোল্ডারের `layout.tsx` হয়ে যায় এবং `<Outlet />` হয়ে যায় `children`:

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

মূল `layout.tsx` নথির মালিক। স্থাপন করার জন্য কোন `<Scripts />` বা `<Links />` নেই: Nexy নিজেই ক্লায়েন্ট বান্ডিল যোগ করে।

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

একটি `.tsx` পৃষ্ঠার কোন `meta` রপ্তানি নেই: রুট লেআউটে ট্যাগ লিখুন। সার্ভার মোডে, একটি `.nexy` পৃষ্ঠা তাদের `metadata = {...}` দিয়ে সেট করে এবং এর বিন্যাস তাদের `{{ useMetadata().html() }}` দিয়ে লেখে।

## `<Link>`, `<NavLink>` এবং `useNavigate`

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

`<NavLink>` হল `Link` সহ `activeClassName`, এবং `useNavigate()(path)` হল `router.push(path)`।

## `redirect` এবং সেশন

```tsx filename="app/routes/dashboard.tsx"
export async function loader({ request }: LoaderFunctionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  if (!session.has("user")) throw redirect("/login");
  return null;
}
```

ফোল্ডারের একটি `middleware.py` নীচের প্রতিটি রুটের আগে চলে, পৃষ্ঠাগুলি অন্তর্ভুক্ত:

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

`createCookieSessionStorage` হল `nexyconfig.py` এর একটি ক্ষেত্র, এবং `request.session` হল একটি ডিক্ট:

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

## ত্রুটি সীমানা

একটি রুটের `ErrorBoundary` রপ্তানির কোনো Nexy সমতুল্য নেই। একটি ব্যর্থ লোডার হল একটি স্থিতি কোড: API ক্লায়েন্টরা `{"detail": ...}` পায়, এবং একটি অজানা URL রেন্ডার করে `src/routes/notfound.tsx`। একটি কম্পোনেন্ট রেন্ডার করার সময় নিক্ষিপ্ত ত্রুটিগুলি আপনার নিজের একটি React ত্রুটির সীমানা দ্বারা ধরা হয়, যে অংশটি ব্যর্থ হতে পারে।

## `headers` এবং ক্যাশিং

```tsx filename="app/routes/news.tsx"
export const headers = () => ({ "Cache-Control": "public, s-maxage=60, stale-while-revalidate=60" });
```

সার্ভার মোডে, ফ্রন্টম্যাটারের একটি লাইন সেই শিরোনামটি পাঠায় এবং রেন্ডার করা পৃষ্ঠাটি রাখে:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## চলছে

| Remix / React রাউটার | নেক্সি |
|---|---|
| `npx create-react-router` | `nx new`, টেমপ্লেট `web-fbr-react` |
| `react-router dev` | `nx dev` |
| `react-router build`, তারপর `react-router-serve` | `nx build`, তারপর `nx start` |
| `public/` | `public/`, `/` এ পরিবেশিত |
| রানটাইমে নোড | Python রানটাইমে; নোড শুধুমাত্র ক্লায়েন্ট বান্ডিল তৈরি করে |

## পরবর্তী পদক্ষেপ

- [থেকে Next.js নেক্সি থেকে](nextjs.md)
- [React নেক্সিতে](../views/react/differences.md)
- [কর্ম](../guides/actions.md)
- [সার্ভার মোড এবং ক্লায়েন্ট মোড](../routing/fbr/modes.md)
