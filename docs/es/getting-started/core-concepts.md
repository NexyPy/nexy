# Conceptos centrales

Las palabras que usan el resto de los documentos (ruta, página, vista, componente, controlador, punto final) cada una en una línea, con un enlace a la página que profundiza. ¿Nuevo en Nexy? Comience con [¿Qué es Nexy?](what-is-nexy.md).

## Cómo leer estos documentos

| Nivel | La pregunta que responde | Empezar con |
|---|---|---|
| Arquitectura de aplicaciones | qué capa responde a una solicitud y qué se niega a hacer | [Cómo funciona Nexy](how-nexy-works.md) |
| Estructura de la aplicación | dónde vive el código y en qué se convierte un archivo | [Estructura del proyecto](project-structure.md) |
| Presentación y renderizado | qué ve el lector y quién produce el HTML | [Vistas](../views/README.md), [Renderizado](../rendering/README.md) |
| Interacción de la aplicación | Qué hace el lector y qué se ejecuta en respuesta. | [Acciones](../guides/actions.md) |

Los niveles se leen en ese orden una vez. Después de eso, la página que necesita es una búsqueda, no un curso.

## Arquitectura de aplicaciones

Tres formas de decidir qué código responde a una URL. Son alternativas, no capas:

- **Enrutamiento basado en archivos (FBR)**: un archivo en `src/routes/` es una ruta. El valor predeterminado.
- **Enrutador modular**: controladores y módulos bajo `src/apps/`, declarados con decoradores, para una base de código estilo NestJS.
- **Enrutador personalizado**: un FastAPI `APIRouter` existente incluido en la aplicación.

La elección es una línea de la clase `NexyConfig` en `nexyconfig.py`.

<!-- router:fbr -->
El enrutamiento basado en archivos no necesita línea: sin `useRouter`, Nexy lee `src/routes/`.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    pass  # file-based: no useRouter, the files of src/routes/ are the routes
```
<!-- /router -->

<!-- router:modular -->
El enrutador modular es el módulo raíz de `src/apps/`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule  # modular: the root module of src/apps/
```
<!-- /router -->

<!-- router:custom -->
Un enrutador personalizado es un `APIRouter` que ya tienes:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import api  # an APIRouter you already have


class NexyConfig(NexyConfigModel):
    useRouter = api  # custom: your router, included as it is
```
<!-- /router -->

Elegir uno de los tres es una decisión. La elección de un marco de interfaz de usuario es otra opción independiente: consulte [Elija un enrutador](../routing/README.md) y [Vistas](../views/README.md).

## Estructura de la aplicación

Cinco nociones que un lector procedente de Next.js suele fusionar en una sola. No son lo mismo y la diferencia explica la mayoría de las preguntas de "por qué mi página no muestra".

| noción | que es | lo que no es |
|---|---|---|
| **Ruta** | un patrón de URL, producido por la ruta de un archivo | un archivo: un archivo puede responder a varias URL (`[slug]`) |
| **Página** | un archivo de ruta que representa una vista: `.nexy`, `.md`, `.mdx`, `.tsx`, `.vue`, `.svelte` | un punto final: responde a un documento, no a datos |
| **Ver** | qué produce el cuerpo de una página: Jinja2 y Python, Markdown, o un componente de cliente | una ruta: la misma vista puede servir a varias páginas |
| **Componente** | una pieza reutilizable una página importa | una ruta: en modo servidor un componente nunca se sirve por sí solo |
| **Controlador de ruta** | la función de un archivo de ruta `.py`, llamado así por el método HTTP (`GET`, `POST`,…) | una página: devuelve JSON, un archivo o un `Response` |
| **Punto final** | el par (URL, método) que responde un controlador | un controlador: un archivo puede responder a varios puntos finales |

En una frase: **una página es un archivo de ruta, una vista es lo que la representa, un componente es lo que una página reutiliza, un controlador responde a un punto final.**

<!-- router:fbr -->
Los cinco en un pequeño proyecto:

```text
src/
├─ routes/
│  ├─ blog/[slug].nexy    a route (/blog/{slug}) whose file is a page
│  └─ api/posts.py        a route whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```nexy filename="src/rutas/blog/[slug].nexy"
---
from "@/components/Like.tsx" import Like

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Like post="{{ slug }}" />
```

