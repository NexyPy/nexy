# Remix से नेक्सी तक

नेक्सी में एक Remix या React राउटर रूट अपना React घटक रखता है, जबकि इसका `loader` एक Python हैंडलर बन जाता है, इसका `action` एक Python एक्शन होता है, और नेस्टेड रूट एक `layout.tsx` के साथ फ़ोल्डर बन जाते हैं।

नीचे प्रत्येक अनुभाग एक Remix आदत दिखाता है, फिर नेक्सी में भी वही चीज़। React फ्रेमवर्क मोड में राउटर v7 समान नामों का उपयोग करता है।

## मोड चुनें

एक Remix ऐप क्लाइंट पर नेविगेट करता है, इसलिए यह क्लाइंट मोड पर मैप होता है:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

एक सामग्री साइट जिसे केवल कुछ इंटरैक्टिव भागों की आवश्यकता होती है, सर्वर मोड में बेहतर फिट बैठती है: `.nexy` पृष्ठों वाले React द्वीप। [सर्वर मोड और क्लाइंट मोड](../routing/fbr/modes.md) देखें।

## फ़ाइलें रूट करें

| Remix (`app/routes/`) | नेक्सी (`src/routes/`) |
|---|---|
| `_index.tsx` | `index.tsx` |
| `about.tsx` | `about.tsx` |
| `blog.$slug.tsx` | `blog/[slug].tsx` |
| `files.$.tsx` (छींट) | `files/[...path].tsx` |
| `_auth.login.tsx` (पथहीन लेआउट) | `(auth)/login.tsx`, एक मार्ग समूह |
| `api.items.$id.ts` (संसाधन मार्ग) | `api/items/[id].py` |

बिंदु फ़ोल्डर बन जाते हैं, और `$param` `[param]` बन जाते हैं।

## `useParams`

```tsx filename="ऐप/रूट्स/ब्लॉग.$slug.tsx"
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

## `loader` और `useLoaderData`

```tsx filename="ऐप/रूट्स/यूजर्स.tsx"
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

लोडर एक Python हैंडलर पर चला जाता है, और पेज इसे पढ़ता है:

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

सर्वर मोड में, एक `.nexy` पेज एक फ़ाइल में लोडर और दृश्य है, और डेटा पहले HTML में है:

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

## `params` और `request` एक लोडर में

```tsx filename="ऐप/रूट्स/api.orders.$id.ts"
export async function loader({ params, request }: LoaderFunctionArgs) {
  const currency = new URL(request.url).searchParams.get("currency") ?? "EUR";
  if (Number(params.id) > 100) throw new Response("No such order", { status: 404 });
  return json({ id: Number(params.id), currency });
}
```

पथ और क्वेरी मान टाइप किए गए पैरामीटर हैं, और एक त्रुटि उत्पन्न होती है:

```python filename="src/routes/api/orders/[id].py"
from nexy.http import HTTPException


async def GET(id: int, currency: str = "EUR"):
    if id > 100:
        raise HTTPException(status_code=404, detail="No such order")
    return {"id": id, "currency": currency}
```

## `action`, `<Form>` और `useActionData`

```tsx filename="ऐप/रूट्स/todos.tsx"
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

कार्रवाई टाइप किए गए क्लाइंट के साथ एक Python फ़ंक्शन है, और `useAction` वही रखता है जो `useActionData` और `useNavigation().state` रखता है:

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

`revalidate("/todos")` वही करता है जो Remix प्रत्येक क्रिया के बाद करता है: पृष्ठ अपना डेटा फिर से लोड करता है।

## `useFetcher`

```tsx
const fetcher = useFetcher();
fetcher.submit({ title: "Write the docs" }, { method: "post", action: "/todos" });
```

`useAction` एक फ़ेचर है जो एक क्रिया से बंधा हुआ है: इसे उतने घटकों से कॉल करें जितनी आपको आवश्यकता हो, प्रत्येक का अपना `pending` और `data` हो।

## प्रगतिशील वृद्धि

एक Remix `<Form>` JavaScript लोड होने से पहले काम करता है। सर्वर मोड में, एक सादा फॉर्म उसी तरह से एक क्रिया पर पोस्ट करता है, और विज़िटर `303` के साथ पृष्ठ पर वापस आता है:

```nexy filename="src/routes/notes.nexy"
---
from src.actions.todos import add_todo
---
<form method="post" action="{{ __actions_path['add_todo'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
```

## नेस्टेड मार्ग और `<Outlet />`

```tsx filename="ऐप/रूट्स/डैशबोर्ड.tsx"
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

