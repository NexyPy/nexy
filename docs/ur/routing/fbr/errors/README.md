# خرابی والے صفحات

ایک درخواست جو ناکام ہو جاتی ہے اسے اب بھی آپ کی باقی سائٹ کی طرح جواب دینا چاہیے: ایک وزیٹر کے لیے آپ کے اپنے الفاظ میں ایک صفحہ، API کلائنٹ کے لیے JSON جیسی ناکامی۔ Nexy دونوں کا جواب دیتا ہے، اور ایک فائل ہر جواب کی جگہ لے لیتی ہے۔

یہ صفحہ نقشہ ہے: کون سی فائل جواب دیتی ہے کہ کون سی حیثیت ہے، اور اپنا پہلا صفحہ کیسے بنانا ہے۔ فولڈر کے صفحات کو [اپنا صفحہ](folder-pages.md) ملتا ہے۔

## ایک ناکامی، دو جواب

```diagram filename="جو ناکام درخواست کا جواب دیتا ہے۔"
a request that fails
      │
      ├── a browser (Accept: text/html)              ──►  an HTML page
      └── an API client (Accept: application/json)   ──►  {"detail": "…"}  with the same status

the HTML page
      ├── the deepest folder of the URL that holds a file   ──►  your file
      └── no folder of the chain holds one                 ──►  the built-in page
```

## آپ کا پہلا صفحہ

`src/routes/notfound.nexy` بنائیں اور لکھیں کہ آنے والے کو کیا پڑھنا چاہئے:

```nexy filename="src/routes/notfound.nexy"
---
title: Page not found
---
<h1>Page not found</h1>
<p>The page moved or never existed. <a href="/">Back home</a>.</p>
```

محفوظ کریں، اور یو آر ایل کے لیے پوچھیں کچھ بھی کام نہیں کرتا:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/nowhere
# HTTP/1.1 404 Not Found
```

روٹس روٹ پر موجود فائل پورے پروجیکٹ کا جواب دیتی ہے۔ ایک فولڈر میں ایک کاپی صرف اس فولڈر کا جواب دیتی ہے اور [باقی کو اسی طرح رکھتی ہے](folder-pages.md)۔ بغیر کسی فائل کے، Nexy اپنے بلٹ ان اسٹائل والے صفحے کو پیش کرتا ہے۔

## جو فائل جواب دیتی ہے۔

| فائل | جوابات |
|---|---|
| `notfound.nexy` | `404` اس کی ڈائرکٹری کے لیے |
| `errors.nexy` | `500` اس کی ڈائرکٹری کے لیے |
| `forbidden.nexy` | `403` اس کی ڈائریکٹری کے لیے |
| `unauthorized.nexy` | `401` اس کی ڈائریکٹری کے لیے |
| `loading.nexy` | محفوظ؛ ابھی تک کوئی رن ٹائم اثر نہیں |

| صورتحال | جواب |
|---|---|
| کوئی راستہ نہیں ملتا | `404` |
| ایک متحرک طبقہ کو اس کی تشریح میں تبدیل نہیں کیا جا سکتا | `404` |
| صفحہ یا API ہینڈلر میں ایک غیر ہینڈل شدہ استثناء | `500` |
| `raise HTTPException(status_code=403)` | وہ اسٹیٹس جسے آپ نے اٹھایا، بطور HTML یا JSON |
| `notFound()`، `forbidden()`، `unauthorized()` | `404`، `403`، `401`، درخواست میں کہیں سے بھی |
| `redirect()`، `permanentRedirect()` | ایک حقیقی ری ڈائریکٹ بغیر کسی خامی کے صفحہ |

## ایک صفحہ چھوڑیں یا کوڈ سے جواب دیں۔

`redirect`، `permanentRedirect`، `notFound`، `forbidden` اور `unauthorized` ایک HTTP استثنیٰ کو بڑھاتے ہیں، لہذا وہی کال ایک `.nexy` صفحہ، ایک API ہینڈلر، ایک ماڈیولر کنٹرولر، ایک گارڈ اور `dependencies.py` میں کام کرتی ہے۔ کلائنٹ پر ان کے ایک جیسے نام ہیں (`@nexy/client`)۔

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound, redirect

from src.posts import find

slug: prop[str]
post = find(slug)
if post is None:
    notFound()
if post.moved_to:
    redirect(post.moved_to)
---
<h1>{{ post.title }}</h1>
```

