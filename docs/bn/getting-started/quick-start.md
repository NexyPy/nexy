# দ্রুত শুরু

আপনি একটি Nexy প্রকল্প তৈরি করবেন, এটি চালাবেন এবং এটি সম্পাদনা করার সাথে সাথে একটি পৃষ্ঠা পরিবর্তন দেখতে পাবেন। তিন মিনিট সময় লাগে। [টিউটোরিয়াল](tutorial.md) তারপর একটি এন্ডপয়েন্ট এবং একটি প্রোডাকশন বিল্ড যোগ করে।

## আপনি শুরু করার আগে

| আপনার প্রয়োজন | কেন |
|---|---|
| Python 3.12+ | `requires-python` `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | প্রদান করে `uvx`, প্রকল্প তৈরি করে এবং এর প্যাকেজ ইনস্টল করে |
| Node.js 18+ | শুধুমাত্র যদি আপনি একটি ক্লায়েন্ট ফ্রেমওয়ার্ক ব্যবহার করেন (React, Vue, Svelte, Solid, Preact) |

এখনো নেই uv? [ইনস্টলেশন](installation.md) দেখুন।

## 1. প্রকল্প তৈরি করুন

```bash
uvx nexy new my-app
```

`uvx` uv এর সাথে আসে, তাই প্রথমে uv ইনস্টল করুন। এটি একটি অস্থায়ী পরিবেশে Nexy চালায়, যথেষ্ট **তৈরি** প্রকল্প `nexy new` তারপর প্রকল্পের নিজস্ব `.venv` করে এবং সেখানে এর প্যাকেজ ইনস্টল করে। চারটি প্রম্পট তারের স্থির করে:

| প্রম্পট | প্রভাব |
|---|---|
| ফাইল ভিত্তিক রাউটার? | `Yes` স্ক্যান `src/routes/`; `No` মডুলার রাউটারটিকে `src/apps/` | এ স্ক্যাফোল্ড করে
| প্রকল্পের ধরন | `Web` একটি লেআউট এবং ক্লায়েন্ট সম্পদ যোগ করে, `API` দেখা ছাড়াই শুরু হয় |
| ক্লায়েন্ট উপাদান? | একটি কাঠামো এবং এর Vite সেটআপ যোগ করে |
| ORM / ডাটাবেস | একটি মডেল স্তর যোগ করে, বা কিছুই |

নিশ্চিত নন? উত্তর `Yes`, `Web`, এবং কোনো ক্লায়েন্ট উপাদান নেই। আপনি প্রতিটি পরে যোগ করতে পারেন.

## 2. এটি চালান

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

খুলুন <http://localhost:3000>। আপনি স্টার্টার পৃষ্ঠা দেখতে হবে. পোর্টটি আসে `usePort` থেকে (ডিফল্ট `3000`); `--port` এবং `--host` প্রতি রানে এটিকে ওভাররাইড করে।

> [!NOTE]
> প্রজেক্টের ভার্চুয়াল এনভায়রনমেন্টের ভিতরে `new` এবং `init` ছাড়া প্রতিটি কমান্ড চালান, অথবা `uv run` এর সাথে প্রিফিক্স করুন, যেমন `uv run nexy dev`। এর বাইরে, একটি প্রকল্প যার প্রয়োজন `sqlmodel` `No module named 'sqlmodel'` এর সাথে ব্যর্থ হয়।

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

খুলুন <http://localhost:3000/hello>। `"Hello"` তে `"Bonjour"` পরিবর্তন করুন এবং সংরক্ষণ করুন: পৃষ্ঠাটি ম্যানুয়াল রিলোড ছাড়াই আপডেট হয়। কোডটি ভুল হলে, ব্রাউজার একটি ফাঁকা পৃষ্ঠার পরিবর্তে ত্রুটি দেখায়।

`prop[str]` একটি টাইপ করা সম্পত্তি ঘোষণা করে। ফ্রন্টম্যাটারের অধীনে মার্কআপ হল Jinja2 - [.nexy ফাইলগুলি](../views/nexy/README.md) দেখুন।

## যেখানে পরের

| আপনি | পড়তে চান |
|---|---|
| একটি Python এন্ডপয়েন্ট যোগ করুন এবং একটি বিল্ড পাঠান | [টিউটোরিয়াল](tutorial.md) |
| প্রতিটি ফাইল কোথায় রয়েছে তা জানুন | [প্রকল্প কাঠামো](project-structure.md) |
| বুঝুন কে কি তৈরি করে | [নেক্সি কীভাবে কাজ করে](how-nexy-works.md) |
| React, Vue, Svelte, Solid বা Preact | [ভিউ](../views/README.md) | ব্যবহার করুন
