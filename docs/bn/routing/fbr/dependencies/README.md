# নির্ভরতা এবং রক্ষক

FastAPI নির্ভরতা সহ রুট জুড়ে প্রমাণীকরণ, ডাটাবেস সেশন এবং অন্যান্য সেটআপ শেয়ার করুন। তারা দুটি স্তরে কাজ করে, এবং ডিরেক্টরি স্তরটি লেআউটের মতো উত্তরাধিকারসূত্রে পাওয়া যায়।

| স্তর | যেখানে | প্রযোজ্য |
|---|---|---|
| ডিরেক্টরি | `dependencies.py` | ডিরেক্টরির প্রতিটি রুট এবং নীচে, পৃষ্ঠাগুলি অন্তর্ভুক্ত |
| হ্যান্ডলার | `Depends`, `@UseGuard`, `@Middleware` | একজন হ্যান্ডলার |

## প্রতি ডিরেক্টরি: `dependencies.py`

একটি `dependencies.py` প্লেইন ফাংশনের একটি `dependencies` তালিকা ঘোষণা করে। Nexy প্রত্যেককে `Depends` এ মোড়ানো।

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

> [!NOTE]
> ফাংশন নিজেদের তালিকা. তালিকার একটি `Depends(...)` অবজেক্ট উপেক্ষা করা হয়।

`src/routes/admin/`-এর অধীনে প্রতিটি রুটে এখন শিরোনাম, `.py` হ্যান্ডলার এবং `.nexy` পৃষ্ঠার প্রয়োজন।

## উত্তরাধিকার

নির্ভরতা সংগ্রহ করা হয় রুট রুট থেকে ডাউন রুটের ডিরেক্টরিতে, **প্রথম বাইরের**, ঠিক লেআউটের মতো, এবং হ্যান্ডলারের নিজস্ব গার্ডরা শেষ পর্যন্ত চলে:

```text
src/routes/
├─ dependencies.py              1. root
└─ admin/
   ├─ dependencies.py           2. admin
   └─ users/
      ├─ dependencies.py        3. users
      └─ index.py               4. handler guards, then the handler
```

`GET /admin/users` এর জন্য অর্ডার হল `root`, `admin`, `users`, হ্যান্ডলারের `@UseGuard` ফাংশন, এর `@Middleware` ফাংশন, তারপর হ্যান্ডলার। একটি রুট গ্রুপ (`(group)/`) অন্য যেকোন একটি ডিরেক্টরির মতো, তাই এটির `dependencies.py` অংশ নেয়।

## হ্যান্ডলার প্রতি

যেকোনো FastAPI অ্যাপের মতো স্বাক্ষরে `Depends` ব্যবহার করুন:

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header, HTTPException


def current_user(authorization: str = Header(...)) -> str:
    if authorization != "Bearer secret":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return "ada"


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## একটি হ্যান্ডলারে গার্ড এবং মিডলওয়্যার

`@UseGuard` এবং `@Middleware` স্বাক্ষর পরিবর্তন না করে একটি হ্যান্ডলারের সাথে FastAPI নির্ভরতা সংযুক্ত করে। উভয়ই নির্ভরতা, ASGI মিডলওয়্যার নয়:

```python filename="src/routes/admin/users/index.py"
from nexy.decorators import Middleware, UseGuard


def audit() -> None: ...


def must_be_staff(x_staff: str = Header(...)) -> None: ...


@UseGuard(must_be_staff)
@Middleware(audit)
async def GET():
    return {"ok": True}
```

আসল ASGI মিডলওয়্যারের জন্য (CORS, GZip, সেশন, আপনার নিজের) `useMiddlewares` এবং `use*` বিকল্পগুলি [মিডলওয়্যার এবং নিরাপত্তা](../../../guides/middleware-and-security.md) ব্যবহার করুন।

## একটি নির্ভরতা ব্যর্থ

একটি নির্ভরতা উত্থাপন দ্বারা একটি অনুরোধ প্রত্যাখ্যান. `HTTPException` আপনার উত্থাপিত স্থিতি সহ উত্তর, API ক্লায়েন্টদের জন্য JSON হিসাবে (`Accept: application/json`) এবং ব্রাউজারগুলির জন্য একটি ত্রুটি পৃষ্ঠা হিসাবে। দেখুন [বৈধকরণ এবং ত্রুটি](../handlers/validation-and-errors.md)।

## পরবর্তী পদক্ষেপ

- [উত্তরাধিকার](../inheritance.md)
- [হ্যান্ডলার](../handlers/README.md)
- [মিডলওয়্যার এবং নিরাপত্তা](../../../guides/middleware-and-security.md)
