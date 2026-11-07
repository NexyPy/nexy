# Nexy দিয়ে একটি নোট অ্যাপ তৈরি করুন, পার্ট 6: একটি ফর্ম থেকে একটি নোট তৈরি করুন

পার্ট 6 তালিকার উপরে একটি ফর্ম যোগ করে: এটি একটি Python চিহ্নিত ফাংশনে পোস্ট করে `@Action`, যা নোটটি সংরক্ষণ করে এবং দর্শক নতুন নোটের সাথে তালিকায় ফিরে আসে।

**আপনি শুরু করার আগে:** [পার্ট 5](store-the-notes.md) এর অ্যাপ, এর ডাটাবেস সহ।

## একটি নোট সংরক্ষণ করুন

একটি ফাংশন যোগ করুন যা একটি নোট সংরক্ষণ করে এবং এটিকে ফেরত দেয়, দুটির পাশে যা সেগুলি পড়ে:

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

## এটিকে একটি অ্যাকশনে পরিণত করুন

একটি অ্যাকশন হল একটি Python ফাংশন যা ব্রাউজার কল করতে পারে। `@Action` এটি একটি `POST` হিসাবে পরিবেশন করে, টাইপ ইঙ্গিতগুলির বিরুদ্ধে ইনপুট পরীক্ষা করে এবং এটি চালায়:

```python filename="src/actions/notes.py"
from nexy.decorators import Action
from src.notes import add_note


@Action
async def create_note(text: str) -> int:
    return add_note(text).id
```

স্টার্টআপে, Nexy `src/`-এর প্রতিটি মডিউল আমদানি করে এবং এটি খুঁজে পাওয়া অ্যাকশনগুলি পরিবেশন করে: কোনও রাউটারের জন্য ঘোষণা করার কোনও রুট নেই। `src/actions/` যেখানে এই টিউটোরিয়াল তাদের রাখে।

## এটিতে ফর্মটি পোস্ট করুন

একটি `.nexy` টেমপ্লেট প্রতিটি কর্মের পথ `__actions_path["name"]` হিসাবে জানে। একটি সাধারণ HTML ফর্ম সেখানে পোস্ট করে, তাই কোনো স্ক্রিপ্ট লোড হওয়ার আগে পৃষ্ঠাটি কাজ করে:

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

ইনপুটটির নামকরণ করা হয়েছে `text`, `create_note`-এর প্যারামিটারের মতো: এইভাবে ক্ষেত্রটি এটিতে পৌঁছায়।

## একটি নোটকে পাঠ্য হিসাবে দেখান, HTML হিসাবে নয়

এখন থেকে, একটি নোট যা একজন দর্শক টাইপ করেছেন। একটি `.nexy` টেমপ্লেট যেমন আছে তেমন একটি মান লিখে, তাই একটি নোট `<script>…</script>` যারা তালিকাটি খুলবে তাদের ব্রাউজারে চলবে। `| e` এটি এড়িয়ে যায়: `<` হয়ে যায় `&lt;`, এবং নোটটি পাঠ্য হিসাবে দেখায়।

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

ভিজিটর বা ডাটাবেস থেকে আসা প্রতিটি মান এড়িয়ে যান। `| safe` বিপরীতটি করে: আপনি নিজের লেখা HTML এর জন্য এটি রাখুন।

## চেষ্টা করে দেখুন

*ডক্স পড়ুন* টাইপ করুন এবং **যোগ করুন** টিপুন। অ্যাকশন নোটটিকে সেভ করে, তারপর উত্তর দেয় `303` `/notes`-এ, এবং ব্রাউজার আবার তালিকাটি দেখায়, নীচে তৃতীয় নোটটি রয়েছে।

## আপনি যা শিখেছেন

- `@Action` একটি Python ফাংশনকে `POST` এন্ডপয়েন্টে পরিণত করে, ইনপুট হিসাবে এর টাইপ ইঙ্গিত সহ।
- একটি ফর্ম এটিতে `__actions_path["name"]` এর মাধ্যমে পোস্ট করে, কোন JavaScript ছাড়াই, এবং `303` দিয়ে ফিরে আসে।
- ফর্মের ক্ষেত্রের নামগুলি অ্যাকশনের প্যারামিটারের নাম।
- `| e` একজন দর্শক পাঠ্য হিসাবে কী টাইপ করেছেন তা দেখায়: আপনার কাছ থেকে আসেনি এমন প্রতিটি মান এড়িয়ে যান।

## পরবর্তী পদক্ষেপ

- [পার্ট 7: বৈধতা ত্রুটি দেখান](validation-errors.md)
- [অ্যাকশন ](../guides/actions.md): ব্রাউজার থেকে টাইপ করা কল, ত্রুটি এবং নিরাপত্তা
