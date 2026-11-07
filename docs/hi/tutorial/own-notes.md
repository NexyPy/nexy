# नेक्सी के साथ एक नोट्स ऐप बनाएं, भाग 11: प्रत्येक उपयोगकर्ता को अपने स्वयं के नोट्स दें

भाग 11 प्रत्येक नोट को उस उपयोगकर्ता से जोड़ता है जिसने इसे लिखा है: नोट्स पृष्ठ साइन-इन मांगते हैं, प्रत्येक उपयोगकर्ता केवल अपने स्वयं के नोट्स देखता है और बदलता है, और एपीआई एक आगंतुक को उत्तर `401` देता है।

**शुरू करने से पहले:** [भाग 10](accounts.md) का ऐप, एक खाते के साथ।

## इसके उपयोगकर्ता को एक नोट बांधें

एक नोट को उसके उपयोगकर्ता की आईडी मिलती है। `foreign_key` डेटाबेस उस आईडी को अस्वीकार कर देता है जो उपयोगकर्ता नहीं है:

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

`user_id` खाली हो सकता है, क्योंकि इस भाग से पहले लिखे गए नोट्स का कोई उपयोगकर्ता नहीं है। वे मेज़ पर बैठे रहते हैं, और अब उन्हें कोई नहीं देखता।

```bash
nx migrate -m "notes belong to users"
nx migrate --upgrade
```

## एक उपयोगकर्ता के नोट्स के लिए डेटाबेस से पूछें

प्रत्येक फ़ंक्शन अब उपयोगकर्ता की आईडी लेता है, और उस पर फ़िल्टर करता है। किसी और के नोट का उत्तर इस तरह दिया जाता है मानो वह अस्तित्व में ही नहीं है, इसलिए उसकी आईडी जिज्ञासु आगंतुक को कुछ नहीं बताती है:

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

## किसी विज़िटर को साइन-इन पृष्ठ पर भेजें

एक फ़ंक्शन सत्र को पढ़ता है, और बिना उपयोगकर्ता के किसी को भी `/signin` पर भेजता है:

```python filename="src/guard.py"
from nexy import redirect, useSession


def signed_in_user() -> int:
    """The id of the signed-in user; a visitor is sent to the sign-in page."""
    user_id = useSession().get("user_id")
    if user_id is None:
        redirect("/signin")
    return user_id
```

`redirect` पेज या कार्रवाई को वहीं रोक देता है: चलने के बाद कुछ भी नहीं।

## क्रियाओं की रक्षा करें

प्रत्येक कार्रवाई पहले उपयोगकर्ता से पूछती है, इसलिए सत्र के बिना पोस्ट किया गया फॉर्म कुछ नहीं करता:

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

## पेजों और एपीआई की सुरक्षा करें

एक पेज किसी विज़िटर को किसी फ़ॉर्म पर नहीं भेज सकता है, लेकिन एक एपीआई जवाब दे सकता है कि उसने मना क्यों किया: एपीआई जवाब देता है `401`, पेज रीडायरेक्ट करते हैं।

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

साइन आउट करें, फिर <http://localhost:3000/notes> खोलें: आप साइन-इन पृष्ठ पर पहुंच जाएंगे। साइन इन करें और जब तक आप नोट नहीं लिखते तब तक सूची खाली रहती है। एक निजी विंडो में दूसरा खाता बनाएं: यह पहले के नोट्स नहीं देखता है।

## आपने क्या सीखा

- एक `foreign_key` एक उपयोगकर्ता को एक नोट जोड़ता है, और प्रत्येक क्वेरी उस उपयोगकर्ता पर फ़िल्टर होती है।
- किसी और के नोट का उत्तर दिया जाता है `404`, उस नोट की तरह जिसका अस्तित्व ही नहीं है।
- `redirect()` किसी पृष्ठ या कार्रवाई को रोकता है; एक एपीआई `401` का उत्तर `HTTPException` से देता है।

## अगले चरण

- [भाग 12: ईमेल द्वारा भूले हुए पासवर्ड को रीसेट करें](password-reset.md)
- [अपवाद और त्रुटियाँ](../reference/exceptions.md): `401`, `403`, `404` और प्रत्येक को कैसे दिखाया जाता है
