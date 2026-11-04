# Dependencias y guardias

Comparta autenticación, sesiones de bases de datos y otras configuraciones a través de rutas con dependencias FastAPI.
Funcionan en dos niveles y el nivel del directorio se hereda como los diseños.

| Nivel | Donde | Se aplica a |
|---|---|---|
| Directorio | `dependencies.py` | todas las rutas en el directorio y debajo, páginas incluidas |
| Controlador | `Depends`, `@UseGuard`, `@Middleware` | un controlador |

## Por directorio: `dependencies.py`

Un `dependencies.py` declara una `dependencies` lista de funciones simples. Nexy envuelve cada uno en
`Depends`.

```python filename="src/rutas/admin/dependencias.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

> [!NOTA]
> enumera las funciones en sí. Se ignora un objeto `Depends(...)` en la lista.

Cada ruta en `src/routes/admin/` ahora requiere el encabezado, los controladores `.py` y las páginas `.nexy`
por igual.

## Herencia

Las dependencias se recopilan desde la raíz de las rutas hasta el directorio de la ruta, **más externo primero**,
exactamente igual que los diseños, y los propios guardias del controlador corren al final:

```text
src/routes/
├─ dependencies.py              1. root
└─ admin/
   ├─ dependencies.py           2. admin
   └─ users/
      ├─ dependencies.py        3. users
      └─ index.py               4. handler guards, then the handler
```

Para `GET /admin/users` el orden es `root`, `admin`, `users`, las funciones `@UseGuard` del controlador,
sus funciones `@Middleware`, luego el controlador. Un grupo de rutas (`(group)/`) es un directorio como cualquier
otro, por lo que su `dependencies.py` participa.

## Por controlador

Utilice `Depends` en la firma, como en cualquier aplicación FastAPI:

```python filename="src/rutas/api/me.py"
from nexy.http import Depends, Header, HTTPException


def current_user(authorization: str = Header(...)) -> str:
    if authorization != "Bearer secret":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return "ada"


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## Guardias y middleware en un controlador

`@UseGuard` y `@Middleware` adjuntan dependencias FastAPI a un controlador sin cambiar su
firma. Ambas son dependencias, no middleware ASGI:

```python filename="src/rutas/admin/users/index.py"
from nexy.decorators import Middleware, UseGuard


def audit() -> None: ...


def must_be_staff(x_staff: str = Header(...)) -> None: ...


@UseGuard(must_be_staff)
@Middleware(audit)
async def GET():
    return {"ok": True}
```

Para middleware ASGI real (CORS, GZip, sesiones, el suyo propio) utilice `useMiddlewares` y `use*`
opciones en [Middleware y seguridad](../../../guides/middleware-and-security.md).

## Fallando una dependencia

Una dependencia rechaza una solicitud planteando. `HTTPException` responde con el estado que planteaste, como
JSON para clientes API (`Accept: application/json`) y como página de error para navegadores. Ver
[Validación y errores](../handlers/validation-and-errors.md).

## Próximos pasos

- [Herencia](../inheritance.md)
- [Manejadores](../handlers/README.md)
- [Middleware y seguridad](../../../guides/middleware-and-security.md)