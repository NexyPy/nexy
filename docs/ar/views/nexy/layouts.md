# layout.nexy

ملف تخطيط وضع الخادم (`useCSR = False`). يمتلك الجذر مستند HTML.

## تخطيط الجذر

```nexy filename="src/routes/layout.nexy"
---
from nexy import Vite

children: prop[NexyElement]
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My app</title>
  <Vite />
</head>
<body>
  <main>{{ children | safe }}</main>
</body>
</html>
```

- `<!DOCTYPE html>`، `<html>`، `<head>` و `<body>` يعيشون هنا وليس في أي مكان آخر.
- `<Vite />` يقوم بإدخال نصوص وأنماط العميل مرة واحدة، في `<head>`.
- `{{ children | safe }}` هو المكان الذي تظهر فيه الصفحة، أو التخطيط المتداخل التالي.

## التخطيطات المتداخلة

يقوم `layout.nexy` الموجود في دليل فرعي بتغليف تلك الشجرة الفرعية وعرضها داخل الشجرة الأم. لا يتكرر
علامات الوثيقة:

```nexy filename="src/routes/blog/layout.nexy"
---
children: prop[NexyElement]
---
<nav>...</nav>
<article>{{ children | safe }}</article>
```

`blog/[slug].nexy` يظهر كـ `layout.nexy > blog/layout.nexy > page`.

## المكونات والجزر

يمكن للتخطيط استيراد `.nexy` مكونات (رأس وتذييل) ومكونات العميل. عميل
المكون الموجود في التخطيط هو [island](../../rendering/islands.md) مثل أي عنصر آخر:

```nexy
---
from "@/components/Header.nexy" import Header
from "@/components/theme/theme.tsx" import Theme
---
<Header />
<Theme directive="client:idle" />
```

## بدون تخطيط

مشروع بدون `layout.nexy` لا يزال يجيب بوثيقة صالحة: Nexy يعود إلى الحد الأدنى
Shell مع `<!DOCTYPE html>`، وتعريف إطار العرض وعلامات Vite. أضف تخطيطًا بمجرد الحاجة
العنوان أو الخطوط أو التنقل.

## في جهاز التوجيه المعياري

تختار وحدات التحكم طرق العرض الخاصة بها، لذا فهي تقوم بتكوين التخطيط بنفسها:

```python
return useViews("src/apps/layout.nexy", context={"children": useViews("src/apps/app_view.nexy")})
```

##  ما لا يستطيع فعله

- لا يمكن أن يتواجد مع `layout.tsx`، `layout.vue` أو `layout.svelte`: مشروع وضع الخادم لديه
  لا توجد مسارات للعميل ([الأوضاع](../../routing/fbr/modes.md)).
- لا يعمل على العميل: استخدم جزيرة للتفاعل.

## الخطوات التالية

- [التخطيطات](../../routing/fbr/layouts/README.md)
- [الميراث](../../routing/fbr/inheritance.md)
- [.ملفات .nexy](README.md)