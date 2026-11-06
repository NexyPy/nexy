# Dateibasiertes Routing

Eine Route ist eine Datei. Die URL ist der Dateipfad relativ zu `src/routes/`, abzüglich der Erweiterung.

## Datei zur URL

| Datei | URL |
|---|---|
| `index.nexy` | `/` |
| `about.nexy` | `/about` |
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/{slug}` |
| `docs/[...path].nexy` | `/docs/{path:path}` |
| `(marketing)/pricing.nexy` | `/pricing` |
| `api/users.py` | `/api/users` |

`index` wird seinem Verzeichnis zugeordnet, nicht `/index`. Ein Verzeichnis in Klammern ist eine **Gruppe**: Es organisiert Dateien, ohne in der URL zu erscheinen.

Im Client-Modus sind die Auslagerungsdateien `.tsx`, `.vue` oder `.svelte` anstelle von `.nexy`; Die URL-Regeln sind dieselben.

Zwei Dateien dieser Tabelle: eine Seite, die ihr Segment liest, und ein Handler, der JSON antwortet.

```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str]
---
<h1>{{ slug }}</h1>
```

```python filename="src/routes/api/users.py"
async def GET():
    return {"users": []}
```

## Zwei Modi

`useCSR` entscheidet, was die Seiten sind. Die beiden können nicht in einem Projekt gemischt werden: Nexy weigert sich zu starten, wenn eine Serverseite neben einer Client-Route liegt.

| Modus | Seiten | Root-Layout | Siehe |
|---|---|---|---|
| Server (`useCSR = False`) | `.nexy`, `.md`, `.mdx` | `layout.nexy` | [Servermodus und Clientmodus](modes.md) |
| Kunde (`useCSR = True`) | Framework-Dateien | `layout.tsx` | [layout.tsx](../../views/react/differences.md) |

`.py`-Dateien sind in beiden Modi API-Handler.

Der Schalter ist eine Zeile von `nexyconfig.py`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True  # client mode: src/routes/*.tsx are the pages
```

## Was ist keine Route?

- Reservierte Dateinamen: `layout.*`, `loading.nexy`, `errors.nexy`, `notfound.nexy`, `dependencies.py`, `middleware.py`, `__init__.py`.
- Dateien und Ordner, die mit `_` oder `.` beginnen: Verwenden Sie sie für Teilaufnahmen und Entwürfe.
- Erweiterungen, die für Ihr Projekt nicht aktiv sind. Eine Datei, deren Erweiterung inaktiv ist, wird mit einer Warnung übersprungen.

```text
src/routes/
├─ layout.nexy          wraps the pages, not a route
├─ middleware.py        wraps the requests, not a route
├─ index.nexy           /
├─ _card.nexy           a partial: no URL
└─ .draft.nexy          a draft: no URL
```

## Eine Datei pro URL

Zwei Dateien, die zur gleichen URL aufgelöst werden, werden beide registriert. Erstellen Sie nicht `blog.nexy` neben `blog/index.nexy` und mischen Sie nicht `index.nexy` und `index.py` für denselben Pfad. Wählen Sie eine aus.

```text
src/routes/
├─ blog.nexy            /blog
└─ blog/
   └─ index.nexy        /blog as well: delete one of the two
```

## In diesem Abschnitt

| Ordner | Was es abdeckt |
|---|---|
| [Seiten/](pages/README.md) | Seiten, [dynamische Routen](pages/dynamic-routes.md), Routengruppen |
| [Layouts/](layouts/README.md) | eine Seite pro Layoutdateityp |
| [Handler/](handlers/README.md) | `.py` Handler, Validierung und Fehler |
| [Abhängigkeiten/](dependencies/README.md) | `dependencies.py`, Wachen |
| [Middleware/](middleware/README.md) | `middleware.py` |
| [Fehler/](errors/README.md) | Nicht gefundene Seiten und Fehlerseiten |
| [Navigation/](navigation/linking-and-navigating.md) | Glieder, Haken |
| [Echtzeit/](realtime/websocket.md) | WebSocket |
| [Vererbung](inheritance.md) | die Vererbungsregeln in einer Tabelle |

## Nächste Schritte

- [Servermodus und Clientmodus](modes.md)
- [Layouts](layouts/README.md)
- [Modulares Routing](../modular/README.md)
