# Erstellen Sie eine Notizen-App mit Nexy, Teil 3: dynamische Routen und eine API

Teil 3 gibt jeder Notiz eine eigene URL, `/notes/1`, und stellt dieselben Notizen als JSON unter `/api/notes` bereit, die beide aus einem Python-Modul gelesen werden.

**Bevor Sie beginnen:** die App von [Teil 2](pages-and-layouts.md).

## Bewahren Sie die Notizen in einem Modul auf

Die Seite und die API lesen dieselbe Liste. Verschieben Sie es in ein eigenes Modul mit einer Funktion, die eine Notiz findet:

```python filename="src/notes.py"
NOTES = {1: "Buy milk", 2: "Ship Nexy"}


def find(note_id: int) -> str | None:
    return NOTES.get(note_id)
```

## Verknüpfen Sie jede Notiz mit ihrer Seite

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for id, text in notes %}
    <li><a href="/notes/{{ id }}">{{ text }}</a></li>
    {% endfor %}
  </ul>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for id, text in notes %}
    <li><a href="/notes/{{ id }}">{{ text }}</a></li>
    {% endfor %}
  </ul>
</section>
```
<!-- /router -->

## Fügen Sie eine Seite pro Notiz hinzu

<!-- router:fbr,custom -->
Ein Ordner- oder Dateiname in Klammern ist ein Segment der URL: `[id].nexy` antwortet auf `/notes/1`, `/notes/2` und übergibt das Segment als Requisite an die Seite. `id: prop[int]` wandelt es in eine Zahl um, sodass `/notes/abc` `404` antwortet, bevor die Seite ausgeführt wird.

```nexy filename="src/routes/notes/[id].nexy"
---
from nexy import notFound
from src.notes import find

id: prop[int]
text = find(id)
if text is None:
    notFound()
---
<section class="app-page">
  <h1>{{ text }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

<!-- router:modular -->
Ein `{id}` im Pfad eines Controllers ist ein Segment der URL, das unter diesem Namen an die Methode übergeben wird. `id: int` wandelt es in eine Zahl um, sodass `/notes/abc` `404` antwortet, bevor die Methode ausgeführt wird.

```nexy filename="src/apps/notes/note_view.nexy"
---
text: prop[str]
---
<section class="app-page">
  <h1>{{ text }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

`notFound()` stoppt die Anfrage mit einem `404`: Eine Notiz, die nicht existiert, antwortet wie eine URL, die nicht existiert.

## Stellen Sie die Notizen als JSON bereit

<!-- router:fbr,custom -->
Eine `.py`-Datei unter `src/routes/` ist eine API-Route. Jede nach einer HTTP-Methode benannte Funktion antwortet auf diese Methode:

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": id, "text": text} for id, text in NOTES.items()]
```
<!-- /router -->

<!-- router:modular -->
Die drei Controller der Notizen in einer Datei. Jede nach einer HTTP-Methode benannte Methode antwortet dieser Methode:

```python filename="src/apps/notes/notes_controller.py"
from nexy import notFound
from nexy.decorators import Controller
from nexy.hooks import useViews
from src.notes import NOTES, find

LAYOUT = "src/apps/layout.nexy"


def page(view: str, **context: object):
    return useViews(LAYOUT, context={"children": useViews(view, context=context)})


@Controller("/notes")
class NotesController:
    async def get(self):
        return page("src/apps/notes/notes_view.nexy")


@Controller("/notes/{id}")
class NoteController:
    async def get(self, id: int):
        text = find(id)
        if text is None:
            notFound()
        return page("src/apps/notes/note_view.nexy", text=text)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        return [{"id": id, "text": text} for id, text in NOTES.items()]
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NoteController, NotesApiController, NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController, NoteController, NotesApiController]
```
<!-- /router -->

Überprüfen Sie die drei URLs:

- <http://localhost:3000/notes/1> zeigt *Milch kaufen*;
- <http://localhost:3000/notes/9> Antworten *Seite nicht gefunden*;
- `curl http://localhost:3000/api/notes` druckt `[{"id":1,"text":"Buy milk"},{"id":2,"text":"Ship Nexy"}]`.

Die API ist mit ihrem Schema unter <http://localhost:3000/docs> aufgeführt.

## Was du gelernt hast

<!-- router:fbr,custom -->
- `[id].nexy` ist ein dynamisches Segment; `id: prop[int]` liest und konvertiert es.
- Eine `.py`-Datei unter `src/routes/` antwortet JSON, eine Funktion pro HTTP-Methode.
<!-- /router -->
<!-- router:modular -->
- `{id}` Im Pfad eines Controllers befindet sich ein dynamisches Segment. `id: int` konvertiert es.
- Eine Controller-Methode, die Daten zurückgibt, antwortet JSON; eine, die `useViews` zurückgibt, beantwortet eine Seite.
<!-- /router -->
- `notFound()` antwortet `404` von überall; Ein gemeinsam genutztes Modul hält Seiten und API im Gleichschritt.

## Nächste Schritte

- [Teil 4: Komponenten](components.md)
- [Ausnahmen und Fehler](../reference/exceptions.md): `notFound`, `redirect` und die anderen Exits
