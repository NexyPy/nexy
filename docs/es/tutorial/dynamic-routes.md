# Cree una aplicación de notas con Nexy, parte 3: rutas dinámicas y una API

La parte 3 le da a cada nota su propia URL, `/notes/1`, y muestra las mismas notas que JSON en `/api/notes`, ambas leídas desde un módulo Python.

**Antes de comenzar:** la aplicación de la [parte 2](pages-and-layouts.md).

## Mantenga las notas en un módulo.

La página y la API leerán la misma lista. Muévelo a un módulo propio, con una función que encuentra una nota:

```python filename="src/notas.py"
NOTES = {1: "Buy milk", 2: "Ship Nexy"}


def find(note_id: int) -> str | None:
    return NOTES.get(note_id)
```

## Vincula cada nota a su página

<!-- router:fbr,custom -->
```nexy filename="src/rutas/notas/index.nexy"
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

## Agregar una página por nota

<!-- router:fbr,custom -->
Un nombre de carpeta o archivo entre paréntesis es un segmento de la URL: `[id].nexy` responde a `/notes/1`, `/notes/2` y pasa el segmento a la página como accesorio. `id: prop[int]` lo convierte en un número, por lo que `/notes/abc` responde a `404` antes de que se ejecute la página.

```nexy filename="src/rutas/notas/[id].nexy"
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
Un `{id}` en la ruta de un controlador es un segmento de la URL, pasado al método con ese nombre. `id: int` lo convierte en un número, por lo que `/notes/abc` responde a `404` antes de que se ejecute el método.

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

`notFound()` detiene la solicitud con un `404`: una nota que no existe responde como una URL que no existe.

## Servir las notas como JSON

<!-- router:fbr,custom -->
Un archivo `.py` en `src/routes/` es una ruta API. Cada función que lleva el nombre de un método HTTP responde a ese método:

```python filename="src/rutas/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": id, "text": text} for id, text in NOTES.items()]
```
<!-- /router -->

<!-- router:modular -->
Los tres controladores de los billetes, en un solo fichero. Cada método que lleva el nombre de un método HTTP responde a ese método:

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

Verifique las tres URL:

- <http://localhost:3000/notes/1> muestra *Comprar leche*;
- <http://localhost:3000/notes/9> responde *Página no encontrada*;
- `curl http://localhost:3000/api/notes` imprime `[{"id":1,"text":"Buy milk"},{"id":2,"text":"Ship Nexy"}]`.

La API aparece, con su esquema, en <http://localhost:3000/docs>.

## lo que aprendiste

<!-- router:fbr,custom -->
- `[id].nexy` es un segmento dinámico; `id: prop[int]` lo lee y lo convierte.
- Un archivo `.py` en `src/routes/` responde JSON, una función por método HTTP.
<!-- /router -->
<!-- router:modular -->
- `{id}` en la ruta de un controlador es un segmento dinámico; `id: int` lo convierte.
- Un método de controlador que devuelve datos responde JSON; uno que devuelve `useViews` responde una página.
<!-- /router -->
- `notFound()` responde `404` desde cualquier lugar; un módulo compartido mantiene las páginas y la API en sintonía.

## Próximos pasos

- [Parte 4: componentes](components.md)
- [Excepciones y errores](../reference/exceptions.md): `notFound`, `redirect` y las demás salidas
