# تخطيط.nexy

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
- `{{ children | safe }}` هو المكان الذي يتم فيه عرض الصفحة أو التخطيط المتداخل التالي.

## تخطيطات متداخلة

يقوم `layout.nexy` الموجود في دليل فرعي بتغليف تلك الشجرة الفرعية وعرضها داخل الشجرة الأم. لا يكرر علامات المستند:

```nexy filename="src/routes/blog/layout.nexy"
---
children: prop[NexyElement]
---
<nav>...</nav>
<article>{{ children | safe }}</article>
```

`blog/[slug].nexy` يظهر كـ `layout.nexy > blog/layout.nexy > page`.

## المكونات والجزر

يمكن للتخطيط استيراد `.nexy` مكونات (رأس وتذييل) ومكونات العميل. مكون العميل في التخطيط هو [island](../../rendering/islands.md) مثل أي مكون آخر:

```nexy
---
from "@/components/Header.nexy" import Header
from "@/components/theme/theme.tsx" import Theme
---
<Header />
<Theme directive="client:idle" />
```

## بدون تخطيط

لا يزال المشروع الذي لا يحتوي على `layout.nexy` يجيب بمستند صالح: يعود Nexy إلى الحد الأدنى من الصدفة باستخدام `<!DOCTYPE html>` وإطار العرض التعريفي وعلامات Vite. أضف تخطيطًا بمجرد احتياجك إلى عنوان أو خطوط أو تنقل.

## في جهاز التوجيه المعياري

تختار وحدات التحكم طرق العرض الخاصة بها، لذا فهي تقوم بتكوين التخطيط بنفسها:

```python
return useViews("src/apps/layout.nexy", context={"children": useViews("src/apps/app_view.nexy")})
```

## ما لا يستطيع فعله

- لا يمكن أن يتواجد مع `layout.tsx` أو `layout.vue` أو `layout.svelte`: لا يحتوي مشروع وضع الخادم على مسارات العميل ([الأوضاع](../../routing/fbr/modes.md)).
- لا يعمل على العميل: استخدم جزيرة للتفاعل.

## الخطوات التالية

- [التخطيطات](../../routing/fbr/layouts/README.md)
- [الميراث](../../routing/fbr/inheritance.md)
- [ملفات .nexy](README.md)
