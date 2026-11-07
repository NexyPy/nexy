# De Astro para Nexy

Uma página Nexy `.nexy` é uma página Astro com Python em seu `---` frontmatter em vez de TypeScript: o mesmo HTML server-first, as mesmas ilhas e `client:*` diretivas, renderizadas em cada solicitação.

Cada seção abaixo mostra um hábito Astro, então a mesma coisa no Nexy.

## Uma página

```astro filename="src/pages/about.astro"
---
const title = "About";
---
<h1>{title}</h1>
```

O frontmatter é Python e o modelo é Jinja2:

```nexy filename="src/rotas/about.nexy"
---
title = "About"
---
<h1>{{ title }}</h1>
```

`src/pages/` é `src/routes/` e `index.astro` é `index.nexy`.

## Loops e condições

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
> Astro escapa a cada `{value}`. Os modelos `.nexy` não: escapam do que um visitante digitou com `{{ value | e }}`.

## Componentes e `Astro.props`

```astro filename="src/components/Card.astro"
---
const { title, tone = "neutral" } = Astro.props;
---
<article class={`card card-${tone}`}>
  <h2>{title}</h2>
  <slot />
</article>
```

Props são declarados com `prop[...]`, um padrão é um Python padrão e `<slot />` é `<Slot />`:

```nexy filename="src/componentes/Card.nexy"
---
title: prop[str]
tone: prop[str] = "neutral"
---
<article class="card card-{{ tone }}">
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/rotas/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest" tone="warm">
  <p>This week</p>
</Card>
```

`@` é `src/`: `nx new` escreve `useAliases = {"@": "src"}` em `nexyconfig.py`.

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

Uma página não importa seu layout: o `layout.nexy` mais próximo acima dela a envolve, e a raiz possui o documento.

```nexy filename="src/rotas/layout.nexy"
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

## O título e meta tags

A propriedade `title` do layout se torna `metadata` na página, que `useMetadata().html()` escreve no `<head>` do layout acima:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## Rotas dinâmicas e `getStaticPaths`

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

Uma página dinâmica `.nexy` é renderizada mediante solicitação, portanto não há lista de caminhos: o segmento é um suporte e um segmento desconhecido é um `404`.

```nexy filename="src/rotas/posts/[slug].nexy"
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

`[...path].astro` é `[...path].nexy`.

## Ilhas e `client:*`

```astro filename="src/pages/index.astro"
---
import Counter from "../components/Counter.tsx";
---
<h1>Static heading</h1>
<Counter start={3} client:visible />
```

A diretiva se torna um atributo `directive`, com os mesmos valores:

```nexy filename="src/rotas/home.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

| Astro | Nexy |
|---|---|
| `client:load` | `directive="client:load"`, ou nenhuma diretiva |
| `client:idle` | `directive="client:idle"` |
| `client:visible` | `directive="client:visible"` |
| `client:media="(min-width: 768px)"` | `directive="client:media" media="(min-width: 768px)"` |
| `client:only="react"` | aceito, mas nunca hidrata: use `client:load` |

A estrutura é definida uma vez em `nexyconfig.py`, e um projeto usa uma:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

## Markdown páginas

```md filename="src/pages/changelog.md"
---
layout: ../layouts/Base.astro
---
# Changelog
```

Um arquivo `.md` em `src/routes/` é uma página, agrupada no layout mais próximo sem nenhuma chave `layout:`:

```md filename="src/routes/changelog.md"
# Changelog

Version 2.2 is out.
```

`.mdx` páginas também funcionam, com React ou Preact como estrutura. Consulte [Markdown e MDX](../views/nexy/markdown.md).

## Pontos de extremidade da API

```ts filename="src/pages/api/items/[id].ts"
export function GET({ params }) {
  return Response.json({ id: Number(params.id) });
}
```

```python filename="src/rotas/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

Um corpo é um modelo Pydantic, validado antes da execução da função:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## `Astro.redirect`, `Astro.cookies` e `Astro.url`

```astro filename="src/pages/account.astro"
---
const theme = Astro.cookies.get("theme")?.value ?? "light";
if (!Astro.cookies.has("session")) return Astro.redirect("/login");
const page = Astro.url.searchParams.get("page") ?? "1";
---
<p>{theme} theme, page {page}</p>
```

As mesmas leituras são ganchos e o redirecionamento é uma função:

```nexy filename="src/rotas/account.nexy"
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

Um `middleware.py` em uma subpasta envolve apenas as rotas abaixo dele, o que substitui as verificações de caminho dentro de `onRequest`.

## Astro Ações

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

Uma ação é uma função Python em `src/actions/`; um formulário posta em seu caminho:

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

De uma ilha, `useAction(add_note)` in `@nexy/client` chama a mesma função com entrada digitada.

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

```nexy filename="src/rotas/notfound.nexy"
<h1>Not found</h1>
```

Os clientes da API ainda recebem `{"detail": "Not Found"}`.

## Saída estática e renderização sob demanda

Astro cria HTML estático por padrão e renderiza sob demanda com `output: "server"` ou `export const prerender = false`. Nexy renderiza todas as páginas mediante solicitação e armazena em cache aquelas que você escolher por URL:

```nexy filename="src/routes/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

Não há exportação estática: `nx start` atende o site. Consulte [Renderização](../rendering/README.md).

## Correndo

| Astro | Nexy |
|---|---|
| `npm create astro@latest` | `nx new` |
| `astro dev` | `nx dev` |
| `astro build` e `astro preview` | `nx build`, então `nx start` |
| `public/` | `public/`, servido em `/` |
| `astro add react` | `nx new` com uma estrutura, ou `useFF = react()` |

## Próximas etapas

- [Arquivos .nexy](../views/nexy/README.md)
- [Ilhas](../rendering/islands.md)
- [Markdown e MDX](../views/nexy/markdown.md)
- [De Next.js para Nexy](nextjs.md)
