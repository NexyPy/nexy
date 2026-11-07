# Next.js থেকে নেক্সি পর্যন্ত

Nexy-এ একটি Next.js অ্যাপ রাউটার প্রকল্প তার ফাইলের রুট, লেআউট এবং React উপাদানগুলিকে রাখে, যখন সার্ভার কোড, রুট হ্যান্ডলার এবং সার্ভার অ্যাকশনগুলি তাদের পাশের Python ফাইলগুলিতে চলে যায়।

নীচের প্রতিটি বিভাগ একটি Next.js অভ্যাস দেখায়, তারপর Nexy তে একই জিনিস।

## প্রথমে মোডটি বেছে নিন

একটি Next.js অ্যাপ একটি গাছে সার্ভার এবং ক্লায়েন্ট উপাদানগুলিকে মিশ্রিত করে। একটি Nexy প্রকল্প দুটি আকারের মধ্যে একটি বেছে নেয় `nexyconfig.py`:

| আপনার Next.js অ্যাপটি | নেক্সি মোড | পৃষ্ঠাগুলি হল |
|---|---|---|
| বেশিরভাগই ইন্টারেক্টিভ, ক্লায়েন্ট নেভিগেশন | ক্লায়েন্ট মোড, `useCSR = True` | `.tsx` ফাইল, যেমন `app/` |
| বেশিরভাগ বিষয়বস্তু, কয়েকটি ইন্টারেক্টিভ অংশ | সার্ভার মোড, ডিফল্ট | `.nexy` React দ্বীপ সহ পৃষ্ঠা |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

নীচের বিভাগগুলি ক্লায়েন্ট মোড ব্যবহার করে যদি না তারা অন্যথায় বলে। [সার্ভার মোড এবং ক্লায়েন্ট মোড](../routing/fbr/modes.md) দেখুন।

## `page.tsx`

```tsx filename="app/about/page.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

একটি পৃষ্ঠা নিজেই ফাইল, ফোল্ডারের ভিতরে একটি `page.tsx` নয়:

```tsx filename="src/routes/about.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

`app/page.tsx` হল `src/routes/index.tsx`, এবং `app/blog/page.tsx` হল `src/routes/blog/index.tsx`।

## রুট ফাইল, অ্যাপ রাউটার এবং পেজ রাউটার

উভয় রাউটার এর Next.js মানচিত্রে `src/routes/`. পেজ রাউটারের একটি ফাইল তার পথ ধরে রাখে; অ্যাপ রাউটারের একটি `page.tsx` হয়ে যায় `index.tsx`, অথবা একটি ফাইল এর ফোল্ডারের নামে নামকরণ করা হয়:

| Next.js | নেক্সি |
|---|---|
| `pages/about.tsx` | `src/routes/about.tsx` |
| `pages/blog/[slug].tsx` | `src/routes/blog/[slug].tsx` |
| `app/about/page.tsx` | `src/routes/about/index.tsx`, বা `src/routes/about.tsx` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug]/index.tsx`, বা `src/routes/blog/[slug].tsx` |
| `app/docs/[...slug]/page.tsx` | `src/routes/docs/[...slug].tsx` |
| `app/(marketing)/pricing/page.tsx` | `src/routes/(marketing)/pricing.tsx` |
| `pages/api/items/[id].ts` | `src/routes/api/items/[id].py` |
| `app/api/items/[id]/route.ts` | `src/routes/api/items/[id].py`, বা `src/routes/api/items/[id]/index.py` |

একটি `.tsx` ফাইল হল একটি পৃষ্ঠা এবং একটি `.py` ফাইল হল একটি হ্যান্ডলার: এক্সটেনশন যা বলে, তাই একটি রুট হ্যান্ডলার তার `/route` ফোল্ডারটি হারিয়ে ফেলে।

## গতিশীল সেগমেন্ট এবং `params`

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

`[...slug]` এবং রুট গ্রুপ যেমন `(marketing)` কাজ করে যেমন Next.js।

## `generateStaticParams`

```tsx filename="app/blog/[slug]/page.tsx"
export async function generateStaticParams() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

একই রপ্তানি, এই নামের অধীনে বা `getStaticParams`, প্রতি মূল্যে একটি পূর্ব-প্রস্তুত নথি দেয়। Nexy এটিকে `await` ছাড়াই কল করে, তাই অ্যারে নিজেই ফিরিয়ে দিন:

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

একই ফাইল, একটি ফোল্ডার আপ: রুট লেআউটের মালিকানা `<html>`, এবং একটি `layout.tsx` একটি সাবফোল্ডার এর ভিতরে নেস্ট করে।

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

একটি `.tsx` পৃষ্ঠার কোন `metadata` রপ্তানি নেই: রুট লেআউটে ট্যাগ লিখুন। সার্ভার মোডে, একটি `.nexy` পৃষ্ঠা তাদের প্রতি পৃষ্ঠায় সেট করে:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

মূল `layout.nexy` ট্যাগগুলি লেখে যেখানে Next.js হবে, `<head>` এ:

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

## `next/link` এবং `next/navigation`

```tsx filename="app/nav.tsx"
"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
```

একই নাম, `@nexy/client` থেকে:

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

## রুট হ্যান্ডলার

```ts filename="app/api/items/[id]/route.ts"
export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return Response.json({ id: Number(id) });
}
```

