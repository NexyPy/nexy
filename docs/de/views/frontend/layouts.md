# Frontend-Layouts

Ein **Layout** ist ein Wrapper, der die gemeinsame Struktur um eine oder mehrere Seiten definiert. Layouts ermöglichen ein „App-ähnliches“ Erlebnis, indem sie den Status beibehalten und das Neuladen ganzer Seiten während der Navigation vermeiden.

## Verschachtelungslogik

Layouts folgen einer hierarchischen Struktur, die auf dem Verzeichnisbaum unter `src/routes/` basiert.

1.  **Root-Layout**: Jedes Projekt hat ein Root-Layout (z. B. `src/routes/layout.nexy`). Dies ist das einzige Layout, das für die Definition der Dokumenthülle verantwortlich ist: `<html>`, `<head>` und `<body>`.
2.  **Verschachtelte Layouts**: Jeder Ordner kann seine eigene `layout.*` Datei enthalten. Dieses Layout umschließt alle Seiten und Unterlayouts in diesem Ordner.
3.  **Vererbung**: Eine Seite wird von allen Layouts vom Stammverzeichnis bis hinunter zu ihrem eigenen Ordner umschlossen.

## Gemeinsamer Zustand und Zusammensetzung

Layouts sind auf Stabilität ausgelegt. Beim Navigieren zwischen zwei Seiten mit demselben Layout wird das Layout **nicht** neu gerendert; Nur der untergeordnete Inhalt ändert sich.

- **Slots**: Layouts bieten einen „Slot“ (normalerweise `children` in JSX oder `{{ content }}` in Jinja2), in den die verschachtelte Seite eingefügt wird.
- **Zustandserhaltung**: Da das Layout gemountet bleibt, bleibt jeder darin enthaltene Status (z. B. eine Suchabfrage in einer Kopfzeile) während der Navigation erhalten.

## Statische Einschränkungen

Bei Routen, die vorab gerendert werden (SSG), kann das Root-Layout nicht von Daten zur Anforderungszeit wie Cookies oder Headern abhängen. Es muss als statische Hülle darstellbar sein, die der Kunde dann hydratisiert.

## Framework-Implementierung

Die Implementierung von Slots und Verschachtelungen variiert geringfügig je nach Framework. Sehen Sie sich den Leitfaden **Unterschiede** für die von Ihnen gewählte Technologie an:

- [Auf Unterschiede reagieren](../react/differences.md)
- [Vue-Unterschiede](../vue/differences.md)
- [Kleine Unterschiede](../svelte/differences.md)
- [Feste Unterschiede](../solid/differences.md)
- [Vorgegebene Unterschiede](../preact/differences.md)