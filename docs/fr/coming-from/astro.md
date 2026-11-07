# De Astro à Nexy

Une page Nexy `.nexy` est une page Astro avec Python dans son frontmatter `---` au lieu de TypeScript : le même HTML serveur d'abord, les mêmes îlots et les directives `client:*`, rendues à chaque requête.

Chaque section ci-dessous montre une habitude Astro, puis la même chose dans Nexy.

## Une page

```astro filename="src/pages/about.astro"
---
const title = "About";
---
<h1>{title}</h1>
```

Le thème principal est Python et le modèle est Jinja2 :

```nexy filename="src/routes/about.nexy"
---
title = "About"
---
<h1>{{ title }}</h1>
```

`src/pages/` est `src/routes/` et `index.astro` est `index.nexy`.

## Boucles et conditions

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
> Astro s'échappe tous les `{value}`. Les modèles `.nexy` n'échappent pas à ce qu'un visiteur a tapé avec `{{ value | e }}`.

## Composants et `Astro.props`

```astro filename="src/components/Card.astro"
---
const { title, tone = "neutral" } = Astro.props;
---
<article class={`card card-${tone}`}>
  <h2>{title}</h2>
  <slot />
</article>
```

Les accessoires sont déclarés avec `prop[...]`, une valeur par défaut est une valeur par défaut de Python et `<slot />` est `<Slot />` :

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

`@` est `src/` : `nx new` écrit `useAliases = {"@": "src"}` dans `nexyconfig.py`.

## Mises en page

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

Une page n'importe pas sa mise en page : le `layout.nexy` le plus proche au-dessus d'elle l'enveloppe et la racine est propriétaire du document.

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

## Le titre et les balises méta

Le accessoire `title` de la mise en page devient `metadata` dans la page, que `useMetadata().html()` écrit dans le `<head>` de la mise en page ci-dessus :

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## Itinéraires dynamiques et `getStaticPaths`

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

Une page `.nexy` dynamique s'affiche sur demande, il n'y a donc pas de liste de chemins : le segment est un accessoire et un segment inconnu est un `404`.

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

`[...path].astro` est `[...path].nexy`.

## Îles et `client:*`

```astro filename="src/pages/index.astro"
---
import Counter from "../components/Counter.tsx";
---
<h1>Static heading</h1>
<Counter start={3} client:visible />
```

La directive devient un attribut `directive`, avec les mêmes valeurs :

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

| Astro | Nexy |
|---|---|
| `client:load` | `directive="client:load"`, ou pas de directive |
| `client:idle` | `directive="client:idle"` |
| `client:visible` | `directive="client:visible"` |
| `client:media="(min-width: 768px)"` | `directive="client:media" media="(min-width: 768px)"` |
| `client:only="react"` | accepté, mais n'hydrate jamais : utiliser `client:load` |

Le framework est défini une fois dans `nexyconfig.py`, et un projet en utilise un :

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

## Markdown pages

```md filename="src/pages/changelog.md"
---
layout: ../layouts/Base.astro
---
# Changelog
```

Un fichier `.md` sous `src/routes/` est une page, enveloppée dans la mise en page la plus proche, sans clé `layout:` :

```md filename="src/routes/changelog.md"
# Changelog

Version 2.2 is out.
```

Les pages `.mdx` fonctionnent également, avec React ou Preact comme cadre. Voir [Markdown et MDX](../views/nexy/markdown.md).

## Points de terminaison de l'API

```ts filename="src/pages/api/items/[id].ts"
export function GET({ params }) {
  return Response.json({ id: Number(params.id) });
}
```

```python filename="src/routes/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

Un corps est un modèle Pydantic, validé avant l'exécution de la fonction :

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## `Astro.redirect`, `Astro.cookies` et `Astro.url`

```astro filename="src/pages/compte.astro"
---
const theme = Astro.cookies.get("theme")?.value ?? "light";
if (!Astro.cookies.has("session")) return Astro.redirect("/login");
const page = Astro.url.searchParams.get("page") ?? "1";
---
<p>{theme} theme, page {page}</p>
```

Les mêmes lectures sont des hooks et la redirection est une fonction :

```nexy filename="src/routes/compte.nexy"
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

## Intergiciel

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

Un `middleware.py` dans un sous-dossier encapsule uniquement les routes situées en dessous, ce qui remplace les vérifications de chemin à l'intérieur de `onRequest`.

## Astro Actions

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

Une action est une fonction Python dans `src/actions/` ; un formulaire publie sur son chemin :

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

Depuis un îlot, `useAction(add_note)` dans `@nexy/client` appelle la même fonction avec une entrée saisie.

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

Les clients API reçoivent toujours `{"detail": "Not Found"}`.

## Sortie statique et rendu à la demande

Astro crée du HTML statique par défaut et s'affiche à la demande avec `output: "server"` ou `export const prerender = false`. Nexy affiche chaque page sur demande et met en cache celles que vous choisissez par URL :

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

Il n'y a pas d'export statique : `nx start` dessert le site. Voir [Rendu](../rendering/README.md).

## Courir

| Astro | Nexy |
|---|---|
| `npm create astro@latest` | `nx new` |
| `astro dev` | `nx dev` |
| `astro build` et `astro preview` | `nx build`, puis `nx start` |
| `public/` | `public/`, servi à `/` |
| `astro add react` | `nx new` avec un cadre, ou `useFF = react()` |

## Prochaines étapes

- [Fichiers .nexy](../views/nexy/README.md)
- [Îles](../rendering/islands.md)
- [Markdown et MDX](../views/nexy/markdown.md)
- [De Next.js à Nexy](nextjs.md)
