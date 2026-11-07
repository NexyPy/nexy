# Nexy এর সাথে একটি নোট অ্যাপ তৈরি করুন, পার্ট 5: নোটগুলি SQLite এ সংরক্ষণ করুন

পার্ট 5 একটি Python অভিধান থেকে নোটগুলিকে একটি SQLite ডাটাবেসে নিয়ে যায়, যেখানে একটি মডেল, একটি মাইগ্রেশন এবং দুটি নোট দিয়ে শুরু হয় এবং পৃষ্ঠাগুলি সেখান থেকে সেগুলি পড়ে।

**আপনি শুরু করার আগে:** [পার্ট 4](components.md) এর অ্যাপ।

## ORM এবং মাইগ্রেশন টুল ইনস্টল করুন

```bash
uv add sqlmodel alembic
```

[SQLModel](https://sqlmodel.tiangolo.com/) একটি টেবিলকে Python শ্রেণী হিসেবে বর্ণনা করে এবং Alembic সেই শ্রেণির পরিবর্তনগুলিকে মাইগ্রেশনে পরিণত করে। Nexy হয় মোড়ানো হয় না: আপনি তাদের যেমন আছে ব্যবহার করুন.

## ডাটাবেস খুলুন

ডাটাবেসের ঠিকানা `.env` প্রকল্পের মূলে যায়। `nx migrate` এবং অ্যাপ উভয়ই সেখান থেকে এটি পড়ে:

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

`sqlite:///dev.db` হল একটি ফাইল, `dev.db`, `nexyconfig.py` এর পাশে: SQLite সার্ভারের প্রয়োজন নেই। `.env` কে গিট থেকে দূরে রাখুন: এটি একটি বাস্তব ডাটাবেসের গোপনীয়তা ধারণ করে।

ইঞ্জিন হল ডাটাবেসের সংযোগ। এটি পড়ে `DATABASE_URL`, যখন ভেরিয়েবলটি আনসেট থাকে তখন ডিফল্ট হিসাবে একই ফাইলের সাথে:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///dev.db"))
```

## একটি নোট বর্ণনা করুন

<!-- router:fbr,custom -->
```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

<!-- router:modular -->
মডেলটি তার কন্ট্রোলারের পাশে যে বৈশিষ্ট্যটির সাথে সম্পর্কিত তা নিয়ে বেঁচে থাকে:

```python filename="src/apps/notes/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

`table=True` ক্লাসকে একটি টেবিল তৈরি করে, `note`। একটি নোট সংরক্ষণ করা হলে ডাটাবেস দ্বারা `id` দেওয়া হয়।

## একটি মাইগ্রেশন দিয়ে টেবিল তৈরি করুন

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` `alembic/` ফোল্ডারটি লেখে এবং এটিকে আপনার মডেলের দিকে নির্দেশ করে। `-m` মডেলটিকে ডাটাবেসের সাথে তুলনা করে এবং লেখে যে মাইগ্রেশনটি টেবিল তৈরি করে; `--upgrade` এটি চালায়। পরে মডেলটি পরিবর্তন করুন, শেষ দুটি কমান্ড আবার চালান এবং টেবিলটি অনুসরণ করে।

## ডাটাবেস থেকে নোট পড়ুন

`src/notes.py` এর ফাংশনগুলি তাদের নাম রাখে, তাই পৃষ্ঠাগুলি সামান্য পরিবর্তন করে: তারা এখন একটি সেশন খোলে, টেবিলটি জিজ্ঞাসা করে এবং স্ট্রিংয়ের পরিবর্তে `Note` অবজেক্টগুলি ফেরত দেয়।

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
```
<!-- /router -->

## শুরু করতে দুটি নোট যোগ করুন

একটি বীজ স্ক্রিপ্ট একটি খালি ডাটাবেস পূরণ করে, তাই প্রকল্পের প্রতিটি নতুন অনুলিপি দেখানোর জন্য কিছু দিয়ে শুরু হয়:

<!-- router:fbr,custom -->
```python filename="src/seed.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def seed() -> None:
    with Session(engine) as session:
        if session.exec(select(Note)).first() is None:
            session.add_all([Note(text="Buy milk"), Note(text="Ship Nexy")])
            session.commit()


if __name__ == "__main__":
    seed()
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/seed.py"
from sqlmodel import Session, select

from src.apps.notes.note_model import Note
from src.configs.db import engine


def seed() -> None:
    with Session(engine) as session:
        if session.exec(select(Note)).first() is None:
            session.add_all([Note(text="Buy milk"), Note(text="Ship Nexy")])
            session.commit()


if __name__ == "__main__":
    seed()
```
<!-- /router -->

```bash
python -m src.seed
```

স্টার্টআপে, Nexy [পার্ট 6](create-a-note.md) এর অ্যাকশন খুঁজে পেতে `src/` এর প্রতিটি মডিউল আমদানি করে। `if __name__ == "__main__":` উপরের কমান্ডের জন্য বীজ রাখে: অ্যাপ দ্বারা আমদানি করা, ফাইলটি শুধুমাত্র `seed` নির্ধারণ করে, এবং কিছুই স্পর্শ করে না।

## ডাটাবেস থেকে নোট দেখান

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```

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
  <h1>{{ note.text }}</h1>
  <a href="/notes">All notes</a>
</section>
```

```python filename="src/routes/api/notes.py"
from src.notes import all_notes


async def GET():
    return [note.model_dump() for note in all_notes()]
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
  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
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
        return page("src/apps/notes/note_view.nexy", text=note.text)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        return [note.model_dump() for note in all_notes()]
```
<!-- /router -->

খুলুন <http://localhost:3000/notes>: একই দুটি কার্ড, এখন `dev.db` থেকে পড়ুন। পুনরায় চালু করুন `nexy dev`, এবং তারা এখনও সেখানে আছে।

## আপনি যা শিখেছেন

- SQLModel একটি টেবিলকে ক্লাস হিসাবে বর্ণনা করে; `src/configs/db.py` এর ইঞ্জিন ডাটাবেস খোলে।
- `nx migrate` লেখেন এবং মাইগ্রেশন চালান: `--init` একবার, তারপর `-m` এবং `--upgrade` প্রতি পরিবর্তন।
- পেজ এবং কন্ট্রোলার প্লেইন Python ফাংশনকে কল করে যা ডাটাবেসকে জিজ্ঞাসা করে: Nexy কোনো স্তর যোগ করে না।

## পরবর্তী পদক্ষেপ

- [পার্ট 6: একটি ফর্ম থেকে একটি নোট তৈরি করুন](create-a-note.md)
- [SQLite](../databases/sqlite.md): প্রাগমাস, অ্যাসিঙ্ক অ্যাক্সেস এবং ইন-মেমরি ডাটাবেসের পরীক্ষা
