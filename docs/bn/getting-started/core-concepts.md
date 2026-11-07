# মূল ধারণা

বাকি ডক্স যে শব্দগুলি ব্যবহার করে - রুট, পৃষ্ঠা, ভিউ, কম্পোনেন্ট, হ্যান্ডলার, এন্ডপয়েন্ট - প্রতিটি এক লাইনে, পৃষ্ঠার একটি লিঙ্ক সহ যা গভীরে যায়৷ Nexy এ নতুন? [Nexy কি?](what-is-nexy.md) দিয়ে শুরু করুন।

## কিভাবে এই ডক্স পড়া

| স্তর | এটি যে প্রশ্নের উত্তর দেয় | দিয়ে শুরু করুন |
|---|---|---|
| অ্যাপ্লিকেশন আর্কিটেকচার | কোন স্তর একটি অনুরোধের উত্তর দেয়, এবং এটি কি করতে অস্বীকার করে | [কিভাবে Nexy কাজ করে](how-nexy-works.md) |
| আবেদন কাঠামো | কোডটি কোথায় থাকে এবং একটি ফাইল কী হয় | [প্রকল্পের কাঠামো](project-structure.md) |
| উপস্থাপনা এবং রেন্ডারিং | পাঠক কি দেখেন এবং কে HTML তৈরি করে | [ভিউ ](../views/README.md), [রেন্ডারিং](../rendering/README.md) |
| অ্যাপ্লিকেশন মিথস্ক্রিয়া | পাঠক কি করে, এবং প্রতিক্রিয়ায় কি চলে | [কর্ম](../guides/actions.md) |

স্তরগুলি একবার সেই ক্রমে পড়া হয়। এর পরে, আপনার প্রয়োজন একটি পৃষ্ঠা একটি অনুসন্ধান, একটি কোর্স নয়.

## অ্যাপ্লিকেশন আর্কিটেকচার

কোন কোড কোন URL এর উত্তর দেয় তা নির্ধারণ করার তিনটি উপায়। তারা বিকল্প, স্তর নয়:

- **ফাইল-ভিত্তিক রাউটিং (FBR)**: `src/routes/` এর অধীনে একটি ফাইল একটি রুট। ডিফল্ট।
- **মডুলার রাউটার**: একটি NestJS-স্টাইল কোডবেসের জন্য `src/apps/` এর অধীনে কন্ট্রোলার এবং মডিউল, ডেকোরেটরদের সাথে ঘোষিত।
- **কাস্টম রাউটার**: একটি বিদ্যমান FastAPI `APIRouter` অ্যাপ্লিকেশন অন্তর্ভুক্ত।

পছন্দ হল এক লাইন `NexyConfig` ক্লাসে `nexyconfig.py`।

<!-- router:fbr -->
ফাইল-ভিত্তিক রাউটিং কোন লাইনের প্রয়োজন নেই: `useRouter` ছাড়া, Nexy পড়ে `src/routes/`।

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    pass  # file-based: no useRouter, the files of src/routes/ are the routes
```
<!-- /router -->

<!-- router:modular -->
মডুলার রাউটার হল `src/apps/` এর রুট মডিউল:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule  # modular: the root module of src/apps/
```
<!-- /router -->

<!-- router:custom -->
একটি কাস্টম রাউটার হল একটি `APIRouter` আপনার কাছে ইতিমধ্যেই আছে:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import api  # an APIRouter you already have


class NexyConfig(NexyConfigModel):
    useRouter = api  # custom: your router, included as it is
