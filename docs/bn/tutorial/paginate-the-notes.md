# Nexy-এর সাথে একটি নোট অ্যাপ তৈরি করুন, পার্ট 9: নোটগুলিকে পৃষ্ঠায় রাখুন

পার্ট 9 এ ইউআরএলের `page` `/notes?page=2` থেকে পড়া পরবর্তী এবং পূর্ববর্তী পৃষ্ঠাগুলির লিঙ্ক সহ একটি সময়ে পাঁচটি নোট দেখায়।

**আপনি শুরু করার আগে:** [পার্ট 8](edit-and-delete.md) এর অ্যাপ।

## এক পৃষ্ঠার জন্য ডাটাবেস জিজ্ঞাসা করুন

`OFFSET` আগে পৃষ্ঠার নোট এড়িয়ে যায়, `LIMIT` পাঁচটি রাখে। পাঁচটির বেশি একের জন্য জিজ্ঞাসা করা, বিনামূল্যের জন্য, পরবর্তী পৃষ্ঠা বিদ্যমান কিনা:

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

## URL থেকে পৃষ্ঠা নম্বর পড়ুন

ক্যোয়ারী স্ট্রিং এর `page` হল ভিজিটর দ্বারা পাঠানো পাঠ্য: যেকোন কিছু যেটি ধনাত্মক সংখ্যা নয় তা প্রথম পৃষ্ঠায় ফিরে আসে, তাই `/notes?page=abc` এখনও উত্তর দেয়।

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

`rel="prev"` এবং `rel="next"` ব্রাউজার এবং সার্চ ইঞ্জিনগুলিকে বলে যে কীভাবে পৃষ্ঠাগুলি একে অপরকে অনুসরণ করে এবং `aria-label` একটি স্ক্রিন রিডারের জন্য লিঙ্কগুলির নাম দেয়৷

পাঁচটির বেশি না হওয়া পর্যন্ত নোট যোগ করুন: তালিকাটি একটি **পুরোনো** লিঙ্ক সহ পাঁচটিতে থামে। এটি `/notes?page=2` এর দিকে নিয়ে যায়, যার পিছনে একটি **নতুন** লিঙ্ক রয়েছে।

## আপনি যা শিখেছেন

- `offset` এবং `limit` একটি পৃষ্ঠা পড়ুন; আরও একটি সারি জিজ্ঞাসা করা অন্য পৃষ্ঠা অনুসরণ করে কিনা তা বলে।
- `useSearchParams()` পড়ে `?page=`; ভিজিটর থেকে একটি মান ব্যবহার করার আগে চেক করা হয়।
- `rel="prev"` এবং `rel="next"` ব্রাউজার, ক্রলার এবং স্ক্রিন রিডারগুলির জন্য পৃষ্ঠাগুলি লিঙ্ক করে।

## পরবর্তী পদক্ষেপ

- [ইউনিট 3, পার্ট 10: একটি অ্যাকাউন্ট তৈরি করুন এবং সাইন ইন করুন](accounts.md)
- [SQLite](../databases/sqlite.md): ইন-মেমরি ডাটাবেসের উপর সূচী, প্রাগমাস এবং পরীক্ষা
