# Ausnahmen und Fehler

Eine Anfrage kann an vier Stellen fehlschlagen, und Nexy antwortet jeweils anders. Diese Seite ist der Index: Suchen Sie den Status, den Sie sehen, dann die Zeile, die ihn erzeugt hat, und dann die Datei, die den Hauptteil bestimmt.

> [!NOTE]
> Drei Dinge sind getrennt und können leicht verwechselt werden: die **HTTP-Antwort** (ein Status und ein Text), die **Fehlerseite** (`notfound.nexy`, `errors.nexy`) und die **Protokollzeile** (was Sie im Terminal lesen). Durch das Ändern der Seite wird der Status nicht geändert, und durch das Anpassen der Seite wird das Protokoll nicht ausgeblendet.

## Die Kurzversion

| Was ist passiert? | Status | Browser sieht | API-Client sieht |
|---|---|---|---|
| Keine Route entspricht der URL | `404` | `notfound.nexy`, sonst die eingebaute Seite | `{"detail": "Not Found"}` |
| Ein Pfadsegment passt nicht zu seiner Anmerkung | `404` | die gleiche Seite | `{"detail": "Not Found"}` |
| Ein Abfrage-, Header-, Cookie- oder Textfeld fehlt oder ist ungültig | `422` | FastAPIs JSON-Text | FastAPIs JSON-Text |
| `notFound()` | `404` | die Seite | `{"detail": ...}` |
| `unauthorized()` | `401` | die integrierte Seite | `{"detail": ...}` |
| `forbidden()` | `403` | die integrierte Seite | `{"detail": ...}` |
| `raise HTTPException(409, ...)` | `409` | die integrierte Seite | `{"detail": ...}` |
| Eine Ausnahme, nichts gefangen | `500` | `errors.nexy`, sonst die eingebaute Seite | `{"detail", "reference"}` |
| `redirect(url)` | `307` | das Ziel, keine Seite | das Ziel, kein Körper |
| `permanentRedirect(url)` | `308` | das Ziel, keine Seite | das Ziel |

Ein API-Client ist eine Anfrage, deren Header `Accept` nach JSON und nicht nach einer Seite fragt:

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!WARNING]
> `curl` sendet standardmäßig `Accept: */*`, wodurch die HTML-Seite abgerufen wird. Fügen Sie `-H "Accept: application/json"` hinzu, wenn Sie die JSON-Form testen. Browser rufen ständig Seiten auf.

## Woher ein Fehler kommt

```diagram filename="Eine Anfrage, vier Ausgänge"
Browser ──► Middleware ──► Router ──► Page or handler
                 │            │             │
                 │            │             ├─ return ───────────► 200
                 │            │             ├─ HTTPException ────► its status
                 │            │             └─ other exception ───► 500
                 │            └─ no match ────────────────────────► 404
                 └─ raises ──────────────────────────────────────► 500
```

| Bühne | Was kann scheitern | Die Antwort |
|---|---|---|
| Middleware | Ihre `middleware.py`, CORS, Sitzungen | der Status der Ausnahme, sonst `500` |
| Router | Die URL stimmt mit keiner Datei überein | `404` |
| Validierung | Ein Pfadsegment kann nicht konvertiert werden | `404` |
| Validierung | ein Abfrage-, Header-, Cookie- oder Textfeld | `422` |
| Seite, Handler, Aktion, Wache | `HTTPException` | seinen Status |
| Seite, Handler, Aktion, Wache | irgendetwas anderes | `500` |

## Von überall losfahren

`redirect`, `permanentRedirect`, `notFound`, `forbidden` und `unauthorized` lösen eine HTTP-Ausnahme aus, sodass derselbe Aufruf auf einer `.nexy`-Seite, einem API-Handler, einem modularen Controller, einem Guard, einem `dependencies.py` und einer Aktion funktioniert.

<!-- router:fbr,custom -->
```python filename="src/routes/posts/[slug].py"
from nexy import notFound, redirect

from src.posts import find


async def GET(slug: str):
    post = find(slug)
    if post is None:
        notFound("No such post")
    if post.moved_to:
        redirect(post.moved_to)
    return post
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/posts/posts_by_slug_controller.py"
from nexy import notFound, redirect
from nexy.decorators import Controller

from src.posts import find


@Controller("/posts/{slug}")
class PostsBySlugController:
    async def get(self, slug: str):
        post = find(slug)
        if post is None:
            notFound("No such post")
        if post.moved_to:
            redirect(post.moved_to)
        return post
```

