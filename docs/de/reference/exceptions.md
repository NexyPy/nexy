# Ausnahmen und Fehler

Eine Anfrage kann an vier Stellen fehlschlagen, und Nexy antwortet jeweils anders. Diese Seite ist der Index:
Finden Sie den Status, den Sie sehen, dann die Zeile, die ihn erzeugt hat, und dann die Datei, die über den Text entscheidet.

> [!NOTE]
> Drei Dinge sind getrennt und können leicht verwechselt werden: die **HTTP-Antwort** (ein Status und ein Text), die
> **Fehlerseite** (`notfound.nexy`, `errors.nexy`) und die **Protokollzeile** (was Sie in der gelesen haben
> Terminal). Durch das Ändern der Seite wird der Status nicht geändert, und das Anpassen der Seite wird nicht ausgeblendet
> das Protokoll.

## Die Kurzversion

| Was ist passiert? | Status | Browser sieht | API-Client sieht |
|---|---|---|---|
| Keine Route entspricht der URL | `404` | `notfound.nexy`, sonst die integrierte Seite | `{"detail": "Not Found"}` |
| ein Pfadsegment passt nicht zu seiner Anmerkung | `404` | dieselbe Seite | `{"detail": "Not Found"}` |
| Ein Abfrage-, Header-, Cookie- oder Body-Feld fehlt oder ist ungültig | `422` | JSON-Body von FastAPI | JSON-Body von FastAPI |
| `notFound()` | `404` | die Seite | `{"detail": ...}` |
| `unauthorized()` | `401` | die integrierte Seite | `{"detail": ...}` |
| `forbidden()` | `403` | die integrierte Seite | `{"detail": ...}` |
| `raise HTTPException(409, ...)` | `409` | die integrierte Seite | `{"detail": ...}` |
| eine Ausnahme, nichts abgefangen | `500` | `errors.nexy`, sonst die eingebaute Seite | `{"detail", "reference"}` |
| `redirect(url)` | `307` | das Ziel, keine Seite | das Ziel, kein Text |
| `permanentRedirect(url)` | `308` | das Ziel, keine Seite | das Ziel |

Ein API-Client ist eine Anfrage, deren Header `Accept` nach JSON und nicht nach einer Seite fragt:

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!WARNING]
> `curl` sendet standardmäßig `Accept: */*`, wodurch die HTML-Seite abgerufen wird. Hinzufügen
> `-H "Accept: application/json"`, wenn Sie die JSON-Form testen. Browser rufen ständig Seiten auf.

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

| Phase | Was fehlschlagen kann | Die Antwort |
|---|---|---|
| Middleware | Ihre `middleware.py`, CORS, Sitzungen | der Status der Ausnahme, sonst `500` |
| Router | Die URL stimmt mit keiner Datei überein | `404` |
| Validierung | ein Pfadsegment kann nicht konvertiert werden | `404` |
| Validierung | ein Abfrage-, Header-, Cookie- oder Body-Feld | `422` |
| Seite, Handler, Aktion, Wache | `HTTPException` | sein Status |
| Seite, Handler, Aktion, Wache | alles andere | `500` |

## Von überall aus starten

`redirect`, `permanentRedirect`, `notFound`, `forbidden` und `unauthorized` lösen eine HTTP-Ausnahme aus.
Derselbe Aufruf funktioniert also auf einer `.nexy`-Seite, einem API-Handler, einem modularen Controller, einem Guard usw
`dependencies.py` und eine Aktion.

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

| Anrufen | Antworten | Wenn |
|---|---|---|
| `notFound(detail=None)` | `404` | Die Ressource existiert nicht |
| `unauthorized(detail=None, scheme=None)` | `401` | Der Besucher muss sich zuerst anmelden |
| `forbidden(detail=None)` | `403` | Der Besucher ist bekannt, sieht dies aber möglicherweise nicht |
| `redirect(url, status=307)` | `307` | schicken Sie sie woanders hin und behalten Sie dabei die Methode bei |
| `redirect(url, status=303)` | `303` | nach einem Formular: Die nächste Anfrage ist ein `GET` |
| `permanentRedirect(url)` | `308` | eine verschobene Seite, die sich Suchmaschinen merken sollten |

Bauen Sie das Ziel auf der Grundlage von Werten auf, denen Sie vertrauen. `redirect(request.query_params["next"])` schickt Besucher
wo immer der Link sagt; Es handelt sich um eine offene Weiterleitung. Ein Ziel, das einen Zeilenumbruch enthält, wird abgelehnt.

## Validierung: 422 oder 404

Handler-Parameter werden von FastAPI anhand ihrer Anmerkungen validiert.

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| Problem | Status | Warum |
|---|---|---|
| Abfrage, Header, Cookie oder Textfeld fehlen oder sind ungültig | `422` | Die Anfrage hat den Handler erreicht, die Daten sind falsch |
| ungültiges Pfadsegment (`/api/users/abc` für `id: int`) | `404` | Der Ordner hat keine Route für eine Nicht-Nummer, daher existiert die URL nicht |

Der `422`-Körper ist die Standardform von FastAPI, sodass Clients und generierte SDKs weiterhin funktionieren:

```json
{"detail": [{"loc": ["query", "q"], "msg": "Field required", "type": "missing"}]}
```

