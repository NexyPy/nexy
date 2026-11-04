# Dateibasiertes Routing

Eine Route ist eine Datei. Die URL ist der Dateipfad relativ zu `src/routes/`, abzüglich der Erweiterung.

## Datei zu URL

| Datei | URL |
|---|---|
| `index.nexy` | `/` |
| `about.nexy` | `/about` |
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/{slug}` |
| `docs/[...path].nexy` | `/docs/{path:path}` |
| `(marketing)/pricing.nexy` | `/pricing` |
| `api/users.py` | `/api/users` |

`index` wird seinem Verzeichnis zugeordnet, nicht `/index`. Ein Verzeichnis in Klammern ist eine **Gruppe**: it
organisiert Dateien, ohne dass sie in der URL erscheinen.

Im Client-Modus sind die Auslagerungsdateien `.tsx`, `.vue` oder `.svelte` anstelle von `.nexy`; Die URL-Regeln sind
das gleiche.

## Zwei Modi

`useCSR` entscheidet, was die Seiten sind. Beides lässt sich nicht in einem Projekt vermischen: Nexy weigert sich zu starten
wenn eine Serverseite neben einer Client-Route liegt.

| Modus | Seiten | Root-Layout | Siehe |
|---|---|---|---|
| Server (`useCSR = False`) | `.nexy`, `.md`, `.mdx` | `layout.nexy` | [Servermodus und Clientmodus](modes.md) |
| Client (`useCSR = True`) | Framework-Dateien | `layout.tsx` | [layout.tsx](../../views/react/differences.md) |

`.py`-Dateien sind in beiden Modi API-Handler.

## Was ist keine Route

- Reservierte Dateinamen: `layout.*`, `loading.nexy`, `errors.nexy`, `notfound.nexy`,
  `dependencies.py`, `middleware.py`, `__init__.py`.
- Dateien und Ordner, die mit `_` oder `.` beginnen: Verwenden Sie sie für Teilaufnahmen und Entwürfe.
- Erweiterungen, die für Ihr Projekt nicht aktiv sind. Eine Datei, deren Erweiterung inaktiv ist, wird mit übersprungen
  eine Warnung.

## Eine Datei pro URL

Zwei Dateien, die zur gleichen URL aufgelöst werden, werden beide registriert. Erstellen Sie nicht `blog.nexy` daneben
`blog/index.nexy` und mischen Sie nicht `index.nexy` und `index.py` für denselben Pfad. Wählen Sie eine aus.

## In diesem Abschnitt

| Ordner | Inhalt |
|---|---|
| [Seiten/](pages/README.md) | Seiten, [dynamische Routen](pages/dynamic-routes.md), Routengruppen |
| [layouts/](layouts/README.md) | eine Seite pro Layout-Dateityp |
| [handlers/](handlers/README.md) | `.py` Handler, Validierung und Fehler |
| [Abhängigkeiten/](dependencies/README.md) | `dependencies.py`, Wachen |
| [Middleware/](middleware/README.md) | `middleware.py` |
| [errors/](errors/README.md) | Nicht gefundene und Fehlerseiten |
| [Navigation/](navigation/linking-and-navigating.md) | Links, Hooks |
| [Echtzeit/](realtime/websocket.md) | WebSocket |
| [Vererbung](inheritance.md) | die Vererbungsregeln in einer Tabelle |

## Nächste Schritte

- [Servermodus und Clientmodus](modes.md)
- [Layouts](layouts/README.md)
- [Modulares Routing](../modular/README.md)