```
<!-- /router -->

তিনটির মধ্যে একটি বেছে নেওয়া একটি সিদ্ধান্ত। ফ্রন্টএন্ড ফ্রেমওয়ার্ক বেছে নেওয়া আরেকটি, আলাদা আলাদা: দেখুন [একটি রাউটার চয়ন করুন](../routing/README.md) এবং [ভিউ](../views/README.md)।

## আবেদন কাঠামো

পাঁচটি ধারণা যে Next.js থেকে আসা একজন পাঠক সাধারণত এক হয়ে যায়। তারা একই জিনিস নয়, এবং পার্থক্য সবচেয়ে ব্যাখ্যা করে "কেন আমার পৃষ্ঠা রেন্ডার হচ্ছে না" প্রশ্ন।

| ধারণা | এটা কি | এটা কি না |
|---|---|---|
| **রুট** | একটি URL প্যাটার্ন, একটি ফাইলের পথ দ্বারা উত্পাদিত | একটি ফাইল: একটি ফাইল একাধিক URL এর উত্তর দিতে পারে (`[slug]`) |
| **পৃষ্ঠা** | একটি রুট ফাইল যা একটি ভিউ রেন্ডার করে: `.nexy`, `.md`, `.mdx`, `.tsx`, `.vue`, `.svelte` | একটি শেষ পয়েন্ট: এটি একটি নথির উত্তর দেয়, ডেটা নয় |
| **দেখুন** | একটি পৃষ্ঠার মূল অংশ কী তৈরি করে: Jinja2 এবং Python, Markdown, বা একটি ক্লায়েন্ট উপাদান | একটি রুট: একই দৃশ্য বেশ কয়েকটি পৃষ্ঠা পরিবেশন করতে পারে |
| **উপাদান** | একটি পুনঃব্যবহারযোগ্য টুকরা একটি পৃষ্ঠা আমদানি করে | একটি রুট: সার্ভার মোডে একটি উপাদান কখনই নিজে থেকে পরিবেশিত হয় না |
| **রুট হ্যান্ডলার** | একটি `.py` রুট ফাইলের ফাংশন, HTTP পদ্ধতির নামানুসারে (`GET`, `POST`, …) | একটি পৃষ্ঠা: এটি JSON, একটি ফাইল বা একটি `Response` প্রদান করে |
| **শেষ বিন্দু** | জোড়া (URL, পদ্ধতি) যা একজন হ্যান্ডলার উত্তর দেয় | একটি হ্যান্ডলার: একটি ফাইল বেশ কয়েকটি শেষ পয়েন্টের উত্তর দিতে পারে |

একটি বাক্যে: **একটি পৃষ্ঠা হল একটি রুট ফাইল, একটি ভিউ হল যা এটিকে রেন্ডার করে, একটি উপাদান হল যা একটি পৃষ্ঠা পুনঃব্যবহার করে, একজন হ্যান্ডলার একটি এন্ডপয়েন্টের উত্তর দেয়।**

<!-- router:fbr -->
একটি ছোট প্রকল্পের মধ্যে পাঁচটি:

```text
src/
├─ routes/
│  ├─ blog/[slug].nexy    a route (/blog/{slug}) whose file is a page
│  └─ api/posts.py        a route whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```nexy filename="src/routes/blog/[slug].nexy"
---
from "@/components/Like.tsx" import Like

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Like post="{{ slug }}" />
```

ফ্রন্টম্যাটার এবং এর নীচের টেমপ্লেট হল পৃষ্ঠার দৃশ্য; `Like` হল সেই উপাদান যা এটি পুনরায় ব্যবহার করে।

```python filename="src/routes/api/posts.py"
async def GET():  # the endpoint GET /api/posts
    return {"posts": []}


async def POST():  # the endpoint POST /api/posts
    return {"created": True}
```

<!-- /router -->

<!-- router:modular -->
মডুলার রাউটারের সাথে, একটি রুট হল একটি কন্ট্রোলারের পথ, এবং একটি হ্যান্ডলার হল এর একটি পদ্ধতি, HTTP ক্রিয়াটির নামকরণ করা হয়েছে:

```text
src/
├─ apps/
│  ├─ app_module.py       the root module: lists the controllers
│  └─ posts_controller.py a route (/api/posts) whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```python filename="src/apps/posts_controller.py"
from nexy.decorators import Controller


@Controller("/api/posts")
class PostsController:
    async def get(self) -> dict:  # the endpoint GET /api/posts
        return {"posts": []}

    async def post(self) -> dict:  # the endpoint POST /api/posts
        return {"created": True}
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .posts_controller import PostsController


@Module()
class AppModule:
    controllers = [PostsController]
```

একটি পৃষ্ঠা এখনও `src/routes/` এর একটি ফাইল, অথবা একটি দৃশ্য একটি নিয়ামক `useViews` এর সাথে ফিরে আসে।
<!-- /router -->

<!-- router:custom -->
একটি কাস্টম রাউটারের সাথে, একটি রুট হল আপনার `APIRouter` এর একটি পথ, এবং একটি হ্যান্ডলার হল এটির ডেকোরেটর রেজিস্টার করার ফাংশন:

```python filename="src/legacy.py"
from fastapi import APIRouter

api = APIRouter()


@api.get("/api/posts")  # the endpoint GET /api/posts
async def list_posts():
    return {"posts": []}


@api.post("/api/posts")  # the endpoint POST /api/posts
async def create_post():
    return {"created": True}
