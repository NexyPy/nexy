# ত্রুটি পৃষ্ঠা

একটি অনুরোধ যা ব্যর্থ হয় তার এখনও আপনার সাইটের অন্যান্য অংশের মতো উত্তর দেওয়া উচিত: একটি ভিজিটরের জন্য আপনার নিজের ভাষায় একটি পৃষ্ঠা, একটি API ক্লায়েন্টের জন্য JSON-এর মতো একই ব্যর্থতা৷ Nexy উভয় উত্তর দেয়, এবং একটি ফাইল প্রতিটি উত্তর প্রতিস্থাপন করে।

এই পৃষ্ঠাটি মানচিত্র: কোন ফাইল কোন স্ট্যাটাসের উত্তর দেয় এবং কীভাবে আপনার প্রথমটি তৈরি করবেন। একটি ফোল্ডারের পৃষ্ঠাগুলি [তাদের নিজস্ব পৃষ্ঠা](folder-pages.md) পায়।

## একটি ব্যর্থতা, দুটি উত্তর

```diagram filename="যারা একটি ব্যর্থ অনুরোধের উত্তর দেয়"
a request that fails
      │
      ├── a browser (Accept: text/html)              ──►  an HTML page
      └── an API client (Accept: application/json)   ──►  {"detail": "…"}  with the same status

the HTML page
      ├── the deepest folder of the URL that holds a file   ──►  your file
      └── no folder of the chain holds one                 ──►  the built-in page
```

## আপনার প্রথম পাতা

`src/routes/notfound.nexy` তৈরি করুন এবং একজন দর্শকের যা পড়া উচিত তা লিখুন:

```nexy filename="src/routes/notfound.nexy"
---
title: Page not found
---
<h1>Page not found</h1>
<p>The page moved or never existed. <a href="/">Back home</a>.</p>
```

সংরক্ষণ করুন, এবং একটি URL এর জন্য জিজ্ঞাসা করুন কিছুই কাজ করে না:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/nowhere
# HTTP/1.1 404 Not Found
```

রুট রুটের ফাইলটি পুরো প্রকল্পের উত্তর দেয়; একটি ফোল্ডারে একটি অনুলিপি শুধুমাত্র সেই ফোল্ডারের উত্তর দেয় এবং [বাকিগুলি যেমন আছে তেমনই রাখে](folder-pages.md)। কোনো ফাইল ছাড়াই, Nexy তার অন্তর্নির্মিত স্টাইলযুক্ত পৃষ্ঠাটি পরিবেশন করে।

## কোন ফাইল উত্তর

| ফাইল | উত্তর |
|---|---|
| `notfound.nexy` | `404` এর ডিরেক্টরির জন্য |
| `errors.nexy` | `500` এর ডিরেক্টরির জন্য |
| `forbidden.nexy` | `403` এর ডিরেক্টরির জন্য |
| `unauthorized.nexy` | `401` এর ডিরেক্টরির জন্য |
| `loading.nexy` | সংরক্ষিত; এখনও রানটাইম প্রভাব নেই |

| পরিস্থিতি | উত্তর |
|---|---|
| কোন রুট মেলে না | `404` |
| একটি গতিশীল সেগমেন্টকে তার টীকায় রূপান্তর করা যায় না | `404` |
| একটি পৃষ্ঠা বা একটি API হ্যান্ডলারে একটি আন-হ্যান্ডেল করা ব্যতিক্রম | `500` |
| `raise HTTPException(status_code=403)` | আপনি যে স্ট্যাটাস উত্থাপন করেছেন, HTML বা JSON |
| `notFound()`, `forbidden()`, `unauthorized()` | `404`, `403`, `401`, যেকোনো জায়গা থেকে অনুরোধে |
| `redirect()`, `permanentRedirect()` | কোনো ত্রুটি পৃষ্ঠা ছাড়াই একটি বাস্তব পুনঃনির্দেশ |

## কোড থেকে একটি পৃষ্ঠা বা উত্তর ছেড়ে দিন

`redirect`, `permanentRedirect`, `notFound`, `forbidden` এবং `unauthorized` একটি HTTP ব্যতিক্রম উত্থাপন করে, তাই একই কল একটি `.nexy` পৃষ্ঠা, একটি API হ্যান্ডলার, একটি মডুলার কন্ট্রোলার, একটি গার্ড এবং একটি `dependencies.py` এ কাজ করে। ক্লায়েন্টে তাদের একই নাম রয়েছে (`@nexy/client`)।

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound, redirect

from src.posts import find

slug: prop[str]
post = find(slug)
if post is None:
    notFound()
if post.moved_to:
    redirect(post.moved_to)
---
<h1>{{ post.title }}</h1>
```

