# উপাদান

Nexy সাহায্যকারীর একটি ছোট সেট রপ্তানি করে যা HTML স্ট্রিং ফেরত দেয়। প্রতিটি একটি `.nexy` টেমপ্লেটে দুটি উপায়ে ব্যবহৃত হয়: একটি Jinja কল হিসাবে, অথবা একটি HTML-স্টাইল ট্যাগ হিসাবে।

## দুটি সিনট্যাক্স, একটি ফাংশন

```nexy filename="src/routes/index.nexy"
---
from nexy import Audio
---
{{ Audio("/theme.mp3", controls=True) }}

<Audio src="/theme.mp3" controls=True />
```

উভয় লাইন একই মার্কআপ উত্পাদন করে:

```html
<audio preload="metadata" controls><source src="/theme.mp3" type="audio/mp3" /></audio>
```

কম্পাইলার `<Audio ... />` থেকে `{{ Audio(...) }}` পুনঃলিখন করে, তাই ট্যাগ ফর্মটি দ্বিতীয় API নয়: বৈশিষ্ট্য হল ফাংশনের কীওয়ার্ড আর্গুমেন্ট।

## ট্যাগ ফর্মের নিয়ম

| ট্যাগে | হয়ে যায় |
|---|---|
| `<Audio src="/a.mp3" />` | `Audio(src="/a.mp3")` |
| `controls=True` | `controls=True`, একটি বাস্তব বুলিয়ান |
| `width=640` | `width=640`, একটি সংখ্যা |
| `src="{{ url }}"` | `src=(url)`, Jinja | এ মূল্যায়ন করা হয়েছে
| অন্য কোনো `value` | `"value"`, একটি স্ট্রিং |

- ট্যাগটি একটি বড় হাতের অক্ষর দিয়ে শুরু হতে হবে এবং ফ্রন্ট ম্যাটারে আমদানি করতে হবে; অন্যথায় কম্পাইলার উত্থাপন করে `Missing Import: <Name> used but not declared.`
- ট্যাগ ফর্ম হল **সেলফ-ক্লোজিং**। `<Audio src="/a.mp3" />` এবং `{{ Audio("/a.mp3") }}` সমতুল্য; একটি হেল্পার ট্যাগের ভিতরে শিশুদের লেখা সমর্থিত নয়।
- একটি বেয়ার HTML অ্যাট্রিবিউট এখানে বুলিয়ান নয়: `controls` হয়ে যায় `controls=""`, যা মিথ্যা। লেখ `controls=True`।

> [!NOTE]
> `class_name` হল CSS ক্লাসের নথিভুক্ত কীওয়ার্ড। অতিরিক্ত কীওয়ার্ড আর্গুমেন্ট HTML এট্রিবিউটে পরিণত হয়, তাই `class="nav"` ও আউটপুটে পৌঁছায়।

## ছবি

```nexy
---
from nexy import Image
---
{{ Image("/logo.png", alt="Logo", width=128, height=32) }}

<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

`Image(src, alt="", width=None, height=None, loading="lazy", class_name=None, **attrs)` ডিফল্টরূপে অলস লোডিং সহ একটি `<img>` রেন্ডার করে।

## লিঙ্ক

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` ক্লায়েন্ট রাউটার দ্বারা পরিচালিত একটি `<a data-nexy-link>` রেন্ডার করে। `prefetch=True` এর সাথে, লিঙ্কটিকে ঘোরা বা স্পর্শ করা `window.__nexy_prefetch` এর মাধ্যমে লক্ষ্যকে উষ্ণ করে।

> [!NOTE]
> ট্যাগ ফর্মটি লেবেলটিকে `children` হিসাবে নেয়, উপাদান সামগ্রী হিসাবে নয়: `<Link href="/about" children="About" />`। একটি লিঙ্কের ভিতরে মার্কআপ রাখতে, `children=` অথবা একটি `.nexy` উপাদান যা একটি `<Slot />` রেন্ডার করে তার সাথে কল ফর্মটি ব্যবহার করুন।

## অডিও এবং ভিডিও

