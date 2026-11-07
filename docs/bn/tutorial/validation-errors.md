# Nexy দিয়ে একটি নোট অ্যাপ তৈরি করুন, পার্ট 7: যাচাইকরণের ত্রুটি দেখান

পার্ট 7 একটি নোট প্রত্যাখ্যান করে যা খালি বা খুব দীর্ঘ, এবং দেখায় কেন ফর্মের উপরে, একই পৃষ্ঠায়, এখনও JavaScript ছাড়াই৷

**আপনি শুরু করার আগে:** [পার্ট 6](create-a-note.md) এর অ্যাপ।

## ভুল দুই ধরনের

একটি অ্যাকশনের টাইপ ইঙ্গিত ইতিমধ্যেই একটি ভুল আকৃতি প্রত্যাখ্যান করে: `create_note` রান করার আগে `text` ক্ষেত্র উত্তর `422` ছাড়া একটি ফর্ম। মান সম্পর্কে একটি নিয়ম, যেমন "খালি নয়", অ্যাকশনে লিখতে হবে।

## অ্যাকশনে নোট চেক করুন

একটি ব্যর্থতা ভিজিটরকে URL-এ কারণ সহ তালিকায় ফেরত পাঠায়; একটি সাফল্য এটি ছাড়া তালিকায় ফিরে যায়:

```python filename="src/actions/notes.py"
from urllib.parse import urlencode

from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.notes import add_note

MAX_LENGTH = 200


def back(error: str = "") -> RedirectResponse:
    query = f"?{urlencode({'error': error})}" if error else ""
    return RedirectResponse(f"/notes{query}", status_code=303)


@Action
async def create_note(text: str) -> RedirectResponse:
    text = text.strip()
    if not text:
        return back("A note cannot be blank.")
    if len(text) > MAX_LENGTH:
        return back(f"A note is at most {MAX_LENGTH} characters.")
    add_note(text)
    return back()
```

`303` ব্রাউজারকে পরবর্তী পৃষ্ঠাটি একটি `GET` দিয়ে লোড করতে বলে, তাই একটি রিফ্রেশ ফর্মটি দ্বিতীয়বার পোস্ট করে না।

## ফর্মের উপরে কারণ দেখান

`useSearchParams()` বর্তমান অনুরোধের ক্যোয়ারী স্ট্রিং পড়ে:

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
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
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
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
</section>
```
<!-- /router -->

`| e` বার্তাটি এড়িয়ে যায়: ক্যোয়ারী স্ট্রিংটি ভিজিটরের কাছ থেকে আসে, তাই এটি কখনই পৃষ্ঠায় HTML হিসাবে লেখা হয় না। `role="alert"` একজন স্ক্রিন রিডারকে এটি ঘোষণা করে।

`required` এবং `maxlength` ব্রাউজারটিকে এটি ছেড়ে যাওয়ার আগে বেশিরভাগ ভুল বন্ধ করতে দিন। অ্যাকশন আবার চেক করে: একটি অনুরোধ আপনার ফর্ম থেকে আসতে হবে না।

তিনটি স্পেসের একটি নোট যোগ করুন: তালিকাটি ফর্মের উপরে *একটি নোট ফাঁকা হতে পারে না।* দিয়ে ফিরে আসে।

## আপনি যা শিখেছেন

- টাইপ ইঙ্গিত `422` দিয়ে একটি ভুল আকৃতি প্রত্যাখ্যান করে; মান সম্পর্কে নিয়ম অ্যাকশনে যান।
- একটি ক্রিয়া একটি `RedirectResponse` দিয়ে উত্তর দিতে পারে; `303` একটি ফর্মের পরে একটি দ্বিতীয় পোস্ট এড়িয়ে যায়।
- `useSearchParams()` ক্যোয়ারী স্ট্রিং পড়ে, এবং `| e` পরিদর্শক যা পাঠিয়েছে তা এড়িয়ে যায়।

## পরবর্তী পদক্ষেপ

- [পার্ট 8: একটি নোট সম্পাদনা করুন এবং মুছুন](edit-and-delete.md)
- [ব্যতিক্রম এবং ত্রুটি](../reference/exceptions.md): প্রতিটি স্ট্যাটাস একটি অ্যাকশন এবং একটি পৃষ্ঠা উত্তর দিতে পারে
