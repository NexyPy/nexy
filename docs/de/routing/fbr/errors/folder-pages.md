# Fehlerseiten pro Ordner

Ein Ordner kann seine eigenen Fehler beantworten: ein Blog mit einem 404 in seinen eigenen Worten, ein privater Bereich, der das Anmeldeformular anstelle eines bloßen `401` anbietet. Der Rest der Website behält die Seite, die sie bereits hatte.

Auf dieser Seite wird eine dieser Dateien hinzugefügt und die Antwort angezeigt.

## Die Regel

**Die tiefste Datei, die den URL-Antworten entspricht.** Alles andere bleibt wie es ist: die gleichen Statuscodes, JSON für einen API-Client und die integrierte Seite, sobald kein Ordner der Kette eine Datei enthält.

![Die Bereiche einer Fehlerseite](../../../assets/error-page-scopes.svg)

Für `/blog/2024/hello` geht Nexy den Baum hinauf: `/blog/2024`, dann `/blog`, dann `/`. Der erste Ordner mit einer Datei antwortet. Ein Ordner wird als Ganzes abgeglichen: `/blogger/hello` liegt nicht unter `/blog`, daher antwortet eine Kopie in `blog/` nie darauf.

## Die vier Akten

| Datei | Antworten | Was erreicht es |
|---|---|---|
| `notfound.nexy` | `404` | eine URL, zu der keine Route passt, `notFound()` |
| `errors.nexy` | `500` | eine Ausnahme, die nicht behandelt wurde |
| `forbidden.nexy` | `403` | `forbidden()`, `raise HTTPException(403)` |
| `unauthorized.nexy` | `401` | `unauthorized()`, `raise HTTPException(401)` |

`loading.nexy` bleibt reserviert: Es hat noch keinen Laufzeiteffekt.

Eine Datei irgendwo in `src/routes/` reicht für Nexy aus, um diesen Status zu beantworten: Eine Kopie im Stammverzeichnis antwortet auf das gesamte Projekt, eine Kopie in einem Ordner antwortet auf diesen Ordner und eine URL außerhalb jeder Kopie erhält die integrierte Seite. Reservieren Sie eine weitere Erweiterung für diese Namen in `nexyconfig.py` mit `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions` und `useUnauthorizedExtensions`.

## Ihre erste Ordnerseite

```nexy filename="src/routes/blog/notfound.nexy"
---
title: Nothing here yet
---
<h1>That post is gone</h1>
<p>The <a href="/blog">blog</a> still has the others.</p>
```

Führen Sie das Projekt aus und fordern Sie einen Beitrag an, der nicht existiert:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/blog/old
# HTTP/1.1 404 Not Found
```

Eine URL außerhalb des Ordners behält die Seite bei, die Sie bereits hatten:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/about
# HTTP/1.1 404 Not Found    (the root page, or the built-in one)
```

## Ein 401, der irgendwohin führt

Der Ordner eines geschützten Bereichs antwortet `401` mit der Seite, die den Weg hinein bietet:

```nexy filename="src/routes/private/unauthorized.nexy"
---
title: Sign in to continue
---
<h1>Sign in to see your notes</h1>
<a href="/sign-in" class="button">Sign in</a>
```

```python filename="src/routes/private/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

Jeder Anruf und jeder Status behält seine zwei Antworten:

| Wer fragt | `401` mit einer Datei | `401` ohne eine |
|---|---|---|
| Browser (`Accept: text/html`) | die Seite des Ordners | die integrierte Seite |
| Kunde (`Accept: application/json`) | `{"detail": "..."}` | `{"detail": "..."}` |

`unauthorized(scheme="Bearer")` fügt `WWW-Authenticate: Bearer` zu beiden Antworten hinzu. Ein aus Benutzereingaben erstelltes Detail wird auf der Seite mit HTML-Escapezeichen versehen.

> [!TIP]
> `Accept: */*`, die Standardeinstellung von `curl` und vielen HTTP-Bibliotheken, fragt nach keinem von beiden und empfängt die HTML-Seite. Fügen Sie `-H "Accept: application/json"` hinzu, wenn Sie die JSON-Antwort wünschen.

## Überprüfen Sie es

```python filename="tests/test_private.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_a_private_url_asks_for_sign_in():
    answer = TestClient(app).get("/private/notes")
    assert answer.status_code == 401
    assert "Sign in" in answer.text


def test_an_api_client_gets_json():
    answer = TestClient(app).get(
        "/private/notes", headers={"accept": "application/json"}
    )
    assert answer.json() == {"detail": "Unauthorized"}
```

## Nächste Schritte

- [Fehlerseiten](README.md): Was löst jeden Status aus, HTML oder JSON
- [Abhängigkeiten und Wächter](../dependencies/README.md): Schützt einen ganzen Ordner
- [Testen](../../../guides/testing.md): `TestClient` vom ersten Test
