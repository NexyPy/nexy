# Nexy, পার্ট 4: উপাদানগুলির সাথে একটি নোট অ্যাপ তৈরি করুন

পার্ট 4 প্রতিটি নোটকে একটি পুনঃব্যবহারযোগ্য উপাদানে পরিণত করে, একটি `.nexy` ফাইল যা আপনি একটি Python নামের মতো আমদানি করেন এবং একটি HTML ট্যাগের মতো ব্যবহার করেন৷

**আপনি শুরু করার আগে:** [পার্ট 3](dynamic-routes.md) এর অ্যাপ।

## উপাদান লিখুন

একটি উপাদান হল রুটের বাইরের একটি `.nexy` ফাইল। এর প্রপগুলি `prop[...]` দিয়ে ঘোষণা করা হয়, এবং কলকারী এগুলিকে বৈশিষ্ট্য হিসাবে প্রেরণ করে:

```nexy filename="src/components/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
---
<article class="note">
  <a href="/notes/{{ id }}">{{ text }}</a>
</article>

<style>
  .note { padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
</style>
```

কার্ড ব্যবহার করে এমন প্রতিটি পৃষ্ঠার সাথে `<style>` ব্লক পাঠানো হয়। এটির ব্যাপ্তি নেই: `.note` পুরো পৃষ্ঠার জন্য একটি ক্লাস, তাই শুধুমাত্র এটি ব্যবহার করে এমন একটি উপাদানের নামের ক্লাস দিন।

## তালিকায় এটি ব্যবহার করুন

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

`@/` হল পার্ট 1 এর ইম্পোর্ট উপনাম: এটি `src/` নির্দেশ করে। ফাইলের নাম হল উপাদানের নাম, PascalCase এ: `NoteCard.nexy` রপ্তানি করে `NoteCard`।

খুলুন <http://localhost:3000/notes>: প্রতিটি নোট এখন একটি কার্ড।

## আপনি যা শিখেছেন

- রুটগুলির বাইরে একটি `.nexy` ফাইল একটি উপাদান; এর `prop[...]` গুণাবলী।
- `from "@/components/x.nexy" import X` এটি আমদানি করে; `<X />` এটি রেন্ডার করে।
- একটি `<style>` ব্লক স্কোপ করা হয় না: এটির পরে একটি উপাদানের ক্লাসের নাম দিন।

## পরবর্তী পদক্ষেপ

- [পার্ট 5: নোটগুলি SQLite](store-the-notes.md) এ সংরক্ষণ করুন
- [উপাদান ](../views/nexy/components.md): `Image`, `Link` এবং অন্তর্নির্মিত সাহায্যকারী
