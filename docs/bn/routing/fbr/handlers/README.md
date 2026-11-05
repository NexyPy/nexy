# রুট হ্যান্ডলার

`src/routes/` এর অধীনে একটি `.py` ফাইল হল একটি API হ্যান্ডলার। ফাইল পাথ হল URL, এবং একটি HTTP পদ্ধতির নামানুসারে প্রতিটি ফাংশন একটি এন্ডপয়েন্টে পরিণত হয়।

## একটি শেষ পয়েন্ট তৈরি করুন

```python filename="src/routes/api/items.py"
from nexy.http import Request
from pydantic import BaseModel


class Item(BaseModel):
    name: str


async def GET(request: Request):
    return {"items": []}


async def POST(request: Request, body: Item):
    return {"created": body.name}
```

এই ফাইলটি উত্তর দেয় `GET /api/items` এবং `POST /api/items`।

সমর্থিত ফাংশনের নাম: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`, `HEAD`। `SOCKET` একই পথে একটি WebSocket খোলে - দেখুন [WebSocket](../realtime/websocket.md)।

## HTTP শব্দভান্ডার

একজন হ্যান্ডলারের যা প্রয়োজন তা আমদানি করুন `nexy.http` থেকে:

```python
from nexy.http import Depends, Header, HTTPException, JSONResponse, Request, status
```

এটি অনুরোধ এবং প্রতিক্রিয়া ক্লাসগুলি (`Request`, `Response`, `JSONResponse`, `HTMLResponse`, `PlainTextResponse`, `RedirectResponse`, `StreamingResponse`, `FileResponse`), প্যারামিটার উত্সগুলি (`Header`, `Query`, `Cookie`, `Path`, `Body`), `Depends`, `BackgroundTasks`, `HTTPException` এবং `status`। এই মডিউলের বিরুদ্ধে লিখিত হ্যান্ডলারগুলি Nexy এর চুক্তির উপর নির্ভর করে, তাদের পরিবেশনকারী ইঞ্জিনের উপর নয়। Pydantic মডেলগুলি যথারীতি দেহ এবং প্রতিক্রিয়া বর্ণনা করে।

## পরামিতি

| উত্স | এটি কীভাবে আসে |
|---|---|
| পাথ সেগমেন্ট `[id]` | ফাংশন আর্গুমেন্ট `id`, এর টীকাতে রূপান্তরিত |
| কোয়েরি স্ট্রিং | `page: int = 1` |
| JSON বডি | Pydantic মডেল আর্গুমেন্ট |
| FastAPI আদিম | `Depends`, `Header`, `Cookie`, `Form`, `UploadFile` - অপরিবর্তিত |

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

পাথ সেগমেন্ট হল `{id}`, তাই FastAPI যাচাই করে `id: int`। একটি মান যা একটি পূর্ণসংখ্যা নয় উত্তর দেয় `404`, কারণ একটি গতিশীল রুট যেকোনো URL ক্যাপচার করে এবং একটি URL যা রূপান্তরিত করা যায় না তার অস্তিত্ব নেই। দেখুন [বৈধকরণ এবং ত্রুটি](validation-and-errors.md)।

## প্রতিক্রিয়া

| প্রত্যাবর্তন | প্রতিক্রিয়া |
|---|---|
| `dict`, `list`, `BaseModel` | JSON |
| `JSONResponse`, `HTMLResponse`, যেকোনো `Response` | ঠিক যেমন ঘোষণা করা হয়েছে |
| `None` | খালি প্রতিক্রিয়া - স্ট্যাটাস গুরুত্বপূর্ণ হলে পরিবর্তে একটি `Response` ফেরত দিন |

একটি কাস্টম স্থিতি কোড বা বিষয়বস্তুর প্রকারের জন্য, একটি প্রতিক্রিয়া বস্তু ফেরত দিন:

```python filename="src/routes/api/items.py"
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"created": True}, status_code=201)
```

## ত্রুটি

ক্লায়েন্টদের জন্য ব্যতিক্রম FastAPI বাড়ান। একজন ক্লায়েন্ট যে পাঠায় `Accept: application/json` সে আপনার উত্থাপিত স্ট্যাটাস সহ `{"detail": "..."}` গ্রহণ করে; একটি ব্রাউজার ত্রুটি পৃষ্ঠা গ্রহণ করে। `notfound.nexy` রেন্ডারগুলি `404` এবং `errors.nexy` রেন্ডার করে `500`, প্রতিটি তার ডিরেক্টরিতে বিস্তৃত। [বৈধকরণ এবং ত্রুটি](validation-and-errors.md) এবং [ত্রুটির পৃষ্ঠাগুলি](../errors/README.md) দেখুন।

## OpenAPI

প্রতিটি API রুট জেনারেট করা স্কিমাতে প্রদর্শিত হয়, কারণ রুটগুলি প্লেইন FastAPI রুট। স্কিমাটি `/openapi.json` এ পরিবেশিত হয় এবং `/docs` এ স্কেলার দ্বারা রেন্ডার করা হয়। `nexyconfig.py`-এ `useDocs = False` দিয়ে উভয়ই নিষ্ক্রিয় করুন।

## পরবর্তী পদক্ষেপ

- [নির্ভরতা](../dependencies/README.md): শেয়ার্ড অথ এবং সেটআপ প্রতি হ্যান্ডলার বা প্রতি ডিরেক্টরি
- [বৈধকরণ এবং ত্রুটি](validation-and-errors.md): `422`, `404` এবং JSON ত্রুটি
- [রাউটিং](../../README.md): URL-এ ফাইল পাথ
- [কর্ম](../../../guides/actions.md): উৎপন্ন পাথ সহ শেষ বিন্দু
- [কনফিগ](../../../reference/config.md): মিডলওয়্যার, CORS, সেশন
