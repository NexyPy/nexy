# Solid

يقوم Nexy بعرض مكونات Solid 1.9 على الخادم، ثم يقوم Solid بتوليها في المتصفح. الصفحات والتخطيطات والجزر والإجراءات هي نفسها في كل إطار: تغطي هذه الصفحة الإعداد، ثم الأجزاء التي تختلف عن [العقود المشتركة](../frontend/pages.md).

| الوضع | `nexyconfig.py` | الصفحات هي | Solid هو |
|---|---|---|---|
| الخادم (الافتراضي) | `useCSR = False` | `.nexy` الملفات | [الجزر](../../rendering/islands.md) داخل تلك الصفحات |
| العميل | `useCSR = True` | `.tsx` يقوم بملفات | الصفحة بأكملها، مع [التخطيطات](../frontend/layouts.md) وجهاز توجيه العميل |

## ابدأ مشروعًا

```bash
nx new my-app --template web-fbr-solid
```

القالب عبارة عن مشروع في وضع الخادم يحتوي على Solid جزر. قم بتشغيل `nx new my-app` بدون قالب للإجابة على المطالبات بدلاً من ذلك: جهاز التوجيه، ونوع المشروع، وما إذا كان سيتم استخدام التوجيه من جانب العميل، ثم إطار العمل.

## تمكين Solid في مشروع موجود

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import solid


class NexyConfig(NexyConfigModel):
    useFF = solid()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import solid from "vite-plugin-solid";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), solid()],
  customLogger: nexy.log(),
});
```

في وضع العميل، اكتب `solid({ ssr: true })`: يقوم Solid بتجميع مكون بشكل مختلف للخادم والمتصفح، ويحتاج وضع العميل إلى كليهما. `nx new` يكتب هذا الملف؛ Nexy يكتب `__nexy__/vite.ts` نفسه، لذا لا تقم بتحريره.

| الحزمة | الإصدار `nx new` يكتب |
|---|---|
| `solid-js` | `^1.9.12` |
| `vite-plugin-solid` | `^2.11.0` (تبعية التطوير) |

## فكر في الإشارات

تعمل وظيفة المكون Solid **مرة واحدة**. تتم قراءة ما يتغير لاحقًا من خلال الإشارة، ويتم تحديث التعبيرات التي تقرأها فقط:

```tsx filename="src/components/Counter.tsx"
import { createSignal } from "solid-js";

export default function Counter(props: { start?: number }) {
  const [count, setCount] = createSignal(props.start ?? 0);
  return <button onClick={() => setCount(count() + 1)}>{count()}</button>;
}
```

- قم باستدعاء الإشارة `count()` الموجودة داخل JSX، وليس في متغير فوقها.
- اقرأ الدعائم كـ `props.start`. يؤدي التدمير `{ start }` إلى قراءة القيمة مرة واحدة ويفقد التحديثات.
- Solid يكتب سمات HTML: `class`، `for`، `charset`، وليس `className`.

## القواعد

- **إطار واحد لكل مشروع.** `useFF` يأخذ إطارًا واحدًا بالضبط؛ `useFF = [solid(), react()]` يوقف الخادم عند بدء التشغيل. مع `useFF = solid()`، كل `.tsx` ملف هو Solid.
- **الصفحات هي `.tsx`.** فقط ملف `.tsx` ضمن `src/routes/` يصبح صفحة؛ `.jsx` جيد بالنسبة للمكون.
- **تعيش المكونات خارج `src/routes/`**، عادةً في `src/components/`، لذا فهي ليست صفحات.
- **لا يحتوي مشروع وضع الخادم على `.tsx` صفحة**، ولا يحتوي مشروع وضع العميل على `.nexy` صفحة: يرفض Nexy البدء ويسمي الملف. انظر [الأوضاع](../../routing/fbr/modes.md).
- **لا يوجد `.mdx` مع Solid.** MDX يُترجم إلى React أو Preact؛ `.md` صفحات العمل.

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

تتوفر معلمات URL عبر الخطاف `useParams`، الذي يُرجع موصلاً:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const params = useParams<{ slug: string }>();
  return <h1>{params().slug}</h1>;
}
```

## التخطيطات

### التنفيذ

يحدد التخطيط الجذر غلاف المستند. تقوم التخطيطات المتداخلة بتغليف المحتوى.

```tsx filename="src/routes/layout.tsx"
import type { JSX } from "solid-js";

export default function RootLayout(props: { children: JSX.Element }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{props.children}</main>
      </body>
    </html>
  );
}
```

ولا تهدم `props.children`، فإن Solid يقرأها كسولا.

## جزر

في وضع الخادم، يكون المكون Solid المستورد في ملف `.nexy` عبارة عن جزيرة.

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

استخدم الخطاف `useAction` لإدارة حالة استدعاء الإجراء. في Solid، يؤدي هذا إلى إرجاع الوصول (استدعائهم كوظائف).

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const save = useAction(add_todo);
// ...
<button disabled={save.pending()}>Add</button>
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

تقوم جميع خطافات الموقع بإرجاع أدوات الوصول:

- `usePathname()`: المسار الحالي
- `useParams()`: المقاطع الديناميكية
- `useSearchParams()`: سلسلة الاستعلام
- `useLocation()`: كائن الموقع الكامل

## الخطوات التالية

- [المشاهدات](../README.md): قارن التنسيقات التي يمكن للصفحة استخدامها
- ](../../guides/frontend.md): Vite وبناء العميل
