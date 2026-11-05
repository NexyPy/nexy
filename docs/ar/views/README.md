# وجهات النظر

قبل اختيار تنسيق الملف، من المهم التمييز بين كيفية تعامل Nexy مع الموارد وكيفية عرضها.

| مصطلح | التعريف |
|---|---|
| **الصفحة** | مورد يمكن عنونة URL للتطبيق. يتم تعريفه بواسطة ملف تحت `src/routes/`. |
| **عرض** | عملية إنتاج نص الاستجابة للصفحة. يقوم العرض بتحويل المنطق والبيانات إلى HTML أو JSON. |
| **المكون** | كتلة بناء لواجهة المستخدم قابلة لإعادة الاستخدام تُستخدم لإنشاء طريقة عرض. يمكن أن تكون المكونات مساعدات Nexy أصلية أو خاصة بإطار العمل (React، Vue، وما إلى ذلك). |
| **معالج المسار** | دالة Python تعالج طلب HTTP لطريقة محددة (على سبيل المثال، `GET`، `POST`). |
| **نقطة النهاية** | المزيج الفريد من عنوان URL وطريقة HTTP التي يجيب عليها معالج المسار. |

**لست متأكدا؟ اكتب ملف `.nexy`.** لا يحتاج إلى إطار عمل للعميل، ويمكنك إضافة مكون React أو Vue أو Svelte أو Solid أو Preact بداخله لاحقًا، كجزيرة.

```diagram filename="أي ملف لأي صفحة"
server logic + HTML          →  .nexy      (Python frontmatter + Jinja2)
prose that changes rarely    →  .md        (GitHub-flavoured Markdown)
prose + components           →  .mdx       (React or Preact)
app-like page, client router →  .tsx .vue .svelte (framework files)
API handler                  →  .py        (GET, POST, …)
```

## التنسيقات

| التنسيق | ملف | تقديم الخادم | إطار العميل | ملاحظات |
|---|---|---|---|---|
| `.nexy` | [ملفات .nexy](nexy/README.md) | Jinja2 + Python منطق، متدفق | اختياري | تنسيق صفحة Nexy الأصلي |
| `.md` | [Markdown و MDX](nexy/markdown.md) | Markdown عند الطلب | اختياري عبر التخطيط | نقي Markdown، GFM، مغلف بالتخطيط |
| `.mdx` | [Markdown و MDX](nexy/markdown.md) | الإطار SSR | React أو Preact | Markdown بالمكونات |
| `.tsx` | [React ](react/differences.md)، [Solid ](solid/differences.md) أو [Preact ](preact/differences.md) | وضع العميل: الإطار المعروض في Node | React أو Solid أو Preact | طرق المكونات |
| `.vue` | [Vue](vue/differences.md) | وضع العميل: الإطار المعروض في Node | Vue | طرق SFC |
| `.svelte` | [Svelte](svelte/differences.md) | وضع العميل: الإطار المعروض في Node | Svelte | طرق SFC |

المساعدين المدمجين `Image`، `Link`، `Audio`، `Video` و `Import`: [المكونات](nexy/components.md).

## تنسيقات الخلط

يمكنك مزج تقنيات مختلفة في نفس المشروع:
- **الجزر**: يمكنك استيراد مكون React أو Vue داخل صفحة `.nexy`. يعرض الخادم الصدفة، ويقوم إطار العمل بترطيب المكون الموجود على العميل.
- **المنطق المشترك**: يمكن لمعالجات المسار في ملفات `.py` توفير البيانات للصفحات بأي تنسيق عبر حالة التطبيق المشترك أو استدعاءات واجهة برمجة التطبيقات (API).

## تمكين الإطار

قم بتعيين `useFF` في `nexyconfig.py` وقم بتشغيل `nexy new` لإضافة التبعيات:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

مع تمكين إطار العمل، يتعامل Vite مع حزم العملاء الخاصة به. في وضع العميل، تصبح امتداداته مسارات؛ في وضع الخادم، تكون نفس الملفات عبارة عن مكونات تقوم باستيرادها كجزر - حيث يتم رفض ملف إطار العمل ضمن `src/routes/` هناك. انظر [وضع الخادم ووضع العميل](../routing/fbr/modes.md).

> [!NOTE]
> في وضع [CSR](../rendering/csr.md)، تكون ملفات مسار إطار العمل فقط قابلة للملاحة من جانب العميل.

## التخطيطات

`layout.*` في الدليل يلتف الصفحات الموجودة أسفله. انظر [التخطيطات](../routing/fbr/layouts/README.md).

## الخطوات التالية

- [ملفات .nexy](nexy/README.md): Python + Jinja2 + الدعائم
- [Markdown و MDX](nexy/markdown.md): صفحات المحتوى
- [المكونات](nexy/components.md): مساعدات HTML المضمنة
