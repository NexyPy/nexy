# মিডলওয়্যার ফাইল

একটি রুট ডিরেক্টরিতে একটি `middleware.py` সেই ডিরেক্টরি দ্বারা পরিচালিত অনুরোধগুলিকে মোড়ানো হয়। লেআউট এবং `dependencies.py` এর মতো, ফাইলগুলি রুট থেকে স্ট্যাক ডাউন, বাইরেরতম প্রথমে।

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request
from nexy.http import JSONResponse


async def middleware(request: Request, call_next):
    if request.headers.get("authorization") != "Bearer secret":
        return JSONResponse({"detail": "login required"}, status_code=401)
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

ফাংশনটি হল `async def middleware(request, call_next)`: FastAPI এর `@app.middleware("http")` স্বাক্ষর। রুট চালিয়ে যেতে `await call_next(request)` কে কল করুন, অথবা সেখানে থামার জন্য একটি প্রতিক্রিয়া ফেরত দিন। কল চলার পরে কোড আউট হওয়ার পথে এবং প্রতিক্রিয়া পরিবর্তন করতে পারে।

## এটা কি মোড়ানো

একটি মিডলওয়্যার প্রযোজ্য **রুটের ক্ষেত্রে যার ফাইল তার ডিরেক্টরিতে রয়েছে** বা নীচে, পৃষ্ঠা এবং API হ্যান্ডলার একইভাবে, রুট গ্রুপগুলি অন্তর্ভুক্ত:

```text
src/routes/
├─ middleware.py             every route
├─ open.py                   root only
├─ admin/
│  ├─ middleware.py          /admin and everything below
│  └─ users/
│     ├─ middleware.py       /admin/users and below
│     └─ index.py            root > admin > users
└─ (shop)/
   ├─ middleware.py          only the routes in this group
   └─ cart.py                root > shop     (URL: /cart)
```

একটি অনুরোধের জন্য `/admin/users` অর্ডার হল `root`, `admin`, `users`, তারপর রুট। একটি গোষ্ঠীর নিজস্ব কোনো URL নেই, তাই এটি সেই রুটের মাধ্যমে মেলে যা অনুরোধটি পরিবেশন করে, URL এর মাধ্যমে নয়।

একটি ইউআরএল যা কোনো রুটের সাথে মেলে না (একটি 404) শুধুমাত্র সেই ডিরেক্টরিগুলির মিডলওয়্যার গ্রহণ করে যেগুলি গোষ্ঠী নয়, URL উপসর্গ দ্বারা নির্বাচিত। `[slug]` একটি অংশের সাথে মেলে এবং `[...rest]` বাকি অংশের সাথে মেলে।

## এটা কি মোড়ানো হয় না

- ফ্রেমওয়ার্ক এবং সম্পদ URL: `/__nexy__/`, `/_nexy/`, `/public/`, `/assets/` এবং `/@...` (Vite)।
- WebSocket হ্যান্ডলার এবং সার্ভারের জীবনকাল: শুধুমাত্র HTTP অনুরোধ।
- ডিরেক্টরিতে ফাইলগুলি `_` বা `.` দিয়ে শুরু হয়।

## মিডলওয়্যার, নির্ভরতা বা গার্ড

| ব্যবহার করুন | যখন |
|---|---|
| `middleware.py` | আপনারও **প্রতিক্রিয়া[** দরকার: শিরোনাম, পুনঃনির্দেশ, সময়, একটি পুরো এলাকার জন্য শর্ট সার্কিটিং |
| [`dependencies.py`](../dependencies/README.md) | আপনার পার্স করা পরামিতি প্রয়োজন বা একটি মান ইনজেক্ট করতে (বর্তমান ব্যবহারকারী, ডাটাবেস সেশন) |
| `@UseGuard` একটি হ্যান্ডলারে | একটি রুটে একটি অতিরিক্ত চেক প্রয়োজন |
| `useMiddlewares` [কনফিগারে](../../../reference/config.md) | পুরো অ্যাপ্লিকেশনের জন্য একটি ASGI মিডলওয়্যার (CORS, GZip, সেশন) |

মিডলওয়্যার ফাইলগুলি **নির্ভরতার আগে** চালানো হয়: যখন নির্ভরতা শুরু হয় তখন অনুরোধটি এর প্রতিটি `middleware.py` ডিরেক্টরি অতিক্রম করে।

## নিয়ম

- ফাইল অবশ্যই সংজ্ঞায়িত `async def middleware(request, call_next)`. অন্যথায় Nexy স্টার্টআপে থামে এবং ফাইলটির নাম দেয়।
- এটি একটি স্বাভাবিক Python মডিউল: আপনার যা প্রয়োজন তা আমদানি করুন। এটি একবার লোড হয়, যখন সার্ভার শুরু হয়।
- এটি কখনই একটি রুট নয়: `/middleware` একটি 404।
- বেস পাথ `request.scope["path"]`-এ চেক করে, কখনোই `request.url.path` বা `Host` হেডারে: যেহেতু CVE-2026-48710 ইউআরএল অবজেক্ট সার্ভারের প্রাপ্ত পথের সাথে একমত হতে পারে না। দেখুন [নিরাপত্তা](../../../reference/security.md)।

## খরচ

কোন `middleware.py` ছাড়া একটি প্রকল্প কিছুই প্রদান করে না: স্তর ইনস্টল করা হয় না। ফাইলের সাথে, প্রতিটি মিলে যাওয়া মিডলওয়্যার একটি Starlette `BaseHTTPMiddleware` যোগ করে; তাদের ছোট রাখুন।

## পরবর্তী পদক্ষেপ

- [উত্তরাধিকার](../inheritance.md)
- [নির্ভরতা](../dependencies/README.md)
- [মিডলওয়্যার এবং নিরাপত্তা](../../../guides/middleware-and-security.md)
