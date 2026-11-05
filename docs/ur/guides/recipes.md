# ترکیبیں

تقریباً ہر ایپ کو تین چیزوں کی ضرورت ہوتی ہے، مکمل فائلوں کے بطور آپ کاپی کر سکتے ہیں۔ `filename` کے ساتھ نیچے کا ہر کوڈ بلاک ایک تازہ پروجیکٹ میں لکھا جاتا ہے اور ٹیسٹ سوٹ کے ذریعہ استعمال کیا جاتا ہے، لہذا آپ جو پڑھتے ہیں وہی چلتا ہے۔

وہ سادہ API ہینڈلرز استعمال کرتے ہیں۔ ایک ہی فنکشن کسی بھی صفحے کے پیچھے [موڈ](../routing/fbr/modes.md) میں کام کرتے ہیں۔

## سیشن کے ساتھ سائن ان کریں۔

ایک وزیٹر ایک نام اور پاس ورڈ پوسٹ کرتا ہے، سرور انہیں دستخط شدہ کوکی میں یاد رکھتا ہے، اور `/api/account` کے تحت ہر چیز کسی اور کے لیے بند کردی جاتی ہے۔

سیشنز آن کریں۔ انہیں ضرورت ہے `itsdangerous` (`uv add itsdangerous`):

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me-in-production"}
```

سائن ان اور آؤٹ:

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

ایک [`dependencies.py`](../routing/fbr/dependencies/README.md) کے ساتھ پورے فولڈر کی حفاظت کریں:

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

> [!نوٹ]
> اصلی پاس ورڈز کو ماخذ سے دور رکھیں۔ ایک ہیش اسٹور کریں (`argon2`، `bcrypt`) اور ماحول سے خفیہ کلید پڑھیں۔ سیشن کوکی پر دستخط شدہ ہیں، انکرپٹ نہیں ہیں۔

## تخلیق، پڑھنے اور حذف کے ساتھ ایک JSON API

ماڈیول میں ایک اسٹور، جمع کرنے کا راستہ اور آئٹم کا راستہ۔ لغت کو [ایک ڈیٹا بیس](databases.md) سے تبدیل کریں جب ڈیٹا کو دوبارہ شروع کرنا ضروری ہے۔

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

آپ کے کوڈ کے چلنے سے پہلے ایک باڈی جو `NewNote` فٹ نہیں ہوتی اسے `422` سے انکار کر دیا جاتا ہے، اور واپسی کی تشریح دستاویزی جواب بن جاتی ہے۔ دیکھیں [تصدیق اور غلطیاں](../routing/fbr/handlers/validation-and-errors.md)۔

## ایک فائل وصول کریں۔

اپ لوڈز کی ضرورت ہے `python-multipart` (`uv add python-multipart`)۔ سائز خود چیک کریں، اور کلائنٹ کے فائل کا نام کبھی بھی راستے کے طور پر استعمال نہ کریں:

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

`Path(...).name` کسی بھی فولڈر کو گرا دیتا ہے جو کلائنٹ کا نام رکھتا ہے، جیسے `../../etc/passwd`۔ بائٹس کو اس نام کے تحت محفوظ کریں جو آپ تیار کرتے ہیں، اس کے تحت نہیں۔

## اگلے اقدامات

- [ایکشنز](actions.md): فارم اور بٹن کے لیے ٹائپ شدہ سرور کے افعال
- [مڈل ویئر اور سیکیورٹی](middleware-and-security.md): CORS، میزبان، سیشن
- [ٹیسٹنگ](testing.md): اپنے ہینڈلرز کی اسی طرح جانچ کریں۔