```

পৃষ্ঠাগুলি এখনও `src/routes/` এর ফাইল: অন্তর্ভুক্ত রুটের পাশে একটি `.nexy` পৃষ্ঠা উত্তর দেয়।
<!-- /router -->

আরও দুটি শব্দ যা সর্বত্র ফিরে আসে:

- **লেআউট**: একটি `layout.*` ফাইল যা তার ফোল্ডারের নিচের পৃষ্ঠাগুলিকে মোড়ানো করে; এইচটিএমএল ডকুমেন্টের মালিক রুট। [লেআউটস](../routing/fbr/layouts/README.md) দেখুন।
- **নির্ভরতা**: একটি ফাংশন যা একটি হ্যান্ডলারের আগে চলে, প্রতি রুট বা প্রতি ফোল্ডারে প্রয়োগ করা হয়। দেখুন [নির্ভরতা](../routing/fbr/dependencies/README.md)।

## উপস্থাপনা এবং রেন্ডারিং

দুটি স্বাধীন সিদ্ধান্ত, প্রায়ই বিভ্রান্ত হয়:

- **বিন্যাস** সিদ্ধান্ত নেয় কোন ফাইলটি পৃষ্ঠাটিকে রেন্ডার করবে: [দর্শন](../views/README.md)।
- **মোড** নির্ধারণ করে কে এইচটিএমএল তৈরি করে এবং কখন: [রেন্ডারিং](../rendering/README.md)।

| ধারণা | এক লাইন |
|---|---|
| সার্ভার মোড | সার্ভার রেন্ডার করে `.nexy` এবং `.md` পৃষ্ঠা; উপাদান হল দ্বীপ ([মোড](../routing/fbr/modes.md)) |
| ক্লায়েন্ট মোড | `useCSR = True`: ফ্রেমওয়ার্ক ফাইলগুলি হল রুট, এবং নেভিগেশন ব্রাউজারে ঘটে |
| SSR, ISR, CSR, দ্বীপপুঞ্জ | চারটি রেন্ডারিং মোড, সিএসআর ব্যতীত প্রতি পৃষ্ঠায় সিদ্ধান্ত নেওয়া হয়েছে, যা প্রতি প্রকল্প ([রেন্ডারিং](../rendering/README.md)) |
| হাইড্রেশন | ব্রাউজারটি HTML এর সাথে একটি ফ্রেমওয়ার্ক সংযুক্ত করছে সার্ভারটি ইতিমধ্যেই পাঠিয়েছে ([দ্বীপগুলি](../rendering/islands.md)) |
| প্রপস | অভিভাবক যে মানগুলি একটি উপাদানে পাস করেন, একটি `.nexy` ফাইলে `name: prop[type]` ঘোষণা করা হয় ([.nexy ফাইল](../views/nexy/README.md)) |

একটি দ্বীপ সহ একটি সার্ভার-মোড পৃষ্ঠা: সার্ভারটি পৃষ্ঠাটি রেন্ডার করে, ব্রাউজারটি চার্টটিকে হাইড্রেট করে যখন এটি দৃশ্যে স্ক্রোল করে।

<!-- router:fbr,custom -->
```nexy filename="src/routes/sales.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Sales</h1>
<Chart directive="client:visible" />
```
<!-- /router -->

<!-- router:modular -->
দ্বীপটি দৃশ্যে যায়, এবং নিয়ামক দৃশ্যটি ফিরিয়ে দেয়:

```nexy filename="src/apps/sales_view.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Sales</h1>
<Chart directive="client:visible" />
```

```python filename="src/apps/sales_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/sales")
class SalesController:
    async def get(self):
        return useViews("src/apps/sales_view.nexy")
```
<!-- /router -->

## অ্যাপ্লিকেশন মিথস্ক্রিয়া

| ধারণা | এক লাইন |
|---|---|
| অ্যাকশন | একটি Python ফাংশন চিহ্নিত `@Action`, একটি `POST` হিসাবে পরিবেশিত, একটি ফর্ম থেকে কলযোগ্য বা একটি টাইপ করা ফাংশন হিসাবে ([ক্রিয়া](../guides/actions.md)) |
| ফর্ম | একটি এইচটিএমএল ফর্ম যা একটি অ্যাকশনে পোস্ট করে, বৈধতা ত্রুটিগুলি পৃষ্ঠায় ফিরে আসে ([ক্রিয়া](../guides/actions.md)) |
| নেভিগেশন | যে লিঙ্কগুলি প্রিফেচ করে, এবং হুকগুলি যেগুলি পাথ, ক্যোয়ারী, কুকিজ এবং সেশন পড়ে ([হুকস](../routing/fbr/navigation/hooks.md)) |
| ডেটা আনা হচ্ছে | পৃষ্ঠা বা হ্যান্ডলার যে এটি প্রয়োজন দ্বারা সম্পন্ন; Nexy ক্লায়েন্ট ডেটা লেয়ার পাঠায় না ([হ্যান্ডলার](../routing/fbr/handlers/README.md)) |

একটি ক্রিয়া এবং ফর্ম যা এটিতে পোস্ট করে, যা কোনো স্ক্রিপ্ট লোড হওয়ার আগে কাজ করে:

```python filename="src/actions/newsletter.py"
from nexy.decorators import Action


