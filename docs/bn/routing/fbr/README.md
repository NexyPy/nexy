# ফাইল-ভিত্তিক রাউটিং

একটি রুট একটি ফাইল. URL হল ফাইলের পাথ `src/routes/`, বিয়োগ এক্সটেনশনের সাপেক্ষে।

## ইউআরএলে ফাইল করুন

| ফাইল | URL |
|---|---|
| `index.nexy` | `/` |
| `about.nexy` | `/about` |
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/{slug}` |
| `docs/[...path].nexy` | `/docs/{path:path}` |
| `(marketing)/pricing.nexy` | `/pricing` |
| `api/users.py` | `/api/users` |

`index` এর ডিরেক্টরিতে মানচিত্র, `/index` নয়। বন্ধনীতে একটি ডিরেক্টরি হল একটি **গ্রুপ**: এটি URL-এ উপস্থিত না হয়েই ফাইলগুলিকে সংগঠিত করে।

ক্লায়েন্ট মোডে পৃষ্ঠা ফাইলগুলি `.nexy` এর পরিবর্তে `.tsx`, `.vue` বা `.svelte` হয়; URL নিয়ম একই.

সেই টেবিলের দুটি ফাইল: একটি পৃষ্ঠা যা এর সেগমেন্টটি পড়ে এবং একটি হ্যান্ডলার যা JSON এর উত্তর দেয়।

```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str]
---
<h1>{{ slug }}</h1>
```

```python filename="src/routes/api/users.py"
async def GET():
    return {"users": []}
```

## দুটি মোড

`useCSR` পৃষ্ঠাগুলি কী তা নির্ধারণ করে। দুটি একটি প্রকল্পে মিশ্রিত করা যাবে না: যখন একটি সার্ভার পৃষ্ঠা একটি ক্লায়েন্ট রুটের পাশে বসে তখন Nexy শুরু করতে অস্বীকার করে।

| মোড | পাতা | রুট লেআউট | দেখুন |
|---|---|---|---|
| সার্ভার (`useCSR = False`) | `.nexy`, `.md`, `.mdx` | `layout.nexy` | [সার্ভার মোড এবং ক্লায়েন্ট মোড](modes.md) |
| ক্লায়েন্ট (`useCSR = True`) | ফ্রেমওয়ার্ক ফাইল | `layout.tsx` | [layout.tsx](../../views/react/differences.md) |

`.py` ফাইল উভয় মোডে API হ্যান্ডলার।

সুইচ হল একটি লাইন `nexyconfig.py`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True  # client mode: src/routes/*.tsx are the pages
```

## কি একটি রুট না

- সংরক্ষিত ফাইলের নাম: `layout.*`, `loading.nexy`, `errors.nexy`, `notfound.nexy`, `dependencies.py`, `middleware.py`, `__init__.py`।
- `_` বা `.` দিয়ে শুরু হওয়া ফাইল এবং ফোল্ডার: আংশিক এবং খসড়ার জন্য ব্যবহার করুন।
- আপনার প্রকল্পের জন্য সক্রিয় নয় যে এক্সটেনশন. একটি ফাইল যার এক্সটেনশন নিষ্ক্রিয় আছে একটি সতর্কতা সহ বাদ দেওয়া হয়৷

```text
src/routes/
├─ layout.nexy          wraps the pages, not a route
├─ middleware.py        wraps the requests, not a route
├─ index.nexy           /
├─ _card.nexy           a partial: no URL
└─ .draft.nexy          a draft: no URL
```

## URL প্রতি একটি ফাইল

একই ইউআরএলে সমাধান করা দুটি ফাইল উভয় নিবন্ধন করে। `blog/index.nexy` এর পাশে `blog.nexy` তৈরি করবেন না, এবং একই পথের জন্য `index.nexy` এবং `index.py` মিশ্রিত করবেন না। একটা বেছে নিন।

```text
src/routes/
├─ blog.nexy            /blog
└─ blog/
   └─ index.nexy        /blog as well: delete one of the two
```

## এই বিভাগে

| ফোল্ডার | এটা কভার কি |
|---|---|
| [পৃষ্ঠাগুলি/](pages/README.md) | পৃষ্ঠা, [গতিশীল রুট](pages/dynamic-routes.md), রুট গ্রুপ |
| [বিন্যাস/](layouts/README.md) | লেআউট ফাইল টাইপ প্রতি এক পৃষ্ঠা |
| [হ্যান্ডলার/](handlers/README.md) | `.py` হ্যান্ডলার, বৈধতা এবং ত্রুটি |
| [নির্ভরতা/](dependencies/README.md) | `dependencies.py`, প্রহরী |
| [মিডলওয়্যার/](middleware/README.md) | `middleware.py` |
| [ত্রুটি/](errors/README.md) | পাওয়া যায়নি এবং ত্রুটি পৃষ্ঠা |
| [নেভিগেশন/](navigation/linking-and-navigating.md) | লিঙ্ক, হুক |
| [বাস্তব সময়/](realtime/websocket.md) | WebSocket |
| [উত্তরাধিকার ](inheritance.md) | এক টেবিলে উত্তরাধিকার নিয়ম |

## পরবর্তী পদক্ষেপ

- [সার্ভার মোড এবং ক্লায়েন্ট মোড](modes.md)
- [বিন্যাস](layouts/README.md)
- [মডুলার রাউটিং](../modular/README.md)
