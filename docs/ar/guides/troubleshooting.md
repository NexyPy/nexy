# استكشاف الأخطاء وإصلاحها

المشاكل التي يواجهها الناس أولاً هي ما تراه وماذا تفعل. كل واحد يأتي من المدى الحقيقي.

## تجيب الصفحة على 404 ولكن الملف الخاص بها موجود

انظر إلى المحطة التي تعمل `nx dev` أو `nx start`. عندما لا يمكن استيراد الصفحة، يقوم Nexy بالإبلاغ عن الخطأ بملفها وسطرها، ولا يتم تسجيل المسار:

```text
nexy » error __nexy__/src/routes/index.py:18  ImportError: cannot import name 'FrameworkLogo' ...
```

قم بإصلاح الاستيراد المسمى هناك. الأسباب المعتادة هي مكون لا يتطابق اسم وظيفته مع ما تقوم باستيراده (راجع العنصر التالي) وخطأ مطبعي في المسار.

## لا يتم تجميع صفحة `.nexy`: "خطأ في التحليل المنطقي"

```text
src/components/live-panel.nexy - Logic Parse Error: invalid syntax
```

يتم استيراد مكون `.nexy` كوحدة نمطية Python، لذلك يجب أن يكون اسم الملف الخاص به اسمًا صالحًا. واصلة ليست كذلك. قم بتسميته في PascalCase، `LivePanel.nexy`، وقم باستيراده بنفس الاسم:

```nexy
from "@/components/LivePanel.nexy" import LivePanel
```

## يعرض المكون أطفاله كنص `<slot />`

المكون `.nexy` يضع أطفاله بـ `<Slot />`، بحرف S كبير. ويتم ترك الحرف الصغير `<slot />` في الصفحة كما هو. Vue، الذي له `<slot />` خاصته، لا يتأثر.

## تُظهر الدعامة اسم المتغير

```nexy
<Icon path=icon />          renders: icon
<Icon path="{{ icon }}" />  renders: the value of icon
```

السمة التي لا تحتوي على أقواس هي النص. ضع التعبير Jinja في السمة لتمرير قيمة محسوبة.

## القيمة في `{{ ... }}` تصبح فارغة

Jinja2 يخفي متغير غير محدد. قم بتعريف كل خاصية تستخدمها في المادة الأمامية (`title: prop[str] = ""`)، وتحقق من التهجئة.

## فئات الأدوات المساعدة ليس لها أي تأثير في صفحة `.nexy` (UnoCSS)

UnoCSS يقرأ الملف فقط عندما يكون امتداده في مسار المحتوى الخاص به. مشروع خادم تم إنشاؤه بواسطة `nx new` مع UnoCSS يسرد بالفعل `.nexy`؛ ويحتاج إليه كبير في `uno.config.ts`:

```ts
content: {
  filesystem: ['src/**/*.nexy'],
  pipeline: { include: [/\.(vue|svelte|[jt]sx|mdx?|astro|html|nexy)($|\?)/] },
},
```

Tailwind يعثر على `.nexy` من الملفات بمفرده.

## صفحة `.mdx` تطلب الطرود

```text
[nexy] MDX support requires optional packages that are not installed.
```

تثبيتها في المشروع: `@mdx-js/rollup`، `remark-gfm` و `@mdx-js/react` (زائد `@mdx-js/esbuild` لـ `nx build`). MDX يحتاج إلى React أو Preact في `useFF`. بدون إطار عمل عميل، اكتب الصفحة كـ `.md`. انظر [Markdown و MDX](../views/nexy/markdown.md).

## `No module named 'sqlmodel'` (أو أي حزمة) عند بدء تشغيل الأمر

```text
nexy » nexyconfig.py cannot be loaded: No module named 'sqlmodel'. If it is a package, install it
in this Python (...) or activate the project's virtual environment.
```

وجرى الأمر في الخطأ Python. حزم مشروعك (ORM الخاص بك، مكتباتك) موجودة في `.venv`، و `uvx nexy` أو `nexy` عالمية تعمل في بيئة خاصة بها لا تحتوي على أي منها.

قم بتنشيط البيئة الافتراضية للمشروع، من مجلد المشروع، ثم قم بتشغيل الأمر مرة أخرى:

```bash
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

يبدأ الموجه بـ `(.venv)` عندما يكون نشطًا. أو تخطي التنشيط بـ `uv run nexy dev`. إذا كانت الحزمة مفقودة بالفعل من المشروع، فأضفها مع `uv add sqlmodel`.

## `nx dev` يظهر خطأ وينتظر

عندما لا يمكن بدء تشغيل التطبيق الخاص بك، يقوم `nx dev` بالإبلاغ عن السبب وينتظر تغيير الملف التالي؛ لا يخرج. إصلاح الملف وحفظه. فقط Ctrl + C يوقفه.

## الميناء مشغول

`nx dev` يأخذ المنفذ الحر التالي ويطبعه. لاختيار واحد، استخدم `--port` أو اضبط `usePort` في `nexyconfig.py`.

## يومض الموضوع باللون الأبيض على صفحة داكنة

يجب تطبيق السمة المحفوظة قبل الطلاء الأول. احتفظ بالنص الصغير للمبتدئين في `<head>` من تخطيط الجذر، ثم ضع `suppressHydrationWarning` على `<html>` في React.

## لا تزال عالقة

- اقرأ صفحة الميزة في [فهرس الوثائق](../README.md).
- إذا كانت المستندات والكود غير متوافقين، فإن الكود صحيح: يرجى فتح [إصدار](https://github.com/NexyPy/nexy/issues) لتسمية الصفحة.
