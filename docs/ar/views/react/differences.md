# التفاعل

يعرض Nexy مكونات React 19 على الخادم، ثم يقوم React بترطيبها في المتصفح. الصفحات،
التخطيطات والجزر والإجراءات هي نفسها في كل إطار عمل: تغطي هذه الصفحة الإعداد ثم الأجزاء
التي تختلف عن [العقود المشتركة](../frontend/pages.md).

| الوضع | `nexyconfig.py` | الصفحات هي | التفاعل هو |
|---|---|---|---|
| الخادم (افتراضي) | `useCSR = False` | `.nexy` الملفات | [الجزر](../../rendering/islands.md) داخل تلك الصفحات |
| العميل | `useCSR = True` | `.tsx` ملفات | الصفحة بأكملها، مع [التخطيطات](../frontend/layouts.md) وجهاز توجيه العميل |

## بدء المشروع

```bash
nx new my-app --template web-fbr-react
```

القالب عبارة عن مشروع في وضع الخادم مع جزر React. تشغيل `nx new my-app` بدون قالب ل
أجب عن المطالبات بدلاً من ذلك: جهاز التوجيه، ونوع المشروع، وما إذا كنت تريد استخدام التوجيه من جانب العميل، ثم
الإطار.

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

| الحزمة | الإصدار `nx new` يكتب |
|---|---|
| `react`، `react-dom` | `^19.2.5` |
| `@vitejs/plugin-react` | `^5.2.0` |
| `@types/react`، `@types/react-dom` | تبعيات التطوير |

## القواعد

- **إطار واحد لكل مشروع.** `useFF` يأخذ إطارًا واحدًا بالضبط؛ `useFF = [react(), vue()]` توقف
  الخادم عند بدء التشغيل.
- **الصفحات هي `.tsx`.** تمتلك React `.tsx` و`.jsx` للمكونات، ولكن ملف `.tsx` فقط ضمن
  `src/routes/` تصبح صفحة.
- **المكونات تعيش خارج `src/routes/`**، عادة في `src/components/`، لذا فهي ليست صفحات.
- **مشروع وضع الخادم لا يحتوي على `.tsx` صفحة**، ومشروع وضع العميل لا يحتوي على `.nexy` صفحة: Nexy
  يرفض البدء ويسمي الملف. انظر [الأوضاع](../../routing/fbr/modes.md).

## الصفحات

في وضع العميل (`useCSR = True`)، تكون الصفحة عبارة عن ملف `.tsx`.

### مكون الصفحة

الصفحة هي التصدير الافتراضي للملف. في حالة عدم وجود تصدير افتراضي، يقوم Nexy باختيار الاسم الأول
تصدير.

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

## الجزر

في وضع الخادم، يكون مكون React المستورد في ملف `.nexy` عبارة عن جزيرة.

###  الاستيراد

استيراد المكونات في الجزء الأمامي من الملف `.nexy`:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```

### توجيهات الترطيب

استخدم الدعامة `directive` للتحكم في وقت ترطيب الجزيرة:

- `client:load` (الافتراضي): على الفور
- `client:idle`: عندما يكون المتصفح خاملاً
- `client:visible`: عند التمرير إلى العرض
- `client:media`: عندما يتطابق استعلام الوسائط

## الإجراءات والملاحة

### إجراءات النداء

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

- [المشاهدات](../README.md): قارن التنسيقات التي يمكن للصفحة استخدامها
- [Frontend](../../guides/frontend.md): بناء فايت والعميل