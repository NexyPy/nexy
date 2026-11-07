# Créer une application de notes avec Nexy, partie 3 : itinéraires dynamiques et API

La partie 3 donne à chaque note sa propre URL, `/notes/1`, et sert les mêmes notes que JSON sur `/api/notes`, toutes deux lues à partir d'un module Python.

**Avant de commencer :** l'application de la [partie 2](pages-and-layouts.md).

## Conservez les notes dans un seul module

La page et l'API liront la même liste. Déplacez-le vers un module qui lui est propre, avec une fonction qui trouve une note :

```python filename="src/notes.py"
NOTES = {1: "Buy milk", 2: "Ship Nexy"}


def find(note_id: int) -> str | None:
    return NOTES.get(note_id)
```

## Liez chaque note à sa page

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

## Ajouter une page par note

<!-- router:fbr,custom -->
Un nom de dossier ou de fichier entre parenthèses est un segment de l'URL : `[id].nexy` répond à `/notes/1`, `/notes/2` et transmet le segment à la page en tant qu'accessoire. `id: prop[int]` le transforme en nombre, donc `/notes/abc` répond à `404` avant que la page ne s'exécute.

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
Un `{id}` dans le chemin d'un contrôleur est un segment de l'URL, transmis à la méthode sous ce nom. `id: int` le transforme en nombre, donc `/notes/abc` répond à `404` avant l'exécution de la méthode.

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

`notFound()` arrête la requête avec un `404` : une note qui n'existe pas répond comme une URL qui n'existe pas.

## Servir les notes au format JSON

<!-- router:fbr,custom -->
Un fichier `.py` sous `src/routes/` est une route API. Chaque fonction nommée d'après une méthode HTTP répond à cette méthode :

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": id, "text": text} for id, text in NOTES.items()]
```
<!-- /router -->

<!-- router:modular -->
Les trois contrôleurs des notes, dans un seul fichier. Chaque méthode nommée d'après une méthode HTTP répond à cette méthode :

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

Vérifiez les trois URL :

- <http://localhost:3000/notes/1> affiche *Acheter du lait* ;
- <http://localhost:3000/notes/9> répond *Page non trouvée* ;
- `curl http://localhost:3000/api/notes` imprime `[{"id":1,"text":"Buy milk"},{"id":2,"text":"Ship Nexy"}]`.

L'API est répertoriée, avec son schéma, dans <http://localhost:3000/docs>.

## Ce que tu as appris

<!-- router:fbr,custom -->
- `[id].nexy` est un segment dynamique ; `id: prop[int]` le lit et le convertit.
- Un fichier `.py` sous `src/routes/` répond au JSON, une fonction par méthode HTTP.
<!-- /router -->
<!-- router:modular -->
- `{id}` sur le chemin d'un contrôleur se trouve un segment dynamique ; `id: int` le convertit.
- Une méthode de contrôleur qui renvoie des données répond JSON ; celui qui renvoie `useViews` répond à une page.
<!-- /router -->
- `notFound()` répond à `404` de n'importe où ; un module partagé maintient les pages et l'API en phase.

## Prochaines étapes

- [Partie 4 : composants](components.md)
- [Exceptions et erreurs](../reference/exceptions.md) : `notFound`, `redirect` et les autres sorties
