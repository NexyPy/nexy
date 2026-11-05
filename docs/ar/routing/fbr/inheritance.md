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
| `dependencies.py` | يتم تشغيل كل ملف من الجذر إلى المسار، **الأبعد أولاً**، ثم حراس المعالج |
| `notfound.nexy`، `errors.nexy` | **أقرب** يفوز، لكل رمز حالة |

بالنسبة للصفحة أعلاه، تتداخل التخطيطات كـ `root layout > (shop) layout > cart layout > page`، وتعمل التبعيات كـ `root > (shop) > cart > handler guards`.

## لماذا الأبعد أولاً

يرسم التخطيط الخارجي الإطار وتقرر التبعية الخارجية من يمكنه الحضور على الإطلاق. وضعها أولاً يعني أن العناصر الداخلية يمكنها الاعتماد عليها: يتم تشغيل الدليل الذي يتطلب المصادقة قبل المعالج الذي يقرأ المستخدم.

## التخطيطات

جميع ملفات التخطيط الخاصة بمكدس عائلة المجلدات: راجع [التخطيطات](layouts/README.md). لا تختلط العائلات المختلفة: `layout.vue` لا يلتف أبدًا على صفحة `.tsx`، والمشروع يحتوي إما على `layout.nexy` أو تخطيطات العميل، وليس كلاهما أبدًا ([الأوضاع](modes.md)).

## ملفات الوسيطة

راجع [ملفات البرامج الوسيطة](middleware/README.md): يتم تشغيلها قبل التبعيات ويمكنها الإجابة دون الوصول إلى المسار.

## التبعيات

راجع [التبعيات](dependencies/README.md) لمعرفة الترتيب في ملف المعالج، بما في ذلك `@UseGuard` و `@Middleware`.

## صفحات الخطأ

يتم تثبيت `notfound.nexy` و `errors.nexy` مرة واحدة في جذر المسارات؛ تعمل نسخة في دليل فرعي على تحسين الصفحة لتلك البادئة. انظر [صفحات الخطأ](errors/README.md).

## الخطوات التالية

- [التخطيطات](layouts/README.md)
- [التبعيات](dependencies/README.md)
- [صفحات الخطأ](errors/README.md)
