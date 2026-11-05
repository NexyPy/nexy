# وصفات

ثلاثة أشياء يحتاجها كل تطبيق تقريبًا، مثل الملفات الكاملة التي يمكنك نسخها. تتم كتابة كل كتلة تعليمات برمجية أدناه مع `filename` في مشروع جديد ويتم ممارستها بواسطة مجموعة الاختبار، لذا فإن ما تقرأه هو ما يتم تشغيله.

يستخدمون معالجات API العادية؛ تعمل نفس الوظائف خلف الصفحة في أي من [الوضع](../routing/fbr/modes.md).

## قم بتسجيل الدخول بجلسة

يقوم الزائر بنشر اسم وكلمة مرور، ويتذكرهما الخادم في ملف تعريف ارتباط موقع، وكل شيء تحت `/api/account` مغلق أمام أي شخص آخر.

تشغيل الجلسات. يحتاجون إلى `itsdangerous` (`uv add itsdangerous`):

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me-in-production"}
```

تسجيل الدخول والخروج:

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

قم بحماية مجلد كامل باستخدام [`dependencies.py` ](../routing/fbr/dependencies/README.md)] واحد:

```python filename="src/routes/api/account/dependeency.py"
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

> [!ملاحظة]
> احتفظ بكلمات المرور الحقيقية بعيدًا عن المصدر. قم بتخزين التجزئة (`argon2`، `bcrypt`) وقراءة المفتاح السري من البيئة. ملف تعريف الارتباط للجلسة موقع وليس مشفرًا.

## واجهة برمجة تطبيقات JSON مع الإنشاء والقراءة والحذف

متجر في وحدة نمطية ومسار تجميع ومسار عنصر. استبدل القاموس بـ [قاعدة بيانات](databases.md) عندما يجب أن تظل البيانات على قيد الحياة عند إعادة التشغيل.

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

يتم رفض النص الذي لا يتناسب مع `NewNote` مع `422` قبل تشغيل التعليمات البرمجية الخاصة بك، ويصبح التعليق التوضيحي المرتجع هو الاستجابة الموثقة. انظر [التصديق والأخطاء](../routing/fbr/handlers/validation-and-errors.md).

## تلقي ملف

تحتاج التحميلات إلى `python-multipart` (`uv add python-multipart`). تحقق من الحجم بنفسك، ولا تستخدم أبدًا اسم ملف العميل كمسار:

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

`Path(...).name` يسقط أي مجلد يضعه العميل في الاسم، مثل `../../etc/passwd`. احفظ البايتات تحت الاسم الذي تنشئه، وليس تحت هذا الاسم.

## الخطوات التالية

- [الإجراءات](actions.md)]: وظائف الخادم المكتوبة للنماذج والأزرار
- [البرامج الوسيطة والأمن](middleware-and-security.md): CORS، المضيفون، الجلسات
- [اختبار](testing.md): اختبر معالجاتك بنفس الطريقة
