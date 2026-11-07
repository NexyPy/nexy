# Binden Sie einen vorhandenen FastAPI Router in Nexy ein

Um einen vorhandenen FastAPI-Router in Nexy einzubinden, setzen Sie `useRouter` auf diesen `APIRouter` in der `NexyConfig`-Klasse von `nexyconfig.py`: Seine Routen werden unverändert neben den Dateien von `src/routes/` bereitgestellt.

## Wann sollte ein benutzerdefinierter Router verwendet werden?

- **Schrittweise Migration**: Eine FastAPI-App bewegt sich Route für Route zu Nexy, und ihre alten Routen antworten in der Zwischenzeit weiterhin.
- **Code-Wiederverwendung**: Ein Paket stellt bereits einen `APIRouter` zur Authentifizierung oder Abrechnung bereit.
- **Ein Backend, das Sie behalten**: Die API bleibt einfach FastAPI und Nexy fügt die Seiten hinzu.

## Stellen Sie `useRouter` in `nexyconfig.py` ein

Der Router ist ein beliebiger FastAPI `APIRouter`, der so geschrieben ist, wie Sie ihn bereits geschrieben haben:

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

`useRouter` ist ein Feld der Klasse `NexyConfig`, wie jede Einstellung des Projekts:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

`nx dev` beantwortet dann `GET /api/status` und `GET /api/users/{id}` und `/docs` listet sie auf.

> [!NOTE]
> `useRouter` in `nexyconfig.py` ist eine Einstellung. `from nexy import useRouter` ist eine andere Sache: der Hook, den eine `.nexy`-Seite verwendet, um die aktuelle Route zu lesen. Importieren Sie es nicht, um den Router zu konfigurieren.

## Mehrere Router

`useRouter` benötigt einen Router. Sammeln Sie mehrere unter einem Elternteil mit `include_router`:

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

## Seiten und Routendateien daneben

`src/routes/` wird weiterhin gelesen, während `useRouter` gesetzt ist: Eine `.nexy`-Seite oder eine `.py`-Routendatei antwortet neben den enthaltenen Routen.

```nexy filename="src/routes/index.nexy"
---
title = "Home"
---
<h1>{{ title }}</h1>
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"ok": True}
```

Zwei Grenzwerte, während `useRouter` eingestellt ist:

- Seiten werden nicht von `layout.nexy` umbrochen;
- `useCSR = True` wird abgelehnt: `nx dev` und `nx build` antworten `useCSR requires file-based routing`.

Eine URL wird einmal beantwortet. Geben Sie dem mitgelieferten Router ein Präfix, hier `/api`, und halten Sie die Dateien von `src/routes/` von den von ihm verwendeten Pfaden fern.

## Eine ganze FastAPI App

`useRouter` benötigt eine `APIRouter`-App, keine `FastAPI`-App. Die Routen einer App basieren auf ihrem `router`-Attribut:

```python filename="src/legacy/service.py"
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

Die eigene Middleware, Ausnahmehandler und Startereignisse der App bleiben zurück: Verschieben Sie sie nach `useMiddlewares` und die anderen Felder von `nexyconfig.py`.

## Abhängigkeiten, Authentifizierung und die Datenbank

Der Router läuft im Nexy-Prozess, daher funktionieren `Depends`, Sicherheitsschemata und Datenbanksitzungen wie in der Original-App:

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

## Testen Sie es

```python filename="tests/test_legacy.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_the_included_route_answers():
    assert TestClient(app).get("/api/status").json() == {"status": "ok"}
```

## Nächste Schritte

- [Von FastAPI nach Nexy](../../coming-from/fastapi.md): Verschieben Sie die Routen nacheinander in Dateien
- [Dateibasiertes Routing](../fbr/README.md)
- [Modulares Routing](../modular/README.md): `useRouter = AppModule`
