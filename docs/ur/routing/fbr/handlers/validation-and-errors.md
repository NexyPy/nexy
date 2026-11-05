# توثیق اور غلطیاں

کس طرح ایک API ہینڈلر خراب درخواست کی اطلاع دیتا ہے۔

## توثیق

ہینڈلر پیرامیٹرز کو ان کی تشریحات کے خلاف FastAPI کے ذریعہ توثیق کیا جاتا ہے۔

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| مسئلہ | حیثیت | جسم |
|---|---|---|
| غائب یا غلط استفسار، ہیڈر، کوکی یا باڈی فیلڈ | `422` | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| غلط **پاتھ** طبقہ (`/api/users/abc` `id: int` کے لیے) | `404` | نہ ملا صفحہ، یا `Accept: application/json` کے لیے JSON |

ایک پاتھ سیگمنٹ جسے تبدیل نہیں کیا جا سکتا وہ `422` کے بجائے `404` ہے: ایک متحرک راستہ کسی بھی یو آر ایل کو پکڑتا ہے، اور ایسا یو آر ایل جو تبدیل نہیں کیا جاسکتا وہ موجود نہیں ہے۔

`422` باڈی FastAPI کی معیاری شکل ہے، لہذا موجودہ کلائنٹس اور تیار کردہ SDKs کام کرتے رہتے ہیں۔

## غلطیاں بڑھانا

```python filename="src/routes/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    item = find(id)
    if item is None:
        raise HTTPException(status_code=404, detail="No such item")
    return item
```

| کلائنٹ بھیجتا ہے۔ | جواب |
|---|---|
| `Accept: application/json` | `{"detail": "No such item"}` حیثیت کے ساتھ `404` |
| `Accept: text/html` | [خرابی کا صفحہ](../errors/README.md) |
| `Accept: */*` | غلطی کا صفحہ |

API کلائنٹس میں `Accept: application/json` سیٹ کریں۔ براؤزرز کو صفحات ملتے رہتے ہیں۔

## غیر ہینڈل شدہ مستثنیات

ایک استثناء کہ آپ کا ہینڈلر جوابات `500` کو نہیں پکڑتا، اسی HTML یا JSON انتخاب کے ساتھ۔

## حسب ضرورت جوابات

جب آپ جسم کو کنٹرول کرتے ہیں تو جوابی چیز واپس کریں:

```python
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"error": "conflict"}, status_code=409)
```

## اگلے اقدامات

- [API روٹس](README.md)
- [خرابی صفحات](../errors/README.md)
- [ٹیسٹنگ](../../../guides/testing.md)
