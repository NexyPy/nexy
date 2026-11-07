# Next.js سے Nexy تک

Nexy میں ایک Next.js ایپ راؤٹر پروجیکٹ اپنے فائل کے روٹس، لے آؤٹس اور React اجزاء کو رکھتا ہے، جبکہ سرور کوڈ، روٹ ہینڈلرز اور سرور ایکشنز Python فائلوں میں منتقل ہوتے ہیں۔

ذیل میں ہر سیکشن ایک Next.js عادت دکھاتا ہے، پھر Nexy میں وہی چیز۔

## پہلے موڈ کا انتخاب کریں۔

ایک Next.js ایپ سرور اور کلائنٹ کے اجزاء کو ایک درخت میں ملا دیتی ہے۔ ایک Nexy پروجیکٹ `nexyconfig.py` میں دو شکلوں میں سے ایک کو چنتا ہے:

| آپ کی Next.js ایپ ہے۔ | نیکسی موڈ | صفحات ہیں۔ |
|---|---|---|
| زیادہ تر انٹرایکٹو، کلائنٹ نیویگیشن | کلائنٹ موڈ، `useCSR = True` | `.tsx` فائلیں، جیسا کہ `app/` میں |
| زیادہ تر مواد، چند انٹرایکٹو حصے | سرور موڈ، ڈیفالٹ | `.nexy` صفحات React جزائر کے ساتھ |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

ذیل کے حصے کلائنٹ موڈ کا استعمال کرتے ہیں جب تک کہ وہ دوسری صورت میں نہ کہیں۔ دیکھیں [سرور موڈ اور کلائنٹ موڈ](../routing/fbr/modes.md)۔

## `page.tsx`

```tsx filename="app/about/page.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

صفحہ بذات خود فائل ہے، فولڈر کے اندر `page.tsx` نہیں۔

```tsx filename="src/routes/about.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

`app/page.tsx` ہے `src/routes/index.tsx`، اور `app/blog/page.tsx` ہے `src/routes/blog/index.tsx`۔

## روٹ فائلز، ایپ راؤٹر اور پیجز راؤٹر

Next.js کے دونوں راؤٹرز کو `src/routes/` کا نقشہ۔ پیجز راؤٹر کی فائل اپنا راستہ برقرار رکھتی ہے۔ ایپ راؤٹر کا ایک `page.tsx` بن جاتا ہے `index.tsx`، یا اس کے فولڈر کے نام پر ایک فائل:

| Next.js | نیکسی |
|---|---|
| `pages/about.tsx` | `src/routes/about.tsx` |
| `pages/blog/[slug].tsx` | `src/routes/blog/[slug].tsx` |
| `app/about/page.tsx` | `src/routes/about/index.tsx`، یا `src/routes/about.tsx` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug]/index.tsx`، یا `src/routes/blog/[slug].tsx` |
| `app/docs/[...slug]/page.tsx` | `src/routes/docs/[...slug].tsx` |
| `app/(marketing)/pricing/page.tsx` | `src/routes/(marketing)/pricing.tsx` |
| `pages/api/items/[id].ts` | `src/routes/api/items/[id].py` |
| `app/api/items/[id]/route.ts` | `src/routes/api/items/[id].py`، یا `src/routes/api/items/[id]/index.py` |

ایک `.tsx` فائل ایک صفحہ ہے اور ایک `.py` فائل ایک ہینڈلر ہے: ایکسٹینشن کہتی ہے کہ کون سا، تو روٹ ہینڈلر اپنا `/route` فولڈر کھو دیتا ہے۔

## متحرک طبقات اور `params`

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

`[...slug]` اور روٹ گروپس جیسے `(marketing)` کام کرتے ہیں جیسا کہ Next.js میں ہے۔

## `generateStaticParams`

```tsx filename="app/blog/[slug]/page.tsx"
export async function generateStaticParams() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

وہی برآمد، اس نام یا `getStaticParams` کے تحت، فی قیمت ایک پہلے سے پیش کردہ دستاویز دیتا ہے۔ Nexy اسے بغیر `await` کے کال کرتا ہے، لہذا خود ہی صف کو واپس کریں:

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

ایک ہی فائل، ایک فولڈر اوپر: روٹ لے آؤٹ کا مالک ہے `<html>`، اور اس کے اندر ایک ذیلی فولڈر میں ایک `layout.tsx`۔

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

ایک `.tsx` صفحہ میں کوئی `metadata` برآمد نہیں ہے: روٹ لے آؤٹ میں ٹیگ لکھیں۔ سرور موڈ میں، ایک `.nexy` صفحہ انہیں فی صفحہ متعین کرتا ہے:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

جڑ `layout.nexy` ٹیگ لکھتا ہے جہاں Next.js، `<head>` میں:

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

## `next/link` اور `next/navigation`

```tsx filename="app/nav.tsx"
"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
```

وہی نام، `@nexy/client` سے:

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

## روٹ ہینڈلرز

```ts filename="app/api/items/[id]/route.ts"
export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return Response.json({ id: Number(id) });
}
```

وہی `GET` برآمد، Python میں، `/route` کے بغیر:

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

