# Nexy এর সাথে একটি নোট অ্যাপ তৈরি করুন, পার্ট 11: প্রতিটি ব্যবহারকারীকে তাদের নিজস্ব নোট দিন

পার্ট 11 প্রতিটি নোটকে ব্যবহারকারীর সাথে সংযুক্ত করে যারা এটি লিখেছেন: নোটের পৃষ্ঠাগুলি সাইন-ইন করার জন্য অনুরোধ করে, প্রতিটি ব্যবহারকারী শুধুমাত্র তাদের নিজস্ব নোটগুলি দেখে এবং পরিবর্তন করে, এবং API একজন দর্শককে `401` উত্তর দেয়।

**আপনি শুরু করার আগে:** একটি অ্যাকাউন্ট সহ [পার্ট 10](accounts.md) এর অ্যাপ।

## এর ব্যবহারকারীর কাছে একটি নোট টাই

একটি নোট তার ব্যবহারকারীর আইডি পায়। `foreign_key` ডাটাবেসকে এমন একটি আইডি প্রত্যাখ্যান করে যা ব্যবহারকারী নয়:

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

`user_id` খালি হতে পারে, কারণ এই অংশের আগে লেখা নোটে কোনো ব্যবহারকারী নেই। তারা টেবিলে থাকে, এবং কেউ তাদের আর দেখতে পায় না।

```bash
nx migrate -m "notes belong to users"
nx migrate --upgrade
```

## একজন ব্যবহারকারীর নোটের জন্য ডাটাবেস জিজ্ঞাসা করুন

প্রতিটি ফাংশন এখন ব্যবহারকারীর আইডি নেয় এবং এটিতে ফিল্টার করে। অন্য কারও একটি নোটের উত্তর দেওয়া হয় যেন এটির অস্তিত্ব নেই, তাই এর আইডি একজন কৌতূহলী দর্শককে কিছুই বলে না:

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

## সাইন-ইন পৃষ্ঠায় একজন দর্শককে পাঠান

একটি ফাংশন অধিবেশন পড়ে, এবং ব্যবহারকারী ছাড়া কাউকে পাঠায় `/signin`:

```python filename="src/guard.py"
from nexy import redirect, useSession


def signed_in_user() -> int:
    """The id of the signed-in user; a visitor is sent to the sign-in page."""
    user_id = useSession().get("user_id")
    if user_id is None:
        redirect("/signin")
    return user_id
```

`redirect` পৃষ্ঠা বা অ্যাকশনটি সেখানেই থামে: এটি চালানোর পরে কিছুই নেই।

## অ্যাকশন রক্ষা করুন

প্রতিটি অ্যাকশন প্রথমে ব্যবহারকারীর জন্য জিজ্ঞাসা করে, তাই সেশন ছাড়া পোস্ট করা ফর্ম কিছুই করে না:

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

## পৃষ্ঠা এবং API রক্ষা করুন

একটি পৃষ্ঠা একটি ফর্ম একটি ভিজিটর পাঠাতে পারে না, কিন্তু একটি API উত্তর দিতে পারে কেন এটি প্রত্যাখ্যান করে: API উত্তর দেয় `401`, পৃষ্ঠাগুলি পুনঃনির্দেশ করে।

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

সাইন আউট করুন, তারপর খুলুন <http://localhost:3000/notes>: আপনি সাইন-ইন পৃষ্ঠায় অবতরণ করুন। সাইন ইন করুন, এবং আপনি একটি নোট না লেখা পর্যন্ত তালিকাটি খালি থাকবে। একটি ব্যক্তিগত উইন্ডোতে একটি দ্বিতীয় অ্যাকাউন্ট তৈরি করুন: এটি প্রথমটির নোটগুলি দেখতে পায় না।

## আপনি যা শিখেছেন

- A `foreign_key` ব্যবহারকারীর সাথে একটি নোট বেঁধে দেয় এবং প্রতিটি ক্যোয়ারী সেই ব্যবহারকারীকে ফিল্টার করে।
- অন্য কারো নোটের উত্তর দেওয়া হয় `404`, এমন একটি নোটের মতো যার অস্তিত্ব নেই।
- `redirect()` একটি পৃষ্ঠা বা একটি ক্রিয়া বন্ধ করে; একটি API উত্তর দেয় `401` এর সাথে `HTTPException`।

## পরবর্তী পদক্ষেপ

- [পার্ট 12: ইমেল দ্বারা একটি ভুলে যাওয়া পাসওয়ার্ড পুনরায় সেট করুন](password-reset.md)
- [ব্যতিক্রম এবং ত্রুটি ](../reference/exceptions.md): `401`, `403`, `404` এবং প্রতিটি কীভাবে দেখানো হয়েছে