Listen Sie den Controller im `controllers` des Root-Moduls auf.
<!-- /router -->

| Rufen Sie an | Antwort | Wann |
|---|---|---|
| `notFound(detail=None)` | `404` | Die Ressource existiert nicht |
| `unauthorized(detail=None, scheme=None)` | `401` | Der Besucher muss sich zunächst anmelden |
| `forbidden(detail=None)` | `403` | Der Besucher ist zwar bekannt, sieht dies aber möglicherweise nicht |
| `redirect(url, status=307)` | `307` | Schicken Sie sie woanders hin und behalten Sie dabei die Methode bei |
| `redirect(url, status=303)` | `303` | nach einem Formular: Die nächste Anfrage ist ein `GET` |
| `permanentRedirect(url)` | `308` | eine verschobene Seite, an die sich Suchmaschinen erinnern sollten |

Bauen Sie das Ziel auf der Grundlage von Werten auf, denen Sie vertrauen. `redirect(request.query_params["next"])` schickt Besucher dorthin, wo der Link steht; Es handelt sich um eine offene Weiterleitung. Ein Ziel, das einen Zeilenumbruch enthält, wird abgelehnt.

## Validierung: 422 oder 404

Handler-Parameter werden von FastAPI anhand ihrer Anmerkungen validiert.

<!-- router:fbr,custom -->
```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/search/search_api_controller.py"
from nexy.decorators import Controller
from nexy.http import Header


@Controller("/api/search")
class SearchApiController:
    async def get(self, q: str, limit: int = 10, x_token: str = Header(...)):
        return {"q": q, "limit": limit}
```

Listen Sie den Controller im `controllers` des Root-Moduls auf.
<!-- /router -->

| Problem | Status | Warum |
|---|---|---|
| Fehlendes oder ungültiges Abfrage-, Header-, Cookie- oder Textfeld | `422` | Die Anfrage hat den Handler erreicht, die Daten sind falsch |
| Ungültiges Pfadsegment (`/api/users/abc` für `id: int`) | `404` | Der Ordner hat keine Route für eine Nicht-Nummer, daher existiert die URL nicht |

Der `422`-Körper hat die Standardform von FastAPI, sodass Clients und generierte SDKs weiterhin funktionieren:

```json
{"detail": [{"loc": ["query", "q"], "msg": "Field required", "type": "missing"}]}
```

