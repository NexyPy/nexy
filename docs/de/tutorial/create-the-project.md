# Erstellen Sie eine Notizen-App mit Nexy, Teil 1: Erstellen Sie das Projekt

Teil 1 des Tutorials erstellt das Projekt, aus dem Sie eine Notizen-App erstellen möchten, und führt es in etwa fünf Minuten in Ihrem Browser aus.

**Bevor Sie beginnen:** [uv](https://docs.astral.sh/uv/) und Node.js 20 oder neuer. Das Tutorial folgt dem oben im Menü ausgewählten Router: Wechseln Sie dorthin und überall werden die Dateien dieses Routers angezeigt.

## Was Sie bauen werden

Am Ende des Tutorials verfügt die App über Seiten und eine JSON-API für Notizen, eine Datenbank, Konten, per E-Mail geteilte Notizen, Live-Updates, Tests und einen Produktions-Build. Jeder Teil endet mit einer App, die ausgeführt wird, sodass Sie nach jedem Teil anhalten können.

## Erstellen Sie das Projekt

```bash
uvx nexy new notes
```

Beantworten Sie die Fragen folgendermaßen:

| Frage | Antwort |
|---|---|
| Dateibasierter Router? | `Yes` für die dateibasierten und benutzerdefinierten Router, `No` für den modularen |
| Projekttyp | `Web` |
| Clientseitiges Routing | `No`: Der Server rendert die Seiten |
| Client-Framework | `React`: Es kommt in Einheit 4 zurück, für Inseln |
| Stil | `Tailwind CSS` |
| Alias importieren | `@` |
| ORM | `No database`: Teil 5 fügt einen hinzu |

<!-- router:custom -->
Der benutzerdefinierte Router ist der dateibasierte Router plus ein `APIRouter`, das Sie bereits haben. Das Tutorial erstellt die App mit Dateien; [Einen vorhandenen FastAPI Router einbeziehen](../routing/custom/README.md) zeigt, wie Sie Ihren Router daneben montieren.
<!-- /router -->

## Führen Sie es aus

```bash
cd notes
source .venv/bin/activate    # Windows: .venv\Scripts\activate
nexy dev
```

Öffnen Sie <http://localhost:3000>. Sie sollten die Willkommensseite sehen. Lassen Sie `nexy dev` laufen: Von nun an lädt jede Datei, die Sie speichern, den Browser neu.

## Was du gelernt hast

- `uvx nexy new` erstellt ein Projekt und installiert seine Pakete Python und JavaScript.
- `nexy dev` stellt es bereit und lädt beim Speichern neu.
<!-- router:fbr,custom -->
- Die Seiten leben in `src/routes/`: Der nächste Teil fügt eine hinzu.
<!-- /router -->
<!-- router:modular -->
- Die Controller und ihre Ansichten leben in `src/apps/`: Der nächste Teil fügt eine hinzu.
<!-- /router -->

## Nächste Schritte

- [Teil 2: Seiten und Layouts](pages-and-layouts.md)
- [Projektstruktur](../getting-started/project-structure.md): wozu jede Datei des Projekts dient
