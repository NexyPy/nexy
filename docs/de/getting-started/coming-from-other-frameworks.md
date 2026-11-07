# Kommt aus einem anderen Rahmen

Nexy ist FastAPI plus dateibasiertes Routing, servergerenderte Seiten und optionale React-, Vue-, Svelte-, Solid- oder Preact-Inseln. Diese Seite stellt dar, was Sie bereits wissen.

Jedes der folgenden Frameworks hat außerdem eine eigene Seite, Aufgabe für Aufgabe, mit dem Code, den Sie kennen, und dann dem Nexy-Code:

| Python | Backend | Fullstack JavaScript |
|---|---|---|
| [FastAPI](../coming-from/fastapi.md) | [Express](../coming-from/express.md), [Fastify](../coming-from/fastify.md) | [Next.js](../coming-from/nextjs.md), [Remix](../coming-from/remix.md) |
| [Flask](../coming-from/flask.md) | [Elysia](../coming-from/elysia.md), [Hono](../coming-from/hono.md) | [Nuxt](../coming-from/nuxt.md) |
| [Django](../coming-from/django.md) | [NestJS](../coming-from/nestjs.md), [Frühlingsstiefel](../coming-from/spring-boot.md) | [SvelteKit](../coming-from/sveltekit.md) |
| | [Laravel](../coming-from/laravel.md), [Ruby on Rails](../coming-from/rails.md) | [Astro](../coming-from/astro.md) |

## Von FastAPI

