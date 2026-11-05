# مڈل ویئر فائلیں۔

روٹس ڈائرکٹری میں ایک `middleware.py` اس ڈائرکٹری کے ذریعہ ہینڈل کی گئی درخواستوں کو لپیٹ دیتا ہے۔ لے آؤٹ اور `dependencies.py` کی طرح، فائلیں روٹ سے نیچے، سب سے باہر سب سے پہلے اسٹیک ہوتی ہیں۔

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request
from nexy.http import JSONResponse


async def middleware(request: Request, call_next):
    if request.headers.get("authorization") != "Bearer secret":
        return JSONResponse({"detail": "login required"}, status_code=401)
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

فنکشن ہے `async def middleware(request, call_next)`: FastAPI کے `@app.middleware("http")` کے دستخط۔ راستے پر جانے کے لیے `await call_next(request)` کو کال کریں، یا وہاں رکنے کے لیے جواب واپس کریں۔ کال کے بعد کا کوڈ راستے میں چلتا ہے اور جواب کو تبدیل کرسکتا ہے۔

## یہ کیا لپیٹتا ہے

ایک مڈل ویئر پر لاگو ہوتا ہے۔ **روٹس جن کی فائل اس کی ڈائرکٹری میں ہے** یا نیچے، صفحات اور API ہینڈلرز ایک جیسے ہیں، روٹ گروپس شامل ہیں:

```text
src/routes/
├─ middleware.py             every route
├─ open.py                   root only
├─ admin/
│  ├─ middleware.py          /admin and everything below
│  └─ users/
│     ├─ middleware.py       /admin/users and below
│     └─ index.py            root > admin > users
└─ (shop)/
   ├─ middleware.py          only the routes in this group
   └─ cart.py                root > shop     (URL: /cart)
```

`/admin/users` کی درخواست کے لیے حکم ہے `root`، `admin`، `users`، پھر راستہ۔ ایک گروپ کا اپنا کوئی یو آر ایل نہیں ہے، اس لیے اسے اس راستے سے ملایا جاتا ہے جو درخواست کو پورا کرتا ہے، یو آر ایل کے ذریعے نہیں۔

ایک URL جو کسی روٹ سے میل نہیں کھاتا ہے (a 404) صرف ڈائرکٹریوں کا مڈل ویئر وصول کرتا ہے جو گروپ نہیں ہیں، URL کے سابقہ ​​کے ذریعہ منتخب کی گئی ہیں۔ `[slug]` ایک طبقہ سے میل کھاتا ہے اور `[...rest]` بقیہ سے ملتا ہے۔

## یہ کیا لپیٹ نہیں کرتا

- فریم ورک اور اثاثہ جات کے یو آر ایل: `/__nexy__/`، `/_nexy/`، `/public/`، `/assets/` اور `/@...` (Vite)۔
- WebSocket ہینڈلرز اور سرور کی عمر: صرف HTTP درخواستیں۔
- ڈائریکٹریز میں فائلیں `_` یا `.` سے شروع ہوتی ہیں۔

## مڈل ویئر، انحصار یا محافظ

| استعمال کریں | جب |
|---|---|
| `middleware.py` | آپ کو بھی **جواب** کی ضرورت ہے: ہیڈر، ری ڈائریکٹ، ٹائمنگ، پورے علاقے کے لیے شارٹ سرکیٹنگ |
| [`dependencies.py`](../dependencies/README.md) | آپ کو پارس شدہ پیرامیٹرز کی ضرورت ہے یا کسی قدر (موجودہ صارف، ڈیٹا بیس سیشن) کو انجیکشن کرنے کے لیے |
| `@UseGuard` ایک ہینڈلر پر | ایک راستے کو اضافی چیک کی ضرورت ہے |
| `useMiddlewares` [config](../../../reference/config.md) | میں پوری ایپلیکیشن (CORS، GZip، سیشنز) کے لیے ایک ASGI مڈل ویئر |

مڈل ویئر فائلیں انحصار سے **پہلے** چلتی ہیں: جب انحصار شروع ہوتا ہے تو درخواست اس کی ہر `middleware.py` ڈائریکٹریوں سے گزر جاتی ہے۔

## قواعد

- فائل کو `async def middleware(request, call_next)` کی وضاحت کرنی چاہیے۔ بصورت دیگر Nexy شروع ہونے پر رک جاتا ہے اور فائل کو نام دیتا ہے۔
- یہ ایک عام Python ماڈیول ہے: جس چیز کی ضرورت ہو اسے درآمد کریں۔ یہ ایک بار لوڈ ہوتا ہے، جب سرور شروع ہوتا ہے۔
- یہ کبھی بھی راستہ نہیں ہے: `/middleware` ایک 404 ہے۔
- بنیادی راستے کی جانچ پڑتال `request.scope["path"]` پر ہوتی ہے، کبھی بھی `request.url.path` یا `Host` ہیڈر پر نہیں: CVE-2026-48710 کے بعد سے URL آبجیکٹ سرور کو موصول ہونے والے راستے سے متفق نہیں ہوسکتا ہے۔ دیکھیں [سیکیورٹی](../../../reference/security.md)۔

## لاگت

بغیر کسی `middleware.py` کا پروجیکٹ کچھ بھی ادا نہیں کرتا: پرت انسٹال نہیں ہے۔ فائلوں کے ساتھ، ہر مماثل مڈل ویئر ایک Starlette `BaseHTTPMiddleware` شامل کرتا ہے؛ انہیں چھوٹا رکھیں.

## اگلے اقدامات

- [وراثت](../inheritance.md)
- [انحصارات](../dependencies/README.md)
- [مڈل ویئر اور سیکورٹی ](../../../guides/middleware-and-security.md)
