# Nexy کے ساتھ ایک نوٹس ایپ بنائیں، حصہ 14: صفحہ کو دوبارہ لوڈ کیے بغیر نوٹ پر نشان لگائیں

حصہ 14 ہر نوٹ میں ایک **ہو گیا** بٹن شامل کرتا ہے۔ یہ ایک ایسی شکل ہے جو بغیر کسی JavaScript کے کام کرتی ہے، اور JavaScript کی چند سطریں صفحہ کو دوبارہ لوڈ کیے بغیر اسے اپنی جگہ پر محفوظ کرتی ہیں۔

**شروع کرنے سے پہلے:** [پارٹ 13](search-the-notes.md) کی ایپ۔

## ایک نوٹ کیا گیا ہے، یا نہیں

<!-- router:fbr,custom -->
```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    done: bool = Field(default=False, sa_column_kwargs={"server_default": "0"})
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/notes/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    done: bool = Field(default=False, sa_column_kwargs={"server_default": "0"})
```
<!-- /router -->

ٹیبل میں پہلے سے ہی نوٹ موجود ہیں، اور SQLite کوئی ایسا کالم شامل نہیں کر سکتا جس میں موجودہ قطاروں میں ڈالنے کے لیے ایک قدر نہ ہو۔ `server_default` دیتا ہے: ہجرت لکھتی ہے `DEFAULT 0`، اور ہر نوٹ شروع ہوتا ہے جیسا کہ نہیں ہوا ہے۔

```bash
nx migrate -m "notes can be done"
nx migrate --upgrade
```

## اسے ڈیٹا بیس میں ایک ایکشن کے پیچھے پلٹائیں۔

<!-- router:fbr,custom -->
```python filename="src/notes.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note

PAGE_SIZE = 5


def notes_page(user_id: int, number: int) -> tuple[list[Note], bool]:
    """One page of the notes of *user_id*, oldest first, and whether a page comes after it."""
    query = select(Note).where(Note.user_id == user_id).order_by(Note.id)
    with Session(engine) as session:
        found = list(session.exec(query.offset((number - 1) * PAGE_SIZE).limit(PAGE_SIZE + 1)))
    return found[:PAGE_SIZE], len(found) > PAGE_SIZE


def all_notes(user_id: int) -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).where(Note.user_id == user_id).order_by(Note.id)))


def find(user_id: int, note_id: int) -> Note | None:
    """The note, when it belongs to *user_id*: someone else's note is not found."""
    with Session(engine) as session:
        note = session.get(Note, note_id)
    return note if note is not None and note.user_id == user_id else None


def add_note(user_id: int, text: str) -> Note:
    note = Note(text=text, user_id=user_id)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note


def change_note(user_id: int, note_id: int, text: str) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None or note.user_id != user_id:
            return False
        note.text = text
        session.commit()
    return True


def remove_note(user_id: int, note_id: int) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None or note.user_id != user_id:
            return False
        session.delete(note)
        session.commit()
    return True


def toggle_done(user_id: int, note_id: int) -> bool | None:
    """The new state of the note, or None when the user has no such note."""
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None or note.user_id != user_id:
            return None
        note.done = not note.done
        session.commit()
        return note.done
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/notes.py"
from sqlmodel import Session, select

from src.apps.notes.note_model import Note
from src.configs.db import engine

PAGE_SIZE = 5


def notes_page(user_id: int, number: int) -> tuple[list[Note], bool]:
    """One page of the notes of *user_id*, oldest first, and whether a page comes after it."""
    query = select(Note).where(Note.user_id == user_id).order_by(Note.id)
    with Session(engine) as session:
        found = list(session.exec(query.offset((number - 1) * PAGE_SIZE).limit(PAGE_SIZE + 1)))
    return found[:PAGE_SIZE], len(found) > PAGE_SIZE


def all_notes(user_id: int) -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).where(Note.user_id == user_id).order_by(Note.id)))


def find(user_id: int, note_id: int) -> Note | None:
    """The note, when it belongs to *user_id*: someone else's note is not found."""
    with Session(engine) as session:
        note = session.get(Note, note_id)
    return note if note is not None and note.user_id == user_id else None


def add_note(user_id: int, text: str) -> Note:
    note = Note(text=text, user_id=user_id)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note


def change_note(user_id: int, note_id: int, text: str) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None or note.user_id != user_id:
            return False
        note.text = text
        session.commit()
    return True


def remove_note(user_id: int, note_id: int) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None or note.user_id != user_id:
            return False
        session.delete(note)
        session.commit()
    return True


def toggle_done(user_id: int, note_id: int) -> bool | None:
    """The new state of the note, or None when the user has no such note."""
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None or note.user_id != user_id:
            return None
        note.done = not note.done
        session.commit()
        return note.done
```
<!-- /router -->

