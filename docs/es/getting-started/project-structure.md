# Estructura del proyecto

Cada archivo en un proyecto Nexy tiene un trabajo y su destino depende del enrutador: `src/routes/` para el enrutamiento basado en archivos, `src/apps/` para el enrutador modular.

## Nivel superior

<!-- router:fbr -->
```text
my-app/
├─ src/
│  ├─ routes/            every file is a route
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Para elegir una carpeta, pregunte cuál es el archivo:

- **Algo que el navegador puede abrir** - una ruta: `src/routes/`.
- **Una pieza utilizada por varias rutas** - un componente o un módulo: `src/components/`, `src/`.
- **Un archivo servido tal como está** - `public/`.
- **Generado** - `__nexy__/`; nunca lo edites.

> [!WARNING]
> `src/routes/` es escaneado: un ayudante colocado allí se convierte en una ruta. Coloque un ayudante que no sea una ruta fuera de `src/routes/`, o comience su nombre con `_`.
<!-- /router -->

<!-- router:modular -->
```text
my-app/
├─ src/
│  ├─ apps/              controllers, modules and their views
│  │  ├─ app_module.py   the root module, given to useRouter
│  │  ├─ app_controller.py
│  │  ├─ app_view.nexy   a view a controller returns
│  │  ├─ layout.nexy     the frame the controllers pass their view to
│  │  └─ users/          one folder per feature: controller, module, service, model
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = AppModule
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Para elegir una carpeta, pregunte cuál es el archivo:

- **Una URL** - un método de un controlador en `src/apps/`, registrado por su módulo.
- **Una página** - una vista `.nexy` junto a su controlador, devuelta con `useViews`.
- **Una pieza utilizada por varias vistas** - `src/components/`.
- **Un archivo servido tal como está** - `public/`.
- **Generado** - `__nexy__/`; nunca lo edites.
<!-- /router -->

<!-- router:custom -->
```text
my-app/
├─ src/
│  ├─ legacy/            the FastAPI router you include
│  │  └─ api.py          router = APIRouter(prefix="/api")
│  ├─ routes/            pages and route files, served next to it
│  │  └─ index.nexy      → /
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = router
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Para elegir una carpeta, pregunte cuál es el archivo:

- **Una ruta de la aplicación incluida** - donde ya está, aquí `src/legacy/`.
- **Una nueva página o ruta** - `src/routes/`, al lado del router incluido.
- **Un archivo servido tal como está** - `public/`.
- **Generado** - `__nexy__/`; nunca lo edites.
<!-- /router -->

<!-- router:fbr,custom -->
## `src/routes/`

Cada archivo se convierte en una ruta, excepto los nombres reservados a continuación. La ruta del archivo menos la extensión es la URL; consulte [enrutamiento basado en archivos](../routing/fbr/README.md).

| Archivo | Rol |
|---|---|
| `layout.nexy` | envuelve páginas hermanas y secundarias |
| `errors.nexy` | 500 páginas para el directorio. |
| `notfound.nexy` | Página 404 para el directorio. |
| `dependencies.py` | dependencias compartidas FastAPI para el directorio |
| `__init__.py` | Python marcador de paquete |
| `loading.nexy` | reservado: excluido de las rutas, pero aún no tiene efecto de tiempo de ejecución |

El nombre de cada página también existe por marco. Con `react()` configurado, `layout.jsx` y `layout.tsx` se reservan exactamente igual que `layout.nexy`. Las listas están construidas en `nexy/core/config.py` (`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`).

> [!NOTE]
> `notfound.nexy` y `errors.nexy` solo se instalan cuando existe una copia en la raíz de las rutas. Luego, una copia en un subdirectorio refina la página para ese prefijo.
<!-- /router -->

<!-- router:modular -->
## `src/apps/`

Un controlador responde URL, un módulo agrupa controladores y proveedores, y el módulo raíz se monta con `useRouter` en `nexyconfig.py`:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller()
class AppController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/app_view.nexy")})
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    useAliases = {"@": "src"}  # the views import @/components/...
```

Ningún archivo en `src/apps/` es una ruta por su nombre: solo los controladores que enumera un módulo responden. Consulte [enrutamiento modular](../routing/modular/README.md).
<!-- /router -->

## `public/`

Los archivos aquí se sirven desde la raíz del sitio: `/favicon.ico`, `/robots.txt`, imágenes, fuentes.

## `__nexy__/`

Generado por `nx build` (y por `nx dev` para las piezas que necesita). Contiene:

- los archivos `.nexy` compilados, como un paquete Python (`__nexy__/src/...`);
- los puntos de entrada del cliente generados (`main.ts`, `vite.ts`, `*.auto.ts`);
- `client/` después de una compilación Vite - recursos, manifiesto, HTML prerenderizado;
- `build-cache.json`.

Trate todo el directorio como desechable: elimínelo, reconstrúyalo. Al editarlo a mano, se pierde el cambio en la siguiente compilación. Agréguelo a `.gitignore`.

## Próximos pasos

<!-- router:fbr -->
- [Enrutamiento basado en archivos](../routing/fbr/README.md): cómo una ruta se convierte en una URL
<!-- /router -->
<!-- router:modular -->
- [Enrutamiento modular](../routing/modular/README.md): controladores, módulos y proveedores
<!-- /router -->
<!-- router:custom -->
- [Enrutamiento personalizado](../routing/custom/README.md): incluye un enrutador FastAPI existente
<!-- /router -->
- [Configuración](../reference/config.md): cada opción del proyecto
- [Frontend](../guides/frontend.md): Vite, estilo y compilación del cliente
