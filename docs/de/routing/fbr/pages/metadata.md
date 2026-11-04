# Seitenmetadaten

Eine Seite benennt ihren Titel und ihre Head-Tags, und das Root-Layout schreibt sie einmal.

## Sagen Sie es auf der Seite

Für eine Seite, die sich nie ändert, schreiben Sie oben in die Titelzeile ein Literal:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

Wenn der Titel von den Daten abhängt, rufen Sie stattdessen `setMetadata` auf:

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound, setMetadata

from src.posts import find

slug: prop[str]
post = find(slug) or notFound()
setMetadata(title=post.title, description=post.summary, og={"image": post.cover})
---
<h1>{{ post.title }}</h1>
```

Ein modularer Controller ruft `setMetadata(...)` auf, bevor er `useViews(...)` zurückgibt.

## Schreiben Sie es in das Layout

Das Root-Layout besitzt das `<head>`. Eine Zeile schreibt, was die Seite gesagt hat, mit Escapezeichen:

```nexy filename="src/routes/layout.nexy"
---
from nexy import setMetadata, useMetadata

children: prop[NexyElement]
setMetadata(title_template="%s | My site")
---
<!DOCTYPE html>
<html>
  <head>
    {{ useMetadata().html() }}
  </head>
  <body>{{ children }}</body>
</html>
```

Eine Seite wird vor ihren Layouts ausgeführt, sodass das Layout findet, wonach die Seite gefragt hat. Eine Seite, die sagt
Nichts erhält das `useTitle` Ihres `nexyconfig.py` und kein anderes Tag.

## Die Felder

| Feld | Geschrieben als |
|---|---|
| `title` | `<title>`; mit `title_template="%s \| My site"` wird der Titel in das `%s` | gesetzt
| `description` | `<meta name="description">` |
| `canonical` | `<link rel="canonical">` |
| `robots` | `<meta name="robots">`, zum Beispiel `"noindex"` |
| `icon` | `<link rel="icon">` |
| `og` | ein `<meta property="og:...">` pro Schlüssel: `{"image": "/cover.png"}` ergibt `og:image` |
| `twitter` | ein `<meta name="twitter:...">` pro Schlüssel |
| `extra` | eine Liste von Attributdiktaten, jeweils eins `<meta>`: `[{"name": "theme-color", "content": "#fff"}]` |

Ein späterer Aufruf ersetzt einen Wert; `og`, `twitter` und `extra` ergänzen das, was da ist. Ein Feld, das das tut
not exist löst `TypeError` aus, sodass ein Tippfehler nicht stillschweigend nichts bewirkt.

## Standardmäßig sicher

Jeder Wert ist mit HTML-Escapezeichen versehen, sodass ein aus einer URL oder aus der Datenbank erstellter Titel das Tag nicht schließen kann
und ein Skript einfügen. Ein Wert wird einmal maskiert, wenn das Layout `html()` aufruft: maskieren Sie ihn nicht
sich selbst.

## Nächste Schritte

- [Seiten](README.md)
- [Layouts](../layouts/README.md)
- [Fehlerseiten](../errors/README.md)