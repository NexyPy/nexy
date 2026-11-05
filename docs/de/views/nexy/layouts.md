# layout.nexy

Die Layoutdatei des Servermodus (`useCSR = False`). Der Root besitzt das HTML-Dokument.

## Root-Layout

```nexy filename="src/routes/layout.nexy"
---
from nexy import Vite

children: prop[NexyElement]
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My app</title>
  <Vite />
</head>
<body>
  <main>{{ children | safe }}</main>
</body>
</html>
```

- `<!DOCTYPE html>`, `<html>`, `<head>` und `<body>` leben hier und nirgendwo anders.
- `<Vite />` fügt die Client-Skripte und -Stile einmal in `<head>` ein.
- `{{ children | safe }}` ist der Ort, an dem die Seite oder das nächste verschachtelte Layout gerendert wird.

## Verschachtelte Layouts

Ein `layout.nexy` in einem Unterverzeichnis umschließt diesen Unterbaum und rendert ihn in seinem übergeordneten Verzeichnis. Die Dokument-Tags werden nicht wiederholt:

```nexy filename="src/routes/blog/layout.nexy"
---
children: prop[NexyElement]
---
<nav>...</nav>
<article>{{ children | safe }}</article>
```

`blog/[slug].nexy` wird als `layout.nexy > blog/layout.nexy > page` gerendert.

## Komponenten und Inseln

Ein Layout kann `.nexy` Komponenten (eine Kopfzeile, eine Fußzeile) und Client-Komponenten importieren. Eine Client-Komponente in einem Layout ist eine [Insel](../../rendering/islands.md) wie jede andere:

```nexy
---
from "@/components/Header.nexy" import Header
from "@/components/theme/theme.tsx" import Theme
---
<Header />
<Theme directive="client:idle" />
```

## Ohne Layout

Ein Projekt ohne `layout.nexy` antwortet immer noch mit einem gültigen Dokument: Nexy greift auf eine minimale Shell mit `<!DOCTYPE html>`, dem Viewport-Meta und den Vite-Tags zurück. Fügen Sie ein Layout hinzu, sobald Sie einen Titel, Schriftarten oder eine Navigation benötigen.

## Im modularen Router

Controller wählen ihre Ansichten aus und erstellen das Layout selbst:

```python
return useViews("src/apps/layout.nexy", context={"children": useViews("src/apps/app_view.nexy")})
```

## Was es nicht kann

- Es kann nicht mit `layout.tsx`, `layout.vue` oder `layout.svelte` koexistieren: Ein Projekt im Servermodus hat keine Client-Routen ([Modi](../../routing/fbr/modes.md)).
- Es läuft nicht auf dem Client: Verwenden Sie eine Insel für Interaktivität.

## Nächste Schritte

- [Layouts](../../routing/fbr/layouts/README.md)
- [Vererbung](../../routing/fbr/inheritance.md)
- [.nexy-Dateien](README.md)
