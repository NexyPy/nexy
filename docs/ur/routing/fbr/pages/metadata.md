# صفحہ کا میٹا ڈیٹا

ایک صفحہ اپنے عنوان اور اس کے ہیڈ ٹیگز کا نام دیتا ہے، اور روٹ لے آؤٹ انہیں ایک بار لکھتا ہے۔

## صفحہ میں بتائیں

ایک ایسے صفحہ کے لیے جو کبھی تبدیل نہیں ہوتا، فرنٹ میٹر کے اوپری حصے میں لفظی لکھیں:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

جب عنوان ڈیٹا پر منحصر ہو تو اس کے بجائے `setMetadata` کو کال کریں:

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound, setMetadata

from src.posts import find

slug: prop[str]
post = find(slug) or notFound()
setMetadata(title=post.title, description=post.summary, og={"image": post.cover})
---
<h1>{{ post.title }}</h1>
```

ایک ماڈیولر کنٹرولر کال کرتا ہے `setMetadata(...)` اس کے واپس آنے سے پہلے `useViews(...)`۔

## اسے ترتیب میں لکھیں۔

روٹ لے آؤٹ `<head>` کا مالک ہے۔ ایک سطر لکھتی ہے کہ صفحہ نے کیا کہا، فرار:

```nexy filename="src/routes/layout.nexy"
---
from nexy import setMetadata, useMetadata

children: prop[NexyElement]
setMetadata(title_template="%s | My site")
---
<!DOCTYPE html>
<html>
  <head>
    {{ useMetadata().html() }}
  </head>
  <body>{{ children }}</body>
</html>
```

ایک صفحہ اس کے لے آؤٹ سے پہلے چلتا ہے، لہذا لے آؤٹ تلاش کرتا ہے کہ صفحہ نے کیا پوچھا ہے۔ ایک ایسا صفحہ جو کہتا ہے کہ آپ کے `nexyconfig.py` کا `useTitle`، اور کوئی ٹیگ نہیں ملتا۔

## کھیتیاں

| فیلڈ | لکھا گیا |
|---|---|
| `title` | `<title>`; `title_template="%s \| My site"` کے ساتھ عنوان `%s` | میں رکھا گیا ہے۔
| `description` | `<meta name="description">` |
| `canonical` | `<link rel="canonical">` |
| `robots` | `<meta name="robots">`، مثال کے طور پر `"noindex"` |
| `icon` | `<link rel="icon">` |
| `og` | ایک `<meta property="og:...">` فی کلید: `{"image": "/cover.png"}` دیتا ہے `og:image` |
| `twitter` | ایک `<meta name="twitter:...">` فی کلید |
| `extra` | صفات کے احکام کی فہرست، ایک `<meta>` ہر ایک: `[{"name": "theme-color", "content": "#fff"}]` |

بعد کی کال ایک قدر کی جگہ لے لیتی ہے۔ `og`، `twitter` اور `extra` جو کچھ ہے اس میں اضافہ کریں۔ ایک فیلڈ جو موجود نہیں ہے وہ اٹھاتا ہے `TypeError`، لہذا ٹائپنگ خاموشی سے کچھ نہیں کرتی ہے۔

## ڈیفالٹ کے لحاظ سے محفوظ

ہر قدر ایچ ٹی ایم ایل سے بچ جاتی ہے، لہذا یو آر ایل یا ڈیٹا بیس سے بنایا گیا ٹائٹل ٹیگ کو بند نہیں کر سکتا اور اسکرپٹ کو انجیکشن نہیں کر سکتا۔ ایک قدر ایک بار بچ جاتی ہے، جب لے آؤٹ کال کرتا ہے `html()`: اسے خود نہ بچائیں۔

## اگلے اقدامات

- [صفحات](README.md)
- [لے آؤٹ](../layouts/README.md)
- [خرابی کے صفحات](../errors/README.md)
