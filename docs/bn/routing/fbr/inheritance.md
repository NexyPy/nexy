# উত্তরাধিকার

`src/routes/`-এর বেশ কিছু ফাইল তাদের ডিরেক্টরির নীচের সমস্ত কিছুতে প্রযোজ্য। তারা সবাই একইভাবে সমাধান করে: Nexy রুটের ডিরেক্টরি থেকে শুরু হয় এবং `src/routes/` পর্যন্ত চলে।

```text
src/routes/
├─ layout.nexy               1. outermost
├─ dependencies.py           1. runs first
├─ middleware.py             1. wraps first
├─ notfound.nexy             fallback for every URL
├─ (shop)/                   a group is a directory: it takes part, it is not in the URL
│  ├─ layout.nexy            2.
│  ├─ dependencies.py        2.
│  └─ cart/
│     ├─ layout.nexy         3. innermost
│     ├─ dependencies.py     3. runs last
│     └─ index.nexy          the page
```

| ফাইল | নিয়ম |
|---|---|
| `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` | রুট থেকে পৃষ্ঠা পর্যন্ত প্রতিটি বিন্যাস এটিকে মোড়ানো, **প্রথম বাইরের** |
| `middleware.py` | রুট থেকে রুট পর্যন্ত প্রতিটি ফাইল রিকোয়েস্ট মোড়ক করে, **বাইরের সর্বপ্রথম**, নির্ভরতার আগে |
| `dependencies.py` | রুট থেকে রুট পর্যন্ত প্রতিটি ফাইল চলে, **প্রথমে বাইরের**, তারপর হ্যান্ডলারের নিজস্ব গার্ড |
| `notfound.nexy`, `errors.nexy` | দ **নিকটতম** একটি জিতেছে, প্রতি স্ট্যাটাস কোড |

উপরের পৃষ্ঠার জন্য, লেআউটগুলি `root layout > (shop) layout > cart layout > page` হিসাবে নেস্ট করে এবং নির্ভরতাগুলি `root > (shop) > cart > handler guards` হিসাবে চলে।

## কেন বাইরেরতম প্রথম

একটি বাইরের বিন্যাস ফ্রেমটি আঁকে এবং একটি বাইরের নির্ভরতা সিদ্ধান্ত নেয় কে আদৌ আসতে পারে। এগুলিকে প্রথমে রাখার অর্থ হল অভ্যন্তরীণগুলি তাদের উপর নির্ভর করতে পারে: একটি ডিরেক্টরি যা প্রমাণীকরণের প্রয়োজন হয় এমন একটি হ্যান্ডলারের আগে চলে যা ব্যবহারকারীকে পড়ে।

গাছের `(shop)` নির্ভরতা কার্ট কুকি চেক করে, তাই নীচের কার্ট নির্ভরতা আবার চেক না করেই কার্ট পড়তে পারে:

```python filename="src/routes/(shop)/dependencies.py"
from nexy.http import HTTPException, Request


def require_cart(request: Request) -> None:
    if "cart" not in request.cookies:
        raise HTTPException(status_code=400, detail="No cart")


dependencies = [require_cart]
```

## বিন্যাস

একটি ফোল্ডার ফ্যামিলি স্ট্যাকের সমস্ত লেআউট ফাইল: [লেআউটস](layouts/README.md) দেখুন। বিভিন্ন পরিবার মিশ্রিত হয় না: একটি `layout.vue` কখনও একটি `.tsx` পৃষ্ঠা মোড়ানো হয় না, এবং একটি প্রকল্পে হয় `layout.nexy` বা ক্লায়েন্ট লেআউট থাকে, উভয়ই ([মোড](modes.md)) নয়।

গাছের অভ্যন্তরীণ লেআউটটি শুধুমাত্র তার নিজস্ব ফ্রেম যুক্ত করে: এর চারপাশে মূল বিন্যাসটি এখনও নথিটি আঁকে।

```nexy filename="src/routes/(shop)/cart/layout.nexy"
---
children: prop[NexyElement]
---
<section class="cart">
  <h2>Your cart</h2>
  {{ children | safe }}
</section>
```

## মিডলওয়্যার ফাইল

[মিডলওয়্যার ফাইলগুলি](middleware/README.md) দেখুন: তারা নির্ভরতার আগে চলে এবং রুটে না পৌঁছে উত্তর দিতে পারে।

একটি শিকড় `middleware.py` গাছের প্রতিটি রুটকে মোড়ানো, কার্টে অন্তর্ভুক্ত:

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## নির্ভরতা

দেখুন [নির্ভরতা](dependencies/README.md) একটি হ্যান্ডলার ফাইলের অর্ডারের জন্য, `@UseGuard` এবং `@Middleware` সহ।

## ত্রুটি পৃষ্ঠা

`notfound.nexy` এবং `errors.nexy` রুট রুটে একবার ইনস্টল করা হয়; একটি সাবডিরেক্টরিতে একটি অনুলিপি সেই উপসর্গের জন্য পৃষ্ঠাটিকে পরিমার্জন করে। [ত্রুটির পৃষ্ঠাগুলি](errors/README.md) দেখুন।

`cart/` এর একটি অনুলিপি `/cart` এর অধীনে 404 এর উত্তর দেয়, এবং মূলটি বাকিটি রাখে:

```nexy filename="src/routes/(shop)/cart/notfound.nexy"
<h1>This product is gone</h1>
<p><a href="/cart">Back to your cart</a></p>
```

## পরবর্তী পদক্ষেপ

- [বিন্যাস](layouts/README.md)
- [নির্ভরতা ](dependencies/README.md)
- [ত্রুটি পৃষ্ঠাগুলি](errors/README.md)
