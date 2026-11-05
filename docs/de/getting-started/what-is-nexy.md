# Was ist Nexy?

Nexy ist ein Python Framework für Fullstack-Webanwendungen: Ihre Seiten und Ihre API leben in einem Projekt und werden von einem Server bereitgestellt.

## Was Sie bekommen

- **Seiten in Python.** Eine `.nexy`-Datei ist HTML mit ein paar Zeilen Python oben; Eine `.md`-Datei ist auch eine Seite. Zum Rendern einer Seite ist kein JavaScript erforderlich.
- **Eine API im selben Projekt.** Eine `.py`-Datei unter `src/routes/` beantwortet HTTP-Anfragen: Eine Funktion namens `GET` antwortet `GET`, eine Funktion namens `POST` antwortet `POST`.
- **Kostenlose API-Dokumentation.** Jede API-Route erscheint in einem OpenAPI-Schema und Scalar zeigt sie als interaktive Referenz unter `/docs`.
- **Formulare, die Python.** aufrufen. Ein Formular oder ein eingegebener Aufruf vom Browser erreicht dieselbe Python-Funktion.
- **Ein Frontend-Framework, wenn Sie eines wünschen.** React, Vue, Svelte, Solid oder Preact, für eine Komponente oder für die gesamte Site.
- **Ein Befehl zum Arbeiten, einer zum Versenden.** `nx dev` wird beim Speichern neu geladen; `nx build` bereitet die Produktion vor.

## Worauf es aufgebaut ist

Die aktuelle Version 2.2 basiert auf Tools, die Sie vielleicht bereits kennen:

| Teil | Aufgebaut | Was es für Sie bedeutet |
|---|---|---|
| Server und API | [FastAPI](https://fastapi.tiangolo.com/) | Eine API-Route ist eine FastAPI-Route: Pydantic-Validierung und Abhängigkeiten funktionieren wie gewohnt |
| API-Referenz | OpenAPI und [Skalar](https://scalar.com/) | das Schema ist bei `/openapi.json`, die Referenz bei `/docs` |
| Seiten | Jinja2 | Eine `.nexy`-Seite verwendet Jinja2-Tags wie `{{ title }}` |
| Frontend (optional) | [Vite](https://vite.dev/) | nur mit einem Frontend-Framework, das auch Node.js benötigt |

## Eine erste Seite und ein erster Endpunkt

Eine Seite, unter `/hello`:

```nexy filename="src/routes/hello.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

Ein Endpunkt unter `GET /api/items`, aufgeführt unter `/docs` ohne zusätzlichen Code:

```python filename="src/routes/api/items.py"
from nexy.http import Request


async def GET(request: Request):
    return {"items": []}
```

## Was Nexy Ihnen überlässt

Zu Ihrer Anwendung gehören die Datenbank, das Login und die Regeln, wer was tun darf, also wählen Sie die Bibliotheken aus. [Datenbanken](../guides/databases.md) und [Middleware und Sicherheit](../guides/middleware-and-security.md) zeigen, wo sie jeweils eingebunden sind.

## Nächste Schritte

- [Installation](installation.md): Installieren Sie uv und erstellen Sie ein Projekt
- [Schnellstart](quick-start.md): ausführen, eine Seite ändern, erstellen
- [Kernkonzepte](core-concepts.md): die wenigen Wörter, die im Rest der Dokumente verwendet werden
