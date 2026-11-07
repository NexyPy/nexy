# Crea una aplicación de notas con Nexy, parte 9: pagina las notas

La parte 9 muestra las notas de cinco en cinco, con enlaces a las páginas anterior y siguiente, leídas desde el `page` de la URL: `/notes?page=2`.

**Antes de comenzar:** la aplicación de la [parte 8](edit-and-delete.md).

## Solicite una página a la base de datos.

`OFFSET` se salta las notas de las páginas anteriores, `LIMIT` se queda con cinco. Al solicitar uno más de cinco se indica, de forma gratuita, si existe una página siguiente:

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


def change_note(note_id: int, text: str) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        note.text = text
        session.commit()
    return True


def remove_note(note_id: int) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        session.delete(note)
        session.commit()
    return True


PAGE_SIZE = 5


def notes_page(number: int) -> tuple[list[Note], bool]:
    """One page of notes, oldest first, and whether a page comes after it."""
    with Session(engine) as session:
        query = select(Note).order_by(Note.id).offset((number - 1) * PAGE_SIZE).limit(PAGE_SIZE + 1)
        found = list(session.exec(query))
    return found[:PAGE_SIZE], len(found) > PAGE_SIZE
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


def change_note(note_id: int, text: str) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        note.text = text
        session.commit()
    return True


def remove_note(note_id: int) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        session.delete(note)
        session.commit()
    return True


PAGE_SIZE = 5


def notes_page(number: int) -> tuple[list[Note], bool]:
    """One page of notes, oldest first, and whether a page comes after it."""
    with Session(engine) as session:
        query = select(Note).order_by(Note.id).offset((number - 1) * PAGE_SIZE).limit(PAGE_SIZE + 1)
        found = list(session.exec(query))
    return found[:PAGE_SIZE], len(found) > PAGE_SIZE
```
<!-- /router -->

## Leer el número de página de la URL

El `page` de la cadena de consulta es texto enviado por el visitante: cualquier cosa que no sea un número positivo vuelve a la primera página, por lo que `/notes?page=abc` aún responde.

<!-- router:fbr,custom -->
```nexy filename="src/rutas/notas/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import notes_page

params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(number)
notes = found[0]
more = found[1]
---
<section class="app-page">
  <h1>Notes</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import notes_page

params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(number)
notes = found[0]
more = found[1]
---
<section class="app-page">
  <h1>Notes</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

`rel="prev"` y `rel="next"` indican a los navegadores y motores de búsqueda cómo se suceden las páginas entre sí, y `aria-label` nombra los enlaces para un lector de pantalla.

Agregue notas hasta que haya más de cinco: la lista se detiene en cinco, con un enlace **Más antiguo**. Conduce a `/notes?page=2`, que tiene un enlace **más nuevo**.

## lo que aprendiste

- `offset` y `limit` leen una página; pedir una fila más dice si sigue otra página.
- `useSearchParams()` lee `?page=`; Se verifica un valor del visitante antes de usarlo.
- `rel="prev"` y `rel="next"` vinculan las páginas para navegadores, rastreadores y lectores de pantalla.

## Próximos pasos

- [Unidad 3, parte 10: crea una cuenta e inicia sesión](accounts.md)
- [SQLite](../databases/sqlite.md): índices, pragmas y pruebas en una base de datos en memoria
