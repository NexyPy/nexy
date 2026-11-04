# দ্রুত শুরু

আপনি একটি Nexy প্রকল্প তৈরি করবেন, এটি চালাবেন এবং এটি সম্পাদনা করার সাথে সাথে একটি পৃষ্ঠা পরিবর্তন দেখতে পাবেন। এটা তিন লাগে
মিনিট [টিউটোরিয়াল](tutorial.md) তারপর একটি এন্ডপয়েন্ট এবং একটি প্রোডাকশন বিল্ড যোগ করে।

## আপনি শুরু করার আগে

| আপনার প্রয়োজন | কেন |
|---|---|
| পাইথন 3.12+ | `requires-python` `pyproject.toml` | এ
| [uv](https://docs.astral.sh/uv/) | প্রদান করে `uvx`, প্রকল্প তৈরি করে এবং এর প্যাকেজ ইনস্টল করে |
| Node.js 18+ | শুধুমাত্র যদি আপনি একটি ক্লায়েন্ট ফ্রেমওয়ার্ক ব্যবহার করেন (React, Vue, Svelte, Solid, Preact) |

এখনও ইউভি নেই? [ইনস্টলেশন](installation.md) দেখুন।

## 1. প্রকল্পটি তৈরি করুন

```bash
uvx nexy new my-app
```

`uvx` ইউভির সাথে আসে, তাই প্রথমে ইউভি ইনস্টল করুন। এটি একটি অস্থায়ী পরিবেশে Nexy চালায়, প্রকল্পটি **তৈরি করার** জন্য যথেষ্ট। `nexy new` তারপর তৈরি করে
প্রকল্পের নিজস্ব `.venv` এবং সেখানে এর প্যাকেজ ইনস্টল করে। চারটি প্রম্পট তারের স্থির করে:

| প্রম্পট | প্রভাব |
|---|---|
| ফাইল-ভিত্তিক রাউটার? | `Yes` স্ক্যান `src/routes/`; `No` মডুলার রাউটারটিকে `src/apps/` | এ স্ক্যাফোল্ড করে
| প্রকল্পের ধরন | `Web` একটি লেআউট এবং ক্লায়েন্ট সম্পদ যোগ করে, `API` দেখা ছাড়াই শুরু হয় |
| ক্লায়েন্ট উপাদান? | একটি কাঠামো এবং এর Vite সেটআপ যোগ করে |
| ORM/ডাটাবেস | একটি মডেল স্তর যোগ করে, বা কিছুই না |

নিশ্চিত নন? উত্তর `Yes`, `Web`, এবং কোনো ক্লায়েন্ট উপাদান নেই। আপনি প্রতিটি পরে যোগ করতে পারেন.

## ২. চালান

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

খুলুন <http://localhost:3000>। আপনি স্টার্টার পৃষ্ঠা দেখতে হবে. বন্দরটি আসে `usePort` থেকে
(ডিফল্ট `3000`); `--port` এবং `--host` রান প্রতি এটিকে ওভাররাইড করে।

> [!নোট]
> প্রকল্পের ভার্চুয়াল এনভায়রনমেন্টের ভিতরে `new` এবং `init` ব্যতীত প্রতিটি কমান্ড চালান বা এটির উপসর্গ দিন
>  `uv run` সহ, যেমন `uv run nexy dev`। এর বাইরে, একটি প্রকল্প যার প্রয়োজন `sqlmodel` ব্যর্থ হয়
> `No module named 'sqlmodel'`।

## 3. একটি পৃষ্ঠা পরিবর্তন করুন

<!-- router:fbr,custom -->
`src/routes/` এর অধীনে একটি ফাইল একটি রুট। তৈরি করুন `src/routes/hello.nexy`:

```nexy filename="src/routes/hello.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```
<!-- /router -->

<!-- router:modular -->
একটি নিয়ামক একটি দৃশ্য প্রদান করে। তৈরি করুন `src/apps/hello_view.nexy`:

```nexy filename="src/apps/hello_view.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

তারপরে `src/apps/app_controller.py` পৃষ্ঠাটি ঘোষণা করুন এবং এটি মডিউলে যুক্ত করুন:

```python filename="src/apps/app_controller.py"
@Controller("/hello")
class HelloController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/hello_view.nexy")})
```

```python filename="src/apps/app_module.py"
from .app_controller import AboutController, AppController, HelloController

controllers = [AppController, AboutController, HelloController]
```
<!-- /router -->

খোলা <http://localhost:3000/hello>। পরিবর্তন `"Hello"` থেকে `"Bonjour"` এবং সংরক্ষণ করুন: পৃষ্ঠা আপডেট
একটি ম্যানুয়াল পুনরায় লোড ছাড়া। কোডটি ভুল হলে, ব্রাউজার একটি ফাঁকা পৃষ্ঠার পরিবর্তে ত্রুটি দেখায়।

`prop[str]` একটি টাইপ করা সম্পত্তি ঘোষণা করে। ফ্রন্টম্যাটারের অধীনে মার্কআপটি হল জিনজা 2 - দেখুন
[.nexy ফাইল](../views/nexy/README.md)।

## যেখানে পরবর্তী

| আপনি | পড়তে চান |
|---|---|
| একটি পাইথন এন্ডপয়েন্ট যোগ করুন এবং একটি বিল্ড পাঠান | [টিউটোরিয়াল](tutorial.md) |
| প্রতিটি ফাইল কোথায় রয়েছে তা জানুন | [প্রকল্প কাঠামো](project-structure.md) |
| বুঝুন কে কী তৈরি করে | [নেক্সি কীভাবে কাজ করে](how-nexy-works.md) |
| React, Vue, Svelte, Solid বা Preact ব্যবহার করুন | [দর্শন](../views/README.md) |