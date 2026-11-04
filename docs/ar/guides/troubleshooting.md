# استكشاف الأخطاء وإصلاحها

المشاكل التي يواجهها الناس أولاً هي ما تراه وماذا تفعل. كل واحد يأتي من المدى الحقيقي.

## صفحة تجيب على 404 ولكن الملف الخاص بها موجود

انظر إلى المحطة التي تعمل `nx dev` أو `nx start`. عندما لا يمكن استيراد الصفحة، يقوم Nexy بالإبلاغ
الخطأ في الملف والخط الخاص به، ولم يتم تسجيل المسار:

```text
nexy » error __nexy__/src/routes/index.py:18  ImportError: cannot import name 'FrameworkLogo' ...
```

قم بإصلاح الاستيراد المسمى هناك. الأسباب المعتادة هي مكون لا يتطابق اسم وظيفته
ما تقوم باستيراده (راجع العنصر التالي) وخطأ مطبعي في المسار.

## لا يتم تجميع صفحة `.nexy`: "خطأ في التحليل المنطقي"

```text
src/components/live-panel.nexy - Logic Parse Error: invalid syntax
```

يتم استيراد مكون `.nexy` كوحدة نمطية لـ Python، لذا يجب أن يكون اسم الملف الخاص به اسمًا صالحًا. واصلة
ليس كذلك. قم بتسميته في PascalCase، `LivePanel.nexy`، وقم باستيراده بنفس الاسم:

```nexy
from "@/components/LivePanel.nexy" import LivePanel
```

## يعرض المكون أطفاله على هيئة النص `<slot />`

المكون `.nexy` يضع أبنائه مع `<Slot />`، بحرف S الكبير. الحرف الصغير `<slot />` هو
تركت في الصفحة كما هي. Vue، الذي له `<slot />`، لا يتأثر.

## الخاصية تظهر اسم المتغير

```nexy
<Icon path=icon />          renders: icon
<Icon path="{{ icon }}" />  renders: the value of icon
```

السمة التي لا تحتوي على أقواس هي النص. ضع تعبير Jinja في السمة لتمرير عملية محسوبة
قيمة.

## القيمة في `{{ ... }}` تصبح فارغة

يخفي Jinja2 متغيرًا غير محدد. أعلن عن كل خاصية تستخدمها في المادة الأمامية
(`title: prop[str] = ""`)، والتدقيق الإملائي.

## فئات الأدوات المساعدة ليس لها أي تأثير في صفحة `.nexy` (UnoCSS)

يقرأ UnoCSS الملف فقط عندما يكون امتداده في مسار المحتوى الخاص به. تم إنشاء مشروع الخادم
بواسطة `nx new` مع UnoCSS يسرد بالفعل `.nexy`؛ ويحتاج إليه كبير في `uno.config.ts`:

```ts
content: {
  filesystem: ['src/**/*.nexy'],
  pipeline: { include: [/\.(vue|svelte|[jt]sx|mdx?|astro|html|nexy)($|\?)/] },
},
```

يعثر Tailwind على `.nexy` من الملفات بمفرده.

## صفحة `.mdx` تطلب الطرود

```text
[nexy] MDX support requires optional packages that are not installed.
```

تثبيتها في المشروع: `@mdx-js/rollup`، `remark-gfm` و `@mdx-js/react` (زائد
`@mdx-js/esbuild` لـ `nx build`). يحتاج MDX إلى React أو Preact في `useFF`. بدون إطار العميل،
اكتب الصفحة كـ `.md`. انظر [تخفيض السعر وMDX](../views/nexy/markdown.md).

## `No module named 'sqlmodel'` (أو أي حزمة) عند بدء تشغيل الأمر

```text
nexy » nexyconfig.py cannot be loaded: No module named 'sqlmodel'. If it is a package, install it
in this Python (...) or activate the project's virtual environment.
```

تم تشغيل الأمر في لغة بايثون الخاطئة. حزم مشروعك (ORM الخاص بك، مكتباتك) موجودة
`.venv`، و`uvx nexy` أو `nexy` عالمي يعمل في بيئة خاصة به لا تحتوي على أي من
لهم.

قم بتنشيط البيئة الافتراضية للمشروع، من مجلد المشروع، ثم قم بتشغيل الأمر مرة أخرى:

```bash
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

يبدأ الموجه بـ `(.venv)` عندما يكون نشطًا. أو تخطي التنشيط مع
`uv run nexy dev`. إذا كانت الحزمة مفقودة بالفعل من المشروع، فأضفها مع `uv add sqlmodel`.

## `nx dev` يظهر خطأ وينتظر

عندما لا يمكن بدء تشغيل التطبيق الخاص بك، `nx dev` يبلغ عن السبب وينتظر تغيير الملف التالي؛ إنه كذلك
لا خروج. إصلاح الملف وحفظه. فقط Ctrl + C يوقفه.

## الميناء مشغول

`nx dev` يأخذ المنفذ الحر التالي ويطبعه. لاختيار واحد، استخدم `--port` أو قم بتعيين `usePort` في
`nexyconfig.py`.

## يومض الموضوع باللون الأبيض على صفحة داكنة

يجب تطبيق السمة المحفوظة قبل الطلاء الأول. احتفظ بالنص الصغير للمبتدئين في ملف
`<head>` من تخطيط الجذر، ووضع `suppressHydrationWarning` على `<html>` في React.

## لا يزال عالقا

- اقرأ صفحة الميزة في [فهرس الوثائق](../README.md).
- إذا اختلفت المستندات والكود، فالرمز صحيح: يرجى فتح ملف
  [المسألة](https://github.com/NexyPy/nexy/issues) تسمية الصفحة.