একই `GET` রপ্তানি, Python মধ্যে, `/route` ছাড়া:

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

একটি বডি একটি Pydantic মডেল, এবং `/docs` প্রত্যেক হ্যান্ডলারকে তালিকাভুক্ত করে:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## সার্ভার কর্ম এবং `revalidatePath`

```ts filename="app/actions.ts"
"use server";
import { revalidatePath } from "next/cache";

export async function addTodo(title: string) {
  await db.todo.create({ data: { title } });
  revalidatePath("/todos");
}
```

একটি ক্রিয়া একটি Python ফাংশন। Nexy তার টাইপ করা ক্লায়েন্ট তৈরি করে `@nexy/actions`:

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

`useActionState` এবং `useFormStatus` মানচিত্র `pending`, `error` এবং `data` এর `useAction`।

## সার্ভার উপাদান হল `.nexy` পৃষ্ঠা

```tsx filename="app/users/page.tsx"
export default async function Users() {
  const users = await db.user.findMany();
  return <ul>{users.map((user) => <li key={user.id}>{user.name}</li>)}</ul>;
}
```

একটি Next.js সার্ভার কম্পোনেন্ট সার্ভারে চলে, ডেটা পড়ে এবং এইচটিএমএল পাঠায়। সার্ভার মোডে একটি `.nexy` পৃষ্ঠা একই জিনিস: এর ফ্রন্টম্যাটার হল অ্যাসিঙ্ক কম্পোনেন্টের বডি, Python-এ, এবং টেমপ্লেট হল এটি যা রিটার্ন করে।

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

| Next.js সার্ভার উপাদান | `.nexy` পৃষ্ঠা |
|---|---|
| `app/users/page.tsx`, না `"use client"` | `src/routes/users.nexy` |
| `await db.user.findMany()` উপাদানে | সামনে একটি প্রশ্ন |
| `{params}` এবং `{searchParams}` | `slug: prop[str]` এবং `useSearchParams()` |
| `cookies()` এবং `headers()` `next/headers` থেকে | `useCookies()` এবং `useHeaders()` |
| `export const revalidate = 60` | `revalidate = 60` |
| এর ভিতরে একটি `"use client"` উপাদান | একটি দ্বীপ: `<Counter directive="client:load" />` |

ক্লায়েন্ট মোডে, একটি `.tsx` পৃষ্ঠা ব্রাউজারে চলে, তাই এটি একটি হ্যান্ডলার থেকে ডেটা পড়ে:

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

## `"use client"` সার্ভার পৃষ্ঠার ভিতরে উপাদান

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

সার্ভার মোডে, ক্লায়েন্ট উপাদান হল একটি দ্বীপ, এবং এর নির্দেশিকা বলে যখন এটি হাইড্রেট করে:

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

`client:load`, `client:idle`, `client:visible` এবং `client:media` এর জন্য [দ্বীপগুলি](../rendering/islands.md) দেখুন।

## আইএসআর সহ `revalidate`

```tsx filename="app/news/page.tsx"
export const revalidate = 60;
```

একই লাইন, একটি সার্ভার-মোড পৃষ্ঠার ফ্রন্ট ম্যাটারে:

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

`matcher` হল ফোল্ডার: একটি `middleware.py` `dashboard/` এর নিচের প্রতিটি রুটকে মোড়ানো।

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

## `notFound()` এবং `not-found.tsx`

```tsx filename="app/blog/[slug]/page.tsx"
import { notFound } from "next/navigation";

if (!post) notFound();
```

একটি হ্যান্ডলার মধ্যে, বাড়াতে; একটি সার্ভার-মোড পৃষ্ঠায়, কল `notFound()`:

```python filename="src/routes/api/posts/[slug].py"
from nexy.http import HTTPException

POSTS = {"hello": "Hello, world"}


async def GET(slug: str):
    if slug not in POSTS:
        raise HTTPException(status_code=404, detail="No such post")
    return {"title": POSTS[slug]}
```

`app/not-found.tsx` হল `src/routes/notfound.tsx` ক্লায়েন্ট মোডে, এবং `notfound.nexy` সার্ভার মোডে।

## `next/image`

```tsx
import Image from "next/image";

<Image src="/logo.png" alt="Logo" width={128} height={32} />
```

একটি `.nexy` পৃষ্ঠায়, `nexy` এর `Image` উপাদান:

```nexy filename="src/routes/brand.nexy"
---
from nexy import Image
---
<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

## চলছে

| Next.js | নেক্সি |
|---|---|
| `npx create-next-app` | `nx new`, টেমপ্লেট `web-fbr-react` |
| `next dev` | `nx dev` |
| `next build && next start` | `nx build`, তারপর `nx start` |
| `public/` | `public/`, `/` এ পরিবেশিত |
| রানটাইমে নোড | Python রানটাইমে; নোড শুধুমাত্র ক্লায়েন্ট বান্ডিল তৈরি করে |

## পরবর্তী পদক্ষেপ

- [সার্ভার মোড এবং ক্লায়েন্ট মোড](../routing/fbr/modes.md)
- [React নেক্সিতে](../views/react/differences.md)
- [কর্ম](../guides/actions.md)
- [দ্বীপপুঞ্জ](../rendering/islands.md)
