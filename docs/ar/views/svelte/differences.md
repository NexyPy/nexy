# Svelte

يعرض Nexy Svelte 5 مكونات على الخادم، ثم يتولى Svelte تشغيلها في المتصفح. الصفحات والتخطيطات والجزر والإجراءات هي نفسها في كل إطار: تغطي هذه الصفحة الإعداد، ثم الأجزاء التي تختلف عن [العقود المشتركة](../frontend/pages.md).

| الوضع | `nexyconfig.py` | الصفحات هي | Svelte هو |
|---|---|---|---|
| الخادم (الافتراضي) | `useCSR = False` | `.nexy` الملفات | [الجزر](../../rendering/islands.md) داخل تلك الصفحات |
| العميل | `useCSR = True` | `.svelte` يقوم بملفات | الصفحة بأكملها، مع [التخطيطات](../frontend/layouts.md) وجهاز توجيه العميل |

## ابدأ مشروعًا

```bash
nx new my-app --template web-fbr-svelte
```

القالب عبارة عن مشروع في وضع الخادم يحتوي على Svelte جزر. قم بتشغيل `nx new my-app` بدون قالب للإجابة على المطالبات بدلاً من ذلك: جهاز التوجيه، ونوع المشروع، وما إذا كان سيتم استخدام التوجيه من جانب العميل، ثم إطار العمل.

## تمكين Svelte في مشروع موجود

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), svelte()],
  customLogger: nexy.log(),
});
```

`nx new` يكتب هذا الملف؛ Nexy يكتب `__nexy__/vite.ts` نفسه، فلا تقم بتحريره.

| الحزمة | الإصدار `nx new` يكتب |
|---|---|
| `svelte` | `^5.20.2` |
| `@sveltejs/vite-plugin-svelte` | `^5.0.0` |

## القواعد

- **Svelte 5.** تستخدم المكونات الأحرف الرونية: `$props()`، `$state()`، ومقتطفات للأطفال.
- **إطار واحد لكل مشروع.** `useFF` يأخذ إطارًا واحدًا بالضبط؛ `useFF = [svelte(), vue()]` يقوم بإيقاف الخادم عند بدء التشغيل.
- **مكون واحد لكل ملف.** الاسم الذي تستورد ملف `.svelte` تحته هو فقط العلامة التي تكتبها.
- **تعيش المكونات خارج `src/routes/`**، عادةً في `src/components/`، لذا فهي ليست صفحات.
- **لا يحتوي مشروع وضع الخادم على `.svelte` صفحة**، ولا يحتوي مشروع وضع العميل على `.nexy` صفحة: يرفض Nexy البدء ويسمي الملف. انظر [الأوضاع](../../routing/fbr/modes.md).

## الصفحات

في وضع العميل (`useCSR = True`)، تكون الصفحة عبارة عن ملف `.svelte`.

### مكون الصفحة

الصفحة هي المكون المحدد بواسطة كتلة البرنامج النصي للملف `.svelte`.

```svelte filename="src/routes/index.svelte"
<script lang="ts">
</script>

<h1>Hello</h1>
```

### القطاعات الديناميكية

تصل معلمات URL إلى الصفحة كدعائم عبر الأمر `$props()`:

```svelte filename="src/routes/blog/[slug].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

وبدلاً من ذلك، استخدم المخزن `$params` من `@nexy/client` في أي مكون.

## التخطيطات

### التنفيذ

يحدد التخطيط الجذر غلاف المستند. تقوم التخطيطات المتداخلة بتغليف المحتوى باستخدام المقتطف `children`.

```svelte filename="src/routes/layout.svelte"
<script lang="ts">
  import type { Snippet } from "svelte";
  let { children }: { children?: Snippet } = $props();
</script>

<html>
  <body>
    <header>My app</header>
    <main>{@render children?.()}</main>
  </body>
</html>
```

## جزر

في وضع الخادم، يكون المكون Svelte المستورد في ملف `.nexy` عبارة عن جزيرة.

### استيراد

قم باستيراد المكونات الموجودة في الجزء الأمامي من الملف `.nexy`:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.svelte" import Counter
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

استخدم الخطاف `useAction` لإدارة حالة استدعاء الإجراء. في Svelte، يؤدي هذا إلى إرجاع متجر (اقرأ مع `$`).

```svelte
<script lang="ts">
  import { useAction } from "@nexy/client";
  import { add_todo } from "@nexy/actions";

  let title = $state("");
  const save = useAction(add_todo, { onSuccess: () => (title = "") });
</script>

<form onsubmit={(e) => { e.preventDefault(); save.run({ title }); }}>
  <input bind:value={title} />
  <button disabled={$save.pending}>Add</button>
</form>
```

### الملاحة

استخدم المكون `Link` للانتقالات من جانب العميل:

```svelte
<script lang="ts">
  import Link from "@nexy/Link.svelte";
</script>

<Link href="/about" activeClass="active">About</Link>
```

للتنقل البرمجي، استخدم الكائن `router` من `@nexy/client`:

```ts
import { router } from "@nexy/client";

router.push("/dashboard");
```

### الوصول إلى URL

يتم توفير جميع بيانات الموقع كمتاجر:

- `$pathname`: المسار الحالي
- `$params`: المقاطع الديناميكية
- `$searchParams`: سلسلة الاستعلام
- `$location`: كائن الموقع الكامل

## الخطوات التالية

- [المشاهدات](../README.md): قارن التنسيقات التي يمكن للصفحة استخدامها
- ](../../guides/frontend.md): Vite وبناء العميل
