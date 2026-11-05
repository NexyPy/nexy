# রেসিপি

তিনটি জিনিস প্রায় প্রতিটি অ্যাপের প্রয়োজন, সম্পূর্ণ ফাইল হিসেবে আপনি কপি করতে পারেন। একটি `filename` সহ নীচের প্রতিটি কোড ব্লক একটি নতুন প্রকল্পে লেখা হয় এবং পরীক্ষা স্যুট দ্বারা অনুশীলন করা হয়, তাই আপনি যা পড়েন তা চলে।

তারা প্লেইন API হ্যান্ডলার ব্যবহার করে; একই ফাংশন একটি পৃষ্ঠার পিছনে কাজ করে [মোড](../routing/fbr/modes.md)।

## একটি অধিবেশন দিয়ে সাইন ইন করুন

একজন দর্শক একটি নাম এবং একটি পাসওয়ার্ড পোস্ট করেন, সার্ভার তাদের একটি স্বাক্ষরিত কুকিতে মনে রাখে এবং `/api/account` এর অধীনে থাকা সবকিছু অন্য কারো জন্য বন্ধ থাকে।

সেশন চালু করুন। তাদের প্রয়োজন `itsdangerous` (`uv add itsdangerous`):

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me-in-production"}
```

সাইন ইন এবং আউট:

```python filename="src/routes/api/login.py"
from pydantic import BaseModel

from nexy.http import HTTPException, Request

USERS = {"ada": "lovelace"}


class Credentials(BaseModel):
    name: str
    password: str


async def POST(request: Request, body: Credentials):
    if USERS.get(body.name) != body.password:
        raise HTTPException(status_code=401, detail="Wrong name or password")
    request.session["user"] = body.name
    return {"user": body.name}
```

```python filename="src/routes/api/logout.py"
from nexy.http import Request


async def POST(request: Request):
    request.session.clear()
    return {"signed_out": True}
```

একটি [`dependencies.py`](../routing/fbr/dependencies/README.md) দিয়ে একটি সম্পূর্ণ ফোল্ডার রক্ষা করুন:

```python filename="src/routes/api/account/dependencies.py"
from nexy.http import HTTPException, Request


def current_user(request: Request) -> str:
    if not request.session.get("user"):
        raise HTTPException(status_code=401, detail="Sign in first")
    return request.session["user"]


dependencies = [current_user]
```

```python filename="src/routes/api/account/index.py"
from nexy.http import Request


async def GET(request: Request):
    return {"user": request.session["user"]}
```

> [!দ্রষ্টব্য]
> আসল পাসওয়ার্ডগুলিকে উত্সের বাইরে রাখুন। একটি হ্যাশ সংরক্ষণ করুন (`argon2`, `bcrypt`) এবং পরিবেশ থেকে গোপন কী পড়ুন। সেশন কুকি স্বাক্ষরিত, এনক্রিপ্ট করা নয়।

## তৈরি, পড়া এবং মুছে ফেলা সহ একটি JSON API

একটি মডিউলে একটি দোকান, একটি সংগ্রহের রুট এবং একটি আইটেম রুট। [একটি ডাটাবেস](databases.md) দিয়ে অভিধানটি প্রতিস্থাপন করুন যখন ডেটা পুনরায় চালু করতে হবে।

```python filename="src/notes.py"
from pydantic import BaseModel


class Note(BaseModel):
    id: int
    title: str


NOTES: dict[int, Note] = {}
```

```python filename="src/routes/api/notes/index.py"
from pydantic import BaseModel

from src.notes import NOTES, Note


class NewNote(BaseModel):
    title: str


async def GET() -> list[Note]:
    return list(NOTES.values())


async def POST(body: NewNote) -> Note:
    note = Note(id=max(NOTES, default=0) + 1, title=body.title)
    NOTES[note.id] = note
    return note
```

```python filename="src/routes/api/notes/[id].py"
from nexy.http import HTTPException

from src.notes import NOTES, Note


async def GET(id: int) -> Note:
    if id not in NOTES:
        raise HTTPException(status_code=404, detail="No such note")
    return NOTES[id]


async def DELETE(id: int) -> dict[str, bool]:
    if NOTES.pop(id, None) is None:
        raise HTTPException(status_code=404, detail="No such note")
    return {"deleted": True}
```

আপনার কোড চলার আগে `NewNote` ফিট না হওয়া একটি বডি `422` দিয়ে প্রত্যাখ্যান করা হয় এবং রিটার্ন টীকাটি নথিভুক্ত প্রতিক্রিয়া হয়ে ওঠে। দেখুন [বৈধকরণ এবং ত্রুটি](../routing/fbr/handlers/validation-and-errors.md)।

## একটি ফাইল গ্রহণ

আপলোডের প্রয়োজন `python-multipart` (`uv add python-multipart`)। আকারটি নিজেই পরীক্ষা করুন এবং ক্লায়েন্টের ফাইলের নামটি কখনই পথ হিসাবে ব্যবহার করবেন না:

```python filename="src/routes/api/upload.py"
from pathlib import Path

from nexy.http import HTTPException, UploadFile

MAX_BYTES = 1_000_000


async def POST(file: UploadFile) -> dict[str, int | str]:
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    name = Path(file.filename or "upload").name
    return {"name": name, "size": len(data)}
```

`Path(...).name` ক্লায়েন্টের নামে যে কোনো ফোল্ডার ফেলে দেয়, যেমন `../../etc/passwd`। আপনার তৈরি করা একটি নামের অধীনে বাইটগুলি সংরক্ষণ করুন, এটির অধীনে নয়।

## পরবর্তী পদক্ষেপ

- [ক্রিয়াগুলি](actions.md): ফর্ম এবং বোতামগুলির জন্য টাইপ করা সার্ভার ফাংশন
- [মিডলওয়্যার এবং নিরাপত্তা](middleware-and-security.md): CORS, হোস্ট, সেশন
- [পরীক্ষা](testing.md): একইভাবে আপনার নিজের হ্যান্ডলারদের পরীক্ষা করুন