```python filename="src/actions/notes.py"
from urllib.parse import urlencode

from nexy import notFound
from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.guard import signed_in_user
from src.notes import add_note, change_note, remove_note, toggle_done

MAX_LENGTH = 200


def back(path: str = "/notes", error: str = "") -> RedirectResponse:
    query = f"?{urlencode({'error': error})}" if error else ""
    return RedirectResponse(f"{path}{query}", status_code=303)


def problem(text: str) -> str:
    if not text:
        return "A note cannot be blank."
    if len(text) > MAX_LENGTH:
        return f"A note is at most {MAX_LENGTH} characters."
    return ""


@Action
async def create_note(text: str) -> RedirectResponse:
    user_id = signed_in_user()
    text = text.strip()
    if error := problem(text):
        return back(error=error)
    add_note(user_id, text)
    return back()


@Action
async def update_note(note_id: int, text: str) -> RedirectResponse:
    user_id = signed_in_user()
    text = text.strip()
    if error := problem(text):
        return back(f"/notes/{note_id}", error)
    if not change_note(user_id, note_id, text):
        notFound()
    return back(f"/notes/{note_id}")


@Action
async def delete_note(note_id: int) -> RedirectResponse:
    if not remove_note(signed_in_user(), note_id):
        notFound()
    return back()


@Action
async def toggle_note(note_id: int) -> bool:
    done = toggle_done(signed_in_user(), note_id)
    if done is None:
        notFound()
    return done
```

`toggle_note` نئی حالت کو لوٹاتا ہے، ایک `bool`۔ اس پر پوسٹ کیا جانے والا فارم معمول کے مطابق `303` صفحہ پر واپس آجاتا ہے۔ ایک اسکرپٹ جو JSON کا مطالبہ کرتا ہے اسے `true` یا `false` مل جاتا ہے۔ ایک ایکشن دونوں کام کرتا ہے۔

## ایک بٹن جو ایک شکل ہے۔

کارڈ وہ حالت دکھاتا ہے جسے سرور جانتا ہے، اور اپنے نوٹ کی شناخت پوسٹ کرتا ہے:

```nexy filename="src/components/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
done: prop[bool]
---
<article class="note{% if done %} note-done{% endif %}">
  <a href="/notes/{{ id }}">{{ text | e }}</a>
  <form method="post" action="{{ __actions_path['toggle_note'] }}" data-toggle>
    <input type="hidden" name="note_id" value="{{ id }}">
    <button type="submit" aria-pressed="{{ 'true' if done else 'false' }}">{{ 'Done' if done else 'To do' }}</button>
  </form>
</article>

<style>
  .note { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
  .note-done a { text-decoration: line-through; opacity: 0.6; }
</style>
```

`aria-pressed` اسکرین ریڈر کو بتاتا ہے کہ بٹن ایک ٹوگل ہے، اور آیا یہ آن ہے۔

## دوبارہ لوڈ کیے بغیر محفوظ کریں۔

فہرست ہر کارڈ میں `done` گزرتی ہے، اور صفحہ کے تمام کارڈز کے لیے ایک اسکرپٹ شامل کرتی ہے۔

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from "@/components/NoteSearch.tsx" import NoteSearch
from nexy import useSearchParams
from src.guard import signed_in_user
from src.notes import all_notes, notes_page

