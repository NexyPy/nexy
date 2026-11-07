# Nexy এর সাথে একটি নোট অ্যাপ তৈরি করুন, পার্ট 13: আপনি টাইপ করার সাথে সাথে নোটগুলি অনুসন্ধান করুন৷

পার্ট 13 নোটগুলির উপরে একটি অনুসন্ধান বাক্স যুক্ত করেছে: একটি React দ্বীপ ব্যবহারকারীর প্রতিটি নোটকে ফিল্টার করে প্রতিটি কী প্রেসে, ব্রাউজারে, সার্ভারের কাছে কোনো অনুরোধ ছাড়াই।

**আপনি শুরু করার আগে:** [পার্ট 12](password-reset.md) এর অ্যাপ। প্রকল্পটি React দিয়ে [পার্ট 1](create-the-project.md)-এ তৈরি করা হয়েছিল, তাই React ইতিমধ্যেই ইনস্টল করা আছে।

## একটি দ্বীপ, এবং কেন এখানে

পৃষ্ঠার বাকি অংশটি সার্ভার দ্বারা রেন্ডার করা HTML থাকে: তালিকা, ফর্ম, নোটের পৃষ্ঠা। শুধুমাত্র সার্চ বক্সে ব্রাউজার প্রয়োজন, তাই শুধুমাত্র সার্চ বক্স হল React। এটি একটি *দ্বীপ*: একটি সার্ভার পৃষ্ঠার মধ্যে একটি ক্লায়েন্ট উপাদান, এটি নিজে থেকেই ইন্টারেক্টিভ করে।

## অনুসন্ধান উপাদান

```tsx filename="src/components/NoteSearch.tsx"
import { useState } from "react"

type Note = { id: number; text: string }

export default function NoteSearch({ notes }: { notes: Note[] }) {
  const [query, setQuery] = useState("")
  const words = query.trim().toLowerCase()
  const found = words ? notes.filter((note) => note.text.toLowerCase().includes(words)) : []
  return (
    <section className="note-search" aria-label="Search the notes">
      <label>
        Search
        <input type="search" value={query} onChange={(event) => setQuery(event.target.value)} />
      </label>
      <div aria-live="polite">
        {words && found.length === 0 && <p>No note matches “{query}”.</p>}
        {found.length > 0 && (
          <ul>
            {found.map((note) => (
              <li key={note.id}>
                <a href={`/notes/${note.id}`}>{note.text}</a>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
```

React টেক্সট হিসাবে `{note.text}` লিখেছেন: একটি নোট `<b>x</b>` এর বন্ধনী দেখায়, যোগ করার জন্য কোন `| e` নেই।

`found` শুধুমাত্র একবার কিছু টাইপ করার পরে গণনা করা হয়, এবং এটি বিল্ডের জন্য গুরুত্বপূর্ণ: `nx build` প্রতিটি দ্বীপকে একবার HTML-এ রেন্ডার করে, এর প্রপসের পরিবর্তে স্থানধারক সহ। একটি কম্পোনেন্ট যেটি প্রথম রেন্ডারের সময় একটি তালিকা প্রপ পড়ে তা একটি তালিকার পরিবর্তে একটি স্থানধারক পায় এবং এইচটিএমএল পাঠায় না। এটি একটি কী চাপার পরেই `notes` পড়ে, তাই বিল্ডটি তার অনুসন্ধান বাক্সটি রেন্ডার করে এবং যে কোনও JavaScript রান হওয়ার আগে পৃষ্ঠাটি এটি দেখায়।

`aria-live="polite"` একটি স্ক্রিন রিডারকে ফলাফলগুলিকে পড়তে বাধ্য করে যখন তারা পরিবর্তন করে, কোনো বাধা ছাড়াই।

## পাতায় দ্বীপ রাখুন

পৃষ্ঠাটি একটি প্রপ হিসাবে নোটগুলি পাস করে: অভিধানগুলির একটি তালিকা, যা Nexy ব্রাউজারের জন্য JSON-এ পরিণত হয়৷ প্রতিটি নোট যায়, শুধুমাত্র বর্তমান পৃষ্ঠার পাঁচটি নয়, তাই অনুসন্ধানটি সেগুলিকে কভার করে:

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
<!-- /router -->

`from "@/components/NoteSearch.tsx" import NoteSearch` একটি React উপাদান একটি `.nexy` পৃষ্ঠায় আমদানি করে; ট্যাগ প্রপস হিসাবে তার বৈশিষ্ট্যগুলি পাস করে। `notes="{{ searchable }}"` একটি স্ট্রিং নয়, Python তালিকাটি নিজেই পাস করে। `directive="client:idle"` ব্রাউজারটির আর জরুরী কিছু করার না থাকলে দ্বীপটিকে ইন্টারেক্টিভ করে তোলে।

খুলুন <http://localhost:3000/notes> এবং একটি নোটের কয়েকটি অক্ষর টাইপ করুন: ম্যাচিং নোটগুলি প্রতিটি কী চাপলে বাক্সের নীচে প্রদর্শিত হয়। বাক্সটি সাফ করুন, এবং ফলাফল চলে যাবে।

> [!NOTE]
> পৃষ্ঠায় একটি দ্বীপ ভ্রমণের প্রপস, JSON হিসাবে। প্রতিটি নোট পাঠানো তাদের কয়েক শত স্যুট; হাজার হাজারের জন্য, সার্ভারে অনুসন্ধান করুন, একটি প্রশ্ন এবং একটি `LIKE` ফিল্টার সহ।

## আপনি যা শিখেছেন

- একটি দ্বীপ একটি সার্ভার পৃষ্ঠার ভিতরে একটি ক্লায়েন্ট উপাদান: এখানে, শুধুমাত্র অনুসন্ধান বাক্সের জন্য React।
- একটি `.nexy` পৃষ্ঠা এটিকে পাথ দ্বারা আমদানি করে এবং প্রপস হিসাবে Python মানগুলিকে JSON-এ সিরিয়ালাইজ করে পাস করে।
- বিল্ডটি একটি দ্বীপকে একবার রেন্ডার করে, এর প্রপসের জন্য স্থানধারক সহ: প্রথম রেন্ডারের পরে তালিকা প্রপস পড়ুন এবং দ্বীপটি HTML পাঠায়।

## পরবর্তী পদক্ষেপ

- [পার্ট 14: পৃষ্ঠা পুনরায় লোড না করে একটি নোটে টিক দিন](tick-a-note.md)
- [দ্বীপপুঞ্জ এবং হাইড্রেশন ](../rendering/islands.md): নির্দেশাবলী, প্রপস এবং সীমাবদ্ধতা
