# Build a notes app with Nexy, part 3: dynamic routes and an API

Part 3 gives each note its own URL, `/notes/1`, and serves the same notes as JSON at `/api/notes`,
both read from one Python module.

**Before you start:** the app of [part 2](pages-and-layouts.md).

## Keep the notes in one module

The page and the API will read the same list. Move it to a module of its own, with a function that
finds one note:

```python filename="src/notes.py"
NOTES = {1: "Buy milk", 2: "Ship Nexy"}


def find(note_id: int) -> str | None:
    return NOTES.get(note_id)
```

## Link each note to its page

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

## Add a page per note

<!-- router:fbr,custom -->
A folder or file name in brackets is a segment of the URL: `[id].nexy` answers `/notes/1`,
`/notes/2`, and passes the segment to the page as a prop. `id: prop[int]` turns it into a number,
so `/notes/abc` answers `404` before the page runs.

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
A `{id}` in the path of a controller is a segment of the URL, passed to the method under that
name. `id: int` turns it into a number, so `/notes/abc` answers `404` before the method runs.

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

`notFound()` stops the request with a `404`: a note that does not exist answers like a URL that
does not exist.

## Serve the notes as JSON

<!-- router:fbr,custom -->
A `.py` file under `src/routes/` is an API route. Each function named after an HTTP method answers
that method:

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": id, "text": text} for id, text in NOTES.items()]
```
<!-- /router -->

<!-- router:modular -->
The three controllers of the notes, in one file. Each method named after an HTTP method answers
that method:

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

Check the three URLs:

- <http://localhost:3000/notes/1> shows *Buy milk*;
- <http://localhost:3000/notes/9> answers *Page not found*;
- `curl http://localhost:3000/api/notes` prints `[{"id":1,"text":"Buy milk"},{"id":2,"text":"Ship Nexy"}]`.

The API is listed, with its schema, at <http://localhost:3000/docs>.

## What you learned

<!-- router:fbr,custom -->
- `[id].nexy` is a dynamic segment; `id: prop[int]` reads and converts it.
- A `.py` file under `src/routes/` answers JSON, one function per HTTP method.
<!-- /router -->
<!-- router:modular -->
- `{id}` in the path of a controller is a dynamic segment; `id: int` converts it.
- A controller method that returns data answers JSON; one that returns `useViews` answers a page.
<!-- /router -->
- `notFound()` answers `404` from anywhere; a shared module keeps pages and API in step.

## Next steps

- [Part 4: components](components.md)
- [Exceptions and errors](../reference/exceptions.md): `notFound`, `redirect` and the other exits
