# من Remix إلى النكسي

في Nexy، يحتفظ مسار جهاز التوجيه Remix أو React بمكونه React، بينما يصبح `loader` معالجًا Python، وإجراء `action` إلى Python، وتصبح المسارات المتداخلة مجلدات ذات `layout.tsx`.

كل قسم أدناه يوضح عادة Remix، ثم نفس الشيء في Nexy. React يستخدم جهاز التوجيه v7 في وضع الإطار نفس الأسماء.

## اختر الوضع

يتنقل تطبيق Remix على العميل، لذلك يتم تعيينه إلى وضع العميل:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

موقع المحتوى الذي يحتاج فقط إلى عدد قليل من الأجزاء التفاعلية يناسب وضع الخادم بشكل أفضل: `.nexy` صفحات تحتوي على React جزر. انظر [وضع الخادم ووضع العميل](../routing/fbr/modes.md).

## ملفات الطريق

| Remix (`app/routes/`) | نكسي (`src/routes/`) |
|---|---|
| `_index.tsx` | `index.tsx` |
| `about.tsx` | `about.tsx` |
| `blog.$slug.tsx` | `blog/[slug].tsx` |
| `files.$.tsx` (ضجة) | `files/[...path].tsx` |
| `_auth.login.tsx` (تخطيط بلا مسار) | `(auth)/login.tsx`، مجموعة طريق |
| `api.items.$id.ts` (طريق الموارد) | `api/items/[id].py` |

تصبح النقاط مجلدات، و `$param` تصبح `[param]`.

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

## `loader` و `useLoaderData`

```tsx filename="التطبيق/الطرق/users.tsx"
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

ينتقل المُحمل إلى معالج Python، وتقرأه الصفحة:

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

في وضع الخادم، تكون الصفحة `.nexy` هي المُحمل والعرض في ملف واحد، وتكون البيانات في ملف HTML الأول:

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

## `params` و `request` في محمل

```tsx filename="app/routes/api.orders.$id.ts"
export async function loader({ params, request }: LoaderFunctionArgs) {
  const currency = new URL(request.url).searchParams.get("currency") ?? "EUR";
  if (Number(params.id) > 100) throw new Response("No such order", { status: 404 });
  return json({ id: Number(params.id), currency });
}
```

تعد قيم المسار والاستعلام معلمات مكتوبة، ويظهر خطأ:

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `action`، `<Form>` و `useActionData`

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

الإجراء هو وظيفة Python مع عميل مكتوب، و `useAction` يحمل ما يحمله `useActionData` و `useNavigation().state`:

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

`revalidate("/todos")` يفعل ما يفعله Remix بعد كل إجراء: تقوم الصفحة بتحميل بياناتها مرة أخرى.

## `useFetcher`

```tsx
const fetcher = useFetcher();
fetcher.submit({ title: "Write the docs" }, { method: "post", action: "/todos" });
```

`useAction` هو جلب مرتبط بإجراء واحد: قم باستدعائه من العديد من المكونات التي تحتاجها، ولكل منها `pending` و `data` الخاصة به.

## تعزيز تدريجي

يعمل Remix `<Form>` قبل تحميل JavaScript. في وضع الخادم، يقوم النموذج العادي بنشر إجراء بنفس الطريقة، ويعود الزائر إلى الصفحة بـ `303`:

```nexy filename="src/routes/notes.nexy"
---
from src.actions.todos import add_todo
---
<form method="post" action="{{ __actions_path['add_todo'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
```

## المسارات المتداخلة و `<Outlet />`

```tsx filename="التطبيق/الطرق/dashboard.tsx"
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

يصبح المسار الأصلي هو `layout.tsx` للمجلد، ويصبح `<Outlet />` `children`:

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

الجذر `layout.tsx` يملك الوثيقة. لا يوجد `<Scripts />` أو `<Links />` لوضعه: يضيف Nexy حزمة العميل نفسها.

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

صفحة `.tsx` لا تحتوي على `meta` تصدير: اكتب العلامات في تخطيط الجذر. في وضع الخادم، تقوم صفحة `.nexy` بتعيينها بـ `metadata = {...}`، ويكتبها تخطيطها بـ `{{ useMetadata().html() }}`.

## `<Link>`، `<NavLink>` و `useNavigate`

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

`<NavLink>` هو `Link` مع `activeClassName`، و `useNavigate()(path)` هو `router.push(path)`.

## `redirect` والجلسات

```tsx filename="التطبيق/الطرق/dashboard.tsx"
export async function loader({ request }: LoaderFunctionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  if (!session.has("user")) throw redirect("/login");
  return null;
}
```

يتم تشغيل `middleware.py` في المجلد قبل كل مسار أسفله، بما في ذلك الصفحات:

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

`createCookieSessionStorage` يصبح حقل واحد من `nexyconfig.py`، و `request.session` هو إملاء:

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

## حدود الخطأ

تصدير `ErrorBoundary` للمسار ليس له مكافئ Nexy. أداة التحميل الفاشلة هي رمز الحالة: يحصل عملاء API على `{"detail": ...}`، ويعرض عنوان URL غير معروف `src/routes/notfound.tsx`. يتم اكتشاف الأخطاء التي يتم طرحها أثناء عرض المكون من خلال حد الخطأ React الخاص بك، حول الجزء الذي يمكن أن يفشل.

## `headers` والتخزين المؤقت

```tsx filename="التطبيق/الطرق/news.tsx"
export const headers = () => ({ "Cache-Control": "public, s-maxage=60, stale-while-revalidate=60" });
```

في وضع الخادم، يرسل سطر واحد في المادة الأمامية هذا الرأس ويحتفظ بالصفحة المعروضة:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## الجري

| Remix / React جهاز التوجيه | نكسي |
|---|---|
| `npx create-react-router` | `nx new`، القالب `web-fbr-react` |
| `react-router dev` | `nx dev` |
| `react-router build`، ثم `react-router-serve` | `nx build`، ثم `nx start` |
| `public/` | `public/`، خدم في `/` |
| عقدة في وقت التشغيل | Python في وقت التشغيل؛ تقوم العقدة ببناء حزم العميل فقط |

## الخطوات التالية

- [من Next.js إلى نكسي](nextjs.md)
- [React في نكسي](../views/react/differences.md)
- [الإجراءات](../guides/actions.md)
- [وضع الخادم ووضع العميل](../routing/fbr/modes.md)