@Action
async def subscribe(email: str) -> bool:
    return True
```

<!-- router:fbr,custom -->
```html filename="src/routes/index.nexy"
<form method="post" action="{{ __actions_path['subscribe'] }}">
  <input name="email" type="email">
  <button type="submit">Subscribe</button>
</form>
```
<!-- /router -->

<!-- router:modular -->
```html filename="src/apps/home_view.nexy"
<form method="post" action="{{ __actions_path['subscribe'] }}">
  <input name="email" type="email">
  <button type="submit">Subscribe</button>
</form>
```
<!-- /router -->

## নেক্সি যা করে না

প্রমাণীকরণ, অনুমোদন, ডাটাবেস, আন্তর্জাতিকীকরণ, ব্যাকগ্রাউন্ড জব, ইমেল, অর্থপ্রদান এবং অনুসন্ধান **আপনার আবেদনের দায়িত্ব**, কাঠামোর নয়। Nexy এক্সটেনশন পয়েন্ট দেয় এবং বলে যে প্রতিটিকে কোথায় প্লাগ করতে হবে: দেখুন [Nexy আপনার কাছে কী রেখে যায়](how-nexy-works.md#what-nexy-leaves-to-you)।

<!-- router:fbr -->
প্রমাণীকরণ, উদাহরণস্বরূপ, এটি সুরক্ষিত ফোল্ডারের একটি নির্ভরতা প্লাগ ইন করে। Nexy নিচের প্রতিটি রুটের আগে এটি চালায়; ব্যবহারকারী কে আপনার সিদ্ধান্ত থেকে যায়:

```python filename="src/routes/account/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```
<!-- /router -->

<!-- router:modular -->
প্রমাণীকরণ, উদাহরণস্বরূপ, এটি সুরক্ষিত কন্ট্রোলারের গার্ডে প্লাগ করে। Nexy ক্লাসের প্রতিটি হ্যান্ডলারের আগে এটি চালায়; ব্যবহারকারী কে আপনার সিদ্ধান্ত থেকে যায়:

```python filename="src/apps/account_controller.py"
from nexy import unauthorized
from nexy.decorators import Controller, UseGuard
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


@Controller("/account")
@UseGuard(require_login)
class AccountController:
    async def get(self) -> dict:
        return {"ok": True}
```
<!-- /router -->

<!-- router:custom -->
প্রমাণীকরণ, উদাহরণস্বরূপ, এটি সুরক্ষিত রাউটারের নির্ভরতার সাথে প্লাগ করে, যেমন FastAPI; ব্যবহারকারী কে আপনার সিদ্ধান্ত থেকে যায়:

```python filename="src/account.py"
from fastapi import APIRouter, Depends

from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


api = APIRouter(prefix="/account", dependencies=[Depends(require_login)])
```
<!-- /router -->

কারণটি তার নিজের স্বার্থে ন্যূনতমতা নয়: একটি কাঠামো যা আপনার ORM বা আপনার প্রমাণীকরণ লাইব্রেরি বাছাই করে এমন কিছু সিদ্ধান্ত নিয়েছে শুধুমাত্র আপনার অ্যাপ্লিকেশন সিদ্ধান্ত নিতে পারে।

## পরবর্তী পদক্ষেপ

- [প্রকল্প কাঠামো ](project-structure.md): একটি প্রকল্পের প্রতিটি ফোল্ডার এবং ফাইল
- [শব্দকোষ ](../reference/glossary.md): একই শব্দ, একটি বর্ণানুক্রমিক সূচকে
- [কিভাবে Nexy কাজ](how-nexy-works.md): স্তরগুলি, কে কী তৈরি করে এবং Nexy আপনার কাছে কী রেখে যায়৷