| কল | উত্তর |
|---|---|
| `redirect(url)` | `307`; `redirect(url, status=303)` একটি পোস্টকে একটি ফর্মের পরে একটি GET এ পরিণত করে |
| `permanentRedirect(url)` | `308`; ব্রাউজার এবং সার্চ ইঞ্জিন এটি মনে রাখে |
| `notFound(detail=None)` | `404`: একটি API ক্লায়েন্টের জন্য `notfound` পৃষ্ঠা, বা JSON |
| `forbidden(detail=None)` | `403`: দর্শনার্থী পরিচিত কিন্তু এটি দেখতে পান না |
| `unauthorized(detail=None, scheme=None)` | `401`; `scheme="Bearer"` যোগ করে `WWW-Authenticate` |

একটি এপিআই ক্লায়েন্টের কাছেও `Location` শিরোনাম এবং কোনো পৃষ্ঠা ছাড়াই একটি পুনঃনির্দেশিত উত্তর। আপনার বিশ্বাসের মানগুলি থেকে গন্তব্য তৈরি করুন: একটি `redirect(request.query_params["next"])` যেখানেই লিঙ্ক বলে সেখানে দর্শকদের পাঠায়। একটি লাইন বিরতি সহ একটি গন্তব্য প্রত্যাখ্যান করা হয়েছে৷

একটি গার্ড একটি সম্পূর্ণ ফোল্ডার রক্ষা করে:

```python filename="src/routes/private/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

## HTML বা JSON

কে জিজ্ঞাসা করে তার উপর নির্ভর করে একই ব্যতিক্রম ভিন্নভাবে উত্তর দেয়:

- একটি ব্রাউজার (`Accept: text/html`) একটি HTML পৃষ্ঠা পায়। বিশদটি HTML-এস্কেপড, তাই ব্যবহারকারীর ইনপুট থেকে নির্মিত একটি বার্তা মার্কআপ ইনজেক্ট করতে পারে না।
- একটি ক্লায়েন্ট যে JSON এর জন্য জিজ্ঞাসা করে এবং একটি পৃষ্ঠা (`Accept: application/json`) এর জন্য নয়, একই স্ট্যাটাস কোড সহ `{"detail": "..."}` পায়।

```python filename="src/routes/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=403, detail="Out of range")
    return {"id": id}
```

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!NOTE]
> একটি ক্লায়েন্ট যেটি `Accept: */*` পাঠায় (`curl` এবং অনেক HTTP লাইব্রেরির ডিফল্ট) এইচটিএমএল পৃষ্ঠা গ্রহণ করে। JSON ত্রুটির জন্য `Accept: application/json` সেট করুন।

## অব্যবহিত ব্যতিক্রম

একটি ব্যতিক্রম যে পরিচালনা করা কিছুই একবার লগ করা হয় না, ব্যতিক্রম, এটি কোথা থেকে এসেছে এবং এর চারপাশের কোড এবং মোড অনুযায়ী উত্তর দেওয়া হয়েছে।

| | `nx dev` | `nx start` |
|---|---|---|
| ব্রাউজার | ত্রুটি সহ একটি পৃষ্ঠা, আপনার কোডের লাইন যা এটিকে উত্থাপন করেছে এবং সম্পূর্ণ ট্রেসব্যাক | বিল্ট-ইন `500` পৃষ্ঠা (বা আপনার `errors.nexy`) একটি রেফারেন্স সহ |
| JSON ক্লায়েন্ট | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| সার্ভার লগ | আপনার কোডের ব্যতিক্রম এবং লাইন | ব্যতিক্রম এবং পুরো ট্রেসব্যাক, একই রেফারেন্স সহ |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

রেফারেন্সটি আটটি অক্ষর, প্রতিটি ব্যর্থতার জন্য নতুন। একজন দর্শক এটি উদ্ধৃত করতে পারেন, এবং আপনি এটির জন্য লগ অনুসন্ধান করে ট্রেসব্যাক খুঁজে পাবেন। ব্যতিক্রম বা কোডটিও উৎপাদনে দর্শকের কাছে পৌঁছায় না। একটি কাস্টম `errors.nexy` শুধুমাত্র পৃষ্ঠা প্রতিস্থাপন করে; লগ লাইন থাকে।

## বৈধতা ত্রুটি

একটি অনুপস্থিত শিরোনাম, ক্যোয়ারী প্যারামিটার বা বডি ফিল্ড প্রতিটি ক্লায়েন্টের জন্য FastAPI এর JSON বডি সহ `422` উত্তর দেয়। দেখুন [বৈধকরণ এবং ত্রুটি](../handlers/validation-and-errors.md)।

## পরবর্তী পদক্ষেপ

- [ফোল্ডার প্রতি ত্রুটি পৃষ্ঠা](folder-pages.md): একটি ফোল্ডারে আপনার নিজস্ব একটি 404, 403 বা 401
- [গতিশীল রুট](../pages/dynamic-routes.md)
- [API রুট](../handlers/README.md)
- [পরীক্ষা](../../../guides/testing.md)
