# Next.js से नेक्सी तक

नेक्सी में एक Next.js ऐप राउटर प्रोजेक्ट अपने फ़ाइल रूट, लेआउट और React घटकों को रखता है, जबकि सर्वर कोड, रूट हैंडलर और सर्वर एक्शन उनके बगल में Python फाइलों में चले जाते हैं।

नीचे प्रत्येक अनुभाग एक Next.js आदत दिखाता है, फिर नेक्सी में भी वही चीज़।

## सबसे पहले मोड चुनें

एक Next.js ऐप सर्वर और क्लाइंट घटकों को एक ट्री में मिलाता है। एक नेक्सी प्रोजेक्ट `nexyconfig.py` में दो आकृतियों में से एक को चुनता है:

| आपका Next.js ऐप है | नेक्सी मोड | पन्ने हैं |
|---|---|---|
| अधिकतर इंटरैक्टिव, क्लाइंट नेविगेशन | क्लाइंट मोड, `useCSR = True` | `.tsx` फ़ाइलें, जैसा कि `app/` में है |
| अधिकतर सामग्री, कुछ इंटरैक्टिव भाग | सर्वर मोड, डिफ़ॉल्ट | `.nexy` React द्वीपों वाले पृष्ठ |

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

नीचे दिए गए अनुभाग क्लाइंट मोड का उपयोग करते हैं जब तक कि वे अन्यथा न कहें। [सर्वर मोड और क्लाइंट मोड](../routing/fbr/modes.md) देखें।

## `page.tsx`

```tsx filename="ऐप/अबाउट/पेज.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

एक पेज स्वयं फ़ाइल है, न कि किसी फ़ोल्डर के अंदर `page.tsx`:

```tsx filename="src/routes/about.tsx"
export default function About() {
  return <h1>About</h1>;
}
```

`app/page.tsx` है `src/routes/index.tsx`, और `app/blog/page.tsx` है `src/routes/blog/index.tsx`।

## रूट फ़ाइलें, ऐप राउटर और पेज राउटर

Next.js के दोनों राउटर `src/routes/` पर मैप करते हैं। पेज राउटर की एक फ़ाइल अपना पथ बनाए रखती है; ऐप राउटर का `page.tsx` `index.tsx` बन जाता है, या उसके फ़ोल्डर के नाम पर एक फ़ाइल बन जाती है:

| Next.js | नेक्सी |
|---|---|
| `pages/about.tsx` | `src/routes/about.tsx` |
| `pages/blog/[slug].tsx` | `src/routes/blog/[slug].tsx` |
| `app/about/page.tsx` | `src/routes/about/index.tsx`, या `src/routes/about.tsx` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug]/index.tsx`, या `src/routes/blog/[slug].tsx` |
| `app/docs/[...slug]/page.tsx` | `src/routes/docs/[...slug].tsx` |
| `app/(marketing)/pricing/page.tsx` | `src/routes/(marketing)/pricing.tsx` |
| `pages/api/items/[id].ts` | `src/routes/api/items/[id].py` |
| `app/api/items/[id]/route.ts` | `src/routes/api/items/[id].py`, या `src/routes/api/items/[id]/index.py` |

एक `.tsx` फ़ाइल एक पेज है और एक `.py` फ़ाइल एक हैंडलर है: एक्सटेंशन कहता है, इसलिए एक रूट हैंडलर अपना `/route` फ़ोल्डर खो देता है।

## गतिशील खंड और `params`

```tsx filename="ऐप/ब्लॉग/[स्लग]/पेज.tsx"
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

`[...slug]` और मार्ग समूह जैसे `(marketing)` Next.js की तरह काम करते हैं।

## `generateStaticParams`

```tsx filename="ऐप/ब्लॉग/[स्लग]/पेज.tsx"
export async function generateStaticParams() {
  return [{ slug: "hello" }, { slug: "world" }];
}
```

वही निर्यात, इस नाम या `getStaticParams` के तहत, प्रति मूल्य एक पूर्व-रेंडर दस्तावेज़ देता है। नेक्सी इसे `await` के बिना कॉल करता है, इसलिए सरणी को ही वापस करें:

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

```tsx filename="ऐप/लेआउट.tsx"
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

एक ही फ़ाइल, ऊपर एक फ़ोल्डर: रूट लेआउट का स्वामी है `<html>`, और एक `layout.tsx` उसके अंदर एक सबफ़ोल्डर में स्थित है।

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

```tsx filename="ऐप/ब्लॉग/पेज.tsx"
export const metadata = { title: "Blog", description: "Posts about Nexy" };
```

एक `.tsx` पृष्ठ में कोई `metadata` निर्यात नहीं है: रूट लेआउट में टैग लिखें। सर्वर मोड में, एक `.nexy` पेज उन्हें प्रति पेज सेट करता है:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

रूट `layout.nexy` वहां टैग लिखता है जहां Next.js, `<head>` में:

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

## `next/link` और `next/navigation`

```tsx filename="ऐप/nav.tsx"
"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
```

वही नाम, `@nexy/client` से:

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

## मार्ग संचालक

