# De Astro a Nexy

Una página Nexy `.nexy` es una página Astro con Python en su `---` portada en lugar de TypeScript: el mismo HTML primero en el servidor, las mismas islas y directivas `client:*`, renderizadas en cada solicitud.

Cada sección a continuación muestra un hábito Astro, luego lo mismo en Nexy.

## una pagina

```astro filename="src/pages/about.astro"
---
const title = "About";
---
<h1>{title}</h1>
```

El frontmatter es Python y la plantilla es Jinja2:

```nexy filename="src/rutas/about.nexy"
---
title = "About"
---
<h1>{{ title }}</h1>
```

`src/pages/` es `src/routes/` y `index.astro` es `index.nexy`.

## Bucles y condiciones

```astro filename="src/pages/usuarios.astro"
---
const users = [{ name: "Ada", admin: true }, { name: "Alan", admin: false }];
---
<ul>
  {users.map((user) => <li>{user.name}{user.admin && <strong> admin</strong>}</li>)}
</ul>
```

```nexy filename="src/rutas/usuarios.nexy"
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
> Astro escapa cada `{value}`. Las plantillas `.nexy` no: escapan de lo que un visitante escribió con `{{ value | e }}`.

## Componentes y `Astro.props`

```astro filename="src/components/Card.astro"
---
const { title, tone = "neutral" } = Astro.props;
---
<article class={`card card-${tone}`}>
  <h2>{title}</h2>
  <slot />
</article>
```

Los accesorios se declaran con `prop[...]`, un valor predeterminado es un valor predeterminado Python y `<slot />` es `<Slot />`:

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

```nexy filename="src/rutas/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest" tone="warm">
  <p>This week</p>
</Card>
```

`@` es `src/`: `nx new` escribe `useAliases = {"@": "src"}` en `nexyconfig.py`.

## Diseños

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

Una página no importa su diseño: el `layout.nexy` más cercano encima de ella la envuelve y la raíz es propietaria del documento.

```nexy filename="src/rutas/layout.nexy"
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

## El título y las metaetiquetas.

El accesorio `title` del diseño se convierte en `metadata` en la página, que `useMetadata().html()` escribe en el `<head>` del diseño anterior:

```nexy filename="src/rutas/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## Rutas dinámicas y `getStaticPaths`

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

Una página dinámica `.nexy` se representa a pedido, por lo que no hay una lista de rutas: el segmento es un accesorio y uno desconocido es un `404`.

```nexy filename="src/rutas/publicaciones/[slug].nexy"
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

`[...path].astro` es `[...path].nexy`.

## Islas y `client:*`

```astro filename="src/pages/index.astro"
---
import Counter from "../components/Counter.tsx";
---
<h1>Static heading</h1>
<Counter start={3} client:visible />
```

La directiva se convierte en un atributo `directive`, con los mismos valores:

```nexy filename="src/rutas/home.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

| Astro | nexy |
|---|---|
| `client:load` | `directive="client:load"`, o ninguna directiva |
| `client:idle` | `directive="client:idle"` |
| `client:visible` | `directive="client:visible"` |
| `client:media="(min-width: 768px)"` | `directive="client:media" media="(min-width: 768px)"` |
| `client:only="react"` | aceptado, pero nunca hidrata: usar `client:load` |

El marco se establece una vez en `nexyconfig.py` y un proyecto usa uno:

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

Un archivo `.md` bajo `src/routes/` es una página, envuelta en el diseño más cercano sin clave `layout:`:

```md filename="src/rutas/changelog.md"
# Changelog

Version 2.2 is out.
```

Las páginas `.mdx` también funcionan, con React o Preact como marco. Ver [Markdown y MDX](../views/nexy/markdown.md).

## Puntos finales API

```ts filename="src/pages/api/items/[id].ts"
export function GET({ params }) {
  return Response.json({ id: Number(params.id) });
}
```

```python filename="src/rutas/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

Un cuerpo es un modelo Pydantic, validado antes de que se ejecute la función:

```python filename="src/rutas/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## `Astro.redirect`, `Astro.cookies` y `Astro.url`

```astro filename="src/pages/account.astro"
---
const theme = Astro.cookies.get("theme")?.value ?? "light";
if (!Astro.cookies.has("session")) return Astro.redirect("/login");
const page = Astro.url.searchParams.get("page") ?? "1";
---
<p>{theme} theme, page {page}</p>
```

Las mismas lecturas son ganchos y la redirección es una función:

```nexy filename="src/rutas/cuenta.nexy"
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

## software intermedio

```ts filename="src/middleware.ts"
export function onRequest(context, next) {
  return next().then((response) => {
    response.headers.set("x-app", "demo");
    return response;
  });
}
```

```python filename="src/rutas/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

Un `middleware.py` en una subcarpeta solo envuelve las rutas debajo de ella, lo que reemplaza las comprobaciones de ruta dentro de `onRequest`.

## Astro Acciones

```ts filename="src/acciones/index.ts"
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

Una acción es una función Python en `src/actions/`; un formulario publica en su ruta:

```python filename="src/acciones/notas.py"
from nexy.decorators import Action

NOTES: list[str] = []


@Action
async def add_note(title: str) -> None:
    NOTES.append(title)
```

```nexy filename="src/rutas/notas.nexy"
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

Desde una isla, `useAction(add_note)` en `@nexy/client` llama a la misma función con entrada escrita.

## `<Image />`

```astro
---
import { Image } from "astro:assets";
import logo from "../assets/logo.png";
---
<Image src={logo} alt="Logo" width={128} height={32} />
```

```nexy filename="src/rutas/marca.nexy"
---
from nexy import Image
---
<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

## `404.astro`

```astro filename="src/pages/404.astro"
<h1>Not found</h1>
```

```nexy filename="src/rutas/notfound.nexy"
<h1>Not found</h1>
```

Los clientes de API aún obtienen `{"detail": "Not Found"}`.

## Salida estática y renderizado bajo demanda

Astro construye HTML estático de forma predeterminada y lo renderiza bajo demanda con `output: "server"` o `export const prerender = false`. Nexy procesa cada página a pedido y almacena en caché las que usted elige por URL:

```nexy filename="src/rutas/noticias.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

No hay exportación estática: `nx start` sirve al sitio. Consulte [Renderizado](../rendering/README.md).

## corriendo

| Astro | nexy |
|---|---|
| `npm create astro@latest` | `nx new` |
| `astro dev` | `nx dev` |
| `astro build` y `astro preview` | `nx build`, luego `nx start` |
| `public/` | `public/`, servido en `/` |
| `astro add react` | `nx new` con un marco, o `useFF = react()` |

## Próximos pasos

- [Archivos .nexy](../views/nexy/README.md)
- [Islas](../rendering/islands.md)
- [Markdown y MDX](../views/nexy/markdown.md)
- [De Next.js a Nexy](nextjs.md)
