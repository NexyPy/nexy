# Nexy দিয়ে একটি নোট অ্যাপ তৈরি করুন, পার্ট 8: একটি নোট সম্পাদনা করুন এবং মুছুন

পার্ট 8 একটি নোটের পৃষ্ঠায় দুটি ফর্ম রাখে: একটি নতুন পাঠ্য সংরক্ষণ করে, অন্যটি নোটটি মুছে দেয় এবং উভয়ই এটি তৈরি করে এমন একটি ক্রিয়া।

**আপনি শুরু করার আগে:** [পার্ট 7](validation-errors.md) এর অ্যাপ।

## ডাটাবেসে একটি নোট পরিবর্তন করুন এবং সরান

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
```
<!-- /router -->

## আরও দুটি অ্যাকশন

`update_note` `create_note` এর মতো একই নিয়মের সাথে পাঠ্যটি পরীক্ষা করে এবং নোটের পৃষ্ঠায় একটি ব্যর্থতা ফেরত পাঠায়। `delete_note` তালিকায় ফিরে যায়:

```python filename="src/actions/notes.py"
from urllib.parse import urlencode

from nexy import notFound
from nexy.decorators import Action
from nexy.http import RedirectResponse
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
    text = text.strip()
    if error := problem(text):
        return back(error=error)
    add_note(text)
    return back()


@Action
async def update_note(note_id: int, text: str) -> RedirectResponse:
    text = text.strip()
    if error := problem(text):
        return back(f"/notes/{note_id}", error)
    if not change_note(note_id, text):
        notFound()
    return back(f"/notes/{note_id}")


@Action
async def delete_note(note_id: int) -> RedirectResponse:
    if not remove_note(note_id):
        notFound()
    return back()
```

`create_note` এর নিয়মগুলি `problem`-এ স্থানান্তরিত হয়েছে, তাই একটি পাঠ্য গ্রহণকারী দুটি ক্রিয়া আলাদা হতে পারে না। একটি নোট যা আর বিদ্যমান নেই উত্তর `404`, তার পৃষ্ঠায় লাইক করুন।

## নোট পাতার ফর্ম

আইডিটি `note_id` নামে একটি লুকানো ক্ষেত্রে ভ্রমণ করে, প্যারামিটারের নাম:

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/[id].nexy"
---
from nexy import notFound, useSearchParams
from src.notes import find

id: prop[int]
note = find(id)
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
<!-- /router -->

<!-- router:modular -->
ভিউটির এখন পুরো নোটের প্রয়োজন, শুধুমাত্র এর পাঠ্য নয়:

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
from nexy import notFound
from nexy.decorators import Controller
from nexy.hooks import useViews
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
        note = find(id)
        if note is None:
            notFound()
        return page("src/apps/notes/note_view.nexy", note=note)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        return [note.model_dump() for note in all_notes()]
```
<!-- /router -->

খুলুন <http://localhost:3000/notes/1>, পরিবর্তন করুন *দুধ কিনুন* *ওট দুধ কিনুন* এবং চাপুন **সংরক্ষণ**: পৃষ্ঠাটি নতুন পাঠ্যের সাথে ফিরে আসে। **মুছুন** টিপুন: আপনি নোট ছাড়াই তালিকায় অবতরণ করেন।

## আপনি যা শিখেছেন

- একটি পৃষ্ঠা বিভিন্ন ফর্ম ধারণ করতে পারে, প্রতিটি তার নিজস্ব অ্যাকশনে পোস্ট করে।
- একটি লুকানো ক্ষেত্র আইডি বহন করে; এর নাম হল অ্যাকশনের প্যারামিটার নাম।
- দুটি ক্রিয়া দ্বারা ভাগ করা নিয়মগুলি একটি ফাংশনে থাকে, যা উভয় দ্বারা বলা হয়।

## পরবর্তী পদক্ষেপ

- [পার্ট 9: নোটগুলিকে পৃষ্ঠায় স্থান দিন](paginate-the-notes.md)
- [ফর্ম ছাড়া JavaScript](../guides/actions.md#forms-without-javascript): কিভাবে একটি ফর্ম একটি অ্যাকশনে পৌঁছায়
