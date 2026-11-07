# Erstellen Sie eine Notizen-App mit Nexy, Teil 6: Erstellen Sie eine Notiz aus einem Formular

Teil 6 fügt über der Liste ein Formular hinzu: Es postet an eine Python-Funktion mit der Bezeichnung `@Action`, die die Notiz speichert, und der Besucher landet mit der neuen Notiz darin wieder auf der Liste.

**Bevor Sie beginnen:** die App von [Teil 5](store-the-notes.md) mit ihrer Datenbank.

## Speichern Sie eine Notiz

Fügen Sie eine Funktion hinzu, die eine Notiz speichert und sie zurückgibt, neben den beiden, die sie gelesen haben:

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

## Verwandeln Sie es in eine Aktion

Eine Aktion ist eine Python Funktion, die der Browser aufrufen kann. `@Action` dient als `POST`, prüft die Eingabe anhand der Typhinweise und führt es aus:

```python filename="src/actions/notes.py"
from nexy.decorators import Action
from src.notes import add_note


@Action
async def create_note(text: str) -> int:
    return add_note(text).id
```

Beim Start importiert Nexy jedes Modul von `src/` und führt die gefundenen Aktionen aus: Für keinen Router muss eine Route deklariert werden. `src/actions/` ist der Ort, an dem sie in diesem Tutorial aufbewahrt werden.

## Posten Sie das Formular dort

Eine `.nexy`-Vorlage kennt den Pfad jeder Aktion als `__actions_path["name"]`. Dort wird ein einfaches HTML-Formular gepostet, sodass die Seite funktioniert, bevor ein Skript geladen wird:

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

Die Eingabe heißt `text`, wie der Parameter von `create_note`: Auf diese Weise erreicht das Feld sie.

## Zeigen Sie eine Notiz als Text und nicht als HTML an

Von nun an ist eine Notiz das, was ein Besucher eingegeben hat. Eine `.nexy`-Vorlage schreibt einen Wert so, wie er ist, sodass im Browser jedes Benutzers, der die Liste öffnet, eine Notiz `<script>…</script>` angezeigt wird. `| e` maskiert es: `<` wird zu `&lt;` und die Notiz wird als Text angezeigt.

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

Escapen Sie jeden Wert, der von einem Besucher oder aus der Datenbank stammt. `| safe` macht das Gegenteil: Behalten Sie es für HTML bei, das Sie selbst geschrieben haben.

## Probieren Sie es aus

Geben Sie *Dokumente lesen* ein und klicken Sie auf **Hinzufügen**. Die Aktion speichert die Notiz, antwortet dann mit `303` zurück auf `/notes` und der Browser zeigt die Liste erneut an, mit der dritten Notiz unten.

## Was du gelernt hast

- `@Action` verwandelt eine Python-Funktion in einen `POST`-Endpunkt mit seinen Typhinweisen als Eingabe.
- Ein Formular sendet es über `__actions_path["name"]` ohne JavaScript und kommt mit `303` zurück.
- Die Feldnamen des Formulars sind die Parameternamen der Aktion.
- `| e` zeigt, was ein Besucher als Text eingegeben hat: Escape jeden Wert, der nicht von Ihnen stammt.

## Nächste Schritte

- [Teil 7: Validierungsfehler anzeigen](validation-errors.md)
- [Aktionen](../guides/actions.md): getippte Aufrufe vom Browser, Fehler und Sicherheit
