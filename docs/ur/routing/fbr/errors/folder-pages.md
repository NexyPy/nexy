# خامی صفحات فی فولڈر

ایک فولڈر اپنی غلطیوں کا جواب خود دے سکتا ہے: ایک بلاگ جس کے اپنے الفاظ میں 404 ہے، ایک پرائیویٹ ایریا جو ننگی `401` کے بجائے سائن ان فارم پیش کرتا ہے۔ باقی سائٹ پہلے سے موجود صفحہ کو رکھتی ہے۔

یہ صفحہ ان فائلوں میں سے ایک کو شامل کرتا ہے اور اس کا جواب دکھاتا ہے۔

## قاعدہ

**سب سے گہری فائل جو URL سے ملتی ہے۔ جوابات** باقی سب کچھ ویسا ہی رہتا ہے: وہی اسٹیٹس کوڈز، ایک API کلائنٹ کے لیے JSON، اور ایک بار چین کے کسی فولڈر میں فائل نہ ہونے کے بعد بلٹ ان پیج۔

![خرابی کے صفحے کے دائرہ کار](../../../assets/error-page-scopes.svg)

کے لیے `/blog/2024/hello` Nexy walks up the tree: `/blog/2024`، پھر `/blog`، پھر `/`۔ فائل کا جواب دینے والا پہلا فولڈر۔ ایک فولڈر پوری طرح مماثل ہے: `/blogger/hello` `/blog` کے تحت نہیں ہے، لہذا `blog/` میں ایک کاپی اس کا جواب نہیں دیتی۔

## چار فائلیں۔

| فائل | جوابات | اس تک کیا پہنچتا ہے |
|---|---|---|
| `notfound.nexy` | `404` | ایک یو آر ایل کوئی راستہ نہیں ملتا، `notFound()` |
| `errors.nexy` | `500` | ایک استثناء کچھ بھی نہیں سنبھالا |
| `forbidden.nexy` | `403` | `forbidden()`، `raise HTTPException(403)` |
| `unauthorized.nexy` | `401` | `unauthorized()`، `raise HTTPException(401)` |

`loading.nexy` محفوظ رہتا ہے: اس کا ابھی تک کوئی رن ٹائم اثر نہیں ہے۔

اس حیثیت کا جواب دینے کے لیے Nexy کے لیے `src/routes/` میں کہیں ایک فائل کافی ہے: روٹ میں موجود ایک کاپی پورے پروجیکٹ کا جواب دیتی ہے، ایک فولڈر میں موجود ایک کاپی اس فولڈر کا جواب دیتی ہے، اور ہر کاپی کے باہر ایک URL بلٹ ان پیج حاصل کرتا ہے۔ ان ناموں کے لیے ایک اور توسیع `nexyconfig.py` میں `useNotFoundExtensions`، `useErrorsExtensions`، `useForbiddenExtensions` اور `useUnauthorizedExtensions` کے ساتھ محفوظ کریں۔

## آپ کا پہلا فولڈر صفحہ

```nexy filename="src/routes/blog/notfound.nexy"
---
title: Nothing here yet
---
<h1>That post is gone</h1>
<p>The <a href="/blog">blog</a> still has the others.</p>
```

پروجیکٹ چلائیں اور ایسی پوسٹ مانگیں جو موجود نہیں ہے:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/blog/old
# HTTP/1.1 404 Not Found
```

فولڈر کے باہر کا یو آر ایل اس صفحہ کو رکھتا ہے جو آپ کے پاس پہلے سے موجود تھا:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/about
# HTTP/1.1 404 Not Found    (the root page, or the built-in one)
```

## ایک 401 جو کہیں لے جاتا ہے۔

ایک محفوظ علاقے کا فولڈر اس صفحے کے ساتھ جواب دیتا ہے `401` جو راستہ پیش کرتا ہے:

```nexy filename="src/routes/private/unauthorized.nexy"
---
title: Sign in to continue
---
<h1>Sign in to see your notes</h1>
<a href="/sign-in" class="button">Sign in</a>
```

```python filename="src/routes/private/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

ہر کال اور ہر حیثیت اپنے دو جواب رکھتی ہے:

| کون پوچھتا ہے | `401` فائل کے ساتھ | `401` بغیر ایک |
|---|---|---|
| براؤزر (`Accept: text/html`) | فولڈر کا صفحہ | بلٹ ان پیج |
| کلائنٹ (`Accept: application/json`) | `{"detail": "..."}` | `{"detail": "..."}` |

`unauthorized(scheme="Bearer")` نے دونوں جوابات میں `WWW-Authenticate: Bearer` کا اضافہ کیا۔ صارف کے ان پٹ سے تیار کردہ ایک تفصیل صفحہ میں HTML سے بچ گئی ہے۔

> [!ٹپ]
> `Accept: */*`، `curl` اور بہت سی HTTP لائبریریوں کا ڈیفالٹ، نہ تو مانگتا ہے اور نہ ہی HTML صفحہ حاصل کرتا ہے۔ جب آپ JSON جواب چاہتے ہیں تو `-H "Accept: application/json"` شامل کریں۔

## اسے چیک کریں۔

```python filename="tests/test_private.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_a_private_url_asks_for_sign_in():
    answer = TestClient(app).get("/private/notes")
    assert answer.status_code == 401
    assert "Sign in" in answer.text


def test_an_api_client_gets_json():
    answer = TestClient(app).get(
        "/private/notes", headers={"accept": "application/json"}
    )
    assert answer.json() == {"detail": "Unauthorized"}
```

## اگلے اقدامات

- [خرابی کے صفحات](README.md): جو ہر اسٹیٹس کو متحرک کرتا ہے، HTML یا JSON
- [انحصار اور محافظ ](../dependencies/README.md): پورے فولڈر کی حفاظت کریں۔
- [ٹیسٹنگ](../../../guides/testing.md): `TestClient` پہلے ٹیسٹ سے
