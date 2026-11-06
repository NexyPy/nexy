# فرنٹ اینڈ لے آؤٹ

ایک **لے آؤٹ** ایک ریپر ہے جو ایک یا زیادہ صفحات کے ارد گرد مشترکہ ڈھانچے کی وضاحت کرتا ہے۔ لے آؤٹ حالت کو محفوظ رکھ کر اور نیویگیشن کے دوران پورے صفحے کے دوبارہ لوڈ ہونے سے گریز کرکے "ایپ کی طرح" کے تجربے کو فعال کرتے ہیں۔

## نیسٹنگ لاجک

لے آؤٹ `src/routes/` کے نیچے ڈائریکٹری کے درخت کی بنیاد پر درجہ بندی کی ساخت کی پیروی کرتے ہیں۔

1.  **روٹ لے آؤٹ**: ہر پروجیکٹ کا روٹ لے آؤٹ ہوتا ہے (مثال کے طور پر، `src/routes/layout.nexy`)۔ دستاویز کے شیل کی وضاحت کے لیے یہ واحد ترتیب ذمہ دار ہے: `<html>`، `<head>`، اور `<body>`۔
2.  **نیسٹڈ لے آؤٹ**: کوئی بھی فولڈر اس کی اپنی `layout.*` فائل رکھ سکتا ہے۔ یہ لے آؤٹ تمام صفحات اور ذیلی ترتیب کو اس فولڈر میں لپیٹ دیتا ہے۔
3.  **وراثت**: ایک صفحہ تمام ترتیب سے جڑ سے نیچے اس کے اپنے فولڈر میں لپیٹ دیا جاتا ہے۔

```text
src/routes/
├─ layout.tsx            root: <html>, <head>, <body>
├─ index.tsx             root > page
└─ dashboard/
   ├─ layout.tsx         nested: the dashboard menu
   └─ settings.tsx       root > dashboard > page
```

نیسٹڈ لے آؤٹ صرف UI کا اپنا حصہ کھینچتا ہے اور اس صفحہ کو رکھتا ہے جہاں `children` جاتا ہے:

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

## مشترکہ ریاست اور ساخت

لے آؤٹ کو مستحکم کرنے کے لیے ڈیزائن کیا گیا ہے۔ کلائنٹ موڈ میں، ایک ہی ترتیب والے دو صفحات کے درمیان نیویگیٹ کرتے وقت، لے آؤٹ کو دوبارہ پیش کیا جاتا ہے **نہیں**؛ صرف بچوں کا مواد تبدیل ہوتا ہے۔ سرور موڈ میں ہر نیویگیشن ایک نئی دستاویز ہے۔

- **سلاٹس**: لے آؤٹ ایک سلاٹ فراہم کرتے ہیں جہاں نیسٹڈ پیج لگایا جاتا ہے: `children` JSX میں، اور `children` ایک `.nexy` لے آؤٹ میں پروپ۔
- **ریاستی تحفظ**: چونکہ لے آؤٹ ماؤنٹ رہتا ہے، اس کے اندر موجود کوئی بھی حالت (مثال کے طور پر، ہیڈر میں تلاش کا سوال) نیویگیشن کے دوران محفوظ رہتی ہے۔

ایک `.nexy` ترتیب میں ایک ہی سلاٹ:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children }}</body>
</html>
```

نیچے دی گئی سرچ فیلڈ ڈیش بورڈ کے صفحات کے درمیان منتقل ہونے کے دوران صارف کے ٹائپ کردہ چیزوں کو برقرار رکھتی ہے، کیونکہ جو ترتیب اسے رکھتی ہے وہ کبھی ان ماؤنٹ نہیں ہوتی:

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

## جامد پابندیاں

ایسے راستوں کے لیے جو پہلے سے پیش کیے گئے ہیں (SSG)، روٹ لے آؤٹ درخواست کے وقت کے ڈیٹا جیسے کوکیز یا ہیڈر پر انحصار نہیں کر سکتا۔ یہ ایک جامد شیل کے طور پر قابل نمائندگی ہونا چاہیے جسے کلائنٹ پھر ہائیڈریٹ کرتا ہے۔

جامد شیل کے اسکرپٹ میں اس کے بجائے براؤزر سے تھیم پڑھیں:

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

## فریم ورک کا نفاذ

سلاٹس اور نیسٹنگ کا نفاذ فریم ورک کے لحاظ سے قدرے مختلف ہوتا ہے۔ اپنی منتخب ٹیکنالوجی کے لیے **اختلافات** گائیڈ دیکھیں:

- [React اختلافات](../react/differences.md)
- [Vue اختلافات](../vue/differences.md)
- [Svelte اختلافات](../svelte/differences.md)
- [Solid اختلافات](../solid/differences.md)
- [Preact اختلافات](../preact/differences.md)
