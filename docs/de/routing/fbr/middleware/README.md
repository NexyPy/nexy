# Middleware-Dateien

Ein `middleware.py` in einem Routenverzeichnis umschließt die von diesem Verzeichnis verarbeiteten Anforderungen. Wie bei Layouts und `dependencies.py` werden die Dateien vom Routenstamm abwärts gestapelt, ganz außen zuerst.

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request
from nexy.http import JSONResponse


async def middleware(request: Request, call_next):
    if request.headers.get("authorization") != "Bearer secret":
        return JSONResponse({"detail": "login required"}, status_code=401)
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

Die Funktion ist `async def middleware(request, call_next)`: die Signatur von FastAPIs `@app.middleware("http")`. Rufen Sie `await call_next(request)` an, um zur Route fortzufahren, oder geben Sie eine Antwort zurück, um dort anzuhalten. Der Code wird nach dem Anruf ausgeführt und kann die Antwort ändern.

## Was es umhüllt

Eine Middleware gilt für die **Routen, deren Datei sich in ihrem Verzeichnis** oder darunter befindet, Seiten und API-Handler gleichermaßen, einschließlich Routengruppen:

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

Bei einer Anfrage an `/admin/users` lautet die Reihenfolge `root`, `admin`, `users` und dann die Route. Eine Gruppe hat keine eigene URL, daher erfolgt der Abgleich über die Route, die die Anfrage bedient, und nicht über die URL.

Eine URL, die keiner Route entspricht (a 404), erhält nur die Middleware von Verzeichnissen, die keine Gruppen sind, ausgewählt nach URL-Präfix. `[slug]` entspricht einem Segment und `[...rest]` entspricht dem Rest.

## Was es nicht umhüllt

- Framework- und Asset-URLs: `/__nexy__/`, `/_nexy/`, `/public/`, `/assets/` und `/@...` (Vite).
- WebSocket Handler und die Serverlebensdauer: nur HTTP-Anfragen.
- Dateien in Verzeichnissen, die mit `_` oder `.` beginnen.

## Middleware, Abhängigkeiten oder Wachen

| Verwenden Sie | wenn |
|---|---|
| `middleware.py` | Sie benötigen auch die **Antwort**: Header, Weiterleitungen, Timing, Kurzschließen für einen ganzen Bereich |
| [`dependencies.py`](../dependencies/README.md) | Sie benötigen geparste Parameter oder um einen Wert einzufügen (aktueller Benutzer, Datenbanksitzung) |
| `@UseGuard` auf einem Handler | eine Route benötigt eine zusätzliche Prüfung |
| `useMiddlewares` in [Konfiguration](../../../reference/config.md) | eine ASGI-Middleware für die gesamte Anwendung (CORS, GZip, Sitzungen) |

Middleware-Dateien werden **vor** Abhängigkeiten ausgeführt: Die Anfrage hat jedes `middleware.py` ihrer Verzeichnisse passiert, als die Abhängigkeiten beginnen.

## Regeln

- Die Datei muss `async def middleware(request, call_next)` definieren. Andernfalls stoppt Nexy beim Start und benennt die Datei.
- Es ist ein normales Python Modul: Importieren Sie, was Sie brauchen. Es wird einmalig geladen, wenn der Server startet.
- Es handelt sich nie um eine Route: `/middleware` ist eine 404.
- Basispfadprüfungen auf `request.scope["path"]`, niemals auf `request.url.path` oder dem `Host`-Header: Seit CVE-2026-48710 kann das URL-Objekt mit dem vom Server empfangenen Pfad nicht übereinstimmen. Siehe [Sicherheit](../../../reference/security.md).

## Kosten

Ein Projekt ohne `middleware.py` zahlt nichts: Der Layer wird nicht installiert. Bei Dateien fügt jede passende Middleware ein Starlette `BaseHTTPMiddleware`; halte sie klein.

## Nächste Schritte

- [Vererbung](../inheritance.md)
- [Abhängigkeiten](../dependencies/README.md)
- [Middleware und Sicherheit](../../../guides/middleware-and-security.md)
