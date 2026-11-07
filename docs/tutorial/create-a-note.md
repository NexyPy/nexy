# Build a notes app with Nexy, part 6: create a note from a form

Part 6 adds a form above the list: it posts to a Python function marked `@Action`, which saves the
note, and the visitor lands back on the list with the new note in it.

**Before you start:** the app of [part 5](store-the-notes.md), with its database.

## Save a note

Add a function that saves one note and returns it, next to the two that read them:

<!-- router:fbr,custom -->
```python filename="src/notes.py"
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
```python filename="src/notes.py"
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

## Turn it into an Action

An Action is a Python function the browser can call. `@Action` serves it as a `POST`, checks the
input against the type hints, and runs it:

```python filename="src/actions/notes.py"
from nexy.decorators import Action
from src.notes import add_note


@Action
async def create_note(text: str) -> int:
    return add_note(text).id
```

At startup, Nexy imports every module of `src/` and serves the Actions it finds: there is no route
to declare, for any router. `src/actions/` is where this tutorial keeps them.

## Post the form to it

A `.nexy` template knows the path of every Action as `__actions_path["name"]`. A plain HTML form
posts there, so the page works before any script loads:

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
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

The input is named `text`, like the parameter of `create_note`: that is how the field reaches it.

## Show a note as text, not as HTML

From now on, a note is what a visitor typed. A `.nexy` template writes a value as it is, so a note
`<script>…</script>` would run in the browser of everyone who opens the list. `| e` escapes it:
`<` becomes `&lt;`, and the note shows as text.

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
```nexy filename="src/routes/notes/[id].nexy"
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

Escape every value that comes from a visitor or from the database. `| safe` does the opposite: keep
it for HTML you wrote yourself.

## Try it

Type *Read the docs* and press **Add**. The Action saves the note, then answers `303` back to
`/notes`, and the browser shows the list again, with the third note at the bottom.

## What you learned

- `@Action` turns a Python function into a `POST` endpoint, with its type hints as the input.
- A form posts to it through `__actions_path["name"]`, with no JavaScript, and comes back with `303`.
- The field names of the form are the parameter names of the Action.
- `| e` shows what a visitor typed as text: escape every value that did not come from you.

## Next steps

- [Part 7: show validation errors](validation-errors.md)
- [Actions](../guides/actions.md): typed calls from the browser, errors and security
