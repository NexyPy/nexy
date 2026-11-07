# Nexy کے ساتھ ایک نوٹس ایپ بنائیں، حصہ 11: ہر صارف کو ان کے اپنے نوٹس دیں۔

حصہ 11 ہر نوٹ کو صارف کے ساتھ جوڑتا ہے جس نے اسے لکھا ہے: نوٹس کے صفحات سائن ان کرنے کے لیے کہتے ہیں، ہر صارف صرف اپنے نوٹس دیکھتا اور تبدیل کرتا ہے، اور API کا جواب `401` دیکھنے والے کو دیتا ہے۔

**اس سے پہلے کہ آپ شروع کریں:** ایک اکاؤنٹ کے ساتھ [حصہ 10](accounts.md) کی ایپ۔

## اس کے صارف کو ایک نوٹ باندھیں۔

ایک نوٹ کو اس کے صارف کی شناخت مل جاتی ہے۔ `foreign_key` ڈیٹا بیس کو ایسی شناخت سے انکار کرتا ہے جو صارف نہیں ہے:

<!-- router:fbr,custom -->
```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/notes/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
```
<!-- /router -->

`user_id` خالی ہو سکتا ہے، کیونکہ اس حصے سے پہلے لکھے گئے نوٹوں کا کوئی صارف نہیں ہے۔ وہ میز پر رہتے ہیں، اور کوئی بھی انہیں مزید نہیں دیکھتا ہے۔

```bash
nx migrate -m "notes belong to users"
nx migrate --upgrade
```

## ایک صارف کے نوٹ کے لیے ڈیٹا بیس سے پوچھیں۔

ہر فنکشن اب صارف کی شناخت لیتا ہے، اور اس پر فلٹر کرتا ہے۔ کسی اور کے نوٹ کا جواب اس طرح دیا جاتا ہے جیسے وہ موجود ہی نہیں ہے، اس لیے اس کی آئی ڈی متجسس مہمان کو کچھ نہیں بتاتی:

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
```
<!-- /router -->

## کسی وزیٹر کو سائن ان پیج پر بھیجیں۔

ایک فنکشن سیشن کو پڑھتا ہے، اور بغیر صارف کے کسی کو بھیجتا ہے `/signin`:

```python filename="src/guard.py"
from nexy import redirect, useSession


def signed_in_user() -> int:
    """The id of the signed-in user; a visitor is sent to the sign-in page."""
    user_id = useSession().get("user_id")
    if user_id is None:
        redirect("/signin")
    return user_id
```

`redirect` صفحہ یا ایکشن کو وہیں روکتا ہے: چلنے کے بعد کچھ نہیں۔

## اعمال کی حفاظت کریں۔

ہر ایکشن پہلے صارف سے پوچھتا ہے، لہذا سیشن کے بغیر پوسٹ کیا گیا فارم کچھ نہیں کرتا:

```python filename="src/actions/notes.py"
from urllib.parse import urlencode

from nexy import notFound
from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.guard import signed_in_user
from src.notes import add_note, change_note, remove_note

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
```

## صفحات اور API کی حفاظت کریں۔

ایک صفحہ کسی وزیٹر کو فارم پر نہیں بھیج سکتا، لیکن ایک API جواب دے سکتا ہے کہ وہ کیوں انکار کرتا ہے: API جواب دیتا ہے `401`، صفحات ری ڈائریکٹ ہوتے ہیں۔

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.guard import signed_in_user
from src.notes import notes_page

user_id = signed_in_user()
params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(user_id, number)
notes = found[0]
more = found[1]
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['sign_out'] }}">
    <button type="submit">Sign out</button>
  </form>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```

```nexy filename="src/routes/notes/[id].nexy"
---
from nexy import notFound, useSearchParams
from src.guard import signed_in_user
from src.notes import find

id: prop[int]
note = find(signed_in_user(), id)
if note is None:
    notFound()
error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>{{ note.text | e }}</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['update_note'] }}">
    <input type="hidden" name="note_id" value="{{ note.id }}">
    <input name="text" value="{{ note.text | e }}" maxlength="200" required>
    <button type="submit">Save</button>
  </form>

  <form method="post" action="{{ __actions_path['delete_note'] }}">
    <input type="hidden" name="note_id" value="{{ note.id }}">
    <button type="submit">Delete</button>
  </form>

  <a href="/notes">All notes</a>
</section>
```

```python filename="src/routes/api/notes.py"
from nexy import useSession
from nexy.http import HTTPException
from src.notes import all_notes


async def GET():
    user_id = useSession().get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Sign in first")
    return [note.model_dump() for note in all_notes(user_id)]
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.guard import signed_in_user
from src.notes import notes_page

user_id = signed_in_user()
params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(user_id, number)
notes = found[0]
more = found[1]
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['sign_out'] }}">
    <button type="submit">Sign out</button>
  </form>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```

```nexy filename="src/apps/notes/note_view.nexy"
---
from nexy import useSearchParams

note: prop[object]
error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>{{ note.text | e }}</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['update_note'] }}">
    <input type="hidden" name="note_id" value="{{ note.id }}">
    <input name="text" value="{{ note.text | e }}" maxlength="200" required>
    <button type="submit">Save</button>
  </form>

  <form method="post" action="{{ __actions_path['delete_note'] }}">
    <input type="hidden" name="note_id" value="{{ note.id }}">
    <button type="submit">Delete</button>
  </form>

  <a href="/notes">All notes</a>
</section>
```

```python filename="src/apps/notes/notes_controller.py"
from nexy import notFound, useSession
from nexy.decorators import Controller
from nexy.hooks import useViews
from nexy.http import HTTPException
from src.guard import signed_in_user
from src.notes import all_notes, find

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
        note = find(signed_in_user(), id)
        if note is None:
            notFound()
        return page("src/apps/notes/note_view.nexy", note=note)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        user_id = useSession().get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Sign in first")
        return [note.model_dump() for note in all_notes(user_id)]
```
<!-- /router -->

سائن آؤٹ کریں، پھر کھولیں <http://localhost:3000/notes>: آپ سائن ان پیج پر اترتے ہیں۔ سائن ان کریں، اور فہرست اس وقت تک خالی رہے گی جب تک آپ نوٹ نہیں لکھتے۔ ایک نجی ونڈو میں دوسرا اکاؤنٹ بنائیں: اس میں پہلے کے نوٹ نظر نہیں آتے۔

## جو آپ نے سیکھا۔

- A `foreign_key` صارف کے ساتھ ایک نوٹ باندھتا ہے، اور ہر سوال اس صارف پر فلٹر کرتا ہے۔
- کسی اور کے نوٹ کا جواب دیا جاتا ہے `404`، ایسے نوٹ کی طرح جو موجود ہی نہ ہو۔
- `redirect()` صفحہ یا ایکشن کو روکتا ہے۔ ایک API جواب دیتا ہے `401` کے ساتھ `HTTPException`۔

## اگلے اقدامات

- [حصہ 12: ای میل کے ذریعے بھولے ہوئے پاس ورڈ کو دوبارہ ترتیب دیں](password-reset.md)
- [مستثنیات اور غلطیاں](../reference/exceptions.md): `401`، `403`، `404` اور ہر ایک کو کیسے دکھایا گیا ہے
