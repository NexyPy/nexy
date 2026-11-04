# Validierung und Fehler

Wie ein API-Handler eine fehlerhafte Anfrage meldet.

## Validierung

Handler-Parameter werden von FastAPI anhand ihrer Anmerkungen validiert.

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| Problem | Status | Text |
|---|---|---|
| fehlendes oder ungültiges Abfrage-, Header-, Cookie- oder Textfeld | `422` | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| ungültiges **Pfad**-Segment (`/api/users/abc` für `id: int`) | `404` | die nicht gefundene Seite oder JSON für `Accept: application/json` |

Ein Pfadsegment, das nicht konvertiert werden kann, ist ein `404` und nicht ein `422`: Eine dynamische Route erfasst jedes
URL, und eine URL, die nicht konvertiert werden kann, existiert nicht.

Der `422`-Körper hat die Standardform von FastAPI, sodass vorhandene Clients und generierte SDKs weiterhin funktionieren.

## Fehler melden

```python filename="src/routes/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    item = find(id)
    if item is None:
        raise HTTPException(status_code=404, detail="No such item")
    return item
```

| Client sendet | Antwort |
|---|---|
| `Accept: application/json` | `{"detail": "No such item"}` mit Status `404` |
| `Accept: text/html` | die [Fehlerseite](../errors/README.md) |
| `Accept: */*` | die Fehlerseite |

Legen Sie `Accept: application/json` in API-Clients fest. Browser rufen ständig Seiten auf.

## Unbehandelte Ausnahmen

Eine Ausnahme besteht darin, dass Ihr Handler keine Antworten `500` mit derselben HTML- oder JSON-Auswahl abfängt.

## Benutzerdefinierte Antworten

Geben Sie ein Antwortobjekt zurück, wenn Sie den Text steuern:

```python
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"error": "conflict"}, status_code=409)
```

## Nächste Schritte

- [API-Routen](README.md)
- [Fehlerseiten](../errors/README.md)
- [Testen](../../../guides/testing.md)