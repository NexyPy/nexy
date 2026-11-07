# Erstellen Sie eine Notizen-App mit Nexy, Teil 4: Komponenten

Teil 4 verwandelt jede Notiz in eine wiederverwendbare Komponente, eine `.nexy`-Datei, die Sie wie einen Python-Namen importieren und wie ein HTML-Tag verwenden.

**Bevor Sie beginnen:** die App von [Teil 3](dynamic-routes.md).

## Schreiben Sie die Komponente

Eine Komponente ist eine `.nexy`-Datei außerhalb der Routen. Seine Requisiten werden mit `prop[...]` deklariert und der Aufrufer übergibt sie als Attribute:

```nexy filename="src/components/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
---
<article class="note">
  <a href="/notes/{{ id }}">{{ text }}</a>
</article>

<style>
  .note { padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
</style>
```

Der `<style>`-Block wird mit jeder Seite gesendet, die die Karte verwendet. Es hat keinen Gültigkeitsbereich: `.note` ist eine Klasse für die gesamte Seite, also geben Sie den Klassen einer Komponente Namen, die nur von ihr verwendet werden.

## Verwenden Sie es in der Liste

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

`@/` ist der Importalias von Teil 1: Er zeigt auf `src/`. Der Dateiname ist der Komponentenname, in PascalCase: `NoteCard.nexy` exportiert `NoteCard`.

Öffnen Sie <http://localhost:3000/notes>: Jede Notiz ist jetzt eine Karte.

## Was du gelernt hast

- Eine `.nexy`-Datei außerhalb der Routen ist eine Komponente; seine `prop[...]` sind seine Attribute.
- `from "@/components/x.nexy" import X` importiert es; `<X />` rendert es.
- Ein `<style>`-Block hat keinen Gültigkeitsbereich: Benennen Sie die Klassen einer Komponente danach.

## Nächste Schritte

- [Teil 5: Speichern Sie die Notizen in SQLite](store-the-notes.md)
- [Komponenten](../views/nexy/components.md): `Image`, `Link` und die integrierten Helfer
