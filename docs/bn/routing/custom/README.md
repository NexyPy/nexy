# Nexy-এ একটি বিদ্যমান FastAPI রাউটার অন্তর্ভুক্ত করুন

Nexy-এ একটি বিদ্যমান FastAPI রাউটার অন্তর্ভুক্ত করতে, `useRouter` কে `APIRouter` এর `NexyConfig` ক্লাসে `nexyconfig.py` সেট করুন: এর রুটগুলি `src/routes/` এর ফাইলগুলির পাশে যেমন রয়েছে সেভাবে পরিবেশন করা হয়।

## কখন কাস্টম রাউটার ব্যবহার করবেন

- **ক্রমান্বয়ে স্থানান্তর**: একটি FastAPI অ্যাপ রুট অনুসারে নেক্সি রুটে চলে যায় এবং এর পুরানো রুটগুলি ইতিমধ্যে উত্তর দিতে থাকে।
- **কোড পুনঃব্যবহার**: একটি প্যাকেজ ইতিমধ্যে প্রমাণীকরণ বা বিলিংয়ের জন্য একটি `APIRouter` প্রকাশ করে।
- **একটি ব্যাকএন্ড আপনি রাখেন**: API সরল থাকে FastAPI, এবং Nexy পৃষ্ঠাগুলি যোগ করে।

## `nexyconfig.py` এ `useRouter` সেট করুন

রাউটারটি যেকোনও FastAPI `APIRouter`, আপনি যেভাবে লিখছেন সেভাবে লেখা:

```python filename="src/legacy/api.py"
from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/status")
async def status():
    return {"status": "ok"}


@router.get("/users/{id}")
async def user(id: int):
    return {"id": id}
```

`useRouter` হল `NexyConfig` শ্রেণীর একটি ক্ষেত্র, যেমন প্রকল্পের প্রতিটি সেটিং:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

`nx dev` তারপর উত্তর দেয় `GET /api/status` এবং `GET /api/users/{id}`, এবং `/docs` তাদের তালিকা করে।

> [!NOTE]
> `useRouter` মধ্যে `nexyconfig.py` একটি সেটিং। `from nexy import useRouter` আরেকটি জিনিস: হুক একটি `.nexy` পৃষ্ঠা বর্তমান রুট পড়ার জন্য ব্যবহার করে। রাউটার কনফিগার করতে এটি আমদানি করবেন না।

## বেশ কয়েকটি রাউটার

`useRouter` একটি রাউটার লাগে। `include_router` সহ এক অভিভাবকের অধীনে একাধিক সংগ্রহ করুন:

```python filename="src/legacy/__init__.py"
from fastapi import APIRouter

from .api import router as api
from .auth import router as auth

router = APIRouter()
router.include_router(api)
router.include_router(auth, prefix="/auth")
```

```python filename="src/legacy/auth.py"
from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login():
    return {"token": "demo"}
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

## এর পাশে পৃষ্ঠা এবং রুট ফাইল

`src/routes/` এখনও পড়া হয় যখন `useRouter` সেট থাকে: একটি `.nexy` পৃষ্ঠা বা একটি `.py` রুট ফাইল অন্তর্ভুক্ত রুটের পাশে উত্তর দেয়।

```nexy filename="src/routes/index.nexy"
---
title = "Home"
---
<h1>{{ title }}</h1>
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"ok": True}
```

`useRouter` সেট করার সময় দুটি সীমা:

- পৃষ্ঠাগুলি `layout.nexy` দ্বারা মোড়ানো হয় না;
- `useCSR = True` প্রত্যাখ্যান করা হয়েছে: `nx dev` এবং `nx build` উত্তর `useCSR requires file-based routing`।

একটি URL একবার উত্তর দেওয়া হয়. অন্তর্ভুক্ত রাউটারটিকে একটি উপসর্গ দিন, এখানে `/api`, এবং `src/routes/` এর ফাইলগুলি এটি ব্যবহার করা পাথগুলি থেকে দূরে রাখুন।

## একটি সম্পূর্ণ FastAPI অ্যাপ

`useRouter` একটি `APIRouter` লাগে, একটি `FastAPI` অ্যাপ নয়। একটি অ্যাপের রুট তার `router` বৈশিষ্ট্যের উপর বসে:

```python filename="src/legacy/service.py"
from fastapi import FastAPI

service = FastAPI(title="Billing")


@service.get("/billing/invoices")
async def invoices():
    return []
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.service import service


class NexyConfig(NexyConfigModel):
    useRouter = service.router
```

অ্যাপের নিজস্ব মিডলওয়্যার, ব্যতিক্রম হ্যান্ডলার এবং স্টার্টআপ ইভেন্টগুলি পিছনে থাকে: তাদের `useMiddlewares` এবং `nexyconfig.py`-এর অন্যান্য ক্ষেত্রগুলিতে নিয়ে যান।

## নির্ভরতা, প্রমাণীকরণ এবং ডাটাবেস

রাউটারটি Nexy প্রক্রিয়ায় চলে, তাই `Depends`, সিকিউরিটি স্কিম এবং ডাটাবেস সেশনগুলি মূল অ্যাপের মতোই কাজ করে:

```python filename="src/legacy/secure.py"
from fastapi import APIRouter, Depends, Header, HTTPException


def require_token(x_token: str = Header("")) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=401, detail="Bad token")


router = APIRouter(prefix="/secure", dependencies=[Depends(require_token)])


@router.get("/data")
async def data():
    return {"data": 42}
```

## এটি পরীক্ষা করুন

```python filename="tests/test_legacy.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_the_included_route_answers():
    assert TestClient(app).get("/api/status").json() == {"status": "ok"}
```

## পরবর্তী পদক্ষেপ

- [থেকে FastAPI নেক্সিতে](../../coming-from/fastapi.md): রুটগুলিকে ফাইলগুলিতে সরান, একে একে
- [ফাইল-ভিত্তিক রাউটিং](../fbr/README.md)
- [মডুলার রাউটিং ](../modular/README.md): `useRouter = AppModule`
