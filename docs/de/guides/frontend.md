# Frontend

Nexy liefert dem Kunden kein eigenes Komponentensystem. Es baut auf Vite auf: React, Vue, Svelte,
Solid und Preact werden alle unterstützt und Vanilla-Seiten funktionieren ganz ohne Client-Framework.

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

Eine Framework-Route ist eine normale Seite, keine reine Client-Insel: Der HTML-Code ist vorhanden, bevor das Bundle ausgeführt wird.
Der erste Paint wartet also nicht auf JavaScript.

Einrichtung pro Framework: [React](../views/react/differences.md), [Vue](../views/vue/differences.md),
[Schlank](../views/svelte/differences.md), [Fest](../views/solid/differences.md),
[Vorwirken](../views/preact/differences.md).

## Entwicklung

`nx dev` startet einen Server an einem Port:

1. Die App kompiliert die von Ihnen geänderten Routen, Server und Client, neu.
2. Vite läuft auf einem internen Port und stellt Framework-Module bereit;
3. Nexy stellt die Endpunkte von Vite über seinen eigenen Ursprung als Proxy bereit.

Der Browser kommuniziert immer nur mit Port `3000`. Es muss keine zweite URL geöffnet und kein CORS konfiguriert werden.

## Bauen

`nx build` erzeugt:

- vorgerendertes HTML für Framework-Routen;
- das Kundenpaket mit Vermögenswerten unter `__nexy__/client/`;
- die kompilierten Python-Routen.

Vite kümmert sich um das Client-Bundle. SSR-HTML wird von esbuild pro Datei erstellt.

> [!NOTE]
> Eine Route, deren Server-Rendering fehlschlägt, wird stattdessen als Nur-Client-Route gemeldet
> Der gesamte Build scheitert.

## Styling

`nexy new` fragt nach einem Stilmodus und richtet ihn für das von Ihnen ausgewählte Client-Framework ein: Tailwind,
UnoCSS oder einfaches CSS. Die Design-Tokens (Farben, Schriftarten, das dunkle Thema) sind CSS-Variablen in
`src/globale.css`, die Datei, die das Gerüst erstellt.

| Modus | Die Startseiten werden mit | geschrieben.
|---|---|
| Tailwind, UnoCSS | Dienstprogrammklassen im Markup, wobei die Token Klassennamen zugeordnet sind |
| Einfache CSS-| semantische Klassennamen und das CSS in `src/globale.css` |

Befolgen Sie den Modus Ihres Projekts, wenn Sie eine Seite hinzufügen: Dienstprogrammklassen in einem Dienstprogrammprojekt, CSS in einem
Plain-CSS eins. Behalten Sie Komponenten-CSS bei, das Dienstprogramme nicht im `<style>`-Block der Komponente ausdrücken können.
In einem Serverprojekt (`.nexy` Seiten) liest UnoCSS die `.nexy` Dateien für Klassen; Rückenwind findet sie
von alleine.

## Schriftarten, Bilder, Skripte

Legen Sie statische Dateien in `public/` ab – sie werden von `/` sowohl in der Entwicklung als auch in der Produktion bereitgestellt.

## Nächste Schritte

- [Ansichten](../views/README.md): Wählen Sie ein Seitenformat
- [Config](../reference/config.md): `useFF`, `useVite`, Aliase
- [Deploy](../deployment/README.md): was der Build erzeugt