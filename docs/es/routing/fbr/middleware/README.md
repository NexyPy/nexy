# Archivos de middleware

Un `middleware.py` en un directorio de rutas envuelve las solicitudes manejadas por ese directorio. Como diseños y
`dependencies.py`, los archivos se apilan desde la raíz de las rutas hacia abajo, primero la más externa.

```python filename="src/rutas/admin/middleware.py"
from nexy.http import Request
from nexy.http import JSONResponse


async def middleware(request: Request, call_next):
    if request.headers.get("authorization") != "Bearer secret":
        return JSONResponse({"detail": "login required"}, status_code=401)
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

La función es `async def middleware(request, call_next)`: la firma de FastAPI
`@app.middleware("http")`. Llame a `await call_next(request)` para continuar la ruta, o devolver un
respuesta para detenerse allí. El código después de que la llamada se ejecuta al salir y puede cambiar la respuesta.

## Lo que envuelve

Un middleware se aplica a las **rutas cuyo archivo está en su directorio** o debajo, páginas y API
Manejadores por igual, los grupos de rutas incluyen:

```text
src/routes/
├─ middleware.py             every route
├─ open.py                   root only
├─ admin/
│  ├─ middleware.py          /admin and everything below
│  └─ users/
│     ├─ middleware.py       /admin/users and below
│     └─ index.py            root > admin > users
└─ (shop)/
   ├─ middleware.py          only the routes in this group
   └─ cart.py                root > shop     (URL: /cart)
```

Para una solicitud a `/admin/users` el orden es `root`, `admin`, `users`, luego la ruta. Un grupo no tiene
URL propia, por lo que coincide a través de la ruta que atiende la solicitud, no a través de la URL.

Una URL que no coincide con ninguna ruta (un 404) sólo recibe el middleware de directorios que no son grupos,
seleccionado por prefijo de URL. `[slug]` coincide con un segmento y `[...rest]` coincide con el resto.

## Lo que no envuelve

- URL de marco y activos: `/__nexy__/`, `/_nexy/`, `/public/`, `/assets/` y `/@...` (Vite).
- Manejadores de WebSocket y vida útil del servidor: solo solicitudes HTTP.
- Archivos en directorios que comienzan con `_` o `.`.

## Middleware, dependencias o guardias

| Utilice | cuando |
|---|---|
| `middleware.py` | también necesitas la **respuesta**: encabezados, redirecciones, sincronización, cortocircuitos para un área completa |
| [`dependencies.py`](../dependencies/README.md) | necesita parámetros analizados o inyectar un valor (usuario actual, sesión de base de datos) |
| `@UseGuard` en un controlador | una ruta necesita una verificación adicional |
| `useMiddlewares` en [config](../../../reference/config.md) | un middleware ASGI para toda la aplicación (CORS, GZip, sesiones) |

Los archivos de middleware se ejecutan **antes de las ** dependencias: la solicitud ha pasado cada `middleware.py` de sus
directorios cuando comienzan las dependencias.

## Reglas

- El archivo debe definir `async def middleware(request, call_next)`. De lo contrario, Nexy se detiene al iniciar y
  nombra el archivo.
- Es un módulo Python normal: importa lo que necesites. Se carga una vez, cuando se inicia el servidor.
- Nunca es una ruta: `/middleware` es una 404.
- Verificaciones de ruta base en `request.scope["path"]`, nunca en `request.url.path` o en el encabezado `Host`: desde
  CVE-2026-48710 el objeto URL puede no coincidir con la ruta que recibió el servidor. Ver
  [Seguridad](../../../reference/security.md).

## Costo

Un proyecto sin `middleware.py` no paga nada: la capa no está instalada. Con archivos, cada uno
el middleware coincidente agrega una Starlette `BaseHTTPMiddleware`; mantenlos pequeños.

## Próximos pasos

- [Herencia](../inheritance.md)
- [Dependencias](../dependencies/README.md)
- [Middleware y seguridad](../../../guides/middleware-and-security.md)