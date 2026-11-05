# সার্ভার মোড এবং ক্লায়েন্ট মোড

একটি Nexy প্রজেক্ট হয় **সার্ভার-রেন্ডার করা** অথবা **ক্লায়েন্ট-রাউটেড**, যেমন একটি Next.js প্রোজেক্ট হয় সার্ভারে রেন্ডার করা পৃষ্ঠা বা ক্লায়েন্ট অ্যাপ। `useCSR` মধ্যে `nexyconfig.py` বেছে নেয়।

## সার্ভার মোড (`useCSR = False`)

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

- পৃষ্ঠাগুলি হল `.nexy`, `.md` বা `.mdx` ফাইল `src/routes/` এর অধীনে।
- মূল `layout.nexy` মালিক `<!DOCTYPE html>`, `<html>`, `<head>` এবং `<body>`।
- ক্লায়েন্ট উপাদানগুলি (React, Vue, Svelte, Solid বা Preact) **দ্বীপ** হিসাবে অনুমোদিত: আপনি একটি `.nexy` পৃষ্ঠা থেকে একটি আমদানি করেন এবং এটি ব্রাউজারে হাইড্রেট করে। [দ্বীপগুলি](../../rendering/islands.md) দেখুন।
- একটি ক্লায়েন্ট উপাদান একটি রুট হয় না. তাদের `src/components/` মধ্যে রাখুন।
- এক সময়ে একটি ক্লায়েন্ট ফ্রেমওয়ার্ক।

```text
src/
├─ routes/
│  ├─ layout.nexy         document
│  ├─ index.nexy          page
│  └─ api/users.py        API handler
└─ components/Counter.tsx island
```

## ক্লায়েন্ট মোড (`useCSR = True`)

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

- পৃষ্ঠাগুলি হল আপনার ক্লায়েন্ট ফ্রেমওয়ার্কের ফাইল: `.tsx` React, `.vue`, `.svelte` এর জন্য।
- `.md` এবং `.mdx` ফাইলগুলি বৈধ রুটে থাকে: Nexy সেগুলিকে ক্লায়েন্ট লেআউটের ভিতরে সার্ভারে রেন্ডার করে এবং ক্লায়েন্ট রাউটার সেখান থেকে নেভিগেশন গ্রহণ করে।
- যেকোন ফ্রেমওয়ার্কের রুট লেআউট (`layout.tsx`, `layout.vue`, `layout.svelte`) এর রুট লেআউটের মতো `<!DOCTYPE html>`, `<html>`, `<head>` এবং `<body>` এর মালিক। Next.js অ্যাপ রাউটার। Nexy এটিকে প্রথম প্রতিক্রিয়ার জন্য নোডে রেন্ডার করে এবং ফ্রেমওয়ার্ক পুরো নথিটিকে হাইড্রেট করে। [layout.tsx](../../views/react/differences.md) দেখুন।
- `.py` ফাইলগুলি হল API হ্যান্ডলার যা FastAPI দ্বারা পরিবেশিত হয়, ক্লায়েন্ট রুটের পাশে।
- কোনো `.nexy` ফাইল নেই, এবং কোনো `layout.nexy` নেই।
- পৃষ্ঠাগুলির মধ্যে নেভিগেশন ব্রাউজারে ঘটে।

```text
src/routes/
├─ layout.tsx             document
├─ index.tsx              page
├─ users.tsx              page
└─ api/users.py           API handler
```

## যা প্রত্যাখ্যাত

Nexy প্রকল্পটি `nx dev`, `nx start` এবং `nx build` এর আগে পরীক্ষা করে এবং ফাইলগুলির তালিকা দিয়ে থামে:

| মোড | প্রত্যাখ্যাত | বার্তা |
|---|---|---|
| সার্ভার | `.tsx`, `.jsx`, `.vue` বা `.svelte` `src/routes/` এর অধীনে | উপাদানগুলি `src/components/` এ সরান, অথবা `useCSR = True` সেট করুন |
| ক্লায়েন্ট | `src/routes/` এর অধীনে যে কোনো `.nexy` ফাইল | ফ্রেমওয়ার্ক উপাদান হিসাবে লিখুন, অথবা সেট `useCSR = False` |
| উভয় | একাধিক ফ্রন্টএন্ড ফ্রেমওয়ার্ক `useFF` | `useFF must configure exactly one frontend framework` |
| ক্লায়েন্ট | `useRouter` (মডুলার রাউটার) | `useCSR requires file-based routing` |
| ক্লায়েন্ট | না `useFF` | `useCSR requires a client framework` |

`_` বা `.` দিয়ে শুরু হওয়া ফাইল এবং ফোল্ডার এই চেক দ্বারা উপেক্ষা করা হয়।

## কোনটা

- **বিষয়বস্তু, বিপণন, ডক্স, SEO-প্রথম সাইট**: দ্বীপের সাথে সার্ভার মোড।
- **সমৃদ্ধ ক্লায়েন্ট নেভিগেশন সহ ড্যাশবোর্ড এবং অ্যাপস**: ক্লায়েন্ট মোড।
- **উপরে একটি ক্লায়েন্ট অ্যাপ সহ একটি Python API**: ক্লায়েন্ট মোড, পৃষ্ঠাগুলির পাশে `.py` হ্যান্ডলার সহ।

## পরবর্তী পদক্ষেপ

- [লেআউট](layouts/README.md)
- [রেন্ডারিং](../../rendering/README.md)
- [কনফিগ](../../reference/config.md)
