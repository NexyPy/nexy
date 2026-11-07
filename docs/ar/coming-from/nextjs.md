# من Next.js إلى النكسي

في Nexy، يحتفظ مشروع App Router Next.js بمسارات الملفات والتخطيطات ومكونات React، بينما ينتقل رمز الخادم ومعالجات المسار وإجراءات الخادم إلى الملفات Python المجاورة لها.

كل قسم أدناه يوضح عادة Next.js، ثم نفس الشيء في Nexy.

## اختر الوضع أولاً

يمزج تطبيق Next.js بين مكونات الخادم والعميل في شجرة واحدة. يقوم مشروع Nexy باختيار أحد الشكلين في `nexyconfig.py`:

| تطبيق Next.js الخاص بك هو | وضع نكسي | الصفحات هي |
|---|---|---|
| في الغالب تفاعلية وملاحة العميل | وضع العميل، `useCSR = True` | `.tsx` الملفات، كما في `app/` |
| في الغالب المحتوى، وبعض الأجزاء التفاعلية | وضع الخادم، الافتراضي | `.nexy` صفحة بها React جزر |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

تستخدم الأقسام أدناه وضع العميل ما لم تنص على خلاف ذلك. انظر [وضع الخادم ووضع العميل](../routing/fbr/modes.md).

## `page.tsx`

```tsx filename="app/about/page.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

الصفحة هي الملف نفسه، وليست `page.tsx` داخل المجلد:

```tsx filename="src/routes/about.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

`app/page.tsx` هو `src/routes/index.tsx`، و `app/blog/page.tsx` هو `src/routes/blog/index.tsx`.

## توجيه الملفات، وجهاز توجيه التطبيقات، وجهاز توجيه الصفحات

يقوم كلا الموجهين لـ Next.js بتعيين `src/routes/`. يحتفظ ملف جهاز توجيه الصفحات بمساره؛ يصبح `page.tsx` لجهاز توجيه التطبيقات `index.tsx`، أو ملفًا مسمى على اسم المجلد الخاص به:

| Next.js | نكسي |
|---|---|
| `pages/about.tsx` | `src/routes/about.tsx` |
| `pages/blog/[slug].tsx` | `src/routes/blog/[slug].tsx` |
| `app/about/page.tsx` | `src/routes/about/index.tsx`، أو `src/routes/about.tsx` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug]/index.tsx`، أو `src/routes/blog/[slug].tsx` |
| `app/docs/[...slug]/page.tsx` | `src/routes/docs/[...slug].tsx` |
| `app/(marketing)/pricing/page.tsx` | `src/routes/(marketing)/pricing.tsx` |
| `pages/api/items/[id].ts` | `src/routes/api/items/[id].py` |
| `app/api/items/[id]/route.ts` | `src/routes/api/items/[id].py`، أو `src/routes/api/items/[id]/index.py` |

الملف `.tsx` هو صفحة والملف `.py` هو معالج: الامتداد يقول ذلك، لذلك يفقد معالج المسار المجلد `/route` الخاص به.

## القطاعات الديناميكية و `params`

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

`[...slug]` ومجموعات المسار مثل `(marketing)` تعمل كما في Next.js.

## `generateStaticParams`

```tsx filename="app/blog/[slug]/page.tsx"
export async function generateStaticParams() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

نفس التصدير، تحت هذا الاسم أو `getStaticParams`، يعطي مستندًا واحدًا معروضًا مسبقًا لكل قيمة. يستدعيه Nexy بدون `await`، لذا قم بإرجاع المصفوفة نفسها:

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

نفس الملف، مجلد واحد لأعلى: يمتلك التخطيط الجذر `<html>`، و `layout.tsx` في مجلد فرعي يتداخل بداخله.

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

لا تحتوي صفحة `.tsx` على تصدير `metadata`: اكتب العلامات في تخطيط الجذر. في وضع الخادم، تقوم صفحة `.nexy` بتعيينها لكل صفحة:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

يكتب الجذر `layout.nexy` العلامات حيث سيكون Next.js، في `<head>`:

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

## `next/link` و `next/navigation`

```tsx filename="app/nav.tsx"
"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
```

نفس الأسماء، من `@nexy/client`:

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

## معالجات الطريق

```ts filename="app/api/items/[id]/route.ts"
export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return Response.json({ id: Number(id) });
}
```

نفس `GET` التصدير، في Python، دون `/route`:

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

