# Recetas

Tres cosas que casi todas las aplicaciones necesitan, como archivos completos que puedes copiar. Cada bloque de código a continuación con un
`filename` está escrito en un proyecto nuevo y ejercido por el conjunto de pruebas, por lo que lo que lees es lo que
corre.

Utilizan controladores API simples; las mismas funciones funcionan detrás de una página en cualquier [modo](../routing/fbr/modes.md).

## Iniciar sesión con una sesión

Un visitante publica un nombre y una contraseña, el servidor los recuerda en una cookie firmada y todo
bajo `/api/account` está cerrado para cualquier otra persona.

Activa las sesiones. Necesitan `itsdangerous` (`uv add itsdangerous`):

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me-in-production"}
```

Iniciar y cerrar sesión:

```python filename="src/rutas/api/login.py"
from pydantic import BaseModel

from nexy.http import HTTPException, Request

USERS = {"ada": "lovelace"}


class Credentials(BaseModel):
    name: str
    password: str


async def POST(request: Request, body: Credentials):
    if USERS.get(body.name) != body.password:
        raise HTTPException(status_code=401, detail="Wrong name or password")
    request.session["user"] = body.name
    return {"user": body.name}
```

```python filename="src/rutas/api/logout.py"
from nexy.http import Request


async def POST(request: Request):
    request.session.clear()
    return {"signed_out": True}
```

Guarde una carpeta completa con un [`dependencies.py`](../routing/fbr/dependencies/README.md):

```python filename="src/routes/api/account/dependencies.py"
from nexy.http import HTTPException, Request


def current_user(request: Request) -> str:
    if not request.session.get("user"):
        raise HTTPException(status_code=401, detail="Sign in first")
    return request.session["user"]


dependencies = [current_user]
```

```python filename="src/rutas/api/account/index.py"
from nexy.http import Request


async def GET(request: Request):
    return {"user": request.session["user"]}
```

> [!NOTA]
> mantenga las contraseñas reales fuera de la fuente. Almacene un hash (`argon2`, `bcrypt`) y lea
> la clave secreta del entorno. La cookie de sesión está firmada, no cifrada.

## Una API JSON con creación, lectura y eliminación

Una tienda en un módulo, una ruta de recogida y una ruta de artículos. Reemplace el diccionario con
[una base de datos](databases.md) cuando los datos deben sobrevivir a un reinicio.

```python filename="src/notas.py"
from pydantic import BaseModel


class Note(BaseModel):
    id: int
    title: str


NOTES: dict[int, Note] = {}
```

```python filename="src/rutas/api/notes/index.py"
from pydantic import BaseModel

from src.notes import NOTES, Note


class NewNote(BaseModel):
    title: str


async def GET() -> list[Note]:
    return list(NOTES.values())


async def POST(body: NewNote) -> Note:
    note = Note(id=max(NOTES, default=0) + 1, title=body.title)
    NOTES[note.id] = note
    return note
```

```python filename="src/rutas/api/notes/[id].py"
from nexy.http import HTTPException

from src.notes import NOTES, Note


async def GET(id: int) -> Note:
    if id not in NOTES:
        raise HTTPException(status_code=404, detail="No such note")
    return NOTES[id]


async def DELETE(id: int) -> dict[str, bool]:
    if NOTES.pop(id, None) is None:
        raise HTTPException(status_code=404, detail="No such note")
    return {"deleted": True}
```

Un cuerpo que no se ajusta a `NewNote` se rechaza con `422` antes de que se ejecute el código y la devolución
la anotación se convierte en la respuesta documentada. Ver
[validación y errores](../routing/fbr/handlers/validation-and-errors.md).

## Recibir un archivo

Las cargas necesitan `python-multipart` (`uv add python-multipart`). Comprueba el tamaño tú mismo y nunca lo uses.
el nombre del archivo del cliente como ruta:

```python filename="src/rutas/api/upload.py"
from pathlib import Path

from nexy.http import HTTPException, UploadFile

MAX_BYTES = 1_000_000


async def POST(file: UploadFile) -> dict[str, int | str]:
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    name = Path(file.filename or "upload").name
    return {"name": name, "size": len(data)}
```

`Path(...).name` elimina cualquier carpeta que el cliente haya puesto en el nombre, como `../../etc/passwd`. guardar el
bytes bajo un nombre que genere, no bajo este.

## Próximos pasos

- [Acciones](actions.md): funciones de servidor escritas para formularios y botones
- [Middleware y seguridad](middleware-and-security.md): CORS, hosts, sesiones
- [Probando](testing.md): prueba tus propios controladores de la misma manera