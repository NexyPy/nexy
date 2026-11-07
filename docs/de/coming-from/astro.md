# Von Astro zu Nexy

Eine Nexy-`.nexy`-Seite ist eine Astro-Seite mit Python in der `---`-Frontmatter anstelle von TypeScript: das gleiche Server-First-HTML, die gleichen Inseln und `client:*`-Anweisungen, die bei jeder Anfrage gerendert werden.

Jeder Abschnitt unten zeigt eine Astro-Gewohnheit, dann dasselbe in Nexy.

## Eine Seite

```astro filename="src/pages/about.astro"
---
const title = "About";
---
<h1>{title}</h1>
```

Die Titelseite ist Python und die Vorlage ist Jinja2:

```nexy filename="src/routes/about.nexy"
---
title = "About"
---
<h1>{{ title }}</h1>
```

`src/pages/` ist `src/routes/` und `index.astro` ist `index.nexy`.

## Schleifen und Bedingungen

```astro filename="src/pages/users.astro"
---
const users = [{ name: "Ada", admin: true }, { name: "Alan", admin: false }];
---
<ul>
  {users.map((user) => <li>{user.name}{user.admin && <strong> admin</strong>}</li>)}
</ul>
```

```nexy filename="src/routes/users.nexy"
---
users = [{"name": "Ada", "admin": True}, {"name": "Alan", "admin": False}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}{% if user.admin %}<strong> admin</strong>{% endif %}</li>
  {% endfor %}
</ul>
```

> [!WARNING]
> Astro entkommt alle `{value}`. `.nexy`-Vorlagen entkommen nicht: dem, was ein Besucher mit `{{ value | e }}` eingegeben hat.

## Komponenten und `Astro.props`

```astro filename="src/components/Card.astro"
---
const { title, tone = "neutral" } = Astro.props;
---
<article class={`card card-${tone}`}>
  <h2>{title}</h2>
  <slot />
</article>
```

Requisiten werden mit `prop[...]` deklariert, ein Standard ist ein Python-Standard und `<slot />` ist `<Slot />`:

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
tone: prop[str] = "neutral"
---
<article class="card card-{{ tone }}">
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/routes/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest" tone="warm">
  <p>This week</p>
</Card>
```

`@` ist `src/`: `nx new` schreibt `useAliases = {"@": "src"}` in `nexyconfig.py`.

## Layouts

```astro filename="src/layouts/Base.astro"
---
const { title } = Astro.props;
---
<html>
  <head><title>{title}</title></head>
  <body><slot /></body>
</html>
```

```astro filename="src/pages/about.astro"
---
import Base from "../layouts/Base.astro";
---
<Base title="About"><h1>About</h1></Base>
```

Eine Seite importiert ihr Layout nicht: Das nächstgelegene `layout.nexy` über ihr umschließt sie und die Stammseite ist Eigentümer des Dokuments.

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

## Der Titel und die Meta-Tags

Die `title`-Requisite des Layouts wird zu `metadata` auf der Seite, die `useMetadata().html()` in die `<head>` des obigen Layouts schreibt:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## Dynamische Routen und `getStaticPaths`

```astro filename="src/pages/posts/[slug].astro"
---
export function getStaticPaths() {
  return [
    { params: { slug: "hello" }, props: { title: "Hello" } },
    { params: { slug: "world" }, props: { title: "World" } },
  ];
}
const { title } = Astro.props;
---
<h1>{title}</h1>
```

Eine dynamische `.nexy`-Seite wird auf Anfrage gerendert, daher gibt es keine Liste von Pfaden: Das Segment ist eine Requisite und ein unbekanntes ist ein `404`.

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello", "world": "World"}

slug: prop[str]
if slug not in POSTS:
    notFound()
title = POSTS[slug]
---
<h1>{{ title }}</h1>
```

`[...path].astro` ist `[...path].nexy`.

## Inseln und `client:*`

```astro filename="src/pages/index.astro"
---
import Counter from "../components/Counter.tsx";
---
<h1>Static heading</h1>
<Counter start={3} client:visible />
```

Die Direktive wird zu einem `directive`-Attribut mit denselben Werten:

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

| Astro | Nexy |
|---|---|
| `client:load` | `directive="client:load"` oder keine Anweisung |
| `client:idle` | `directive="client:idle"` |
| `client:visible` | `directive="client:visible"` |
| `client:media="(min-width: 768px)"` | `directive="client:media" media="(min-width: 768px)"` |
| `client:only="react"` | akzeptiert, aber niemals feuchtigkeitsspendend: verwenden Sie `client:load` |

Das Framework wird einmal in `nexyconfig.py` festgelegt und ein Projekt verwendet eines:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