Für ein Formular oder eine Aktion erhält der Client ein `ActionError` mit `status` und `detail`; a `422` füllt auch `error.fields` mit einer Nachricht pro Feld. Siehe [Aktionen](../guides/actions.md#errors-and-failures).

> [!TIP]
> Validieren Sie die Signatur, wenn die Regel ein Feld betrifft (`limit: int = 10`). Validieren Sie im Text, wenn die Regel die Datenbank oder ein anderes Feld benötigt („Diese E-Mail-Adresse wird bereits verwendet“): Erhöhen Sie `HTTPException(409)` und behalten Sie die Nachricht für den Client bei.

## Benutzerdefinierte Fehlerseiten

<!-- router:fbr,custom -->
```nexy filename="src/routes/notfound.nexy"
<h1>Page not found</h1>
<p>The link may be old. <a href="/">Start from the home page</a>.</p>
```

```nexy filename="src/routes/errors.nexy"
<h1>Something went wrong</h1>
<p>Try again in a moment.</p>
```

| Datei | Status | Umfang |
|---|---|---|
| `src/routes/notfound.nexy` | `404` | jede Route des Projekts |
| `src/routes/errors.nexy` | `500` | jede Route des Projekts |
| `src/routes/forbidden.nexy` | `403` | jede Route des Projekts |
| `src/routes/unauthorized.nexy` | `401` | jede Route des Projekts |
| `src/routes/blog/notfound.nexy` | `404` | `/blog` und darunter |
| `src/routes/blog/errors.nexy` | `500` | `/blog` und darunter |
| `src/routes/loading.nexy` | - | reserviert, noch kein Laufzeiteffekt |

Eine Datei irgendwo in den Routen installiert die Antwort für ihren Status: Eine Kopie im Stammverzeichnis antwortet auf das gesamte Projekt, eine Kopie in einem Ordner antwortet auf diesen Ordner und die tiefste Datei, die mit der URL übereinstimmt, gewinnt. Eine URL außerhalb jeder Kopie und ein Status ohne Datei führen zu den integrierten gestalteten Seiten. Siehe [Fehlerseiten pro Ordner](../routing/fbr/errors/folder-pages.md).

> [!IMPORTANT]
> Eine `errors.nexy`-Seite ersetzt die `500`-Seite; Die Ausnahme wird nicht abgefangen und die Protokollzeile wird nicht geändert. Wenn der ausgelöste Handler die Seite selbst ist, kann die Seite ihre eigenen Fehlerdetails nicht anzeigen: Halten Sie `errors.nexy` einfach und unabhängig.
<!-- /router -->

<!-- router:modular -->
Der modulare Router hat keine Fehlerseite in einer Datei: `404`, `500`, `403` oder `401` erhält die integrierte gestaltete Seite. Fehlerseiten pro Ordner sind eine Konvention des dateibasierten Routers.
<!-- /router -->

## Nicht behandelte Ausnahmen

Eine Ausnahme, bei der nichts abgefangen wurde, wird einmalig protokolliert, mit ihrer Referenz, woher sie kam und dem Code um sie herum. Der Status ist `500` und der Körper ist von der Umgebung abhängig.

| | `nexy dev` | `nexy build` dann `nexy start` |
|---|---|---|
| Browser | den Fehler, die Zeilen Ihres Codes und den Traceback | `errors.nexy`, sonst die integrierte Seite, mit einer Referenz |
| API-Client | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| Terminal | die Ausnahme und die Zeilen Ihres Codes | die Ausnahme, der gesamte Traceback und die Referenz |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

Die Referenz besteht aus acht Zeichen und ist für jeden Fehler neu. Ein Besucher kann es zitieren, und Sie finden den Traceback, indem Sie das Protokoll danach durchsuchen. Weder die Ausnahme noch der Code erreichen den Besucher in der Produktion.

> [!CAUTION]
> Geben Sie den Traceback nicht an einen Besucher in der Produktion zurück und fügen Sie keine Geheimnisse in eine Fehlermeldung ein: Der `detail` eines `HTTPException` wird mit HTML-Escapezeichen an den Client gesendet. Tragen Sie das Geheimnis in das Protokoll ein, nicht in die Antwort.

## Aktionen und Formen

Eine Aktion ist ein `POST` Endpunkt mit einem generierten Pfad. Seine Fehler folgen den gleichen Regeln:

| Situation | Status | Kunde |
|---|---|---|
| Ein Feld fehlt oder ist ungültig | `422` | `ActionError` mit `fields` |
| `HTTPException(403)` in der Klage erhoben | `403` | `ActionError` mit `status` und `detail` |
| eine unbehandelte Ausnahme | `500` | `ActionError`; Die Referenz befindet sich im Serverprotokoll |
| Der `Origin`-Header ist eine andere Site | `403` | abgelehnt, bevor die Aktion ausgeführt wird |

Ein Formular ohne JavaScript Beiträge zum Aktionspfad; Bei Erfolg wird `303` auf die Seite zurückgeleitet, bei Fehler wird die Fehlerseite angezeigt. Siehe [Aktionen](../guides/actions.md#forms-without-javascript).

## Eine Checkliste, wenn eine Seite die falsche Antwort gibt

1. **Sehen Sie sich den Status** an, nicht die Seite. Ein Brauch `notfound.nexy` antwortet immer noch `404`.
2. **Lesen Sie das Terminal.** Eine Seite, deren Import fehlschlägt, ist nicht registriert, daher antwortet ihre URL `404`, solange die Datei vorhanden ist. Der Importfehler steht im Protokoll.
3. **Überprüfen Sie die Erweiterung.** Mit `useCSR = True` gehören `.nexy` Seiten zum Servermodus; Eine Seite im falschen Modus ist keine Route.
4. **Überprüfen Sie die Tiefe.** Ein `notfound.nexy` oder `errors.nexy` funktioniert nur, wenn die Root-Kopie vorhanden ist.
5. **Fragen Sie nach JSON** mit `Accept: application/json`, um die Form zu sehen, die Ihr API-Client erhält.
6. **Geben Sie die Referenz** eines `500` an, wenn Sie ein Problem öffnen oder das Protokoll durchsuchen.

## Nächste Schritte

- [Fehlerseiten](../routing/fbr/errors/README.md): das vollständige Seitenverhalten mit Beispielen
- [Validierung und Fehler](../routing/fbr/handlers/validation-and-errors.md): API-Handler
- [Fehlerbehebung](../guides/troubleshooting.md): Die Fehler, auf die die Leute tatsächlich stoßen
- [Testen](../guides/testing.md): Stellen Sie einen Status und einen Körper sicher