Für ein Formular oder eine Aktion erhält der Client ein `ActionError` mit `status` und `detail`; ein `422`
füllt auch `error.fields` mit einer Nachricht pro Feld. Siehe [Aktionen](../guides/actions.md#errors-and-failures).

> [!TIP]
> In der Signatur validieren, wenn die Regel ein Feld betrifft (`limit: int = 10`). Validieren Sie im
> Body, wenn die Regel die Datenbank oder ein anderes Feld benötigt („diese E-Mail wird bereits verwendet“): erhöhen
> `HTTPException(409)` und bewahren Sie die Nachricht für den Client auf.

## Benutzerdefinierte Fehlerseiten

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

Eine Datei irgendwo in den Routen installiert die Antwort für ihren Status: Eine Kopie im Stammverzeichnis antwortet darauf
Das gesamte Projekt, eine Kopie in einem Ordner, beantwortet diesen Ordner und die tiefste Datei, die mit der URL übereinstimmt
gewinnt. Eine URL außerhalb jeder Kopie und ein Status ohne Datei führen zu den integrierten gestalteten Seiten.
Siehe [Fehlerseiten pro Ordner](../routing/fbr/errors/folder-pages.md).

> [!IMPORTANT]
> Eine `errors.nexy`-Seite ersetzt die `500`-Seite; Es fängt die Ausnahme nicht ab und tut es auch nicht
> Ändern Sie die Protokollzeile. Wenn der ausgelöste Handler die Seite selbst ist, kann die Seite ihre eigene Seite nicht anzeigen
> Fehlerdetails: Halten Sie `errors.nexy` einfach und unabhängig.

## Unbehandelte Ausnahmen

Eine Ausnahme, bei der nichts abgefangen wurde, wird einmalig mit Referenz, Herkunft und Code protokolliert
drumherum. Der Status ist `500` und der Körper ist von der Umgebung abhängig.

| | `nexy dev` | `nexy build` dann `nexy start` |
|---|---|---|
| Browser | den Fehler, die Zeilen Ihres Codes und den Traceback | `errors.nexy`, sonst die eingebaute Seite, mit einer Referenz |
| API-Client | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| Terminal | die Ausnahme und die Zeilen Ihres Codes | die Ausnahme, der gesamte Traceback und die Referenz |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

Die Referenz besteht aus acht Zeichen und ist für jeden Fehler neu. Ein Besucher kann es zitieren, und Sie finden es
Traceback, indem Sie das Protokoll danach durchsuchen. Weder die Ausnahme noch der Code erreichen den Besucher
Produktion.

> [!ACHTUNG]
> Geben Sie den Traceback nicht an einen Besucher in der Produktion zurück und fügen Sie keine Geheimnisse in einen Fehler ein
> -Nachricht: Das `detail` eines `HTTPException` wird mit HTML-Escape an den Client gesendet. Geben Sie das Geheimnis ein
> das Protokoll, nicht in der Antwort.

## Aktionen und Formen

Eine Aktion ist ein `POST` Endpunkt mit einem generierten Pfad. Seine Fehler folgen den gleichen Regeln:

| Situation | Status | Kunde |
|---|---|---|
| ein Feld fehlt oder ist ungültig | `422` | `ActionError` mit `fields` |
| `HTTPException(403)` erhoben in der Klage | `403` | `ActionError` mit `status` und `detail` |
| eine nicht behandelte Ausnahme | `500` | `ActionError`; Die Referenz befindet sich im Serverprotokoll |
| Der `Origin`-Header ist eine andere Site. | `403` | wurde abgelehnt, bevor die Aktion ausgeführt wird. |

Ein Formular ohne JavaScript sendet Beiträge an den Aktionspfad. ein Erfolg antwortet `303` zurück zur Seite, a
„failure“ zeigt die Fehlerseite an. Siehe [Aktionen](../guides/actions.md#forms-without-javascript).

## Eine Checkliste, wenn eine Seite die falsche Antwort gibt

1. **Sehen Sie sich den Status an**, nicht die Seite. Ein Brauch `notfound.nexy` antwortet immer noch `404`.
2. **Lesen Sie das Terminal.** Eine Seite, die nicht importiert werden kann, ist nicht registriert, daher antwortet ihre URL `404`
   solange die Datei existiert. Der Importfehler steht im Protokoll.
3. **Überprüfen Sie die Erweiterung.** Mit `useCSR = True` gehören `.nexy` Seiten zum Servermodus; eine Seite in der
   Falscher Modus ist keine Route.
4. **Überprüfen Sie die Tiefe.** Ein `notfound.nexy` oder `errors.nexy` funktioniert nur, wenn die Root-Kopie vorhanden ist.
5. **Fragen Sie nach JSON** mit `Accept: application/json`, um die Form zu sehen, die Ihr API-Client erhält.
6. **Zitieren Sie die Referenz** eines `500`, wenn Sie ein Problem öffnen oder das Protokoll durchsuchen.

## Nächste Schritte

- [Fehlerseiten](../routing/fbr/errors/README.md): das Verhalten der gesamten Seite mit Beispielen
- [Validierung und Fehler](../routing/fbr/handlers/validation-and-errors.md): API-Handler
- [Fehlerbehebung](../guides/troubleshooting.md): Die Fehler, auf die die Leute tatsächlich stoßen
- [Testen](../guides/testing.md): Bestätigen Sie einen Status und einen Körper