La portada y la plantilla debajo son la vista de la página; `Like` es el componente que reutiliza.

```python filename="src/rutas/api/posts.py"
async def GET():  # the endpoint GET /api/posts
    return {"posts": []}


async def POST():  # the endpoint POST /api/posts
    return {"created": True}
```

<!-- /router -->

<!-- router:modular -->
Con el enrutador modular, una ruta es la ruta de un controlador y un controlador es uno de sus métodos, llamado así por el verbo HTTP:

```text
src/
├─ apps/
│  ├─ app_module.py       the root module: lists the controllers
│  └─ posts_controller.py a route (/api/posts) whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```python filename="src/apps/posts_controller.py"
from nexy.decorators import Controller


@Controller("/api/posts")
class PostsController:
    async def get(self) -> dict:  # the endpoint GET /api/posts
        return {"posts": []}

    async def post(self) -> dict:  # the endpoint POST /api/posts
        return {"created": True}
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .posts_controller import PostsController


@Module()
class AppModule:
    controllers = [PostsController]
```

Una página sigue siendo un archivo de `src/routes/`, o una vista que devuelve un controlador con `useViews`.
<!-- /router -->

<!-- router:custom -->
Con un enrutador personalizado, una ruta es una ruta de su `APIRouter` y un controlador es la función que registra su decorador:

```python filename="src/legacy.py"
from fastapi import APIRouter

api = APIRouter()


@api.get("/api/posts")  # the endpoint GET /api/posts
async def list_posts():
    return {"posts": []}


@api.post("/api/posts")  # the endpoint POST /api/posts
async def create_post():
    return {"created": True}
```

Las páginas siguen siendo archivos de `src/routes/`: una página `.nexy` responde junto a las rutas incluidas.
<!-- /router -->

Dos palabras más que vuelven por todas partes:

- **Diseño**: un archivo `layout.*` que envuelve las páginas debajo de su carpeta; el raíz posee el documento HTML. Consulte [Diseños](../routing/fbr/layouts/README.md).
- **Dependencia**: una función que se ejecuta antes de un controlador, se aplica por ruta o por carpeta. Consulte [Dependencias](../routing/fbr/dependencies/README.md).

## Presentación y renderizado

Dos decisiones independientes, a menudo confundidas:

- **El formato** decide qué archivo representa la página: [Vistas](../views/README.md).
- **El modo** decide quién produce el HTML y cuándo: [Renderizado](../rendering/README.md).

| noción | una linea |
|---|---|
| Modo servidor | el servidor muestra las páginas `.nexy` y `.md`; los componentes son islas ([modos](../routing/fbr/modes.md)) |
| Modo cliente | `useCSR = True`: los archivos framework son las rutas y la navegación se realiza en el navegador |
| RSS, ISR, RSC, islas | cuatro modos de renderizado, decididos por página excepto CSR, que es por proyecto ([renderizado](../rendering/README.md)) |
| Hidratación | el navegador adjunta un marco al HTML que el servidor ya envió ([islas](../rendering/islands.md)) |
| Accesorios | los valores que un padre pasa a un componente, declarados `name: prop[type]` en un archivo `.nexy` (archivos [.nexy](../views/nexy/README.md)) |

Una página en modo servidor con una isla: el servidor representa la página, el navegador hidrata el gráfico solo cuando se desplaza a la vista.

<!-- router:fbr,custom -->
```nexy filename="src/rutas/ventas.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Sales</h1>
<Chart directive="client:visible" />
```
<!-- /router -->

<!-- router:modular -->
La isla entra en la vista y el controlador devuelve la vista:

```nexy filename="src/apps/sales_view.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Sales</h1>
<Chart directive="client:visible" />
```

```python filename="src/apps/sales_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/sales")
class SalesController:
    async def get(self):
        return useViews("src/apps/sales_view.nexy")