user_id = signed_in_user()
params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(user_id, number)
notes = found[0]
more = found[1]
searchable = [{"id": note.id, "text": note.text} for note in all_notes(user_id)]
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['sign_out'] }}">
    <button type="submit">Sign out</button>
  </form>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <NoteSearch notes="{{ searchable }}" directive="client:idle" />

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" done="{{ note.done }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>

  <script type="module">
    // With JavaScript on, the Done buttons save without leaving the page.
    document.addEventListener("submit", async (event) => {
      const form = event.target.closest("form[data-toggle]")
      if (!form) return
      event.preventDefault()
      const button = form.querySelector("button")
      button.disabled = true
      const answer = await fetch(form.action, {
        method: "POST",
        headers: { "content-type": "application/json", accept: "application/json" },
        body: JSON.stringify({ note_id: Number(form.elements.note_id.value) }),
      })
      button.disabled = false
      if (!answer.ok) return form.submit()
      const done = await answer.json()
      button.setAttribute("aria-pressed", String(done))
      button.textContent = done ? "Done" : "To do"
      form.closest(".note").classList.toggle("note-done", done)
    })
  </script>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from "@/components/NoteSearch.tsx" import NoteSearch
from nexy import useSearchParams
from src.guard import signed_in_user
from src.notes import all_notes, notes_page

user_id = signed_in_user()
params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(user_id, number)
notes = found[0]
more = found[1]
searchable = [{"id": note.id, "text": note.text} for note in all_notes(user_id)]
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['sign_out'] }}">
    <button type="submit">Sign out</button>
  </form>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <NoteSearch notes="{{ searchable }}" directive="client:idle" />

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" done="{{ note.done }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>

  <script type="module">
    // With JavaScript on, the Done buttons save without leaving the page.
    document.addEventListener("submit", async (event) => {
      const form = event.target.closest("form[data-toggle]")
      if (!form) return
      event.preventDefault()
      const button = form.querySelector("button")
      button.disabled = true
      const answer = await fetch(form.action, {
        method: "POST",
        headers: { "content-type": "application/json", accept: "application/json" },
        body: JSON.stringify({ note_id: Number(form.elements.note_id.value) }),
      })
      button.disabled = false
      if (!answer.ok) return form.submit()
      const done = await answer.json()
      button.setAttribute("aria-pressed", String(done))
      button.textContent = done ? "Done" : "To do"
      form.closest(".note").classList.toggle("note-done", done)
    })
  </script>
</section>
```
<!-- /router -->

اسکرپٹ صفحہ کی ہر شکل کو سنتا ہے، اور صرف نشان زدہ شکلوں کو ہی لیتا ہے `data-toggle`۔ یہ وہی `note_id` فارم بھیجتا ہے، جیسا کہ JSON، اور جواب کے ساتھ بٹن کو اپ ڈیٹ کرتا ہے۔ اگر کال ناکام ہو جاتی ہے، تو یہ فارم کو عام طریقے سے پوسٹ کرنے دیتا ہے، لہذا کلک کبھی ضائع نہیں ہوتا ہے۔

جزیرہ 13 کی طرح React جزیرہ کیوں نہیں؟ ہر نوٹ کی حالت ہر درخواست پر سرور کے ذریعہ معلوم ہوتی ہے، اور کوئی بھی اسکرپٹ چلنے سے پہلے ہی ایک فارم اسے صحیح دکھاتا ہے۔ اسکرپٹ صرف تبدیل کرتا ہے کہ فارم کیسے بھیجا جاتا ہے۔ یہ ہے *ترقی پسند اضافہ*: صفحہ JavaScript کے بغیر کام کرتا ہے، اور اس کے ساتھ بہتر ہے۔

کھولیں <http://localhost:3000/notes> اور ایک نوٹ پر **کرنے کے لیے** کو دبائیں: یہ **ڈن** میں بدل جاتا ہے، نوٹ ٹوٹ جاتا ہے، اور صفحہ دوبارہ لوڈ نہیں ہوتا ہے۔ اسے دوبارہ لوڈ کریں: نوٹ اب بھی ہو گیا ہے۔

## جو آپ نے سیکھا۔

- `server_default` ہجرت کو ایک ٹیبل میں مطلوبہ کالم شامل کرنے دیتا ہے جس میں قطاریں ہوتی ہیں۔
- ون ایکشن ایک فارم کا جواب `303` کے ساتھ دیتا ہے، اور ایک اسکرپٹ جو JSON کو اس کی واپسی کی قیمت کے ساتھ مانگتا ہے۔
- ترقی پسند اضافہ: ایک فارم جو اکیلے کام کرتا ہے، اور ایک اسکرپٹ جو اسے جگہ پر بھیجتا ہے۔

## اگلے اقدامات

- یونٹ 5: درخواست سے آگے (اگلا آنے والا)
- [ایکشنز](../guides/actions.md): براؤزر سے ٹائپ شدہ کالز، غلطیاں اور سیکیورٹی
