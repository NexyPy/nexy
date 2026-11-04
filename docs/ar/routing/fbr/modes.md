# وضع الخادم ووضع العميل

يتم تقديم مشروع Nexy إما ** بواسطة الخادم** أو **يتم توجيهه بواسطة العميل**، مثل مشروع Next.js إما
الصفحات المعروضة على الخادم أو تطبيق العميل. `useCSR` في `nexyconfig.py` يختار.

## وضع الخادم (`useCSR = False`)

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

- الصفحات هي ملفات `.nexy` أو `.md` أو `.mdx` ضمن `src/routes/`.
- الجذر `layout.nexy` يملك `<!DOCTYPE html>`، `<html>`، `<head>` و `<body>`.
- يُسمح بمكونات العميل (React أو Vue أو Svelte أو Solid أو Preact) كـ **جزر**: يمكنك استيراد واحدة
  من صفحة `.nexy` ويرطب في المتصفح. انظر [الجزر](../../rendering/islands.md).
- مكون العميل ليس طريقًا أبدًا. احتفظ بها في `src/components/`.
- إطار عميل واحد في كل مرة.

```text
src/
├─ routes/
│  ├─ layout.nexy         document
│  ├─ index.nexy          page
│  └─ api/users.py        API handler
└─ components/Counter.tsx island
```

## وضع العميل (`useCSR = True`)

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

- الصفحات هي ملفات إطار عمل العميل الخاص بك: `.tsx` لـ React، `.vue`، `.svelte`.
تظل ملفات -  `.md` و `.mdx` مسارات صالحة: يعرضها Nexy على الخادم داخل العميل
  التخطيط، ويتولى جهاز توجيه العميل التنقل من هناك.
- التخطيط الجذري لأي إطار (`layout.tsx`، `layout.vue`، `layout.svelte`) يمتلك `<!DOCTYPE html>`، `<html>`، `<head>` و `<body>`، مثل
  تخطيط الجذر لجهاز توجيه التطبيقات Next.js. يعرضه Nexy في Node للاستجابة الأولى و
  الإطار يرطب الوثيقة بأكملها. انظر [layout.tsx](../../views/react/differences.md).
-  `.py` الملفات هي معالجات واجهة برمجة التطبيقات (API) التي يتم تقديمها بواسطة FastAPI، بجوار مسارات العميل.
- لا يوجد ملف `.nexy` على الإطلاق، ولا يوجد `layout.nexy`.
- يتم التنقل بين الصفحات في المتصفح.

```text
src/routes/
├─ layout.tsx             document
├─ index.tsx              page
├─ users.tsx              page
└─ api/users.py           API handler
```

## ما هو مرفوض

يقوم Nexy بفحص المشروع قبل `nx dev` و `nx start` و `nx build` ويتوقف عند قائمة الملفات:

| الوضع | مرفوض | الرسالة |
|---|---|---|
| الخادم | `.tsx`، `.jsx`، `.vue` أو `.svelte` ضمن `src/routes/` | انقل المكونات إلى `src/components/`، أو قم بتعيين `useCSR = True` |
| العميل | أي `.nexy` ملف ضمن `src/routes/` | كتابتها كمكونات إطار عمل، أو تعيين `useCSR = False` |
| كلاهما | أكثر من إطار أمامي واحد في `useFF` | `useFF must configure exactly one frontend framework` |
| العميل | `useRouter` (جهاز التوجيه المعياري) | `useCSR requires file-based routing` |
| العميل | لا `useFF` | `useCSR requires a client framework` |

يتم تجاهل الملفات والمجلدات التي تبدأ بـ `_` أو `.` من خلال هذا الفحص.

##  أيهما

- **المحتوى والتسويق والمستندات ومواقع SEO الأولى**: وضع الخادم مع الجزر.
- **لوحات المعلومات والتطبيقات مع التنقل الغني بالعميل**: وضع العميل.
- **واجهة برمجة تطبيقات Python مع تطبيق عميل في الأعلى**: وضع العميل، مع وجود معالجات `.py` بجوار الصفحات.

## الخطوات التالية

- [التخطيطات](layouts/README.md)
-  [التقديم](../../rendering/README.md)
- [التكوين](../../reference/config.md)