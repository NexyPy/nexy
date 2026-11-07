# Nexy, পার্ট 3: ডাইনামিক রুট এবং একটি API দিয়ে একটি নোট অ্যাপ তৈরি করুন

পার্ট 3 প্রতিটি নোটের নিজস্ব URL দেয়, `/notes/1`, এবং JSON-এর মতো একই নোটগুলি `/api/notes`-এ পরিবেশন করে, উভয়ই একটি Python মডিউল থেকে পড়া হয়।

**আপনি শুরু করার আগে:** [পার্ট 2](pages-and-layouts.md) এর অ্যাপ।

## নোটগুলিকে একটি মডিউলে রাখুন

পৃষ্ঠা এবং API একই তালিকা পড়বে। এটিকে নিজস্ব একটি মডিউলে নিয়ে যান, একটি ফাংশন সহ যা একটি নোট খুঁজে পায়:

```python filename="src/notes.py"
NOTES = {1: "Buy milk", 2: "Ship Nexy"}


def find(note_id: int) -> str | None:
    return NOTES.get(note_id)
```

## প্রতিটি নোটকে তার পৃষ্ঠায় লিঙ্ক করুন

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for id, text in notes %}
    <li><a href="/notes/{{ id }}">{{ text }}</a></li>
    {% endfor %}
  </ul>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for id, text in notes %}
    <li><a href="/notes/{{ id }}">{{ text }}</a></li>
    {% endfor %}
  </ul>
</section>
```
<!-- /router -->

## নোট প্রতি একটি পৃষ্ঠা যোগ করুন

<!-- router:fbr,custom -->
বন্ধনীতে একটি ফোল্ডার বা ফাইলের নাম হল URL এর একটি সেগমেন্ট: `[id].nexy` উত্তর দেয় `/notes/1`, `/notes/2`, এবং একটি প্রপ হিসাবে সেগমেন্টটিকে পৃষ্ঠায় প্রেরণ করে। `id: prop[int]` এটিকে একটি সংখ্যায় পরিণত করে, তাই `/notes/abc` পৃষ্ঠাটি চলার আগে `404` উত্তর দেয়।

```nexy filename="src/routes/notes/[id].nexy"
---
from nexy import notFound
from src.notes import find

id: prop[int]
text = find(id)
if text is None:
    notFound()
---
<section class="app-page">
  <h1>{{ text }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

<!-- router:modular -->
একটি কন্ট্রোলারের পাথে একটি `{id}` হল URL-এর একটি সেগমেন্ট, যে নামে পদ্ধতিতে পাস করা হয়। `id: int` এটিকে একটি সংখ্যায় পরিণত করে, তাই পদ্ধতিটি চলার আগে `/notes/abc` উত্তর দেয় `404`।

```nexy filename="src/apps/notes/note_view.nexy"
---
text: prop[str]
---
<section class="app-page">
  <h1>{{ text }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

`notFound()` অনুরোধটি একটি `404` দিয়ে থামায়: একটি নোট যা বিদ্যমান নেই এমন একটি URL এর মতো উত্তর যা বিদ্যমান নেই।

## JSON হিসাবে নোট পরিবেশন করুন

<!-- router:fbr,custom -->
একটি `.py` ফাইল `src/routes/` এর অধীনে একটি API রুট। একটি HTTP পদ্ধতির নাম অনুসারে প্রতিটি ফাংশন সেই পদ্ধতির উত্তর দেয়:

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": id, "text": text} for id, text in NOTES.items()]
```
<!-- /router -->

<!-- router:modular -->
নোটের তিনটি কন্ট্রোলার, একটি ফাইলে। একটি HTTP পদ্ধতির নাম অনুসারে প্রতিটি পদ্ধতি সেই পদ্ধতির উত্তর দেয়:

```python filename="src/apps/notes/notes_controller.py"
from nexy import notFound
from nexy.decorators import Controller
from nexy.hooks import useViews
from src.notes import NOTES, find

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
        text = find(id)
        if text is None:
            notFound()
        return page("src/apps/notes/note_view.nexy", text=text)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        return [{"id": id, "text": text} for id, text in NOTES.items()]
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NoteController, NotesApiController, NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController, NoteController, NotesApiController]
```
<!-- /router -->

তিনটি URL চেক করুন:

- <http://localhost:3000/notes/1> শো *দুধ কিনুন*;
- <http://localhost:3000/notes/9> উত্তর *পৃষ্ঠা পাওয়া যায়নি*;
- `curl http://localhost:3000/api/notes` প্রিন্ট `[{"id":1,"text":"Buy milk"},{"id":2,"text":"Ship Nexy"}]`।

API এর স্কিমা সহ <http://localhost:3000/docs> এ তালিকাভুক্ত করা হয়েছে।

## আপনি যা শিখেছেন

<!-- router:fbr,custom -->
- `[id].nexy` একটি গতিশীল সেগমেন্ট; `id: prop[int]` এটি পড়ে এবং রূপান্তর করে।
- `src/routes/` এর অধীনে একটি `.py` ফাইল JSON উত্তর দেয়, প্রতি HTTP পদ্ধতিতে একটি ফাংশন।
<!-- /router -->
<!-- router:modular -->
- `{id}` একটি নিয়ামকের পথে একটি গতিশীল সেগমেন্ট; `id: int` এটিকে রূপান্তরিত করে।
- একটি নিয়ামক পদ্ধতি যা ডেটা উত্তর JSON প্রদান করে; যেটি `useViews` একটি পৃষ্ঠার উত্তর দেয়।
<!-- /router -->
- যে কোন জায়গা থেকে `notFound()` উত্তর `404`; একটি ভাগ করা মডিউল ধাপে পৃষ্ঠা এবং API রাখে।

## পরবর্তী পদক্ষেপ

- [পার্ট 4: উপাদান](components.md)
- [ব্যতিক্রম এবং ত্রুটি](../reference/exceptions.md): `notFound`, `redirect` এবং অন্যান্য প্রস্থান
