# وراثت

`src/routes/` میں کئی فائلیں ان کی ڈائرکٹری کے نیچے ہر چیز پر لاگو ہوتی ہیں۔ وہ سب اسی طرح حل کرتے ہیں: Nexy روٹ کی ڈائرکٹری سے شروع ہوتا ہے اور `src/routes/` تک چلتا ہے۔

```text
src/routes/
├─ layout.nexy               1. outermost
├─ dependencies.py           1. runs first
├─ middleware.py             1. wraps first
├─ notfound.nexy             fallback for every URL
├─ (shop)/                   a group is a directory: it takes part, it is not in the URL
│  ├─ layout.nexy            2.
│  ├─ dependencies.py        2.
│  └─ cart/
│     ├─ layout.nexy         3. innermost
│     ├─ dependencies.py     3. runs last
│     └─ index.nexy          the page
```

| فائل | قاعدہ |
|---|---|
| `layout.nexy`، `layout.tsx`، `layout.vue`، `layout.svelte` | جڑ سے صفحہ تک ہر ترتیب اسے لپیٹ دیتی ہے، **سب سے پہلے** |
| `middleware.py` | روٹ سے روٹ تک ہر فائل درخواست کو لپیٹ دیتی ہے، **بیرونی پہلے**، انحصار سے پہلے |
| `dependencies.py` | ہر فائل روٹ سے روٹ تک چلتی ہے، **سب سے پہلے بیرونی**، پھر ہینڈلر کے اپنے محافظ |
| `notfound.nexy`، `errors.nexy` | دی **قریب ترین** ایک جیت، فی اسٹیٹس کوڈ |

اوپر والے صفحے کے لیے، ترتیب `root layout > (shop) layout > cart layout > page` کے طور پر، اور انحصار `root > (shop) > cart > handler guards` کے طور پر چلتا ہے۔

## سب سے پہلے بیرونی کیوں؟

ایک بیرونی ترتیب فریم کو کھینچتی ہے اور بیرونی انحصار یہ فیصلہ کرتا ہے کہ کون بالکل اندر آسکتا ہے۔ ان کو پہلے رکھنے کا مطلب ہے کہ اندرونی لوگ ان پر بھروسہ کر سکتے ہیں: ایک ڈائرکٹری جس میں تصدیق کی ضرورت ہوتی ہے صارف کو پڑھنے والے ہینڈلر سے پہلے چلتی ہے۔

درخت کی `(shop)` انحصار کارٹ کوکی کو چیک کرتی ہے، لہذا اس کے نیچے کارٹ انحصار دوبارہ چیک کیے بغیر کارٹ کو پڑھ سکتا ہے:

```python filename="src/routes/(shop)/dependencies.py"
from nexy.http import HTTPException, Request


def require_cart(request: Request) -> None:
    if "cart" not in request.cookies:
        raise HTTPException(status_code=400, detail="No cart")


dependencies = [require_cart]
```

## لے آؤٹ

فولڈر فیملی اسٹیک کی تمام لے آؤٹ فائلیں: دیکھیں [لے آؤٹ](layouts/README.md)۔ مختلف خاندان آپس میں نہیں ملتے ہیں: ایک `layout.vue` کبھی بھی `.tsx` صفحہ نہیں لپیٹتا، اور ایک پروجیکٹ میں یا تو `layout.nexy` یا کلائنٹ لے آؤٹ ہوتے ہیں، دونوں کبھی نہیں ([موڈز](modes.md))۔

درخت کا سب سے اندرونی ترتیب صرف اس کا اپنا فریم جوڑتا ہے: اس کے ارد گرد جڑ کی ترتیب اب بھی دستاویز کو کھینچتی ہے۔

```nexy filename="src/routes/(shop)/cart/layout.nexy"
---
children: prop[NexyElement]
---
<section class="cart">
  <h2>Your cart</h2>
  {{ children | safe }}
</section>
```

## مڈل ویئر فائلیں۔

دیکھیں [مڈل ویئر فائلیں](middleware/README.md): وہ انحصار سے پہلے چلتی ہیں اور راستے تک پہنچے بغیر جواب دے سکتی ہیں۔

ایک جڑ `middleware.py` درخت کے ہر راستے کو لپیٹ دیتی ہے، کارٹ میں شامل ہیں:

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## انحصار

ہینڈلر فائل میں آرڈر کے لیے [انحصارات](dependencies/README.md) دیکھیں، بشمول `@UseGuard` اور `@Middleware`۔

## خرابی والے صفحات

`notfound.nexy` اور `errors.nexy` روٹس روٹ پر ایک بار انسٹال ہوتے ہیں۔ ذیلی ڈائرکٹری میں ایک کاپی اس سابقے کے لیے صفحہ کو بہتر کرتی ہے۔ دیکھیں [خرابی صفحات](errors/README.md)۔

`cart/` میں ایک کاپی `/cart` کے تحت 404 کا جواب دیتی ہے، اور جڑ باقی رکھتی ہے:

```nexy filename="src/routes/(shop)/cart/notfound.nexy"
---
title: Product not found
---
<h1>This product is gone</h1>
<p><a href="/cart">Back to your cart</a></p>
```

## اگلے اقدامات

- [ترتیب ](layouts/README.md)
- [انحصار](dependencies/README.md)
- [خرابی کے صفحات](errors/README.md)
