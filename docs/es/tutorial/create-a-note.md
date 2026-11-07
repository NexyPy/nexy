# Cree una aplicación de notas con Nexy, parte 6: cree una nota a partir de un formulario

La parte 6 agrega un formulario encima de la lista: se publica en una función Python marcada `@Action`, que guarda la nota, y el visitante regresa a la lista con la nueva nota.

**Antes de comenzar:** la aplicación de la [parte 5](store-the-notes.md), con su base de datos.

## guardar una nota

Agregue una función que guarde una nota y la devuelva, junto a las dos que las leen:

<!-- router:fbr,custom -->
```python filename="src/notas.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def all_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).order_by(Note.id)))


def find(note_id: int) -> Note | None:
    with Session(engine) as session:
        return session.get(Note, note_id)


def add_note(text: str) -> Note:
    note = Note(text=text)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/notas.py"
from sqlmodel import Session, select

from src.apps.notes.note_model import Note
from src.configs.db import engine


def all_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).order_by(Note.id)))


def find(note_id: int) -> Note | None:
    with Session(engine) as session:
        return session.get(Note, note_id)


def add_note(text: str) -> Note:
    note = Note(text=text)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note
```
<!-- /router -->

## Conviértelo en una acción

Una acción es una función Python que el navegador puede llamar. `@Action` lo sirve como `POST`, compara la entrada con las sugerencias de tipo y lo ejecuta:

```python filename="src/acciones/notas.py"
from nexy.decorators import Action
from src.notes import add_note


@Action
async def create_note(text: str) -> int:
    return add_note(text).id
```

Al inicio, Nexy importa todos los módulos de `src/` y realiza las acciones que encuentra: no hay ninguna ruta que declarar, para ningún enrutador. `src/actions/` es donde los guarda este tutorial.

## Publica el formulario en él.

Una plantilla `.nexy` conoce la ruta de cada acción como `__actions_path["name"]`. Allí se publica un formulario HTML simple, por lo que la página funciona antes de que se cargue cualquier script:

<!-- router:fbr,custom -->
```nexy filename="src/rutas/notas/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

La entrada se llama `text`, al igual que el parámetro de `create_note`: así llega el campo.

## Mostrar una nota como texto, no como HTML

De ahora en adelante, una nota es lo que escribe un visitante. Una plantilla `.nexy` escribe un valor tal como está, por lo que se ejecutará una nota `<script>…</script>` en el navegador de todos los que abran la lista. `| e` se escapa: `<` se convierte en `&lt;` y la nota se muestra como texto.

```nexy filename="src/components/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
---
<article class="note">
  <a href="/notes/{{ id }}">{{ text | e }}</a>
</article>

<style>
  .note { padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
</style>
```

<!-- router:fbr,custom -->
```nexy filename="src/rutas/notas/[id].nexy"
---
from nexy import notFound
from src.notes import find

id: prop[int]
note = find(id)
if note is None:
    notFound()
---
<section class="app-page">
  <h1>{{ note.text | e }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/note_view.nexy"
---
text: prop[str]
---
<section class="app-page">
  <h1>{{ text | e }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

Escapa de cada valor que proviene de un visitante o de la base de datos. `| safe` hace lo contrario: guárdalo para el HTML que escribiste tú mismo.

## Pruébalo

Escriba *Lea los documentos* y presione **Agregar**. La acción guarda la nota, luego responde `303` a `/notes` y el navegador muestra la lista nuevamente, con la tercera nota en la parte inferior.

## lo que aprendiste

- `@Action` convierte una función Python en un punto final `POST`, con sus sugerencias de tipo como entrada.
- Se publica un formulario a través de `__actions_path["name"]`, sin JavaScript, y regresa con `303`.
- Los nombres de los campos del formulario son los nombres de los parámetros de la Acción.
- `| e` muestra lo que un visitante escribió como texto: escape todos los valores que no provengan de usted.

## Próximos pasos

- [Parte 7: mostrar errores de validación](validation-errors.md)
- [Acciones](../guides/actions.md): llamadas tecleadas desde el navegador, errores y seguridad
