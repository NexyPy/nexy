# روٹ ہینڈلرز

`src/routes/` کے تحت ایک `.py` فائل ایک API ہینڈلر ہے۔ فائل کا راستہ یو آر ایل ہے، اور ہر ایک فنکشن جسے HTTP طریقہ کے نام سے منسوب کیا گیا ہے ایک اختتامی نقطہ بن جاتا ہے۔

## ایک اختتامی نقطہ بنائیں

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

یہ فائل `GET /api/items` اور `POST /api/items` کا جواب دیتی ہے۔

معاون فنکشن کے نام: `GET`، `POST`، `PUT`، `PATCH`، `DELETE`، `OPTIONS`، `HEAD`۔ `SOCKET` اسی راستے پر ایک WebSocket کھولتا ہے - دیکھیں [WebSocket](../realtime/websocket.md)۔

## HTTP الفاظ

اس سے درآمد کریں جو ایک ہینڈلر کی ضرورت ہے `nexy.http`:

```python
from nexy.http import Depends, Header, HTTPException, JSONResponse, Request, status
```

یہ درخواست اور جواب کی کلاسز (`Request`، `Response`، `JSONResponse`، `HTMLResponse`، `PlainTextResponse`، `RedirectResponse`، `StreamingResponse`، `FileResponse`، پیرامیٹر کے ذرائع (`Header`، `Query`، کو ظاہر کرتا ہے۔ `Cookie`، `Path`، `Body`، `Depends`، `BackgroundTasks`، `HTTPException` اور `status`۔ اس ماڈیول کے خلاف لکھے گئے ہینڈلرز کا انحصار Nexy کے کنٹریکٹ پر ہے، نہ کہ اس انجن پر جو ان کی خدمت کرتا ہے۔ Pydantic ماڈل جسموں اور ردعمل کو معمول کے مطابق بیان کرتے ہیں۔

## پیرامیٹرز

| ماخذ | یہ کیسے آتا ہے |
|---|---|
| پاتھ سیگمنٹ `[id]` | فنکشن آرگومنٹ `id`، اس کی تشریح میں تبدیل |
| سوال کی تار | `page: int = 1` |
| JSON باڈی | Pydantic ماڈل دلیل |
| FastAPI قدیم | `Depends`، `Header`، `Cookie`، `Form`، `UploadFile` - غیر تبدیل شدہ |

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

راستہ کا حصہ `{id}` ہے، اس لیے FastAPI تصدیق کرتا ہے `id: int`۔ ایک ایسی قدر جو انٹیجر نہیں ہے جواب دیتا ہے `404`، کیونکہ ایک ڈائنامک روٹ کسی بھی یو آر ایل کو پکڑ لیتا ہے اور ایک یو آر ایل جو تبدیل نہیں کیا جا سکتا ہے وہ موجود نہیں ہے۔ دیکھیں [تصدیق اور غلطیاں](validation-and-errors.md)۔

## جوابات

| واپسی | جواب |
|---|---|
| `dict`، `list`، `BaseModel` | JSON |
| `JSONResponse`، `HTMLResponse`، کوئی بھی `Response` | بالکل جیسا کہ اعلان کیا گیا |
| `None` | خالی جواب - اس کے بجائے ایک `Response` واپس کریں جب حیثیت اہم ہو |

حسب ضرورت اسٹیٹس کوڈ یا مواد کی قسم کے لیے، جوابی اعتراض واپس کریں:

```python filename="src/routes/api/items.py"
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"created": True}, status_code=201)
```

## غلطیاں

کلائنٹس کے لیے مستثنیات FastAPI میں اضافہ کریں۔ ایک کلائنٹ جو بھیجتا ہے `Accept: application/json` وصول کرتا ہے `{"detail": "..."}` اس حیثیت کے ساتھ جو آپ نے اٹھایا ہے۔ ایک براؤزر غلطی کا صفحہ وصول کرتا ہے۔ `notfound.nexy` رینڈرز `404` اور `errors.nexy` رینڈرز `500`، ہر ایک کا دائرہ کار اس کی ڈائریکٹری میں ہے۔ دیکھیں [تصدیق اور غلطیاں](validation-and-errors.md) اور [خرابی کے صفحات](../errors/README.md)۔

## OpenAPI

ہر API روٹ تیار کردہ اسکیما میں ظاہر ہوتا ہے، کیونکہ روٹس سادہ FastAPI روٹس ہیں۔ اسکیما کو `/openapi.json` پر پیش کیا جاتا ہے اور اسکیلر کے ذریعہ `/docs` پر پیش کیا جاتا ہے۔ `nexyconfig.py` میں `useDocs = False` کے ساتھ دونوں کو غیر فعال کریں۔

## اگلے اقدامات

- [انحصارات](../dependencies/README.md): مشترکہ تصدیق اور سیٹ اپ فی ہینڈلر یا فی ڈائرکٹری
- [تصدیق اور غلطیاں](validation-and-errors.md): `422`، `404` اور JSON کی غلطیاں
- [روٹنگ](../../README.md): URL تک فائل کا راستہ
- [اعمال](../../../guides/actions.md): پیدا شدہ راستوں کے ساتھ اختتامی نقطہ
- [تشکیل](../../../reference/config.md): مڈل ویئر، CORS، سیشن
