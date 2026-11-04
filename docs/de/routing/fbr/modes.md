# Servermodus und Clientmodus

Ein Nexy-Projekt wird entweder **vom Server gerendert** oder **vom Client weitergeleitet**, wie es auch bei einem Next.js-Projekt der Fall ist
Seiten, die auf dem Server oder einer Client-App gerendert werden. `useCSR` in `nexyconfig.py` wählt.

## Servermodus (`useCSR = False`)

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

- Seiten sind `.nexy`-, `.md`- oder `.mdx`-Dateien unter `src/routes/`.
- Die Wurzel `layout.nexy` besitzt `<!DOCTYPE html>`, `<html>`, `<head>` und `<body>`.
- Client-Komponenten (React, Vue, Svelte, Solid oder Preact) sind als **Inseln** zulässig: Sie importieren eine
  von einer `.nexy`-Seite und es wird im Browser angezeigt. Siehe [Inseln](../../rendering/islands.md).
- Eine Client-Komponente ist niemals eine Route. Bewahren Sie sie in `src/components/` auf.
- Ein Client-Framework nach dem anderen.

```text
src/
├─ routes/
│  ├─ layout.nexy         document
│  ├─ index.nexy          page
│  └─ api/users.py        API handler
└─ components/Counter.tsx island
```

## Client-Modus (`useCSR = True`)

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

- Seiten sind die Dateien Ihres Client-Frameworks: `.tsx` für React, `.vue`, `.svelte`.
- `.md`- und `.mdx`-Dateien bleiben gültige Routen: Nexy rendert sie auf dem Server im Client
  Layout, und der Client-Router übernimmt von dort aus die Navigation.
- Das Stammlayout jedes Frameworks (`layout.tsx`, `layout.vue`, `layout.svelte`) besitzt `<!DOCTYPE html>`, `<html>`, `<head>` und `<body>`, wie das
  Root-Layout des Next.js App Routers. Nexy rendert es in Node für die erste Antwort und die
  Das Framework hydratisiert das gesamte Dokument. Siehe [layout.tsx](../../views/react/differences.md).
- `.py`-Dateien sind API-Handler, die von FastAPI neben den Client-Routen bereitgestellt werden.
- Es gibt überhaupt keine `.nexy`-Datei und keine `layout.nexy`.
- Die Navigation zwischen den Seiten erfolgt im Browser.

```text
src/routes/
├─ layout.tsx             document
├─ index.tsx              page
├─ users.tsx              page
└─ api/users.py           API handler
```

## Was abgelehnt wird

Nexy prüft das Projekt vor `nx dev`, `nx start` und `nx build` und stoppt mit der Liste der Dateien:

| Modus | Abgelehnt | Nachricht |
|---|---|---|
| Server | `.tsx`, `.jsx`, `.vue` oder `.svelte` unter `src/routes/` | Komponenten nach `src/components/` verschieben oder `useCSR = True` festlegen |
| Client | jede `.nexy` Datei unter `src/routes/` | schreibe sie als Framework-Komponenten oder setze `useCSR = False` |
| beide | mehr als ein Frontend-Framework in `useFF` | `useFF must configure exactly one frontend framework` |
| Client | `useRouter` (modularer Router) | `useCSR requires file-based routing` |
| Kunde | nein `useFF` | `useCSR requires a client framework` |

Dateien und Ordner, die mit `_` oder `.` beginnen, werden bei dieser Prüfung ignoriert.

## Welches

- **Inhalt, Marketing, Dokumente, SEO-First-Sites**: Servermodus mit Inseln.
- **Dashboards und Apps mit Rich-Client-Navigation**: Client-Modus.
- **Eine Python-API mit einer Client-App oben**: Client-Modus, mit `.py` Handlern neben den Seiten.

## Nächste Schritte

- [Layouts](layouts/README.md)
- [Rendering](../../rendering/README.md)
- [Config](../../reference/config.md)