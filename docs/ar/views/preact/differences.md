# Preact

يقوم Nexy بعرض Preact 10 مكونات على الخادم، ثم Preact يتولى إدارتها في المتصفح. الصفحات والتخطيطات والجزر والإجراءات هي نفسها في كل إطار: تغطي هذه الصفحة الإعداد، ثم الأجزاء التي تختلف عن [العقود المشتركة](../frontend/pages.md).

| الوضع | `nexyconfig.py` | الصفحات هي | Preact هو |
|---|---|---|---|
| الخادم (الافتراضي) | `useCSR = False` | `.nexy` ملفات | [جزر](../../rendering/islands.md) داخل تلك الصفحات |
| العميل | `useCSR = True` | `.tsx` ملفات | الصفحة بأكملها، مع [التخطيطات](../frontend/layouts.md) وجهاز توجيه العميل |

## ابدأ مشروعًا

```bash
nx new my-app --template web-fbr-preact
```

القالب عبارة عن مشروع في وضع الخادم يحتوي على Preact جزر. قم بتشغيل `nx new my-app` بدون قالب للإجابة على المطالبات بدلاً من ذلك: جهاز التوجيه، ونوع المشروع، وما إذا كان سيتم استخدام التوجيه من جانب العميل، ثم إطار العمل.

## تمكين Preact في مشروع موجود

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import preact


class NexyConfig(NexyConfigModel):
    useFF = preact()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import preact from "@preact/preset-vite";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), preact()],
  customLogger: nexy.log(),
});
```

`nx new` يكتب هذا الملف؛ Nexy يكتب `__nexy__/vite.ts` نفسه، فلا تقم بتحريره.

| الحزمة | النسخة `nx new` يكتب |
|---|---|
| `preact` | `^10.25.4` |
| `@preact/preset-vite` | `^2.10.1` (تبعية التطوير) |
| `preact-render-to-string` | `^6.7.0` (تبعية التطوير، يتم عرضها على الخادم) |

## اكتب Preact

المكون Preact هو دالة بنمط التفاعل. الاختلافات المهمة هنا:

```tsx filename="src/components/Counter.tsx"
import { useState } from "preact/hooks";

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start);
  return <button class="counter" onClick={() => setCount(count + 1)}>{count}</button>;
}
```

- تأتي الخطافات من `preact/hooks`، وأنواع مثل `ComponentChildren` من `preact`.
- اكتب سمات HTML: `class`، `for`، `charset`. `Link` يقرأ فصوله من `class`.

## القواعد

- **إطار واحد لكل مشروع.** `useFF` يأخذ إطارًا واحدًا بالضبط؛ `useFF = [preact(), react()]` يقوم بإيقاف الخادم عند بدء التشغيل. مع `useFF = preact()`، كل `.tsx` ملف هو Preact.
- **الصفحات هي `.tsx`.** فقط ملف `.tsx` ضمن `src/routes/` يصبح صفحة؛ `.jsx` جيد بالنسبة للمكون.
- **تعيش المكونات خارج `src/routes/`**، عادةً في `src/components/`، لذا فهي ليست صفحات.
- **لا يحتوي مشروع وضع الخادم على `.tsx` صفحة**، ولا يحتوي مشروع وضع العميل على `.nexy` صفحة: يرفض Nexy البدء ويسمي الملف. انظر [الأوضاع](../../routing/fbr/modes.md).
- **يتم استيراد صفحة `.mdx` من `"preact"`.** يقوم Nexy بتجميع ملف `.mdx` مع Preact فقط عندما يرى هذا الاستيراد، على سبيل المثال `import { h } from "preact"`، ومع React بخلاف ذلك. انظر [Markdown و MDX](../nexy/markdown.md).

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

يحدد التخطيط الجذر غلاف المستند. تقوم التخطيطات المتداخلة بتغليف المحتوى.

```tsx filename="src/routes/layout.tsx"
import type { ComponentChildren } from "preact";

export default function RootLayout({ children }: { children: ComponentChildren }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

## جزر

في وضع الخادم، يكون المكون Preact المستورد في ملف `.nexy` عبارة عن جزيرة.

### استيراد

قم باستيراد المكونات الموجودة في الجزء الأمامي من الملف `.nexy`:

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

استخدم المكون `Link` للانتقالات من جانب العميل. لاحظ أن Preact يستخدم `class` بدلاً من `className`:

```tsx
import { Link } from "@nexy/client";

<Link href="/about" class="nav" activeClassName="active">About</Link>
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
