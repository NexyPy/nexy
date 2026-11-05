# Vue

يقوم Nexy بعرض Vue 3 مكونات ذات ملف واحد على الخادم، ثم Vue يتولى تشغيلها في المتصفح. الصفحات والتخطيطات والجزر والإجراءات هي نفسها في كل إطار: تغطي هذه الصفحة الإعداد، ثم الأجزاء التي تختلف عن [العقود المشتركة](../frontend/pages.md).

| الوضع | `nexyconfig.py` | الصفحات هي | Vue هو |
|---|---|---|---|
| الخادم (الافتراضي) | `useCSR = False` | `.nexy` ملفات | [جزر](../../rendering/islands.md) داخل تلك الصفحات |
| العميل | `useCSR = True` | `.vue` ملفات | الصفحة بأكملها، مع [التخطيطات](../frontend/layouts.md) وجهاز توجيه العميل |

## ابدأ مشروعًا

```bash
nx new my-app --template web-fbr-vue
```

القالب عبارة عن مشروع في وضع الخادم يحتوي على Vue جزر. قم بتشغيل `nx new my-app` بدون قالب للإجابة على المطالبات بدلاً من ذلك: جهاز التوجيه، ونوع المشروع، وما إذا كان سيتم استخدام التوجيه من جانب العميل، ثم إطار العمل.

## تمكين Vue في مشروع موجود

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), vue()],
  customLogger: nexy.log(),
});
```

`nx new` يكتب هذا الملف؛ Nexy يكتب `__nexy__/vite.ts` نفسه، فلا تقم بتحريره.

| الحزمة | النسخة `nx new` يكتب |
|---|---|
| `vue` | `^3.5.33` |
| `@vitejs/plugin-vue` | `^6.0.0` |

## القواعد

- **إطار واحد لكل مشروع.** `useFF` يأخذ إطارًا واحدًا بالضبط؛ `useFF = [vue(), react()]` يقوم بإيقاف الخادم عند بدء التشغيل.
- **مكون واحد لكل ملف.** يقوم الملف `.vue` بتصدير مكونه بشكل افتراضي؛ الاسم الذي تستورده تحته هو فقط العلامة التي تكتبها.
- **تعيش المكونات خارج `src/routes/`**، عادةً في `src/components/`، لذا فهي ليست صفحات.
- **لا يحتوي مشروع وضع الخادم على `.vue` صفحة**، ولا يحتوي مشروع وضع العميل على `.nexy` صفحة: يرفض Nexy البدء ويسمي الملف. انظر [الأوضاع](../../routing/fbr/modes.md).

## الصفحات

في وضع العميل (`useCSR = True`)، تكون الصفحة عبارة عن ملف `.vue`.

### مكون الصفحة

الصفحة هي المكون المحدد بواسطة الكتلة `<script setup>`.

```vue filename="src/routes/index.vue"
<template>
  <h1>Hello</h1>
</template>
```

### القطاعات الديناميكية

تصل معلمات URL إلى الصفحة كدعائم. يمكنك إعلانها باستخدام `defineProps`:

```vue filename="src/routes/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

وبدلاً من ذلك، استخدم الخطاف `useParams` من `@nexy/client` في أي مكون.

## التخطيطات

### التنفيذ

يحدد التخطيط الجذر غلاف المستند. تقوم التخطيطات المتداخلة بتغليف المحتوى في الفتحة الافتراضية الخاصة بها.

```vue filename="src/routes/layout.vue"
<template>
  <html>
    <body>
      <header>My app</header>
      <main><slot /></main>
    </body>
  </html>
</template>
```

## جزر

في وضع الخادم، يكون المكون Vue المستورد في ملف `.nexy` عبارة عن جزيرة.

### استيراد

استيراد المكونات في الجزء الأمامي من الملف `.nexy`:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.vue" import Counter
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

استخدم الخطاف `useAction` لإدارة حالة استدعاء الإجراء. في Vue، الحالة التي تم إرجاعها (`pending`، `data`، `error`) هي مراجع محسوبة.

```vue
<script setup lang="ts">
import { ref } from "vue";
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const title = ref("");
const { run, pending, error, data } = useAction(add_todo, {
  onSuccess: () => (title.value = ""),
});
</script>

<template>
  <form @submit.prevent="run({ title })">
    <input v-model="title" />
    <button :disabled="pending">Add</button>
  </form>
</template>
```

### الملاحة

استخدم المكون `Link` للانتقالات من جانب العميل:

```vue
<template>
  <Link href="/about" active-class="active">About</Link>
</template>
```

للتنقل البرمجي، استخدم الخطاف `useRouter`:

```ts
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### الوصول إلى URL

تُرجع جميع خطافات الموقع المراجع المحسوبة:

- `usePathname()`: المسار الحالي
- `useParams()`: المقاطع الديناميكية
- `useSearchParams()`: سلسلة الاستعلام
- `useLocation()`: كائن الموقع الكامل

## الخطوات التالية

- [طرق العرض](../README.md): قارن التنسيقات التي يمكن للصفحة استخدامها
- [الواجهة الأمامية](../../guides/frontend.md): Vite وبناء العميل