<!-- router:fbr,custom -->
| FastAPI | Nexy |
|---|---|
| `@app.get("/users")` in einem Modul, das Sie importieren | `GET`-Funktion in `src/routes/users.py` |
| `app.include_router(router)` | der Dateipfad ist die URL; nichts zu registrieren |
| Pfadparameter `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | immer noch `Depends(...)`: Handler sind FastAPI Handler |
| Jinja2 `TemplateResponse` | eine `.nexy`-Seite neben dem Endpunkt |
| Laufen mit `uvicorn main:app` | `nx dev`, dann `nx build && nx start` |

Alles unter `src/routes/*.py` ist normal FastAPI: Abhängigkeiten, Pydantic Modelle, Middleware und `/docs` funktionieren weiterhin.

Derselbe Endpunkt, vorher und nachher:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{id}")
async def get_user(id: int):
    return {"id": id}
```

```python filename="src/routes/users/[id].py"
async def GET(id: int):
    return {"id": id}
```
<!-- /router -->

<!-- router:modular -->
| FastAPI | Nexy |
|---|---|
| `@app.get("/users")` in einem Modul, das Sie importieren | `async def get(self)` in einer `@Controller("/users")`-Klasse |
| `app.include_router(router)` | der im `controllers` eines `@Module` aufgeführte Controller |
| Pfadparameter `/users/{id}` | `@Controller("/users/{id}")`, mit `async def get(self, id: int)` |
| `Depends(...)` | immer noch `Depends(...)`: Eine Controller-Methode ist ein FastAPI Endpunkt |
| Jinja2 `TemplateResponse` | `useViews("src/apps/....nexy")`, zurückgegeben von der Methode |
| Laufen mit `uvicorn main:app` | `nx dev`, dann `nx build && nx start` |

Abhängigkeiten, Pydantic Modelle, Middleware und `/docs` funktionieren weiterhin.

Derselbe Endpunkt, vorher und nachher:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{id}")
async def get_user(id: int):
    return {"id": id}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users/{id}")
class UserController:
    async def get(self, id: int):
        return {"id": id}
```
<!-- /router -->

## Von Next.js

<!-- router:fbr,custom -->
| Next.js | Nexy |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` oder `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (besitzt `<html>`) | `src/routes/layout.tsx` mit `useCSR = True` (React) oder `src/routes/layout.nexy` im Servermodus |
| verschachtelt `layout.tsx` | verschachtelt `layout.tsx` / `layout.vue` / `layout.svelte` im Client-Modus, verschachtelt `layout.nexy` im Server-Modus |
| `use client` Komponenten auf einer Serverseite | [Inseln](../rendering/islands.md) im Servermodus |
| Routenhandler `route.ts` | `src/routes/api/x.py`, geschrieben in Python |
| `(group)` Ordner | gleich: `(group)/` |
| Serveraktionen | [`@Action`](../guides/actions.md) Funktionen, die aus einem Formular oder als typisierte Clientfunktionen aufgerufen werden |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

Das Backend ist Python, sodass Ihre API den Code mit Ihren Daten und Ihrer ML-Arbeit teilt. Client-Komponenten hydratisieren als Inseln statt als ganzseitiger React Baum.

Eine Next.js-Seite bewegt sich fast so, wie sie ist, und ihre `"use client"`-Komponente wird zu einer Insel einer Serverseite:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

```nexy filename="src/routes/blog/[slug].nexy"
---
from "@/components/Comments.tsx" import Comments

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Comments post="{{ slug }}" directive="client:visible" />
```
<!-- /router -->

<!-- router:modular -->
| Next.js | Nexy |
|---|---|
| `app/page.tsx` | ein Controller, der `useViews("src/apps/home_view.nexy")` zurückgibt |
| `app/blog/[slug]/page.tsx` | `@Controller("/blog/{slug}")`, mit `async def get(self, slug: str)` |
| `app/layout.tsx` (besitzt `<html>`) | eine Layoutansicht, die der Controller um seine Ansicht herum umschließt, durch `children` |
| `use client` Komponenten auf einer Serverseite | [Inseln](../rendering/islands.md) in einer Ansicht |
| Routenhandler `route.ts` | ein Controller, der ein Diktat zurückgibt, geschrieben in Python |
| Serveraktionen | [`@Action`](../guides/actions.md) Funktionen, die aus einem Formular oder als typisierte Clientfunktionen aufgerufen werden |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

Das Backend ist Python, sodass Ihre API Code mit Ihren Daten und ML-Arbeit teilt. Client-Komponenten hydratisieren als Inseln anstelle eines ganzseitigen React-Baums.

Eine Next.js-Seite wird zu einem Controller und seiner Ansicht, und seine `"use client"`-Komponente wird zu einer Insel der Ansicht:

```python filename="src/apps/blog/post_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/blog/post_view.nexy", context={"slug": slug})
```

```nexy filename="src/apps/blog/post_view.nexy"
---
from "@/components/Comments.tsx" import Comments

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Comments post="{{ slug }}" directive="client:visible" />
```
<!-- /router -->

## Von Express- oder Node-Backends

<!-- router:fbr,custom -->
| Express | Nexy |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` mit `async def GET(id)` |
| `app.use(middleware)` | FastAPI Middleware, registriert von `nexyconfig.py` |
| `res.json(obj)` | Gibt ein Diktat oder ein Pydantic-Modell zurück |
| EJS/Pug-Ansichten | `.nexy` (Jinja2) Seiten |
| `npm run dev` | `nx dev` |

`app.use(...)` wird zu einem Feld von `nexyconfig.py` und `res.json(...)` wird zu einem Rückgabewert:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

```python filename="src/routes/users/[id].py"
async def GET(id: int):
    return {"id": id, "name": "Ada"}  # res.json({ id, name })
```
<!-- /router -->

<!-- router:modular -->
| Express | Nexy |
|---|---|
| `app.get("/users/:id", handler)` | `@Controller("/users/{id}")`, mit `async def get(self, id: int)` |
| `app.use(middleware)` | FastAPI Middleware, registriert von `nexyconfig.py` |
| `res.json(obj)` | Gibt ein Diktat oder ein Pydantic-Modell zurück |
| EJS/Pug-Ansichten | `.nexy` (Jinja2) Aufrufe, zurückgegeben von `useViews` |
| `npm run dev` | `nx dev` |

`app.use(...)` wird zu einem Feld von `nexyconfig.py` und `res.json(...)` wird zu einem Rückgabewert:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users/{id}")
class UserController:
    async def get(self, id: int):
        return {"id": id, "name": "Ada"}  # res.json({ id, name })
```
<!-- /router -->

## Auswahl eines Routers

| Benutzen | Wann |
|---|---|
| Dateibasierter Router | aus Dateien zugeordnete Seiten und Endpunkte; die Standardeinstellung |
| Modularer Router | Controller, Module und Abhängigkeitsinjektion im NestJS-Stil |

Der modulare Router besteht aus zwei Dateien: einem Controller und dem Modul `nexyconfig.py` mit `useRouter = AppModule`:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller


@Controller()
class AppController:
    async def get(self):
        return {"message": "Hello"}
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

Beide basieren auf `nx new` und werden von denselben End-to-End-Tests abgedeckt. Siehe [Routing](../routing/README.md) und [Modulares Routing](../routing/modular/README.md).

## Wohin als nächstes

- [Schnellstart](quick-start.md): Erstellen Sie ein Projekt und führen Sie es aus
- [Projektstruktur](project-structure.md): Wohin jede Datei gehört
- [Routing](../routing/README.md): Wählen Sie den Router aus
