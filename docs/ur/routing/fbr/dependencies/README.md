# انحصار اور محافظ

FastAPI انحصار کے ساتھ راستوں پر تصدیق، ڈیٹا بیس سیشنز اور دیگر سیٹ اپ کا اشتراک کریں۔ وہ دو سطحوں پر کام کرتے ہیں، اور ڈائریکٹری کی سطح ترتیب کی طرح وراثت میں ملی ہے۔

| سطح | کہاں | پر لاگو ہوتا ہے۔ |
|---|---|---|
| ڈائرکٹری | `dependencies.py` | ڈائرکٹری میں ہر راستہ اور نیچے، صفحات شامل ہیں۔ |
| ہینڈلر | `Depends`، `@UseGuard`، `@Middleware` | ایک ہینڈلر |

## فی ڈائریکٹری: `dependencies.py`

A `dependencies.py` سادہ افعال کی `dependencies` فہرست کا اعلان کرتا ہے۔ Nexy ہر ایک کو `Depends` میں لپیٹتا ہے۔

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

> [!NOTE]
> افعال کی فہرست خود بنائیں۔ فہرست میں ایک `Depends(...)` آبجیکٹ کو نظر انداز کر دیا گیا ہے۔

`src/routes/admin/` کے تحت ہر روٹ کو اب ہیڈر، `.py` ہینڈلرز اور `.nexy` صفحات کی ضرورت ہوتی ہے۔

## وراثت

انحصار کو روٹس سے روٹ ڈائرکٹری تک جمع کیا جاتا ہے، **سب سے پہلے**، بالکل لے آؤٹ کی طرح، اور ہینڈلر کے اپنے محافظ سب سے آخر میں چلتے ہیں:

```text
src/routes/
├─ dependencies.py              1. root
└─ admin/
   ├─ dependencies.py           2. admin
   └─ users/
      ├─ dependencies.py        3. users
      └─ index.py               4. handler guards, then the handler
```

`GET /admin/users` کے لیے ترتیب ہے `root`، `admin`، `users`، ہینڈلر کے `@UseGuard` افعال، اس کے `@Middleware` افعال، پھر ہینڈلر۔ ایک روٹ گروپ (`(group)/`) کسی دوسرے کی طرح ایک ڈائریکٹری ہے، لہذا اس کا `dependencies.py` حصہ لیتا ہے۔

## فی ہینڈلر

دستخط میں `Depends` استعمال کریں، جیسے کسی بھی FastAPI ایپ میں:

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header, HTTPException


def current_user(authorization: str = Header(...)) -> str:
    if authorization != "Bearer secret":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return "ada"


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## ہینڈلر پر گارڈز اور مڈل ویئر

`@UseGuard` اور `@Middleware` ہینڈلر کے ساتھ FastAPI انحصار اس کے دستخط کو تبدیل کیے بغیر منسلک کریں۔ دونوں انحصار ہیں، ASGI مڈل ویئر نہیں:

```python filename="src/routes/admin/users/index.py"
from nexy.decorators import Middleware, UseGuard


def audit() -> None: ...


def must_be_staff(x_staff: str = Header(...)) -> None: ...


@UseGuard(must_be_staff)
@Middleware(audit)
async def GET():
    return {"ok": True}
```

حقیقی ASGI مڈل ویئر (CORS، GZip، سیشنز، آپ کے اپنے) کے لیے `useMiddlewares` اور `use*` اختیارات [مڈل ویئر اور سیکیورٹی](../../../guides/middleware-and-security.md) میں استعمال کریں۔

## انحصار میں ناکامی

ایک انحصار بڑھا کر ایک درخواست کو مسترد کرتا ہے۔ `HTTPException` جوابات آپ کے اٹھائے گئے اسٹیٹس کے ساتھ، بطور JSON برائے API کلائنٹس (`Accept: application/json`) اور براؤزرز کے لیے غلطی والے صفحے کے طور پر۔ دیکھیں [تصدیق اور غلطیاں](../handlers/validation-and-errors.md)۔

## اگلے اقدامات

- [وراثت](../inheritance.md)
- [ہینڈلر ](../handlers/README.md)
- [مڈل ویئر اور سیکورٹی](../../../guides/middleware-and-security.md)
