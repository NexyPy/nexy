# ফোল্ডার প্রতি ত্রুটি পৃষ্ঠা

একটি ফোল্ডার তার নিজস্ব ত্রুটির উত্তর দিতে পারে: একটি 404 এর নিজস্ব শব্দে একটি ব্লগ, একটি ব্যক্তিগত এলাকা যা একটি বেয়ার `401` এর পরিবর্তে সাইন-ইন ফর্ম অফার করে৷ সাইটের বাকি পৃষ্ঠাটি আগে থেকেই ছিল।

এই পৃষ্ঠাটি সেই ফাইলগুলির মধ্যে একটি যোগ করে এবং এটির উত্তর দেখায়।

## নিয়ম

**ইউআরএল উত্তরগুলির সাথে মেলে এমন গভীরতম ফাইল।** অন্য সবকিছু যেমন আছে তেমনই থাকে: একই স্ট্যাটাস কোড, একটি API ক্লায়েন্টের জন্য JSON, এবং চেইনের কোনো ফোল্ডারে ফাইল না থাকলে বিল্ট-ইন পৃষ্ঠা।

![একটি ত্রুটি পৃষ্ঠার সুযোগ](../../../assets/error-page-scopes.svg)

জন্য `/blog/2024/hello` Nexy walks up the tree: `/blog/2024`, তারপর `/blog`, তারপর `/`। একটি ফাইল ধারণ প্রথম ফোল্ডার উত্তর. একটি ফোল্ডার সম্পূর্ণ মেলে: `/blogger/hello` `/blog` এর অধীনে নয়, তাই `blog/` এর একটি অনুলিপি কখনই এটির উত্তর দেয় না।

## চারটি ফাইল

| ফাইল | উত্তর | এতে কী পৌঁছায় |
|---|---|---|
| `notfound.nexy` | `404` | একটি URL কোনো রুট মেলে না, `notFound()` |
| `errors.nexy` | `500` | একটি ব্যতিক্রম কিছুই পরিচালনা করেনি |
| `forbidden.nexy` | `403` | `forbidden()`, `raise HTTPException(403)` |
| `unauthorized.nexy` | `401` | `unauthorized()`, `raise HTTPException(401)` |

`loading.nexy` সংরক্ষিত থাকে: এটির এখনও কোন রানটাইম প্রভাব নেই।

কোথাও একটি ফাইল `src/routes/` সেই স্থিতির উত্তর দেওয়ার জন্য Nexy-এর পক্ষে যথেষ্ট: রুটে একটি অনুলিপি পুরো প্রকল্পের উত্তর দেয়, একটি ফোল্ডারের একটি অনুলিপি সেই ফোল্ডারটির উত্তর দেয় এবং প্রতিটি অনুলিপির বাইরে একটি URL বিল্ট-ইন পৃষ্ঠা পায়। `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions` এবং `useUnauthorizedExtensions` সহ `nexyconfig.py` এই নামের জন্য আরেকটি এক্সটেনশন সংরক্ষণ করুন।

## আপনার প্রথম ফোল্ডার পৃষ্ঠা

```nexy filename="src/routes/blog/notfound.nexy"
---
title: Nothing here yet
---
<h1>That post is gone</h1>
<p>The <a href="/blog">blog</a> still has the others.</p>
```

প্রকল্পটি চালান এবং এমন একটি পোস্টের জন্য জিজ্ঞাসা করুন যা বিদ্যমান নেই:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/blog/old
# HTTP/1.1 404 Not Found
```

ফোল্ডারের বাইরের একটি URL আপনার আগে থেকে থাকা পৃষ্ঠাটিকে রাখে:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/about
# HTTP/1.1 404 Not Found    (the root page, or the built-in one)
```

## একটি 401 যা কোথাও বাড়ে

একটি সুরক্ষিত এলাকার ফোল্ডারটি পৃষ্ঠার সাথে `401` উত্তর দেয় যা এই পথের প্রস্তাব দেয়:

```nexy filename="src/routes/private/unauthorized.nexy"
---
title: Sign in to continue
---
<h1>Sign in to see your notes</h1>
<a href="/sign-in" class="button">Sign in</a>
```

```python filename="src/routes/private/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

প্রতিটি কল এবং প্রতিটি স্ট্যাটাস তার দুটি উত্তর রাখে:

| কে জিজ্ঞাসা করে | `401` একটি ফাইল সহ | `401` একটি ছাড়া |
|---|---|---|
| ব্রাউজার (`Accept: text/html`) | ফোল্ডারের পৃষ্ঠা | অন্তর্নির্মিত পৃষ্ঠা |
| ক্লায়েন্ট (`Accept: application/json`) | `{"detail": "..."}` | `{"detail": "..."}` |

`unauthorized(scheme="Bearer")` উভয় উত্তরেই `WWW-Authenticate: Bearer` যোগ করে। ব্যবহারকারীর ইনপুট থেকে তৈরি একটি বিশদ পৃষ্ঠায় HTML-এস্কেপড।

> [!TIP]
> `Accept: */*`, `curl` এবং অনেক HTTP লাইব্রেরির ডিফল্ট, HTML পৃষ্ঠা দুটির জন্যই জিজ্ঞাসা করে না এবং গ্রহণ করে না। আপনি যখন JSON উত্তর চান তখন `-H "Accept: application/json"` যোগ করুন।

## এটা পরীক্ষা করুন

```python filename="tests/test_private.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_a_private_url_asks_for_sign_in():
    answer = TestClient(app).get("/private/notes")
    assert answer.status_code == 401
    assert "Sign in" in answer.text


def test_an_api_client_gets_json():
    answer = TestClient(app).get(
        "/private/notes", headers={"accept": "application/json"}
    )
    assert answer.json() == {"detail": "Unauthorized"}
```

## পরবর্তী পদক্ষেপ

- [ত্রুটির পৃষ্ঠাগুলি](README.md): যা প্রতিটি স্থিতি, HTML বা JSON কে ট্রিগার করে
- [নির্ভরতা এবং রক্ষী ](../dependencies/README.md): একটি সম্পূর্ণ ফোল্ডার রক্ষা করুন
- [পরীক্ষা ](../../../guides/testing.md): `TestClient` প্রথম পরীক্ষা থেকে
