# বৈধতা এবং ত্রুটি

কিভাবে একটি API হ্যান্ডলার একটি খারাপ অনুরোধ রিপোর্ট.

## বৈধতা

হ্যান্ডলার প্যারামিটারগুলি তাদের টীকাগুলির বিরুদ্ধে FastAPI দ্বারা যাচাই করা হয়।

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| সমস্যা | অবস্থা | শরীর |
|---|---|---|
| অনুপস্থিত বা অবৈধ ক্যোয়ারী, হেডার, কুকি বা বডি ফিল্ড | `422` | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| অবৈধ **পাথ** সেগমেন্ট (`/api/users/abc` এর জন্য `id: int`) | `404` | না-পাওয়া পৃষ্ঠা, অথবা `Accept: application/json` | এর জন্য JSON

একটি পাথ সেগমেন্ট যা রূপান্তরিত করা যায় না একটি `404` পরিবর্তে একটি `422`: একটি গতিশীল রুট যেকোনো URL ক্যাপচার করে, এবং একটি URL যা রূপান্তরিত করা যায় না তার অস্তিত্ব নেই।

`422` বডিটি FastAPI-এর আদর্শ আকৃতি, তাই বিদ্যমান ক্লায়েন্ট এবং জেনারেট করা SDKগুলি কাজ করে চলেছে।

## ত্রুটি উত্থাপন

```python filename="src/routes/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    item = find(id)
    if item is None:
        raise HTTPException(status_code=404, detail="No such item")
    return item
```

| ক্লায়েন্ট পাঠায় | প্রতিক্রিয়া |
|---|---|
| `Accept: application/json` | `{"detail": "No such item"}` স্ট্যাটাস সহ `404` |
| `Accept: text/html` | [ত্রুটির পৃষ্ঠা](../errors/README.md) |
| `Accept: */*` | ত্রুটি পৃষ্ঠা |

API ক্লায়েন্টে `Accept: application/json` সেট করুন। ব্রাউজার পেজ পেতে রাখা.

## অব্যবহিত ব্যতিক্রম

একটি ব্যতিক্রম যে আপনার হ্যান্ডলার উত্তরগুলি ধরে না `500`, একই HTML বা JSON পছন্দের সাথে।

## কাস্টম প্রতিক্রিয়া

আপনি যখন শরীর নিয়ন্ত্রণ করেন তখন একটি প্রতিক্রিয়া বস্তু ফেরত দিন:

```python
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"error": "conflict"}, status_code=409)
```

## পরবর্তী পদক্ষেপ

- [API রুট](README.md)
- [ত্রুটির পৃষ্ঠাগুলি](../errors/README.md)
- [পরীক্ষা](../../../guides/testing.md)
