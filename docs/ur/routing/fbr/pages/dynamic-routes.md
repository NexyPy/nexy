# متحرک راستے

مربع بریکٹ میں لکھا ہوا پاتھ سیگمنٹ کسی بھی قدر سے میل کھاتا ہے اور اسے صفحہ یا ہینڈلر کے حوالے کرتا ہے۔

## متحرک طبقات

`blog/[slug].nexy` سرو کرتا ہے `/blog/{slug}`۔ ایک صفحہ میں، سیگمنٹ کو بطور پراپرٹی قرار دیں؛ ایک Python ہینڈلر میں، اسے ایک دلیل کے طور پر لیں۔

```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str]
---
<h1>{{ slug }}</h1>
```

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

## ٹائپ شدہ حصے

تشریح قسم کا فیصلہ کرتی ہے۔

| جہاں | تبدیلی |
|---|---|
| `.py` ہینڈلر | کوئی بھی FastAPI قسم کی تشریح (`int`، `UUID`، `Enum`...) |
| `.nexy` صفحہ | `int` اور `float` تبدیل ہو گئے ہیں۔ باقی سب کچھ تار ہی رہتا ہے |

ایک قدر جو تشریح سے مماثل نہیں ہے وہ ہے **نہیں ملی**: `/api/users/abc` جوابات `404`، کیونکہ ایک متحرک راستہ کسی بھی یو آر ایل کو پکڑتا ہے اور ایک یو آر ایل جسے تبدیل نہیں کیا جاسکتا وہ موجود نہیں ہے۔ دیکھیں [تصدیق اور غلطیاں](../handlers/validation-and-errors.md)۔

## تمام طبقات کو پکڑیں۔

`docs/[...path].nexy` سرو کرتا ہے `/docs/{path:path}`۔ بقیہ حصے ایک تار کے طور پر آتے ہیں، سلیشز شامل ہیں۔

```nexy filename="src/routes/docs/[...path].nexy"
---
path: prop[str]
---
<pre>{{ path }}</pre>
```

`/docs/a/b/c` دیتا ہے `path == "a/b/c"`۔

## روٹ گروپس

قوسین میں ایک ڈائریکٹری URL میں ظاہر کیے بغیر فائلوں کو منظم کرتی ہے۔ یہ اب بھی [وراثت](../inheritance.md) میں حصہ لیتا ہے: اس کا `layout.*` اور `dependencies.py` اندر کی چیزوں پر لاگو ہوتا ہے۔

```text
src/routes/
├─ (marketing)/
│  ├─ layout.nexy        applies to the pages in the group
│  ├─ pricing.nexy       /pricing
│  └─ about.nexy         /about
└─ (app)/
   └─ dashboard.nexy     /dashboard
```

مختلف حصوں کو ان کے URL کو تبدیل کیے بغیر مختلف ترتیب دینے کے لیے گروپس کا استعمال کریں۔

## ترجیح

جامد راستے متحرک راستوں پر جیت جاتے ہیں، اور متحرک راستے کیچ آل پر: `/blog/new` میچ `blog/new.nexy` `blog/[slug].nexy` سے پہلے۔

## ایک فائل فی URL

دو فائلیں جو ایک ہی URL کو حل کرتی ہیں دونوں رجسٹر ہوتی ہیں۔ اسی راستے کے لیے `blog.nexy` کو `blog/index.nexy` کے آگے نہ لگائیں، یا `index.nexy` اور `index.py` کو ملا دیں۔

## اگلے اقدامات

- [صفحات](README.md)
- [خرابی صفحات](../errors/README.md)
- [فائل کنونشنز](../../../reference/file-conventions.md)
