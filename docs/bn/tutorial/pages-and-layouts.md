# Nexy, পার্ট 2: পৃষ্ঠা এবং লেআউট দিয়ে একটি নোট অ্যাপ তৈরি করুন

পার্ট 2 সেই পৃষ্ঠাটি যোগ করে যা নোটগুলি তালিকাভুক্ত করে, এবং লেআউটটি HTML নথিতে এটিকে কীভাবে মোড়ানো হয় তা দেখায়।

**আপনি শুরু করার আগে:** [পার্ট 1](create-the-project.md) এর প্রকল্প, `nexy dev` চলমান।

## নোট পৃষ্ঠা যোগ করুন

<!-- router:fbr,custom -->
একটি পৃষ্ঠা হল `src/routes/` এর অধীনে একটি ফাইল, এবং এর পাথ হল এর URL। নোট পৃষ্ঠা তৈরি করুন:

```nexy filename="src/routes/notes/index.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

`notes/index.nexy` উত্তর `/notes`।
<!-- /router -->

<!-- router:modular -->
একটি নিয়ামক একটি URL এর উত্তর দেয় এবং একটি দৃশ্য প্রদান করে। একটি ভিউ সহ নোটগুলিকে তাদের নিজস্ব ফোল্ডার দিন:

```nexy filename="src/apps/notes/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

এবং কন্ট্রোলার যে এটি রেন্ডার করে `/notes`:

```python filename="src/apps/notes/notes_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/notes/notes_view.nexy")})
```

একটি নিয়ামক শুধুমাত্র একবার একটি মডিউল এটি তালিকাভুক্ত করে উত্তর দেয়। রুট মডিউলে এটি যোগ করুন:

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController]
```
<!-- /router -->

খুলুন <http://localhost:3000/notes>: আপনি দুটি বুলেট দেখতে হবে. দুটি `---` লাইনের মধ্যবর্তী অংশটি হল Python, সার্ভারে চালানো; বাকিটা হল Jinja2 ট্যাগ সহ `{% for %}` এবং `{{ note }}`।

## লেআউট পরিবর্তন করুন

<!-- router:fbr,custom -->
`src/routes/layout.nexy` HTML নথির মালিক: `<html>`, `<head>` এবং `<body>`। Nexy এটির প্রতিটি পৃষ্ঠা মুড়ে দেয়, যেখানে এটি `{{children | safe}}` লিখে।
<!-- /router -->
<!-- router:modular -->
`src/apps/layout.nexy` HTML নথির মালিক: `<html>`, `<head>` এবং `<body>`। কন্ট্রোলার ভিউটিকে `children` হিসাবে পাস করে এটিতে তার দৃষ্টিভঙ্গি আবৃত করে।
<!-- /router -->

লেআউটটি খুলুন এবং লাইনটি `<title>Nexy App</title>` এতে পরিবর্তন করুন:

```html
<title>Notes</title>
```

সংরক্ষণ করুন: ব্রাউজারের ট্যাবটি এখন প্রতিটি পৃষ্ঠায় *নোট* পড়ে।

## হেডারের নিচে পেজ রুম দিন

লেআউটের শিরোনামটি স্থির করা হয়েছে: এটি পৃষ্ঠার উপরে, উইন্ডোর শীর্ষে থাকে। স্টার্টারের পৃষ্ঠাগুলি এটির নীচে তাদের নিজস্ব স্থান সেট করে; নোট অ্যাপের পৃষ্ঠাগুলি এর জন্য একটি ক্লাস ভাগ করে, `app-page`, যা টিউটোরিয়ালের প্রতিটি পৃষ্ঠা তার বিষয়বস্তুর চারপাশে রাখে। এটি `src/globale.css` এর শেষে যোগ করুন, স্টাইলশীট প্রতিটি পৃষ্ঠা ইতিমধ্যে লোড হয়:

```css
/* The pages of the notes app: one readable column below the fixed header. */
.app-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 42rem;
  margin: 0 auto;
  padding: 8rem 1.5rem 5rem;
}

.app-page h1 {
  font-size: 2rem;
}

.app-page form {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  gap: 0.5rem;
}

.app-page label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.app-page input:not([type="hidden"]) {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-second);
  border-radius: 0.375rem;
  background: var(--background);
}

.app-page button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  background: var(--foreground);
  color: var(--background);
  cursor: pointer;
}

.app-page a {
  text-decoration: underline;
}
```

Tailwind, যা স্টার্টার ব্যবহার করে, ফর্ম ফিল্ডের সীমানা সরিয়ে দেয়: এই নিয়মগুলি তাদের ফিরিয়ে দেয়, যাতে পরবর্তী অংশগুলির ফর্মগুলি দেখা যায়।

## আপনি যা শিখেছেন

<!-- router:fbr,custom -->
- একটি `.nexy` ফাইল `src/routes/` এর অধীনে একটি পৃষ্ঠা; এর ফোল্ডার এবং নাম এর URL।
- রুট `layout.nexy` এইচটিএমএল ডকুমেন্টের প্রতিটি পৃষ্ঠাকে মুড়ে দেয়।
<!-- /router -->
<!-- router:modular -->
- একটি নিয়ামক একটি URL এর উত্তর দেয় এবং `useViews` এর সাথে একটি `.nexy` ভিউ রেন্ডার করে; একটি মডিউল এটি তালিকাভুক্ত করে।
- বিন্যাসটিও একটি দৃশ্য: নিয়ামক এটিকে `children` হিসাবে পৃষ্ঠা দৃশ্যটি পাস করে।
<!-- /router -->
- একটি `.nexy` ফাইল `---` এর মধ্যে Python, তারপর Jinja2 সহ HTML।
- `src/globale.css` প্রতিটি পৃষ্ঠা শেয়ার করা শৈলী ধারণ করে, যেমন `app-page`।

## পরবর্তী পদক্ষেপ

- [পার্ট 3: গতিশীল রুট এবং একটি API](dynamic-routes.md)
- [.nexy ফাইল](../views/nexy/README.md): প্রপস, উপাদান এবং শৈলী
