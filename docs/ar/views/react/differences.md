# React

يعرض Nexy React 19 مكونًا على الخادم، ثم React يرطبها في المتصفح. الصفحات والتخطيطات والجزر والإجراءات هي نفسها في كل إطار: تغطي هذه الصفحة الإعداد، ثم الأجزاء التي تختلف عن [العقود المشتركة](../frontend/pages.md).

| الوضع | `nexyconfig.py` | الصفحات هي | React هو |
|---|---|---|---|
| الخادم (الافتراضي) | `useCSR = False` | `.nexy` ملفات | [جزر](../../rendering/islands.md) داخل تلك الصفحات |
| العميل | `useCSR = True` | `.tsx` ملفات | الصفحة بأكملها، مع [التخطيطات](../frontend/layouts.md) وجهاز توجيه العميل |

## ابدأ مشروعًا

```bash
nx new my-app --template web-fbr-react
```

القالب عبارة عن مشروع في وضع الخادم يحتوي على React جزر. قم بتشغيل `nx new my-app` بدون قالب للإجابة على المطالبات بدلاً من ذلك: جهاز التوجيه، ونوع المشروع، وما إذا كان سيتم استخدام التوجيه من جانب العميل، ثم إطار العمل.

## تمكين React في مشروع موجود

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), react()],
  customLogger: nexy.log(),
});
```

`nx new` يكتب هذا الملف؛ Nexy يكتب `__nexy__/vite.ts` نفسه، فلا تقم بتحريره.

| الحزمة | النسخة `nx new` يكتب |
|---|---|
| `react`، `react-dom` | `^19.2.5` |
| `@vitejs/plugin-react` | `^5.2.0` |
| `@types/react`، `@types/react-dom` | تبعيات التطوير |

## القواعد

- **إطار واحد لكل مشروع.** `useFF` يأخذ إطارًا واحدًا بالضبط؛ `useFF = [react(), vue()]` يقوم بإيقاف الخادم عند بدء التشغيل.
- **الصفحات هي `.tsx`.** React تمتلك `.tsx` و `.jsx` للمكونات، ولكن فقط الملف `.tsx` ضمن `src/routes/` يصبح صفحة.
- **تعيش المكونات خارج `src/routes/`**، عادةً في `src/components/`، لذا فهي ليست صفحات.
- **لا يحتوي مشروع وضع الخادم على `.tsx` صفحة**، ولا يحتوي مشروع وضع العميل على `.nexy` صفحة: يرفض Nexy البدء ويسمي الملف. انظر [أوضاع](../../routing/fbr/modes.md).

## الصفحات

في وضع العميل (`useCSR = True`)، تكون الصفحة عبارة عن ملف `.tsx`.

### مكون الصفحة

الصفحة هي التصدير الافتراضي للملف. في حالة عدم وجود تصدير افتراضي، يقوم Nexy باختيار أول عملية تصدير مسماة.

```tsx filename="src/routes/index.tsx"
export default function Home() {
  return <h1>Hello</h1>;
}
```

### القطاعات الديناميكية

تتوفر معلمات URL عبر الخطاف `useParams`:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

## التخطيطات

### التنفيذ

يحدد التخطيط الجذر غلاف المستند. تقوم التخطيطات المتداخلة بتغليف المحتوى الموجود أسفلها.

```tsx filename="src/routes/layout.tsx"
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
```

## جزر

في وضع الخادم، يكون المكون React المستورد في ملف `.nexy` عبارة عن جزيرة.

### استيراد

استيراد المكونات في الجزء الأمامي من الملف `.nexy`:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```

### توجيهات الترطيب

استخدم الدعامة `directive` للتحكم في وقت ترطيب الجزيرة:

- `client:load` (افتراضي): فورًا
- `client:idle`: عندما يكون المتصفح خاملاً
- `client:visible`: عند التمرير إلى العرض
- `client:media`: عندما يتطابق استعلام الوسائط

## الإجراءات والملاحة

### إجراءات الدعوة

استخدم الخطاف `useAction` لإدارة حالة استدعاء الإجراء:

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const { run, pending, error, data } = useAction(add_todo);
// ...
<button onClick={() => run({ title: "New Task" })}>Add</button>
```

### الملاحة

استخدم المكون `Link` للانتقالات من جانب العميل:

```tsx
import { Link } from "@nexy/client";

<Link href="/about">About</Link>
```

للتنقل البرمجي، استخدم الخطاف `useRouter`:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### الوصول إلى URL

- `usePathname()`: المسار الحالي
- `useParams()`: المقاطع الديناميكية
- `useSearchParams()`: سلسلة الاستعلام
- `useLocation()`: كائن الموقع الكامل

## الخطوات التالية

- [طرق العرض](../README.md): قارن التنسيقات التي يمكن للصفحة استخدامها
- [الواجهة الأمامية](../../guides/frontend.md): Vite وبناء العميل
