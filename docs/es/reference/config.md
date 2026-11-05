# configuración

La configuración es una clase en `nexyconfig.py` en la raíz del proyecto. Nexy lo carga desde el directorio en el que se ejecuta; un proyecto sin el archivo utiliza los valores predeterminados.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    usePort = 3000
    useTitle = "My App"
    useAliases = {"@": "src"}
```

## Servidor

| Campo | Por defecto | Significado |
|---|---|---|
| `usePort` | `3000` | puerto para `dev` y `start` |
| `useHost` | `"0.0.0.0"` | dirección de enlace |
| `useSslKeyfile`, `useSslCertfile` | `None` | sirven HTTPS directamente |
| `useDevTools` | `True` | la barra de herramientas `nexy dev` agrega a cada página (información de la página, rutas, errores, configuración); `False` lo elimina. Nunca presente en producción |
| `useWorkers` | `0` | procesos `nx start` ejecuciones; `0` es uno por CPU en Linux y macOS, uno en Windows |
| `useCSR` | `False` | modo de enrutamiento del lado del cliente; `.nexy` rutas están deshabilitadas |

## Rutas

| Campo | Por defecto | Significado |
|---|---|---|
| `useRouter` | `None` | una `APIRouter` instancia o clase montada junto a las rutas basadas en archivos; `None` significa basado únicamente en archivos |
| `excludeDirs` | `["templates", "extension", "docs"]` | directorios omitidos al escanear rutas |
| `useAliases` | `None` | importar alias, p.e. `{"@": "src"}` (`@/components/Counter.tsx` significa `src/components/Counter.tsx`); `nx new` escribe el que elegiste, y Vite y `tsconfig.json` lo siguen |

## Interfaz

| Campo | Predeterminado | Significado |
|---|---|---|
| `useFF` | `None` | fábrica de marcos de clientes: `react()`, `vue()`, `svelte()`, `solid()`, `preact()` |
| `useVite` | `True` | crear y servir paquetes de clientes con Vite |
| `useMarkdownExtensions` | `[]` | extensiones adicionales para `.md`/`.mdx` renderizado |
| `useWatchExtensions` | `None` | extensiones adicionales que el servidor de desarrollo observa |
| `useWatchExcludePatterns` | `None` | patrones globales que el servidor de desarrollo ignora |

> **Es bueno saberlo**: `NexyConfigModel` declara `useVite = False`; el tiempo de ejecución `Config` predeterminado es `True`.

## Nombres de archivos reservados

Cada campo agrega extensiones a un rol reservado. `useLayoutExtensions = ["md"]` hace que `layout.md` esté reservado, exactamente como `layout.nexy`.

| Campo | Agrega extensiones a |
|---|---|
| `useLayoutExtensions` | `layout.*` |
| `useNotFoundExtensions` | `notfound.*` |
| `useErrorsExtensions` | `errors.*` |
| `useForbiddenExtensions` | `forbidden.*` |
| `useUnauthorizedExtensions` | `unauthorized.*` |
| `useLoadingExtensions` | `loading.*` |

## Documentación API

| Campo | Predeterminado | Significado |
|---|---|---|
| `useDocs` | `True` | sirven el esquema OpenAPI y su página de referencia escalar |
| `useDocsUrl` | `"/docs"` | ruta de la página de referencia de API |
| `useRedocsUrl` | `"/redocs"` | declarado pero no se monta ninguna ruta |
| `useTitle` | `"Nexy App"` | OpenAPI título y título de página (`"Nexy"` en `NexyConfigModel`) |

## software intermedio

| Campo | Predeterminado | Significado |
|---|---|---|
| `useMiddlewares` | `[]` | Clases de middleware ASGI |
| `useCORS` | `None` | kwargs por `CORSMiddleware` |
| `useGZip` | `None` | kwargs por `GZipMiddleware` |
| `useTrustedHost` | `None` | kwargs por `TrustedHostMiddleware` |
| `useSession` | `None` | kwargs por `SessionMiddleware` |
| `useAuth` | `None` | configuración de middleware de autenticación |
| `useHTTPSRedirect` | `False` | redirigir HTTP a HTTPS |

## Markdown

| Campo | Predeterminado | Significado |
|---|---|---|
| `useTocDepth` | `"2-6"` | niveles de encabezado incluidos en el índice |
| `useTocTitle` | `"Table of Contents"` | Título del TOC |
| `useTocAuto` | `True` | generar la tabla de contenidos para las Markdown páginas |

## Rutas fuera del árbol de archivos

Construye un FastAPI `APIRouter` y móntalo con `useRouter`. Se sirve junto a las rutas basadas en archivos:

```python filename="nexyconfig.py"
from fastapi import APIRouter
from nexy.core.models import NexyConfigModel

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


class NexyConfig(NexyConfigModel):
    useRouter = router
```

Los valores predeterminados anteriores se leen desde `nexy/core/config.py`.

## Declarado, aún no leído

Estos campos existen en `NexyConfigModel` pero ningún código los consume. Configurarlos no tiene ningún efecto:

`useViteDevUrl`, `useRTL`.

## Próximos pasos

- [i18n](../guides/i18n.md): internacionalización
- [Frontend](../guides/frontend.md): `useFF` y la compilación del cliente
- [Implementar](../deployment/README.md): opciones de producción
