# Abhängigkeiten und Wachen

Teilen Sie Authentifizierung, Datenbanksitzungen und andere Einstellungen über Routen hinweg mit FastAPI-Abhängigkeiten. Sie arbeiten auf zwei Ebenen und die Verzeichnisebene wird wie Layouts vererbt.

| Ebene | Wobei | gilt für |
|---|---|---|
| Verzeichnis | `dependencies.py` | jede Route im Verzeichnis und darunter, einschließlich Seiten |
| Handler | `Depends`, `@UseGuard`, `@Middleware` | ein Handler |

## Pro Verzeichnis: `dependencies.py`

Ein `dependencies.py` deklariert eine `dependencies`-Liste einfacher Funktionen. Nexy verpackt jedes einzelne in `Depends`.

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

> [!NOTE]
> Listen Sie die Funktionen selbst auf. Ein `Depends(...)`-Objekt in der Liste wird ignoriert.

Jede Route unter `src/routes/admin/` erfordert jetzt den Header, `.py`-Handler und `.nexy`-Seiten gleichermaßen.

## Vererbung

Abhängigkeiten werden vom Routenstamm bis hinunter zum Verzeichnis der Route gesammelt, **äußerstes zuerst**, genau wie Layouts, und die eigenen Wachen des Handlers werden zuletzt ausgeführt:

```text
src/routes/
├─ dependencies.py              1. root
└─ admin/
   ├─ dependencies.py           2. admin
   └─ users/
      ├─ dependencies.py        3. users
      └─ index.py               4. handler guards, then the handler
```

Für `GET /admin/users` ist die Reihenfolge `root`, `admin`, `users`, die `@UseGuard`-Funktionen des Handlers, seine `@Middleware`-Funktionen und dann der Handler. Eine Routengruppe (`(group)/`) ist ein Verzeichnis wie jedes andere, daher nimmt ihr `dependencies.py` teil.

## Pro Handler

Verwenden Sie `Depends` in der Signatur, wie in jeder FastAPI-App:

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header, HTTPException


def current_user(authorization: str = Header(...)) -> str:
    if authorization != "Bearer secret":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return "ada"


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## Guards und Middleware auf einem Handler

`@UseGuard` und `@Middleware` hängen FastAPI Abhängigkeiten an einen Handler an, ohne seine Signatur zu ändern. Beides sind Abhängigkeiten, keine ASGI-Middleware:

```python filename="src/routes/admin/users/index.py"
from nexy.decorators import Middleware, UseGuard


def audit() -> None: ...


def must_be_staff(x_staff: str = Header(...)) -> None: ...


@UseGuard(must_be_staff)
@Middleware(audit)
async def GET():
    return {"ok": True}
```

Für echte ASGI-Middleware (CORS, GZip, Sitzungen, Ihre eigene) verwenden Sie `useMiddlewares` und die `use*`-Optionen in [Middleware und Sicherheit](../../../guides/middleware-and-security.md).

## Eine Abhängigkeit scheitert

Eine Abhängigkeit lehnt eine Anfrage durch Auslösen ab. `HTTPException` antwortet mit dem von Ihnen angesprochenen Status, als JSON für API-Clients (`Accept: application/json`) und als Fehlerseite für Browser. Siehe [Validierung und Fehler](../handlers/validation-and-errors.md).

## Nächste Schritte

- [Vererbung](../inheritance.md)
- [Handler](../handlers/README.md)
- [Middleware und Sicherheit](../../../guides/middleware-and-security.md)
