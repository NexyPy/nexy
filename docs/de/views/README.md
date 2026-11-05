# Ansichten

Bevor Sie ein Dateiformat auswählen, ist es wichtig zu unterscheiden, wie Nexy mit Ressourcen umgeht und wie es sie rendert.

| Begriff | Definition |
|---|---|
| **Seite** | Eine URL-adressierbare Ressource der Anwendung. Es wird durch eine Datei unter `src/routes/` definiert. |
| **View** | Der Prozess der Erstellung des Antworttexts für eine Seite. Eine Ansicht wandelt Logik und Daten in HTML oder JSON um. |
| **Component** | Ein wiederverwendbarer UI-Baustein, der zum Erstellen einer Ansicht verwendet wird. Komponenten können native Nexy-Helfer oder Framework-spezifisch sein (React, Vue usw.). |
| **Routenhandler** | Eine Python Funktion, die eine HTTP-Anfrage für eine bestimmte Methode verarbeitet (z. B. `GET`, `POST`). |
| **Endpunkt** | Die einzigartige Kombination aus einer URL und einer HTTP-Methode, die ein Route-Handler antwortet. |

**Nicht sicher? Schreiben Sie eine `.nexy`-Datei.** Es ist kein Client-Framework erforderlich, und Sie können später eine React-, Vue-, Svelte-, Solid- oder Preact-Komponente als Insel hinzufügen.

```diagram filename="Welche Datei für welche Seite"
server logic + HTML          →  .nexy      (Python frontmatter + Jinja2)
prose that changes rarely    →  .md        (GitHub-flavoured Markdown)
prose + components           →  .mdx       (React or Preact)
app-like page, client router →  .tsx .vue .svelte (framework files)
API handler                  →  .py        (GET, POST, …)
```

## Formate

| Format | Datei | Server-Rendering | Client-Framework | Notizen |
|---|---|---|---|---|
| `.nexy` | [.nexy-Dateien](nexy/README.md) | Jinja2 + Python Logik, gestreamt | optional | Natives Nexy-Seitenformat |
| `.md` | [Markdown und MDX](nexy/markdown.md) | cmarkgfm zum Zeitpunkt der Anfrage | optional über Layout | Rein Markdown, GFM, im Layout verpackt |
| `.mdx` | [Markdown und MDX](nexy/markdown.md) | Framework SSR | React oder Preact | Markdown mit Komponenten |
| `.tsx` | [React](react/differences.md), [Solid](solid/differences.md) oder [Preact](preact/differences.md) | Client-Modus: das Framework, gerendert in Knoten | React, Solid oder Preact | Komponentenrouten |
| `.vue` | [Vue](vue/differences.md) | Client-Modus: das Framework, gerendert in Knoten | Vue | SFC-Routen |
| `.svelte` | [Svelte](svelte/differences.md) | Client-Modus: das Framework, gerendert in Knoten | Svelte | SFC-Routen |

Eingebaute `Image`-, `Link`-, `Audio`-, `Video`- und `Import`-Helfer: [Components](nexy/components.md).

## Formate mischen

Sie können verschiedene Technologien innerhalb desselben Projekts kombinieren:
- **Inseln**: Sie können eine React- oder Vue-Komponente in eine `.nexy`-Seite importieren. Der Server rendert die Shell und das Framework hydriert die Komponente auf dem Client.
- **Gemeinsame Logik**: Routenhandler in `.py`-Dateien können Daten für Seiten in jedem Format über den gemeinsamen Anwendungsstatus oder API-Aufrufe bereitstellen.

## Aktivieren Sie ein Framework

Setzen Sie `useFF` in `nexyconfig.py` und führen Sie `nexy new` aus, um Abhängigkeiten hinzuzufügen:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

Wenn ein Framework aktiviert ist, verwaltet Vite seine Client-Bundles. Im Client-Modus werden seine Erweiterungen zu Routen; Im Servermodus sind die gleichen Dateien Komponenten, die Sie als Inseln importieren – eine Framework-Datei unter `src/routes/` wird dort abgelehnt. Siehe [Servermodus und Clientmodus](../routing/fbr/modes.md).

> [!NOTE]
> Im [CSR](../rendering/csr.md)-Modus sind nur Framework-Routendateien clientseitig navigierbar.

## Layouts

Ein `layout.*` in einem Verzeichnis umschließt Seiten darunter. Siehe [Layouts](../routing/fbr/layouts/README.md).

## Nächste Schritte

- [.nexy-Dateien](nexy/README.md): Python + Jinja2 + Requisiten
- [Markdown und MDX](nexy/markdown.md): Inhaltsseiten
- [Komponenten](nexy/components.md): integrierte HTML-Helfer