```ts filename="ऐप/एपीआई/आइटम/[आईडी]/रूट.टीएस"
export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return Response.json({ id: Number(id) });
}
```

वही `GET` निर्यात, Python में, `/route` के बिना:

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

एक बॉडी एक Pydantic मॉडल है, और `/docs` प्रत्येक हैंडलर को सूचीबद्ध करता है:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## सर्वर क्रियाएँ और `revalidatePath`

```ts filename="ऐप/कार्रवाई.ts"
"use server";
import { revalidatePath } from "next/cache";

export async function addTodo(title: string) {
  await db.todo.create({ data: { title } });
  revalidatePath("/todos");
}
```

एक क्रिया एक Python फ़ंक्शन है। नेक्सी अपना टाइप किया हुआ क्लाइंट `@nexy/actions` में बनाता है:

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

`useActionState` और `useFormStatus` का नक्शा `pending`, `error` और `data` का `useAction`।

## सर्वर घटक `.nexy` पृष्ठ हैं

```tsx filename="ऐप/उपयोगकर्ता/पेज.tsx"
export default async function Users() {
  const users = await db.user.findMany();
  return <ul>{users.map((user) => <li key={user.id}>{user.name}</li>)}</ul>;
}
```

एक Next.js सर्वर घटक सर्वर पर चलता है, डेटा पढ़ता है और HTML भेजता है। एक `.nexy` पेज सर्वर मोड में एक ही चीज़ है: इसका फ्रंटमैटर Python में एसिंक घटक का मुख्य भाग है, और टेम्पलेट वह है जो यह लौटाता है।

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

| Next.js सर्वर घटक | `.nexy` पेज |
|---|---|
| `app/users/page.tsx`, नहीं `"use client"` | `src/routes/users.nexy` |
| `await db.user.findMany()` घटक में | फ्रंटमैटर में एक प्रश्न |
| `{params}` और `{searchParams}` | `slug: prop[str]` और `useSearchParams()` |
| `cookies()` और `headers()` से `next/headers` | `useCookies()` और `useHeaders()` |
| `export const revalidate = 60` | `revalidate = 60` |
| इसके अंदर एक `"use client"` घटक | एक द्वीप: `<Counter directive="client:load" />` |

क्लाइंट मोड में, एक `.tsx` पेज ब्राउज़र में चलता है, इसलिए यह एक हैंडलर से डेटा पढ़ता है:

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

## `"use client"` सर्वर पेजों के अंदर घटक

```tsx filename="ऐप/पेज.tsx"
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

सर्वर मोड में, क्लाइंट घटक एक द्वीप है, और इसका निर्देश कहता है कि यह कब हाइड्रेट होता है:

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

`client:load`, `client:idle`, `client:visible` और `client:media` के लिए [द्वीप](../rendering/islands.md) देखें।

## `revalidate` के साथ आईएसआर

```tsx filename="ऐप/न्यूज़/पेज.tsx"
export const revalidate = 60;
```

सर्वर-मोड पेज के फ्रंटमैटर में वही पंक्ति:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## `middleware.ts`

```ts filename="मिडलवेयर.ts"
import { NextResponse, type NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  if (!request.cookies.get("session")) return NextResponse.redirect(new URL("/login", request.url));
}

export const config = { matcher: "/dashboard/:path*" };
```

`matcher` फ़ोल्डर है: `dashboard/` में एक `middleware.py` इसके नीचे प्रत्येक मार्ग को लपेटता है।

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

## `notFound()` और `not-found.tsx`

```tsx filename="ऐप/ब्लॉग/[स्लग]/पेज.tsx"
import { notFound } from "next/navigation";

if (!post) notFound();
```

एक हैंडलर में, उठाएँ; सर्वर-मोड पेज में, `notFound()` पर कॉल करें:

```python filename="src/routes/api/posts/[slug].py"
from nexy.http import HTTPException

POSTS = {"hello": "Hello, world"}


async def GET(slug: str):
    if slug not in POSTS:
        raise HTTPException(status_code=404, detail="No such post")
    return {"title": POSTS[slug]}
```

`app/not-found.tsx` क्लाइंट मोड में `src/routes/notfound.tsx` है, और सर्वर मोड में `notfound.nexy` है।

## `next/image`

```tsx
import Image from "next/image";

<Image src="/logo.png" alt="Logo" width={128} height={32} />
```

`.nexy` पृष्ठ में, `Image` का `nexy` घटक:

```nexy filename="src/routes/brand.nexy"
---
from nexy import Image
---
<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

## चल रहा है

| Next.js | नेक्सी |
|---|---|
| `npx create-next-app` | `nx new`, टेम्पलेट `web-fbr-react` |
| `next dev` | `nx dev` |
| `next build && next start` | `nx build`, फिर `nx start` |
| `public/` | `public/`, `/` में सेवा दी गई |
| रनटाइम पर नोड | Python रनटाइम पर; नोड केवल क्लाइंट बंडल बनाता है |

## अगले चरण

- [सर्वर मोड और क्लाइंट मोड](../routing/fbr/modes.md)
- [React नेक्सी में](../views/react/differences.md)
- [क्रियाएँ](../guides/actions.md)
- [द्वीप](../rendering/islands.md)
