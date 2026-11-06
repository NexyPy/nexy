# تخطيطات الواجهة الأمامية

**التخطيط** هو غلاف يحدد البنية المشتركة حول صفحة واحدة أو أكثر. تتيح التخطيطات تجربة "شبيهة بالتطبيق" من خلال الحفاظ على الحالة وتجنب إعادة تحميل الصفحة بالكامل أثناء التنقل.

## منطق التعشيش

تتبع التخطيطات بنية هرمية تعتمد على شجرة الدليل ضمن `src/routes/`.

1.  **تخطيط الجذر**: كل مشروع له تخطيط جذر (على سبيل المثال، `src/routes/layout.nexy`). هذا هو التخطيط الوحيد المسؤول عن تعريف غلاف المستند: `<html>`، `<head>`، و `<body>`.
2.  **التخطيطات المتداخلة**: يمكن أن يحتوي أي مجلد على ملف `layout.*` خاص به. يقوم هذا التخطيط بتغليف جميع الصفحات والتخطيطات الفرعية داخل هذا المجلد.
3.  **الوراثة**: يتم تغليف الصفحة بجميع التخطيطات من الجذر إلى المجلد الخاص بها.

```text
src/routes/
├─ layout.tsx            root: <html>, <head>, <body>
├─ index.tsx             root > page
└─ dashboard/
   ├─ layout.tsx         nested: the dashboard menu
   └─ settings.tsx       root > dashboard > page
```

يرسم التخطيط المتداخل الجزء الخاص به فقط من واجهة المستخدم ويضع الصفحة حيث يذهب `children`:

```tsx filename="src/routes/dashboard/layout.tsx"
import type { ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="dashboard">
      <nav>Dashboard</nav>
      <main>{children}</main>
    </div>
  );
}
```

## الحالة المشتركة والتكوين

تم تصميم التخطيطات لتكون مستقرة. في وضع العميل، عند التنقل بين صفحتين تشتركان في نفس التخطيط، لا يتم إعادة عرض التخطيط ****؛ يتغير محتوى الطفل فقط. في وضع الخادم، كل تنقل هو مستند جديد.

- **الفتحات**: توفر التخطيطات فتحة حيث يتم إدخال الصفحة المتداخلة: `children` في JSX، والدعامة `children` في تخطيط `.nexy`.
- **الحفاظ على الحالة**: نظرًا لأن التخطيط يظل مثبتًا، فإن أي حالة موجودة بداخله (على سبيل المثال، استعلام بحث في الرأس) يتم الاحتفاظ بها أثناء التنقل.

نفس الفتحة في تخطيط `.nexy`:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children }}</body>
</html>
```

يحتفظ حقل البحث أدناه بما كتبه المستخدم أثناء تنقله بين صفحات لوحة المعلومات، لأن التخطيط الذي يحمله لا يتم إلغاء تحميله أبدًا:

```tsx filename="src/routes/dashboard/layout.tsx"
import { useState, type ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const [query, setQuery] = useState("");
  return (
    <>
      <input value={query} onChange={(event) => setQuery(event.target.value)} />
      {children}
    </>
  );
}
```

## القيود الثابتة

بالنسبة للمسارات التي تم عرضها مسبقًا (SSG)، لا يمكن أن يعتمد تخطيط الجذر على بيانات وقت الطلب مثل ملفات تعريف الارتباط أو الرؤوس. ويجب أن تكون قابلة للتمثيل كقشرة ثابتة يقوم العميل بعد ذلك بترطيبها.

اقرأ السمة من المتصفح بدلاً من ذلك، في برنامج نصي للصدفة الثابتة:

```tsx filename="src/routes/layout.tsx"
import type { ReactNode } from "react";

const theme = `document.documentElement.dataset.theme =
  localStorage.getItem("theme") ?? "light";`;

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <head>
        <script dangerouslySetInnerHTML={{ __html: theme }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

## تنفيذ الإطار

يختلف تنفيذ الفتحات والتداخل قليلاً حسب الإطار. راجع دليل **الاختلافات** للتكنولوجيا التي اخترتها:

- [React الاختلافات](../react/differences.md)
- [Vue الاختلافات](../vue/differences.md)
- [Svelte الاختلافات](../svelte/differences.md)
- [Solid الاختلافات](../solid/differences.md)
- [Preact الاختلافات](../preact/differences.md)