ایک جسم ایک Pydantic ماڈل ہے، اور `/docs` ہر ہینڈلر کی فہرست دیتا ہے:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## سرور کے اعمال اور `revalidatePath`

```ts filename="app/actions.ts"
"use server";
import { revalidatePath } from "next/cache";

export async function addTodo(title: string) {
  await db.todo.create({ data: { title } });
  revalidatePath("/todos");
}
```

ایک عمل ایک Python فعل ہے۔ Nexy اپنا ٹائپ شدہ کلائنٹ `@nexy/actions` میں تیار کرتا ہے:

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

`useActionState` اور `useFormStatus` کا نقشہ `pending`، `error` اور `data` کا `useAction`۔

## سرور کے اجزاء `.nexy` صفحات ہیں۔

```tsx filename="app/users/page.tsx"
export default async function Users() {
  const users = await db.user.findMany();
  return <ul>{users.map((user) => <li key={user.id}>{user.name}</li>)}</ul>;
}
```

ایک Next.js سرور کا جزو سرور پر چلتا ہے، ڈیٹا پڑھتا ہے اور ایچ ٹی ایم ایل بھیجتا ہے۔ سرور موڈ میں ایک `.nexy` صفحہ ایک ہی چیز ہے: اس کا فرنٹ میٹر async جزو کا باڈی ہے، Python میں، اور ٹیمپلیٹ وہی ہے جو یہ لوٹاتا ہے۔

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

| Next.js سرور جزو | `.nexy` صفحہ |
|---|---|
| `app/users/page.tsx`، نہیں `"use client"` | `src/routes/users.nexy` |
| `await db.user.findMany()` جز میں | سامنے والے معاملے میں ایک سوال |
| `{params}` اور `{searchParams}` | `slug: prop[str]` اور `useSearchParams()` |
| `cookies()` اور `headers()` `next/headers` سے | `useCookies()` اور `useHeaders()` |
| `export const revalidate = 60` | `revalidate = 60` |
| اس کے اندر ایک `"use client"` جزو | ایک جزیرہ: `<Counter directive="client:load" />` |

کلائنٹ موڈ میں، ایک `.tsx` صفحہ براؤزر میں چلتا ہے، لہذا یہ ایک ہینڈلر سے ڈیٹا پڑھتا ہے:

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

## `"use client"` سرور کے صفحات کے اندر اجزاء

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

سرور موڈ میں، کلائنٹ کا جزو ایک جزیرہ ہے، اور اس کی ہدایت یہ کہتی ہے کہ جب یہ ہائیڈریٹ ہوتا ہے:

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

`client:load`، `client:idle`، `client:visible` اور `client:media` کے لیے [جزیرے](../rendering/islands.md) دیکھیں۔

## آئی ایس آر کے ساتھ `revalidate`

```tsx filename="app/news/page.tsx"
export const revalidate = 60;
```

ایک ہی لائن، سرور موڈ پیج کے فرنٹ میٹر میں:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## `middleware.ts`

```ts filename="Middleware.ts"
import { NextResponse, type NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  if (!request.cookies.get("session")) return NextResponse.redirect(new URL("/login", request.url));
}

export const config = { matcher: "/dashboard/:path*" };
```

`matcher` فولڈر ہے: `middleware.py` میں `dashboard/` اس کے نیچے ہر راستے کو لپیٹ دیتا ہے۔

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

## `notFound()` اور `not-found.tsx`

```tsx filename="app/blog/[slug]/page.tsx"
import { notFound } from "next/navigation";

if (!post) notFound();
```

ایک ہینڈلر میں، بڑھانا؛ سرور موڈ صفحہ میں، کال `notFound()`:

```python filename="src/routes/api/posts/[slug].py"
from nexy.http import HTTPException

POSTS = {"hello": "Hello, world"}


async def GET(slug: str):
    if slug not in POSTS:
        raise HTTPException(status_code=404, detail="No such post")
    return {"title": POSTS[slug]}
```

`app/not-found.tsx` کلائنٹ موڈ میں `src/routes/notfound.tsx` ہے، اور سرور موڈ میں `notfound.nexy` ہے۔

## `next/image`

```tsx
import Image from "next/image";

<Image src="/logo.png" alt="Logo" width={128} height={32} />
```

ایک `.nexy` صفحہ میں، `Image` کا جزو `nexy`:

```nexy filename="src/routes/brand.nexy"
---
from nexy import Image
---
<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

## چل رہا ہے۔

| Next.js | نیکسی |
|---|---|
| `npx create-next-app` | `nx new`، سانچہ `web-fbr-react` |
| `next dev` | `nx dev` |
| `next build && next start` | `nx build`، پھر `nx start` |
| `public/` | `public/`، پر خدمت کی `/` |
| رن ٹائم پر نوڈ | Python رن ٹائم پر؛ نوڈ صرف کلائنٹ بنڈل بناتا ہے۔ |

## اگلے اقدامات

- [سرور موڈ اور کلائنٹ موڈ](../routing/fbr/modes.md)
- Nexy میں [React ](../views/react/differences.md)
- [اعمال](../guides/actions.md)
- [جزائر](../rendering/islands.md)