मूल मार्ग फ़ोल्डर का `layout.tsx` बन जाता है, और `<Outlet />` `children` बन जाता है:

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

```tsx filename="ऐप/रूट.tsx"
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

रूट `layout.tsx` दस्तावेज़ का स्वामी है। रखने के लिए कोई `<Scripts />` या `<Links />` नहीं है: नेक्सी क्लाइंट बंडल को स्वयं जोड़ता है।

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

```tsx filename="ऐप/रूट्स/ब्लॉग.tsx"
export const meta = () => [{ title: "Blog" }, { name: "description", content: "Posts" }];
```

एक `.tsx` पृष्ठ में कोई `meta` निर्यात नहीं है: रूट लेआउट में टैग लिखें। सर्वर मोड में, एक `.nexy` पेज उन्हें `metadata = {...}` के साथ सेट करता है, और इसका लेआउट उन्हें `{{ useMetadata().html() }}` के साथ लिखता है।

## `<Link>`, `<NavLink>` और `useNavigate`

```tsx filename="ऐप/घटक/Nav.tsx"
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

`<NavLink>` एक `Link` के साथ `activeClassName` है, और `useNavigate()(path)` `router.push(path)` है।

## `redirect` और सत्र

```tsx filename="ऐप/रूट्स/डैशबोर्ड.tsx"
export async function loader({ request }: LoaderFunctionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  if (!session.has("user")) throw redirect("/login");
  return null;
}
```

फ़ोल्डर में एक `middleware.py` उसके नीचे के प्रत्येक रूट से पहले चलता है, इसमें पेज शामिल हैं:

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

`createCookieSessionStorage` `nexyconfig.py` का एक क्षेत्र बन जाता है, और `request.session` एक तानाशाही है:

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

## त्रुटि सीमाएँ

एक रूट के `ErrorBoundary` निर्यात का कोई नेक्सी समकक्ष नहीं है। एक विफल लोडर एक स्थिति कोड है: एपीआई क्लाइंट को `{"detail": ...}` मिलता है, और एक अज्ञात यूआरएल `src/routes/notfound.tsx` प्रस्तुत करता है। किसी घटक को प्रस्तुत करते समय होने वाली त्रुटियाँ a द्वारा पकड़ी जाती हैं React आपकी अपनी त्रुटि सीमा, उस हिस्से के आसपास जो विफल हो सकता है।

## `headers` और कैशिंग

```tsx filename="ऐप/रूट्स/न्यूज़.tsx"
export const headers = () => ({ "Cache-Control": "public, s-maxage=60, stale-while-revalidate=60" });
```

सर्वर मोड में, फ्रंटमैटर में एक पंक्ति उस हेडर को भेजती है और रेंडर किए गए पेज को रखती है:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

## चल रहा है

| Remix / React राउटर | नेक्सी |
|---|---|
| `npx create-react-router` | `nx new`, टेम्पलेट `web-fbr-react` |
| `react-router dev` | `nx dev` |
| `react-router build`, फिर `react-router-serve` | `nx build`, फिर `nx start` |
| `public/` | `public/`, `/` में सेवा दी गई |
| रनटाइम पर नोड | Python रनटाइम पर; नोड केवल क्लाइंट बंडल बनाता है |

## अगले चरण

- [से Next.js से नेक्सी](nextjs.md)
- [React नेक्सी में](../views/react/differences.md)
- [क्रियाएँ](../guides/actions.md)
- [सर्वर मोड और क्लाइंट मोड](../routing/fbr/modes.md)
