# Viniendo de otro marco

Nexy es FastAPI más enrutamiento basado en archivos, páginas renderizadas por servidor e islas opcionales React, Vue, Svelte, Solid o Preact. Esta página mapea lo que ya sabes.

Cada marco a continuación también tiene una página propia, tarea por tarea, con el código que conoce y luego el código Nexy:

| Python | backend | Pila completa JavaScript |
|---|---|---|
| [FastAPI](../coming-from/fastapi.md) | [Expresar](../coming-from/express.md), [Fastificar](../coming-from/fastify.md) | [Next.js](../coming-from/nextjs.md), [Remix](../coming-from/remix.md) |
| [Flask](../coming-from/flask.md) | [Elysia](../coming-from/elysia.md), [Hono](../coming-from/hono.md) | [Nuxt](../coming-from/nuxt.md) |
| [Django](../coming-from/django.md) | [NestJS](../coming-from/nestjs.md), [Bota de primavera](../coming-from/spring-boot.md) | [Kit esbelto](../coming-from/sveltekit.md) |
| | [Laravel](../coming-from/laravel.md), [Ruby on Rails](../coming-from/rails.md) | [Astro](../coming-from/astro.md) |

## Desde FastAPI

<!-- router:fbr,custom -->
| FastAPI | nexy |
|---|---|
| `@app.get("/users")` en un módulo que importas | Función `GET` en `src/routes/users.py` |
| `app.include_router(router)` | la ruta del archivo es la URL; nada que registrar |
| Parámetro de ruta `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | todavía `Depends(...)`: los controladores son FastAPI controladores |
| Jinja2 `TemplateResponse` | una página `.nexy` al lado del punto final |
| Ejecutar con `uvicorn main:app` | `nx dev`, luego `nx build && nx start` |

Todo lo que hay en `src/routes/*.py` es normal FastAPI: dependencias, Pydantic modelos, middleware y `/docs` siguen funcionando.

El mismo punto final, antes y después:

```python filename="principal.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{id}")
async def get_user(id: int):
    return {"id": id}
```

```python filename="src/rutas/usuarios/[id].py"
async def GET(id: int):
    return {"id": id}
```
<!-- /router -->

<!-- router:modular -->
| FastAPI | nexy |
|---|---|
| `@app.get("/users")` en un módulo que importas | `async def get(self)` en una clase `@Controller("/users")` |
| `app.include_router(router)` | el controlador listado en el `controllers` de un `@Module` |
| Parámetro de ruta `/users/{id}` | `@Controller("/users/{id}")`, con `async def get(self, id: int)` |
| `Depends(...)` | todavía `Depends(...)`: un método de controlador es un punto final FastAPI |
| Jinja2 `TemplateResponse` | `useViews("src/apps/....nexy")`, devuelto por el método |
| Ejecutar con `uvicorn main:app` | `nx dev`, luego `nx build && nx start` |

Las dependencias, los modelos Pydantic, el middleware y `/docs` siguen funcionando.

El mismo punto final, antes y después:

```python filename="principal.py"
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

## Desde Next.js

<!-- router:fbr,custom -->
| Next.js | nexy |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` o `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (posee `<html>`) | `src/routes/layout.tsx` con `useCSR = True` (React), o `src/routes/layout.nexy` en modo servidor |
| anidado `layout.tsx` | anidado `layout.tsx` / `layout.vue` / `layout.svelte` en modo cliente, anidado `layout.nexy` en modo servidor |
| `use client` componentes en una página de servidor | [islas](../rendering/islands.md) en modo servidor |
| Controladores de ruta `route.ts` | `src/routes/api/x.py`, escrito en Python |
| `(group)` carpetas | mismo: `(group)/` |
| Acciones del servidor | [`@Action`](../guides/actions.md) funciones llamadas desde un formulario o como funciones de cliente escritas |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

El backend es Python, por lo que su API comparte código con sus datos y su trabajo de ML. Los componentes del cliente se hidratan como islas en lugar de un árbol de página completa React.

Una página Next.js se mueve casi como está y su componente `"use client"` se convierte en una isla de una página de servidor:

```tsx filename="src/rutas/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

```nexy filename="src/rutas/blog/[slug].nexy"
---
from "@/components/Comments.tsx" import Comments

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Comments post="{{ slug }}" directive="client:visible" />
```
<!-- /router -->

<!-- router:modular -->
| Next.js | nexy |
|---|---|
| `app/page.tsx` | un controlador que devuelve `useViews("src/apps/home_view.nexy")` |
| `app/blog/[slug]/page.tsx` | `@Controller("/blog/{slug}")`, con `async def get(self, slug: str)` |
| `app/layout.tsx` (posee `<html>`) | una vista de diseño que el controlador envuelve alrededor de su vista, a través de `children` |
| `use client` componentes en una página del servidor | [islas](../rendering/islands.md) en una vista |
| Controladores de ruta `route.ts` | un controlador que devuelve un dict, escrito en Python |
| Acciones del servidor | [`@Action`](../guides/actions.md) funciones llamadas desde un formulario o como funciones de cliente escritas |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

El backend es Python, por lo que su API comparte código con sus datos y su trabajo de ML. Los componentes del cliente se hidratan como islas en lugar de un árbol de página completa React.

Una página Next.js se convierte en un controlador y su vista, y su componente `"use client"` en una isla de la vista:

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

## Desde backends Express o Node

<!-- router:fbr,custom -->
| expreso | nexy |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` con `async def GET(id)` |
| `app.use(middleware)` | FastAPI middleware, registrado desde `nexyconfig.py` |
| `res.json(obj)` | devolver un dict o un modelo Pydantic |
| Vistas EJS/Pug | `.nexy` (Jinja2) páginas |
| `npm run dev` | `nx dev` |

`app.use(...)` se convierte en un campo de `nexyconfig.py` y `res.json(...)` se convierte en un valor de retorno:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

```python filename="src/rutas/usuarios/[id].py"
async def GET(id: int):
    return {"id": id, "name": "Ada"}  # res.json({ id, name })
```
<!-- /router -->

<!-- router:modular -->
| expreso | nexy |
|---|---|
| `app.get("/users/:id", handler)` | `@Controller("/users/{id}")`, con `async def get(self, id: int)` |
| `app.use(middleware)` | FastAPI middleware, registrado desde `nexyconfig.py` |
| `res.json(obj)` | devolver un dict o un modelo Pydantic |
| Vistas EJS/Pug | `.nexy` (Jinja2) vistas, devueltas por `useViews` |
| `npm run dev` | `nx dev` |

`app.use(...)` se convierte en un campo de `nexyconfig.py` y `res.json(...)` se convierte en un valor de retorno:

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

## Elegir un enrutador

| uso | cuando |
|---|---|
| Enrutador basado en archivos | páginas y puntos finales mapeados a partir de archivos; el valor predeterminado |
| Enrutador modular | Controladores, módulos e inyección de dependencias, estilo NestJS. |

El enrutador modular en dos archivos: un controlador y el módulo `nexyconfig.py` apunta con `useRouter = AppModule`:

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

Ambos están respaldados por `nx new` y cubiertos por las mismas pruebas de un extremo a otro. Consulte [Enrutamiento](../routing/README.md) y [Enrutamiento modular](../routing/modular/README.md).

## donde sigue

- [Inicio rápido](quick-start.md): crea un proyecto y ejecútalo
- [Estructura del proyecto](project-structure.md): dónde pertenece cada archivo
- [Enrutamiento](../routing/README.md): elige el enrutador
