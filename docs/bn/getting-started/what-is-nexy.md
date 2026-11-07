# নেক্সি কি?

Nexy হল ফুলস্ট্যাক ওয়েব অ্যাপ্লিকেশনের জন্য একটি Python কাঠামো: আপনার পৃষ্ঠাগুলি এবং আপনার APIগুলি একটি প্রকল্পে থাকে এবং একটি সার্ভার দ্বারা পরিবেশিত হয়৷

## যা পাবেন

- **পৃষ্ঠাগুলি Python.** একটি `.nexy` ফাইল হল HTML যার উপরে কয়েকটি লাইন Python থাকে; একটি `.md` ফাইলও একটি পৃষ্ঠা। একটি পৃষ্ঠা রেন্ডার করার জন্য কোন JavaScript প্রয়োজন নেই।
<!-- router:fbr -->
- **একই একটি API প্রকল্প** `src/routes/` এর অধীনে একটি `.py` ফাইল HTTP অনুরোধের উত্তর দেয়: `GET` নামের একটি ফাংশন `GET` উত্তর দেয়, `POST` নামের একটি ফাংশন `POST` উত্তর দেয়।
<!-- /router -->
<!-- router:modular -->
- **একই একটি API প্রকল্প** একটি কন্ট্রোলার HTTP অনুরোধের উত্তর দেয়: এর পদ্ধতি `get` উত্তর দেয় `GET`, এর পদ্ধতি `post` উত্তর দেয় `POST`, এবং একটি মডিউল গ্রুপ কন্ট্রোলার এবং তাদের পরিষেবা।
<!-- /router -->
<!-- router:custom -->
- **একই একটি API প্রকল্প** আপনার ইতিমধ্যেই যে FastAPI রাউটারটি রয়েছে তা উত্তর দিতে থাকে এবং এর পাশে `src/routes/` উত্তরের পৃষ্ঠা এবং রুট ফাইলগুলি।
<!-- /router -->
- **জন্য API ডকুমেন্টেশন বিনামূল্যে** প্রতিটি API রুট একটি OpenAPI স্কিমাতে প্রদর্শিত হয় এবং স্কেলার এটিকে `/docs` এ একটি ইন্টারেক্টিভ রেফারেন্স হিসাবে দেখায়।
- **ফর্ম যে কল Python** একটি ফর্ম, বা ব্রাউজার থেকে একটি টাইপ করা কল, একই Python ফাংশনে পৌঁছায়।
- **একটি ফ্রন্টএন্ড ফ্রেমওয়ার্ক যখন আপনি চান এক** React, Vue, Svelte, Solid বা Preact, একটি উপাদান বা পুরো সাইটের জন্য।
- **কাজ করার জন্য একটি আদেশ, একটি থেকে জাহাজ** `nx dev` আপনি সংরক্ষণ হিসাবে পুনরায় লোড; `nx build` উৎপাদন প্রস্তুত করে।

## এটা কি উপর নির্মিত হয়

বর্তমান সংস্করণ, 2.2, এমন সরঞ্জামগুলির উপর দাঁড়িয়েছে যা আপনি ইতিমধ্যেই জানেন:

| অংশ | উপর নির্মিত | এটা আপনার জন্য মানে কি |
|---|---|---|
| সার্ভার এবং API | [FastAPI](https://fastapi.tiangolo.com/) | একটি API রুট হল একটি FastAPI রুট: Pydantic বৈধতা এবং নির্ভরতা যথারীতি কাজ করে |
| API রেফারেন্স | OpenAPI এবং [স্ক্যালার](https://scalar.com/) | স্কিমাটি `/openapi.json` এ, রেফারেন্সটি `/docs` এ |
| পাতা | Jinja2 | একটি `.nexy` পৃষ্ঠা Jinja2 ট্যাগ ব্যবহার করে যেমন `{{ title }}` |
| ফ্রন্টেন্ড (ঐচ্ছিক) | [Vite](https://vite.dev/) | শুধুমাত্র একটি ফ্রন্টএন্ড ফ্রেমওয়ার্ক সহ, যার প্রয়োজন Node.js |

## একটি প্রথম পৃষ্ঠা এবং একটি প্রথম শেষ পয়েন্ট

<!-- router:fbr,custom -->
একটি পৃষ্ঠা, `/hello` এ:

```nexy filename="src/routes/hello.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

একটি এন্ডপয়েন্ট, `GET /api/items` এ, কোনো অতিরিক্ত কোড ছাড়াই `/docs` এ তালিকাভুক্ত:

```python filename="src/routes/api/items.py"
from nexy.http import Request


async def GET(request: Request):
    return {"items": []}
```
<!-- /router -->

<!-- router:modular -->
একটি দৃশ্য, এবং কন্ট্রোলার যে উত্তর দেয় `/hello/` এবং `GET /api/items/`। কোনো অতিরিক্ত কোড ছাড়াই এন্ডপয়েন্টটি `/docs` এ তালিকাভুক্ত করা হয়েছে, এবং একটি URL এর শেষ স্ল্যাশ ছাড়াই এটিতে পুনঃনির্দেশ করা হয়েছে:

```nexy filename="src/apps/hello_view.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

```python filename="src/apps/hello_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/hello")
class HelloController:
    async def get(self):
        return useViews("src/apps/hello_view.nexy", context={"title": "Hello"})


@Controller("/api/items")
class ItemsController:
    async def get(self):
        return {"items": []}
```

রুট মডিউল তাদের তালিকাভুক্ত করে, এবং `useRouter = AppModule` `nexyconfig.py` এ মাউন্ট করে:

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .hello_controller import HelloController, ItemsController


@Module()
class AppModule:
    controllers = [HelloController, ItemsController]
```
<!-- /router -->

## Nexy আপনার কাছে যা রেখে যায়

ডাটাবেস, লগইন এবং আপনার অ্যাপ্লিকেশনের অন্তর্গত কে কি করতে পারে সে সম্পর্কে নিয়ম, তাই আপনি লাইব্রেরি বেছে নিন। [ডেটাবেস](../guides/databases.md) এবং [মিডলওয়্যার এবং নিরাপত্তা ](../guides/middleware-and-security.md) দেখায় যে প্রতিটি কোথায় প্লাগ ইন করে।

## পরবর্তী পদক্ষেপ

- [ইনস্টলেশন](installation.md): ইনস্টল করুন uv এবং একটি প্রকল্প তৈরি করুন
- [দ্রুত শুরু](quick-start.md): এটি চালান, একটি পৃষ্ঠা পরিবর্তন করুন, এটি তৈরি করুন
- [মূল ধারণা ](core-concepts.md): কিছু শব্দ বাকি ডক্স ব্যবহার করে
