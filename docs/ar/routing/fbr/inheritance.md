# الميراث

تنطبق عدة ملفات في `src/routes/` على كل شيء أسفل الدليل الخاص بها. يتم حلها جميعًا بنفس الطريقة: يبدأ Nexy من دليل المسار ويصل إلى `src/routes/`.

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

| ملف | القاعدة |
|---|---|
| `layout.nexy`، `layout.tsx`، `layout.vue`، `layout.svelte` | كل تخطيط من الجذر إلى الصفحة يلتف حوله، **الأبعد أولاً** |
| `middleware.py` | كل ملف من الجذر إلى المسار يغلف الطلب، **الأبعد أولاً**، قبل التبعيات |
| `dependencies.py` | يتم تشغيل كل ملف من الجذر إلى المسار، **الأبعد أولاً**، ثم حراس المعالج الخاص |
| `notfound.nexy`، `errors.nexy` | **أقرب** يفوز، لكل رمز الحالة |

بالنسبة للصفحة أعلاه، تتداخل التخطيطات كـ `root layout > (shop) layout > cart layout > page`، وتعمل التبعيات كـ `root > (shop) > cart > handler guards`.

## لماذا الأبعد أولاً

يرسم التخطيط الخارجي الإطار وتقرر التبعية الخارجية من يمكنه الحضور على الإطلاق. وضعها أولاً يعني أن العناصر الداخلية يمكنها الاعتماد عليها: يتم تشغيل الدليل الذي يتطلب المصادقة قبل المعالج الذي يقرأ المستخدم.

تقوم تبعية الشجرة `(shop)` بفحص ملف تعريف الارتباط لعربة التسوق، لذا يمكن لتبعية عربة التسوق الموجودة أسفلها قراءة العربة دون التحقق مرة أخرى:

```python filename="src/routes/(shop)/dependeency.py"
from nexy.http import HTTPException, Request


def require_cart(request: Request) -> None:
    if "cart" not in request.cookies:
        raise HTTPException(status_code=400, detail="No cart")


dependencies = [require_cart]
```

## التخطيطات

جميع ملفات التخطيط الخاصة بمكدس عائلة المجلدات: راجع [التخطيطات](layouts/README.md). لا تختلط العائلات المختلفة: `layout.vue` لا يلتف أبدًا على صفحة `.tsx`، والمشروع يحتوي إما على `layout.nexy` أو تخطيطات العميل، وليس كلاهما أبدًا ([الأوضاع](modes.md)).

يضيف التخطيط الأعمق للشجرة إطارًا خاصًا بها فقط: ويستمر التخطيط الجذري حولها في رسم المستند.

```nexy filename="src/routes/(shop)/cart/layout.nexy"
---
children: prop[NexyElement]
---
<section class="cart">
  <h2>Your cart</h2>
  {{ children | safe }}
</section>
```

## ملفات الوسيطة

راجع [ملفات البرامج الوسيطة](middleware/README.md): يتم تشغيلها قبل التبعيات ويمكنها الإجابة دون الوصول إلى المسار.

جذر `middleware.py` يغلف كل مسار للشجرة، تتضمن العربة:

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## التبعيات

راجع [التبعيات](dependencies/README.md) لمعرفة الترتيب في ملف المعالج، بما في ذلك `@UseGuard` و `@Middleware`.

## صفحات الخطأ

يتم تثبيت `notfound.nexy` و `errors.nexy` مرة واحدة في جذر المسارات؛ تعمل نسخة في دليل فرعي على تحسين الصفحة لتلك البادئة. انظر [صفحات الخطأ](errors/README.md).

نسخة في `cart/` تجيب على الـ 404 تحت `/cart`، ويحتفظ الجذر بالباقي:

```nexy filename="src/routes/(shop)/cart/notfound.nexy"
---
title: Product not found
---
<h1>This product is gone</h1>
<p><a href="/cart">Back to your cart</a></p>
```

## الخطوات التالية

- [التخطيطات](layouts/README.md)
- [التبعيات](dependencies/README.md)
- [صفحات الخطأ](errors/README.md)