## Markdown Seiten

```md filename="src/pages/changelog.md"
---
layout: ../layouts/Base.astro
---
# Changelog
```

Eine `.md`-Datei unter `src/routes/` ist eine Seite, die im nächstgelegenen Layout ohne den Schlüssel `layout:` umschlossen ist:

```md filename="src/routes/changelog.md"
# Changelog

Version 2.2 is out.
```

`.mdx`-Seiten funktionieren auch, mit React oder Preact als Framework. Siehe [Markdown und MDX](../views/nexy/markdown.md).

## API-Endpunkte

```ts filename="src/pages/api/items/[id].ts"
export function GET({ params }) {
  return Response.json({ id: Number(params.id) });
}
```

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

Ein Körper ist ein Pydantic Modell, das vor der Ausführung der Funktion validiert wird:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## `Astro.redirect`, `Astro.cookies` und `Astro.url`

```astro filename="src/pages/account.astro"
---
const theme = Astro.cookies.get("theme")?.value ?? "light";
if (!Astro.cookies.has("session")) return Astro.redirect("/login");
const page = Astro.url.searchParams.get("page") ?? "1";
---
<p>{theme} theme, page {page}</p>
```

Die gleichen Lesevorgänge sind Hooks und die Umleitung ist eine Funktion:

```nexy filename="src/routes/account.nexy"
---
from nexy import redirect, useCookies, useSearchParams

cookies = useCookies()
if "session" not in cookies:
    redirect("/login")
theme = cookies.get("theme", "light")
page = useSearchParams().get("page", "1")
---
<p>{{ theme }} theme, page {{ page }}</p>
```

## Middleware

```ts filename="src/middleware.ts"
export function onRequest(context, next) {
  return next().then((response) => {
    response.headers.set("x-app", "demo");
    return response;
  });
}
```

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

Ein `middleware.py` in einem Unterordner umschließt nur die Routen darunter, was die Pfadprüfungen innerhalb von `onRequest` ersetzt.

## Astro Aktionen

```ts filename="src/actions/index.ts"
import { defineAction } from "astro:actions";
import { z } from "astro:schema";

export const server = {
  addNote: defineAction({
    accept: "form",
    input: z.object({ title: z.string() }),
    handler: async ({ title }) => ({ title }),
  }),
};
```

```astro filename="src/pages/notes.astro"
---
import { actions } from "astro:actions";
---
<form method="POST" action={actions.addNote}>
  <input name="title" />
  <button>Add</button>
</form>
```

Eine Aktion ist eine Python-Funktion in `src/actions/`; Ein Formular postet in seinem Pfad:

```python filename="src/actions/notes.py"
from nexy.decorators import Action

NOTES: list[str] = []


@Action
async def add_note(title: str) -> None:
    NOTES.append(title)
```

```nexy filename="src/routes/notes.nexy"
---
from src.actions.notes import NOTES
---
<form method="post" action="{{ __actions_path['add_note'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
<ul>
  {% for note in NOTES %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

Von einer Insel aus ruft `useAction(add_note)` in `@nexy/client` dieselbe Funktion mit typisierter Eingabe auf.

## `<Image />`

```astro
---
import { Image } from "astro:assets";
import logo from "../assets/logo.png";
---
<Image src={logo} alt="Logo" width={128} height={32} />
```

```nexy filename="src/routes/brand.nexy"
---
from nexy import Image
---
<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

## `404.astro`

```astro filename="src/pages/404.astro"
<h1>Not found</h1>
```

```nexy filename="src/routes/notfound.nexy"
<h1>Not found</h1>
```

API-Clients erhalten weiterhin `{"detail": "Not Found"}`.

## Statische Ausgabe und On-Demand-Rendering

Astro erstellt standardmäßig statisches HTML und rendert bei Bedarf mit `output: "server"` oder `export const prerender = false`. Nexy rendert jede Seite auf Anfrage und speichert die von Ihnen ausgewählten Seiten pro URL im Cache:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

Es gibt keinen statischen Export: `nx start` bedient die Site. Siehe [Rendering](../rendering/README.md).

## Laufen

| Astro | Nexy |
|---|---|
| `npm create astro@latest` | `nx new` |
| `astro dev` | `nx dev` |
| `astro build` und `astro preview` | `nx build`, dann `nx start` |
| `public/` | `public/`, serviert am `/` |
| `astro add react` | `nx new` mit einem Framework, oder `useFF = react()` |

## Nächste Schritte

- [.nexy-Dateien](../views/nexy/README.md)
- [Inseln](../rendering/islands.md)
- [Markdown und MDX](../views/nexy/markdown.md)
- [Von Next.js zu Nexy](nextjs.md)
