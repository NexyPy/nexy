# Nexy کے ساتھ ایک نوٹس ایپ بنائیں، حصہ 9: نوٹوں کو صفحہ بندی کریں۔

حصہ 9 ایک وقت میں پانچ نوٹ دکھاتا ہے، اگلے اور پچھلے صفحات کے لنکس کے ساتھ، URL کے `page` سے پڑھا جاتا ہے: `/notes?page=2`۔

**شروع کرنے سے پہلے:** [پارٹ 8](edit-and-delete.md) کی ایپ۔

## ڈیٹا بیس سے ایک صفحے کے لیے پوچھیں۔

`OFFSET` اس سے پہلے کے صفحات کے نوٹ کو چھوڑ دیتا ہے، `LIMIT` پانچ رکھتا ہے۔ پانچ سے زیادہ بتانے کے لیے پوچھنا، مفت میں، آیا اگلا صفحہ موجود ہے:

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

## URL سے صفحہ نمبر پڑھیں

استفسار کی تار کا `page` وزیٹر کے ذریعہ بھیجا گیا متن ہے: کوئی بھی چیز جو مثبت نمبر نہیں ہے وہ پہلے صفحہ پر واپس آتی ہے، لہذا `/notes?page=abc` پھر بھی جواب دیتا ہے۔

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
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

`rel="prev"` اور `rel="next"` براؤزرز اور سرچ انجنوں کو بتاتے ہیں کہ صفحات کس طرح ایک دوسرے کی پیروی کرتے ہیں، اور `aria-label` اسکرین ریڈر کے لیے لنکس کو نام دیتے ہیں۔

نوٹ شامل کریں جب تک کہ پانچ سے زیادہ نہ ہوں: فہرست ایک **پرانی** لنک کے ساتھ، پانچ پر رک جاتی ہے۔ یہ `/notes?page=2` کی طرف جاتا ہے، جس کا ایک **نیا** لنک واپس ہے۔

## جو آپ نے سیکھا۔

- `offset` اور `limit` ایک صفحہ پڑھیں۔ ایک قطار مزید مانگنا کہتا ہے کہ آیا دوسرا صفحہ فالو کرتا ہے۔
- `useSearchParams()` پڑھتا ہے `?page=`؛ وزیٹر کی قیمت استعمال کرنے سے پہلے اس کی جانچ پڑتال کی جاتی ہے۔
- `rel="prev"` اور `rel="next"` براؤزرز، کرالر اور اسکرین ریڈرز کے لیے صفحات کو جوڑتے ہیں۔

## اگلے اقدامات

- [یونٹ 3، حصہ 10: ایک اکاؤنٹ بنائیں اور سائن ان کریں](accounts.md)
- [SQLite](../databases/sqlite.md): انڈیکسز، پراگمس اور ان میموری ڈیٹا بیس پر ٹیسٹ