```nexy
---
from nexy import Audio, Video
---
{{ Audio("/theme.mp3", controls=True) }}
{{ Video("/demo.mp4", width=640, height=360, muted=True, sources=["/demo.webm", "/demo.mp4"]) }}

<Audio src="/theme.mp3" controls=True />
<Video src="/demo.mp4" width=640 height=360 muted=True />
```

`Audio(src, controls=True, autoplay=False, loop=False, muted=False, preload="metadata", class_name=None, sources=None, **attrs)` এবং `Video(src, width=None, height=None, ...)` স্থানীয় খেলোয়াড়দের রেন্ডার করে। `sources` প্রতিটি এক্সটেনশন থেকে প্রাপ্ত MIME প্রকারের সাথে `<source>` ট্যাগ যোগ করে।

## একটি উপাদান আপনি নিজেই লিখুন

একটি পুনঃব্যবহারযোগ্য `.nexy` উপাদান হল `src/components/` এর অধীনে একটি ফাইল: Python উপরে প্রপস, নীচে HTML। এটি অন্য যেকোনো Python মডিউলের মতো আমদানি করা হয়।

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
tone: prop[str] = "neutral"
---
<article class="card card-{{ tone }}">
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/routes/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest notes" tone="warm">
  <p>Everything published this week.</p>
</Card>
```

`title` কোন ডিফল্ট নেই, তাই পৃষ্ঠাটি অবশ্যই পাস করতে হবে; `tone` `"neutral"`-এ ফিরে আসে। ট্যাগগুলির মধ্যে মার্কআপটি ভিতরে আসে `<Slot />` (ক্যাপিটাল এস)। প্রপস, স্লট এবং ট্যাগ ফর্মের নিয়মগুলির জন্য [.nexy ফাইলগুলি](README.md#components) দেখুন।

## একটি ক্লায়েন্ট উপাদান আমদানি করা হচ্ছে

একটি `.nexy` ফাইল থেকে, পাথ দ্বারা একটি ফ্রেমওয়ার্ক উপাদান আমদানি করুন; কম্পাইলার এটিকে ক্লায়েন্টে মাউন্ট করে এবং প্রপস হিসাবে বৈশিষ্ট্যগুলি পাস করে:

```nexy
---
from "@/components/Counter.tsx" import Counter
---
<Counter start="0" />
```

`Import(path, framework, symbol)` একই কাজ করে Python:

```python
from nexy import Import

counter = Import("@/components/Counter.tsx", "react", "Counter")
html = counter(start=0)
```

একই ইম্পোর্ট সিনট্যাক্স তাদের URL-এ `.json`, `.css` এবং ইমেজ ফাইলের সমাধান করে।

## টেমপ্লেট এবং Vite

`Template().render(path, context)` একটি টেমপ্লেট ফাইল (Jinja2, অথবা Markdown `.md` রুটের জন্য HTML-এ রেন্ডার করা হয়। `Template().invalidate(path)` ক্যাশে থেকে এটি ড্রপ করে।

`Vite()` বর্তমান মোডের জন্য ক্লায়েন্ট ট্যাগ প্রদান করে: বিকাশে এইচএমআর স্ক্রিপ্ট, উৎপাদনে নির্মিত ক্লায়েন্ট বান্ডেল। Nexy প্রতিটি পৃষ্ঠার জন্য এটি কল; আপনার খুব কমই সরাসরি এটি প্রয়োজন।

## এখনো বাস্তবায়ন হয়নি

`Form` এবং `Script` কোনো আচরণ ছাড়াই রপ্তানিকৃত স্থানধারক। তাদের উপর নির্ভর করবেন না।

## পরবর্তী পদক্ষেপ

- [.nexy ফাইল](README.md): যেখানে এই সাহায্যকারী ব্যবহার করা হয়
- [React](../react/differences.md): `.tsx` উপাদান আমদানি করা
- [ফ্রন্টেন্ড](../../guides/frontend.md): কিভাবে ক্লায়েন্ট উপাদানগুলি একত্রিত হয়