الجسم هو نموذج Pydantic، و `/docs` يسرد كل معالج:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## إجراءات الخادم و `revalidatePath`

```ts filename="التطبيق/actions.ts"
"use server";
import { revalidatePath } from "next/cache";

export async function addTodo(title: string) {
  await db.todo.create({ data: { title } });
  revalidatePath("/todos");
}
```

والفعل هو دالة Python . يقوم Nexy بإنشاء عميله المكتوب في `@nexy/actions`:

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

`useActionState` و `useFormStatus` خريطة إلى `pending` و `error` و `data` من `useAction`.

## مكونات الخادم هي `.nexy` صفحة

```tsx filename="التطبيق/المستخدمين/page.tsx"
export default async function Users() {
  const users = await db.user.findMany();
  return <ul>{users.map((user) => <li key={user.id}>{user.name}</li>)}</ul>;
}
```

يتم تشغيل مكون الخادم Next.js على الخادم، ويقرأ البيانات ويرسل HTML. صفحة `.nexy` هي نفس الشيء في وضع الخادم: مادتها الأمامية هي نص المكون غير المتزامن، في Python، والقالب هو ما تُرجعه.

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

| Next.js مكون الخادم | `.nexy` صفحة |
|---|---|
| `app/users/page.tsx`، لا `"use client"` | `src/routes/users.nexy` |
| `await db.user.findMany()` في المكون | استعلام في المسألة الأمامية |
| `{params}` و `{searchParams}` | `slug: prop[str]` و `useSearchParams()` |
| `cookies()` و `headers()` من `next/headers` | `useCookies()` و `useHeaders()` |
| `export const revalidate = 60` | `revalidate = 60` |
| مكون `"use client"` بداخله | جزيرة : `<Counter directive="client:load" />` |

في وضع العميل، يتم تشغيل صفحة `.tsx` في المتصفح، بحيث تقرأ البيانات من المعالج:

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

## `"use client"` مكونات داخل صفحات الخادم

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

في وضع الخادم، يكون مكون العميل عبارة عن جزيرة، وتوجيهاته تقول عندما يتم الترطيب:

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

انظر [الجزر](../rendering/islands.md) لـ `client:load`، `client:idle`، `client:visible`، و `client:media`.

## الاستخبارات والمراقبة مع `revalidate`

```tsx filename="app/news/page.tsx"
export const revalidate = 60;
```

نفس السطر، في مقدمة صفحة وضع الخادم:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## `middleware.ts`

```ts filename="الوسيطة.ts"
import { NextResponse, type NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  if (!request.cookies.get("session")) return NextResponse.redirect(new URL("/login", request.url));
}

export const config = { matcher: "/dashboard/:path*" };
```

`matcher` هو المجلد: يلتف `middleware.py` في `dashboard/` كل مسار أسفله.

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

## `notFound()` و `not-found.tsx`

```tsx filename="app/blog/[slug]/page.tsx"
import { notFound } from "next/navigation";

if (!post) notFound();
```

في المعالج، ارفع؛ في صفحة وضع الخادم، اتصل بـ `notFound()`:

```python filename="src/routes/api/posts/[slug].py"
from nexy.http import HTTPException

POSTS = {"hello": "Hello, world"}


async def GET(slug: str):
    if slug not in POSTS:
        raise HTTPException(status_code=404, detail="No such post")
    return {"title": POSTS[slug]}
```

`app/not-found.tsx` هو `src/routes/notfound.tsx` في وضع العميل، و `notfound.nexy` في وضع الخادم.

## `next/image`

```tsx
import Image from "next/image";

<Image src="/logo.png" alt="Logo" width={128} height={32} />
```

في صفحة `.nexy`، المكون `Image` من `nexy`:

```nexy filename="src/routes/brand.nexy"
---
from nexy import Image
---
<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

## الجري

| Next.js | نكسي |
|---|---|
| `npx create-next-app` | `nx new`، القالب `web-fbr-react` |
| `next dev` | `nx dev` |
| `next build && next start` | `nx build`، ثم `nx start` |
| `public/` | `public/`، خدم في `/` |
| عقدة في وقت التشغيل | Python في وقت التشغيل؛ تقوم العقدة ببناء حزم العميل فقط |

## الخطوات التالية

- [وضع الخادم ووضع العميل](../routing/fbr/modes.md)
- [React في نكسي](../views/react/differences.md)
- [الإجراءات](../guides/actions.md)
- [الجزر](../rendering/islands.md)