```
<!-- /router -->

## Interacción de la aplicación

| noción | una linea |
|---|---|
| acción | una función Python marcada `@Action`, servida como `POST`, invocable desde un formulario o como una función escrita ([acciones](../guides/actions.md)) |
| Formulario | un formulario HTML que se publica en una acción, con errores de validación que regresan a la página ([acciones](../guides/actions.md)) |
| Navegación | enlaces que captan previamente y ganchos que leen la ruta, la consulta, las cookies y la sesión ([ganchos](../routing/fbr/navigation/hooks.md)) |
| Obtención de datos | hecho por la página o el controlador que lo necesita; Nexy no incluye ninguna capa de datos del cliente ([manejadores](../routing/fbr/handlers/README.md)) |

Una acción y el formulario que se publica en ella, que funciona antes de que se cargue cualquier script:

```python filename="src/acciones/newsletter.py"
from nexy.decorators import Action


@Action
async def subscribe(email: str) -> bool:
    return True
```

<!-- router:fbr,custom -->
```html filename="src/rutas/index.nexy"
<form method="post" action="{{ __actions_path['subscribe'] }}">
  <input name="email" type="email">
  <button type="submit">Subscribe</button>
</form>
```
<!-- /router -->

<!-- router:modular -->
```html filename="src/apps/home_view.nexy"
<form method="post" action="{{ __actions_path['subscribe'] }}">
  <input name="email" type="email">
  <button type="submit">Subscribe</button>
</form>
```
<!-- /router -->

## Lo que Nexy no hace

La autenticación, autorización, base de datos, internacionalización, trabajos en segundo plano, correo electrónico, pagos y búsqueda son **responsabilidad de su aplicación**, no del marco. Nexy proporciona los puntos de extensión y dice dónde conectar cada uno: consulte [Lo que Nexy te deja](how-nexy-works.md#what-nexy-leaves-to-you).

<!-- router:fbr -->
La autenticación, por ejemplo, se conecta a una dependencia de la carpeta que protege. Nexy lo ejecuta antes de cada ruta a continuación; quién es el usuario sigue siendo tu decisión:

```python filename="src/rutas/cuenta/dependencias.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```
<!-- /router -->

<!-- router:modular -->
La autenticación, por ejemplo, se conecta a una protección del controlador que protege. Nexy lo ejecuta antes que cada controlador de la clase; quién es el usuario sigue siendo tu decisión:

```python filename="src/apps/account_controller.py"
from nexy import unauthorized
from nexy.decorators import Controller, UseGuard
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


@Controller("/account")
@UseGuard(require_login)
class AccountController:
    async def get(self) -> dict:
        return {"ok": True}
```
<!-- /router -->

<!-- router:custom -->
La autenticación, por ejemplo, se conecta a una dependencia del enrutador que protege, como en FastAPI; quién es el usuario sigue siendo tu decisión:

```python filename="src/cuenta.py"
from fastapi import APIRouter, Depends

from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


api = APIRouter(prefix="/account", dependencies=[Depends(require_login)])
```
<!-- /router -->

La razón no es el minimalismo en sí: un marco que elige su ORM o su biblioteca de autenticación ha decidido algo que solo su aplicación puede decidir.

## Próximos pasos

- [Estructura del proyecto](project-structure.md): cada carpeta y archivo de un proyecto
- [Glosario](../reference/glossary.md): las mismas palabras, en un índice alfabético
- [Cómo funciona Nexy](how-nexy-works.md): las capas, quién construye qué y qué te deja Nexy
