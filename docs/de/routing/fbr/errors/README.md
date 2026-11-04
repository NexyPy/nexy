# Fehlerseiten

Eine fehlgeschlagene Anfrage sollte trotzdem wie der Rest Ihrer Website antworten: eine Seite in Ihren eigenen Worten für a
Besucher, der gleiche Fehler wie JSON für einen API-Client. Nexy beantwortet beides und jeweils eine Datei ersetzt sie
Antwort.

Diese Seite ist die Karte: Welche Datei antwortet auf welchen Status und wie Sie Ihren ersten erstellen. Die Seiten von
Ein Ordner erhält [seine eigene Seite](folder-pages.md).

## Ein Fehler, zwei Antworten

```diagram filename="Wer beantwortet eine fehlgeschlagene Anfrage?"
a request that fails
      │
      ├── a browser (Accept: text/html)              ──►  an HTML page
      └── an API client (Accept: application/json)   ──►  {"detail": "…"}  with the same status

the HTML page
      ├── the deepest folder of the URL that holds a file   ──►  your file
      └── no folder of the chain holds one                 ──►  the built-in page
```

## Ihre erste Seite

Erstellen Sie `src/routes/notfound.nexy` und schreiben Sie, was ein Besucher lesen soll:

```nexy filename="src/routes/notfound.nexy"
---
title: Page not found
---
<h1>Page not found</h1>
<p>The page moved or never existed. <a href="/">Back home</a>.</p>
```

Speichern Sie und fragen Sie nach einer URL, die nichts bringt:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/nowhere
# HTTP/1.1 404 Not Found
```

Die Datei im Routen-Stammverzeichnis beantwortet das gesamte Projekt; Eine Kopie in einem Ordner beantwortet nur diesen Ordner
und [lässt den Rest so wie er ist](folder-pages.md). Ohne Datei bietet Nexy seinen integrierten Stil
Seite.

## Welche Datei antwortet

| Datei | Antworten |
|---|---|
| `notfound.nexy` | `404` für sein Verzeichnis |
| `errors.nexy` | `500` für sein Verzeichnis |
| `forbidden.nexy` | `403` für sein Verzeichnis |
| `unauthorized.nexy` | `401` für sein Verzeichnis |
| `loading.nexy` | reserviert; Noch kein Laufzeiteffekt |

| Situation | Antwort |
|---|---|
| Keine Routenübereinstimmungen | `404` |
| Ein dynamisches Segment kann nicht in seine Annotation konvertiert werden | `404` |
| Eine nicht behandelte Ausnahme auf einer Seite oder einem API-Handler | `500` |
| `raise HTTPException(status_code=403)` | der von Ihnen angegebene Status, als HTML oder JSON |
| `notFound()`, `forbidden()`, `unauthorized()` | `404`, `403`, `401`, von überall in einer Anfrage |
| `redirect()`, `permanentRedirect()` | eine echte Weiterleitung ohne Fehlerseite |

## Hinterlassen Sie eine Seite oder antworten Sie über den Code

`redirect`, `permanentRedirect`, `notFound`, `forbidden` und `unauthorized` lösen eine HTTP-Ausnahme aus.
Derselbe Aufruf funktioniert also in einer `.nexy`-Seite, einem API-Handler, einem modularen Controller, einem Guard und einem
`dependencies.py`. Sie haben auf dem Client denselben Namen (`@nexy/client`).

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound, redirect

from src.posts import find

slug: prop[str]
post = find(slug)
if post is None:
    notFound()
if post.moved_to:
    redirect(post.moved_to)
---
<h1>{{ post.title }}</h1>
```

| Anrufen | Antworten |
|---|---|
| `redirect(url)` | `307`; `redirect(url, status=303)` verwandelt einen POST in ein GET nach einem Formular |
| `permanentRedirect(url)` | `308`; Browser und Suchmaschinen erinnern sich daran |
| `notFound(detail=None)` | `404`: die Seite `notfound` oder JSON für einen API-Client |
| `forbidden(detail=None)` | `403`: Der Besucher ist bekannt, sieht dies aber möglicherweise nicht |
| `unauthorized(detail=None, scheme=None)` | `401`; `scheme="Bearer"` fügt `WWW-Authenticate` | hinzu

Eine Weiterleitung antwortet mit dem Header `Location` und ohne Seite, auch an einen API-Client. Bauen Sie die
Ziel aus Werten, denen Sie vertrauen: Ein `redirect(request.query_params["next"])` sendet Besucher
wo immer der Link sagt. Ein Ziel mit Zeilenumbruch wird abgelehnt.

Ein Wächter schützt einen ganzen Ordner:

```python filename="src/routes/private/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

## HTML oder JSON

Die gleiche Ausnahme antwortet unterschiedlich, je nachdem, wer fragt:

- Ein Browser (`Accept: text/html`) erhält eine HTML-Seite. Das Detail ist HTML-escaped, sodass eine Nachricht erstellt wird
  aus Benutzereingaben kann kein Markup eingefügt werden.
- Ein Client, der nach JSON fragt und nicht nach einer Seite (`Accept: application/json`), erhält
  `{"detail": "..."}` mit demselben Statuscode.

```python filename="src/routes/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=403, detail="Out of range")
    return {"id": id}
```

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!NOTE]
> ein Client, der `Accept: */*` sendet (die Standardeinstellung von `curl` und viele HTTP
> Bibliotheken) empfängt die HTML-Seite. Legen Sie `Accept: application/json` für JSON-Fehler fest.

## Unbehandelte Ausnahmen

Eine Ausnahme, bei der nichts behandelt wird, wird einmal protokolliert, mit der Ausnahme, woher sie kam und wie
Code um ihn herum und antwortete entsprechend dem Modus.

| | `nx dev` | `nx start` |
|---|---|---|
| Durchsuchen Sie | eine Seite mit dem Fehler, den Zeilen Ihres Codes, die ihn ausgelöst haben, und dem vollständigen Traceback | die integrierte `500`-Seite (oder Ihre `errors.nexy`) mit einer Referenz |
| JSON-Client | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| Serverprotokoll | die Ausnahme und die Zeilen Ihres Codes | die Ausnahme und den gesamten Traceback, mit derselben Referenz |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

Die Referenz besteht aus acht Zeichen und ist für jeden Fehler neu. Ein Besucher kann es zitieren, und Sie finden es
Traceback, indem Sie das Protokoll danach durchsuchen. Weder die Ausnahme noch der Code erreichen den Besucher
Produktion. Ein benutzerdefiniertes `errors.nexy` ersetzt nur die Seite; Die Protokollzeile bleibt bestehen.

## Validierungsfehler

Ein fehlender Header, Abfrageparameter oder Body-Feld antwortet `422` mit dem JSON-Body von FastAPI, für jeden
Kunde. Siehe [Validierung und Fehler](../handlers/validation-and-errors.md).

## Nächste Schritte

- [Fehlerseiten pro Ordner](folder-pages.md): eine eigene 404, 403 oder 401 in einem Ordner
- [Dynamische Routen](../pages/dynamic-routes.md)
- [API-Routen](../handlers/README.md)
- [Testen](../../../guides/testing.md)