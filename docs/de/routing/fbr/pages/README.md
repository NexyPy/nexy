# Seiten

Eine Auslagerungsdatei gibt HTML zurück. Welchen Dateityp Sie verwenden, ändert die Art und Weise, wie er erstellt wird: siehe [Ansichten](../../../views/README.md). In diesem Abschnitt werden die Routing-Regeln behandelt, die für jedes Seitenformat gelten.

| Seite | Was es abdeckt |
|---|---|
| [Dynamische Routen](dynamic-routes.md) | `[slug]`, `[...path]`, Routengruppen, typisierte Segmente |
| [Fehlerseiten](../errors/README.md) | `notfound.nexy`, `errors.nexy`, JSON für API-Clients |
| [Layouts](../layouts/README.md) | Eine Seite pro Layout-Dateityp |
| [Vererbung](../inheritance.md) | Wie Layouts und Abhängigkeiten gestapelt werden |

## Eine minimale Seite

```nexy filename="src/routes/about.nexy"
---
title: prop[str] = "About"
---
<h1>{{ title }}</h1>
```

Es wird um `/about` serviert. Der Titeltext zwischen den `---`-Zeilen ist Python; das Markup darunter ist Jinja2. Siehe [.nexy-Dateien](../../../views/nexy/README.md).

## Seitenformate

| Modus | Datei | Erzeugt |
|---|---|---|
| Server | `.nexy` | Vom Server gerendertes HTML von Python und Jinja2 |
| Server | `.md`, `.mdx` | Inhaltsseiten |
| Client | `.tsx`, `.jsx`, `.vue`, `.svelte` | Framework-Komponenten, gerendert und navigiert im Browser |

Die beiden Modi können nicht in einem Projekt gemischt werden. Siehe [Servermodus und Clientmodus](../modes.md). Clientkomponenten können weiterhin im Servermodus als [Inseln](../../../rendering/islands.md) innerhalb einer `.nexy`-Seite angezeigt werden.

## Inkrementelles Caching

Fügen Sie `revalidate = 60` zu einer `.nexy`-Seite hinzu, um sie mit stale-while-revalidate zwischenzuspeichern. Siehe [ISR](../../../rendering/isr.md).

## Lesen der Anfrage

Eine Seite liest den Pfad, die Abfragezeichenfolge, Cookies und die Sitzung über Hooks. Siehe [Hooks](../navigation/hooks.md).

## Nächste Schritte

- [Dynamische Routen](dynamic-routes.md)
- [Fehlerseiten](../errors/README.md)
- [Modulares Routing](../../modular/README.md): Controller statt Dateien
