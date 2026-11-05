# Frontend

Nexy liefert dem Kunden kein eigenes Komponentensystem. Es baut auf Vite auf: React, Vue, Svelte, Solid und Preact werden alle unterstützt, und Vanilla-Seiten funktionieren überhaupt ohne Client-Framework.

## Aktivieren Sie ein Framework

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()   # vue(), svelte(), solid(), preact()
```

`useVite` ist standardmäßig `True`; Lassen Sie es eingeschaltet, wenn ein Framework konfiguriert ist.

## Dateien weiterleiten

| Erweiterung | Gerendert |
|---|---|
| `.nexy`, `.md` | von Nexy zum Zeitpunkt der Anfrage |
| `.mdx`, `.tsx`, `.jsx`, `.vue`, `.svelte` | durch das Client-Framework; wird zur Erstellungszeit vorab in HTML gerendert und dann vom Client-Bundle übernommen |

Eine Framework-Route ist eine normale Seite, keine reine Client-Insel: Der HTML-Code ist vorhanden, bevor das Bundle ausgeführt wird, sodass der erste Paint nicht auf JavaScript wartet.

Einrichtung pro Framework: [React](../views/react/differences.md), [Vue](../views/vue/differences.md), [Svelte](../views/svelte/differences.md), [Solid](../views/solid/differences.md), [Preact](../views/preact/differences.md).

## Entwicklung

`nx dev` startet einen Server an einem Port:

1. Die App kompiliert die von Ihnen geänderten Routen, Server und Client, neu.
2. Vite läuft auf einem internen Port und bedient Framework-Module;
3. Nexy vertritt die Endpunkte von Vite über seinen eigenen Ursprung.

Der Browser kommuniziert immer nur mit Port `3000`. Es muss keine zweite URL geöffnet und kein CORS konfiguriert werden.

## Bauen

`nx build` erzeugt:

- Vorgerendertes HTML für Framework-Routen;
- das Kundenpaket mit Vermögenswerten unter `__nexy__/client/`;
- die zusammengestellten Python Routen.

Vite verwaltet das Client-Bundle; SSR-HTML wird von esbuild pro Datei erstellt.

> [!NOTE]
> Eine Route, deren Server-Rendering fehlschlägt, wird als Nur-Client-Route gemeldet, anstatt dass der gesamte Build fehlschlägt.

## Styling

`nexy new` fragt nach einem Stilmodus und richtet ihn für das von Ihnen ausgewählte Client-Framework ein: Tailwind, UnoCSS oder einfaches CSS. Die Design-Tokens (Farben, Schriftarten, das dunkle Thema) sind CSS-Variablen in `src/globale.css`, der Datei, die das Gerüst erstellt.

| Modus | Die Startseiten werden mit geschrieben |
|---|---|
| Tailwind, UnoCSS | Dienstprogrammklassen im Markup, wobei die Token den Klassennamen zugeordnet sind |
| Einfaches CSS | semantische Klassennamen und das CSS in `src/globale.css` |

Befolgen Sie den Modus Ihres Projekts, wenn Sie eine Seite hinzufügen: Dienstprogrammklassen in einem Dienstprogrammprojekt, CSS in einem einfachen CSS-Projekt. Behalten Sie Komponenten-CSS bei, das Dienstprogramme nicht im `<style>`-Block der Komponente ausdrücken können. In einem Serverprojekt (`.nexy` Seiten) liest UnoCSS die `.nexy` Dateien für Klassen; Tailwind findet sie selbstständig.

## Schriftarten, Bilder, Skripte

Legen Sie statische Dateien in `public/` ab – sie werden von `/` sowohl in der Entwicklung als auch in der Produktion bereitgestellt.

## Nächste Schritte

- [Ansichten](../views/README.md): Wählen Sie ein Seitenformat
- [Konfiguration](../reference/config.md): `useFF`, `useVite`, Aliase
- [Deployment](../deployment/README.md): was der Build erzeugt
