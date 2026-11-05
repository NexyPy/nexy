# Routenhandler

Eine `.py`-Datei unter `src/routes/` ist ein API-Handler. Der Dateipfad ist die URL und jede nach einer HTTP-Methode benannte Funktion wird zu einem Endpunkt.

## Erstellen Sie einen Endpunkt

```python filename="src/routes/api/items.py"
from nexy.http import Request
from pydantic import BaseModel


class Item(BaseModel):
    name: str


async def GET(request: Request):
    return {"items": []}


async def POST(request: Request, body: Item):
    return {"created": body.name}
```

Diese Datei beantwortet `GET /api/items` und `POST /api/items`.

Unterstützte Funktionsnamen: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`, `HEAD`. `SOCKET` öffnet ein WebSocket im gleichen Pfad – siehe [WebSocket](../realtime/websocket.md).

## Das HTTP-Vokabular

Importieren Sie, was ein Handler benötigt, von `nexy.http`:

```python
from nexy.http import Depends, Header, HTTPException, JSONResponse, Request, status
```

Es macht die Anforderungs- und Antwortklassen (`Request`, `Response`, `JSONResponse`, `HTMLResponse`, `PlainTextResponse`, `RedirectResponse`, `StreamingResponse`, `FileResponse`), die Parameterquellen (`Header`, `Query`, `Cookie`, `Path`, `Body`), `Depends` verfügbar. `BackgroundTasks`, `HTTPException` und `status`. Für dieses Modul geschriebene Handler hängen von Nexys Vertrag ab, nicht von der Engine, die sie bedient. Pydantic Modelle beschreiben Körper und Reaktionen wie üblich.

## Parameter

| Quelle | Wie es kommt |
|---|---|
| Pfadsegment `[id]` | Funktionsargument `id`, konvertiert in seine Annotation |
| Abfragezeichenfolge | `page: int = 1` |
| JSON-Körper | Pydantic Modellargument |
| FastAPI Grundelemente | `Depends`, `Header`, `Cookie`, `Form`, `UploadFile` – unverändert |

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

Das Pfadsegment ist `{id}`, daher validiert FastAPI `id: int`. Ein Wert, der keine Ganzzahl ist, antwortet `404`, da eine dynamische Route jede URL erfasst und eine URL, die nicht konvertiert werden kann, nicht existiert. Siehe [Validierung und Fehler](validation-and-errors.md).

## Antworten

| Rückgabe | Antwort |
|---|---|
| `dict`, `list`, `BaseModel` | JSON |
| `JSONResponse`, `HTMLResponse`, alle `Response` | genau wie deklariert |
| `None` | leere Antwort – stattdessen ein `Response` zurückgeben, wenn der Status wichtig ist |

Geben Sie für einen benutzerdefinierten Statuscode oder Inhaltstyp ein Antwortobjekt zurück:

```python filename="src/routes/api/items.py"
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"created": True}, status_code=201)
```

## Fehler

Lösen Sie FastAPI Ausnahmen für Clients aus. Ein Client, der `Accept: application/json` sendet, erhält `{"detail": "..."}` mit dem von Ihnen ausgelösten Status; Ein Browser empfängt die Fehlerseite. `notfound.nexy` rendert `404` und `errors.nexy` rendert `500`, jeweils bezogen auf sein Verzeichnis. Siehe [Validierung und Fehler](validation-and-errors.md) und [Fehlerseiten](../errors/README.md).

## OpenAPI

Jede API-Route erscheint im generierten Schema, da es sich bei den Routen um einfache FastAPI Routen handelt. Das Schema wird unter `/openapi.json` bereitgestellt und von Scalar unter `/docs` gerendert. Deaktivieren Sie beide mit `useDocs = False` in `nexyconfig.py`.

## Nächste Schritte

- [Abhängigkeiten](../dependencies/README.md): Gemeinsame Authentifizierung und Einrichtung pro Handler oder pro Verzeichnis
- [Validierung und Fehler](validation-and-errors.md): `422`, `404` und JSON-Fehler
- [Routing](../../README.md): Dateipfad zur URL
- [Aktionen](../../../guides/actions.md): Endpunkte mit generierten Pfaden
- [Config](../../../reference/config.md): Middleware, CORS, Sitzungen