| کال | جواب |
|---|---|
| `redirect(url)` | `307`؛ `redirect(url, status=303)` فارم کے بعد پوسٹ کو GET میں بدل دیتا ہے |
| `permanentRedirect(url)` | `308`؛ براؤزر اور سرچ انجن اسے یاد رکھتے ہیں |
| `notFound(detail=None)` | `404`: `notfound` صفحہ، یا API کلائنٹ کے لیے JSON |
| `forbidden(detail=None)` | `403`: آنے والا جانتا ہے لیکن اسے دیکھ نہیں سکتا |
| `unauthorized(detail=None, scheme=None)` | `401`؛ `scheme="Bearer"` شامل کرتا ہے `WWW-Authenticate` |

ایک API کلائنٹ کو بھی `Location` ہیڈر اور بغیر صفحہ کے جوابات کو ری ڈائریکٹ کرتا ہے۔ ان اقدار سے منزل کی تعمیر کریں جن پر آپ بھروسہ کرتے ہیں: a `redirect(request.query_params["next"])` جہاں بھی لنک کہتا ہے وہاں آنے والوں کو بھیجتا ہے۔ لائن بریک والی منزل سے انکار کر دیا گیا ہے۔

ایک گارڈ پورے فولڈر کی حفاظت کرتا ہے:

```python filename="src/routes/private/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

## HTML یا JSON

وہی استثنیٰ مختلف جواب دیتا ہے اس بات پر منحصر ہے کہ کون پوچھتا ہے:

- ایک براؤزر (`Accept: text/html`) کو HTML صفحہ ملتا ہے۔ تفصیل HTML سے بچ گئی ہے، لہذا صارف کے ان پٹ سے بنایا گیا پیغام مارک اپ کو انجیکشن نہیں کر سکتا۔
- ایک کلائنٹ جو JSON کے لیے پوچھتا ہے نہ کہ کسی صفحہ (`Accept: application/json`) کو اسی اسٹیٹس کوڈ کے ساتھ `{"detail": "..."}` ملتا ہے۔

```python filename="src/routes/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=403, detail="Out of range")
    return {"id": id}
```

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!NOTE]
> ایک کلائنٹ جو `Accept: */*` بھیجتا ہے (`curl` اور بہت سی HTTP لائبریریوں کا ڈیفالٹ) HTML صفحہ وصول کرتا ہے۔ JSON کی غلطیوں کے لیے `Accept: application/json` سیٹ کریں۔

## غیر ہینڈل شدہ مستثنیات

ایک استثناء جس میں کوئی بھی چیز ہینڈل نہیں کی جاتی ہے ایک بار لاگ ان ہوتی ہے، استثناء کے ساتھ، یہ کہاں سے آیا اور اس کے آس پاس کا کوڈ، اور موڈ کے مطابق جواب دیا گیا۔

| | `nx dev` | `nx start` |
|---|---|---|
| براؤزر | خرابی والا صفحہ، آپ کے کوڈ کی لائنیں جنہوں نے اسے اٹھایا اور مکمل ٹریس بیک | بلٹ ان `500` صفحہ (یا آپ کا `errors.nexy`) حوالہ کے ساتھ |
| JSON کلائنٹ | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| سرور لاگ | استثناء اور آپ کے کوڈ کی لائنیں | استثناء اور پورا ٹریس بیک، اسی حوالہ کے ساتھ |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

حوالہ آٹھ حروف ہے، ہر ناکامی کے لیے نیا۔ ایک وزیٹر اس کا حوالہ دے سکتا ہے، اور آپ اس کے لیے لاگ کو تلاش کر کے ٹریس بیک تلاش کر سکتے ہیں۔ پیداوار میں نہ تو استثناء اور نہ ہی کوڈ وزیٹر تک پہنچتا ہے۔ ایک حسب ضرورت `errors.nexy` صرف صفحہ کی جگہ لے لیتا ہے۔ لاگ لائن رہتی ہے.

## توثیق کی غلطیاں

ایک غائب ہیڈر، استفسار پیرامیٹر یا باڈی فیلڈ ہر کلائنٹ کے لیے FastAPI کے JSON باڈی کے ساتھ `422` جواب دیتا ہے۔ دیکھیں [تصدیق اور غلطیاں](../handlers/validation-and-errors.md)۔

## اگلے اقدامات

- [خرابی صفحات فی فولڈر](folder-pages.md): ایک فولڈر میں آپ کا اپنا 404، 403 یا 401
- [متحرک راستے](../pages/dynamic-routes.md)
- [API روٹس](../handlers/README.md)
- [ٹیسٹنگ](../../../guides/testing.md)
