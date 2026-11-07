# Venant d'un autre cadre

Nexy, c'est FastAPI plus un routage basé sur des fichiers, des pages rendues par le serveur et des îles optionnelles React, Vue, Svelte, Solid ou Preact. Cette page cartographie ce que vous savez déjà.

Chaque framework ci-dessous possède également sa propre page, tâche par tâche, avec le code que vous connaissez puis le code Nexy :

| Python | Back-end | Pile complète JavaScript |
|---|---|---|
| [FastAPI](../coming-from/fastapi.md) | [Express](../coming-from/express.md), [Fastify](../coming-from/fastify.md) | [Next.js](../coming-from/nextjs.md), [Remix](../coming-from/remix.md) |
| [Flask](../coming-from/flask.md) | [Élysie](../coming-from/elysia.md), [Hono](../coming-from/hono.md) | [Nuxt](../coming-from/nuxt.md) |
| [Django](../coming-from/django.md) | [NestJS](../coming-from/nestjs.md), [Spring Boot](../coming-from/spring-boot.md) | [SvelteKit](../coming-from/sveltekit.md) |
| | [Laravel](../coming-from/laravel.md), [Ruby sur Rails](../coming-from/rails.md) | [Astro](../coming-from/astro.md) |

## De FastAPI

<!-- router:fbr,custom -->
| FastAPI | Nexy |
|---|---|
| `@app.get("/users")` dans un module que vous importez | Fonction `GET` dans `src/routes/users.py` |
| `app.include_router(router)` | le chemin du fichier est l'URL ; rien à inscrire |
| Paramètres de chemin `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | toujours `Depends(...)` : les gestionnaires sont des FastAPI gestionnaires |
| Jinja2 `TemplateResponse` | une page `.nexy` à côté du point de terminaison |
| Courez avec `uvicorn main:app` | `nx dev`, puis `nx build && nx start` |

Tout sous `src/routes/*.py` est ordinaire FastAPI : les dépendances, les modèles Pydantic, le middleware et `/docs` continuent de fonctionner.

Le même point final, avant et après :

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
| `@app.get("/users")` dans un module que vous importez | `async def get(self)` dans une classe `@Controller("/users")` |
| `app.include_router(router)` | le responsable du traitement répertorié dans le `controllers` d'un `@Module` |
| Paramètres de chemin `/users/{id}` | `@Controller("/users/{id}")`, avec `async def get(self, id: int)` |
| `Depends(...)` | toujours `Depends(...)` : une méthode de contrôleur est un point de terminaison FastAPI |
| Jinja2 `TemplateResponse` | `useViews("src/apps/....nexy")`, renvoyé par la méthode |
| Courir avec `uvicorn main:app` | `nx dev`, puis `nx build && nx start` |

Les dépendances, les modèles Pydantic, le middleware et `/docs` continuent de fonctionner.

Le même point final, avant et après :

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

## De Next.js

<!-- router:fbr,custom -->
| Next.js | Nexy |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` ou `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (possède `<html>`) | `src/routes/layout.tsx` avec `useCSR = True` (React), ou `src/routes/layout.nexy` en mode serveur |
| imbriqué `layout.tsx` | `layout.tsx` / `layout.vue` / `layout.svelte` imbriqués en mode client, `layout.nexy` imbriqués en mode serveur |
| `use client` composants dans une page de serveur | [îles](../rendering/islands.md) en mode serveur |
| Gestionnaires de routes `route.ts` | `src/routes/api/x.py`, écrit en Python |
| `(group)` dossiers | idem : `(group)/` |
| Actions du serveur | [`@Action`](../guides/actions.md) fonctions appelées depuis un formulaire ou sous forme de fonctions client saisies |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

Le backend est Python, donc votre API partage le code avec vos données et votre travail de ML. Les composants clients s'hydratent sous forme d'îlots au lieu d'une page entière React arbre.

Une page Next.js se déplace presque telle quelle et son composant `"use client"` devient un îlot d'une page serveur :

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
| `app/page.tsx` | un contrôleur qui renvoie `useViews("src/apps/home_view.nexy")` |
| `app/blog/[slug]/page.tsx` | `@Controller("/blog/{slug}")`, avec `async def get(self, slug: str)` |
| `app/layout.tsx` (possède `<html>`) | une vue de présentation que le contrôleur enroule autour de sa vue, via `children` |
| `use client` composants dans une page de serveur | [îles](../rendering/islands.md) dans une vue |
| Gestionnaires de routes `route.ts` | un contrôleur qui renvoie un dict, écrit en Python |
| Actions du serveur | [`@Action`](../guides/actions.md) fonctions appelées depuis un formulaire ou sous forme de fonctions client saisies |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

Le backend est Python, donc votre API partage le code avec vos données et votre travail de ML. Les composants clients s'hydratent sous forme d'îlots au lieu d'une page entière React arbre.

Une page Next.js devient un contrôleur et sa vue, et son composant `"use client"` un îlot de la vue :

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

## Depuis les backends Express ou Node

<!-- router:fbr,custom -->
| Exprimer | Nexy |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` avec `async def GET(id)` |
| `app.use(middleware)` | FastAPI middleware, enregistré depuis `nexyconfig.py` |
| `res.json(obj)` | renvoyer un dict ou un modèle Pydantic |
| Vues EJS / Carlin | `.nexy` (Jinja2) pages |
| `npm run dev` | `nx dev` |

`app.use(...)` devient un champ de `nexyconfig.py` et `res.json(...)` devient une valeur de retour :

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
| Exprimer | Nexy |
|---|---|
| `app.get("/users/:id", handler)` | `@Controller("/users/{id}")`, avec `async def get(self, id: int)` |
| `app.use(middleware)` | Middleware FastAPI, enregistré depuis `nexyconfig.py` |
| `res.json(obj)` | renvoyer un dict ou un modèle Pydantic |
| Vues EJS / Carlin | `.nexy` (Jinja2) vues, renvoyées par `useViews` |
| `npm run dev` | `nx dev` |

`app.use(...)` devient un champ de `nexyconfig.py` et `res.json(...)` devient une valeur de retour :

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

## Choisir un routeur

| Utiliser | Quand |
|---|---|
| Routeur basé sur des fichiers | pages et points de terminaison mappés à partir de fichiers ; la valeur par défaut |
| Routeur modulaire | contrôleurs, modules et injection de dépendances, style NestJS |

Le routeur modulaire en deux fichiers : un contrôleur, et le module `nexyconfig.py` pointe avec `useRouter = AppModule` :

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

Les deux sont échafaudés par `nx new` et couverts par les mêmes tests de bout en bout. Voir [Routage](../routing/README.md) et [Routage modulaire](../routing/modular/README.md).

## Où ensuite

- [Démarrage rapide](quick-start.md) : créez un projet et exécutez-le
- [Structure du projet](project-structure.md) : où appartient chaque fichier
- [Routage](../routing/README.md) : choisissez le routeur
