# Incluir un enrutador FastAPI existente en Nexy

Para incluir un enrutador FastAPI existente en Nexy, configure `useRouter` en ese `APIRouter` en la clase `NexyConfig` de `nexyconfig.py`: sus rutas se sirven tal como están, junto a los archivos de `src/routes/`.

## Cuándo usar un enrutador personalizado

- **Migración gradual**: una aplicación FastAPI se mueve a Nexy ruta por ruta, y sus rutas antiguas siguen respondiendo mientras tanto.
- **Reutilización de código**: un paquete ya expone un `APIRouter`, para autenticación o facturación.
- **Un backend que conservas**: la API permanece simple FastAPI y Nexy agrega las páginas.

## Establecer `useRouter` en `nexyconfig.py`

El enrutador es cualquier FastAPI `APIRouter`, escrito de la forma en que ya escribe uno:

```python filename="src/legacy/api.py"
from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/status")
async def status():
    return {"status": "ok"}


@router.get("/users/{id}")
async def user(id: int):
    return {"id": id}
```

`useRouter` es un campo de la clase `NexyConfig`, como cada configuración del proyecto:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

`nx dev` luego responde a `GET /api/status` y `GET /api/users/{id}`, y `/docs` los enumera.

> [!NOTE]
> `useRouter` en `nexyconfig.py` es una configuración. `from nexy import useRouter` es otra cosa: el gancho que usa una página `.nexy` para leer la ruta actual. No lo importe para configurar el enrutador.

## Varios enrutadores

`useRouter` toma un enrutador. Reúna varios bajo un solo padre con `include_router`:

```python filename="src/legacy/__init__.py"
from fastapi import APIRouter

from .api import router as api
from .auth import router as auth

router = APIRouter()
router.include_router(api)
router.include_router(auth, prefix="/auth")
```

```python filename="src/legacy/auth.py"
from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login():
    return {"token": "demo"}
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

## Páginas y archivos de ruta al lado

`src/routes/` todavía se lee mientras `useRouter` está configurado: una página `.nexy` o un archivo de ruta `.py` responde junto a las rutas incluidas.

```nexy filename="src/rutas/index.nexy"
---
title = "Home"
---
<h1>{{ title }}</h1>
```

```python filename="src/rutas/api/health.py"
async def GET():
    return {"ok": True}
```

Dos límites mientras se establece `useRouter`:

- las páginas no están envueltas por `layout.nexy`;
- `useCSR = True` es rechazado: `nx dev` y `nx build` responden a `useCSR requires file-based routing`.

Una URL se responde una vez. Asigne un prefijo al enrutador incluido, aquí `/api`, y mantenga los archivos de `src/routes/` fuera de las rutas que utiliza.

## Toda una aplicación FastAPI

`useRouter` toma una aplicación `APIRouter`, no una `FastAPI`. Las rutas de una aplicación se ubican en su atributo `router`:

```python filename="src/legacy/servicio.py"
from fastapi import FastAPI

service = FastAPI(title="Billing")


@service.get("/billing/invoices")
async def invoices():
    return []
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.service import service


class NexyConfig(NexyConfigModel):
    useRouter = service.router
```

El middleware, los controladores de excepciones y los eventos de inicio propios de la aplicación se quedan atrás: muévalos a `useMiddlewares` y a los demás campos de `nexyconfig.py`.

## Dependencias, autenticación y base de datos.

El enrutador se ejecuta en el proceso Nexy, por lo que `Depends`, los esquemas de seguridad y las sesiones de la base de datos funcionan como en la aplicación original:

```python filename="src/legacy/secure.py"
from fastapi import APIRouter, Depends, Header, HTTPException


def require_token(x_token: str = Header("")) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=401, detail="Bad token")


router = APIRouter(prefix="/secure", dependencies=[Depends(require_token)])


@router.get("/data")
async def data():
    return {"data": 42}
```

## Pruébalo

```python filename="pruebas/test_legacy.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_the_included_route_answers():
    assert TestClient(app).get("/api/status").json() == {"status": "ok"}
```

## Próximos pasos

- [De FastAPI a Nexy](../../coming-from/fastapi.md): mueve las rutas a archivos, una por una
- [Enrutamiento basado en archivos](../fbr/README.md)
- [Enrutamiento modular](../modular/README.md): `useRouter = AppModule`
