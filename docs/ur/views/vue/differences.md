# Vue

Nexy سرور پر 3 سنگل فائل کے اجزاء کو Vue رینڈر کرتا ہے، پھر Vue انہیں براؤزر میں لے جاتا ہے۔ صفحات، ترتیب، جزیرے اور اعمال ہر فریم ورک میں ایک جیسے ہیں: یہ صفحہ سیٹ اپ کا احاطہ کرتا ہے، پھر وہ حصے جو [مشترکہ معاہدوں](../frontend/pages.md) سے مختلف ہوتے ہیں۔

| موڈ | `nexyconfig.py` | صفحات ہیں | Vue ہے |
|---|---|---|---|
| سرور (پہلے سے طے شدہ) | `useCSR = False` | `.nexy` فائلیں | [جزیرے](../../rendering/islands.md) ان صفحات کے اندر |
| کلائنٹ | `useCSR = True` | `.vue` فائلیں | پورا صفحہ، [لے آؤٹس](../frontend/layouts.md) اور کلائنٹ روٹر کے ساتھ |

## ایک پروجیکٹ شروع کریں۔

```bash
nx new my-app --template web-fbr-vue
```

ٹیمپلیٹ ایک سرور موڈ پروجیکٹ ہے جس میں Vue جزائر ہیں۔ اس کی بجائے اشارے کا جواب دینے کے لیے بغیر کسی ٹیمپلیٹ کے `nx new my-app` چلائیں: روٹر، پروجیکٹ کی قسم، آیا کلائنٹ سائیڈ روٹنگ استعمال کرنا ہے، پھر فریم ورک۔

## موجودہ پروجیکٹ میں Vue کو فعال کریں۔

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

`nx new` اس فائل کو لکھتے ہیں۔ Nexy خود `__nexy__/vite.ts` لکھتا ہے، اس لیے اس میں ترمیم نہ کریں۔

| پیکیج | ورژن `nx new` لکھتا ہے |
|---|---|
| `vue` | `^3.5.33` |
| `@vitejs/plugin-vue` | `^6.0.0` |

## قواعد

- **فی پروجیکٹ ایک فریم ورک۔** `useFF` بالکل ایک فریم ورک لیتا ہے۔ `useFF = [vue(), react()]` شروع ہونے پر سرور کو روکتا ہے۔
- **ایک جزو فی فائل** ایک `.vue` فائل اپنے جزو کو بطور ڈیفالٹ برآمد کرتی ہے۔ جس نام کے تحت آپ اسے درآمد کرتے ہیں وہ صرف وہی ٹیگ ہے جو آپ لکھتے ہیں۔
- **اجزاء باہر رہتے ہیں `src/routes/`**، عام طور پر `src/components/` میں، اس لیے وہ صفحات نہیں ہیں۔
- **سرور موڈ پراجیکٹ میں کوئی `.vue` صفحہ** نہیں ہوتا، اور کلائنٹ موڈ پروجیکٹ کا کوئی `.nexy` صفحہ نہیں ہوتا: Nexy شروع کرنے سے انکار کرتا ہے اور فائل کو نام دیتا ہے۔ دیکھیں [موڈز](../../routing/fbr/modes.md)۔

## صفحات

کلائنٹ موڈ (`useCSR = True`) میں، صفحہ ایک `.vue` فائل ہے۔

### صفحہ کا جزو

صفحہ `<script setup>` بلاک کے ذریعہ بیان کردہ جزو ہے۔

```vue filename="src/routes/index.vue"
<template>
  <h1>Hello</h1>
</template>
```

### متحرک طبقات

یو آر ایل کے پیرامیٹرز پرپس کے طور پر صفحہ تک پہنچتے ہیں۔ آپ ان کا اعلان `defineProps` استعمال کر سکتے ہیں:

```vue filename="src/routes/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

متبادل طور پر، کسی بھی جزو میں `@nexy/client` سے `useParams` ہک استعمال کریں۔

## لے آؤٹ

### عمل درآمد

روٹ لے آؤٹ دستاویز کے شیل کی وضاحت کرتا ہے۔ نیسٹڈ لے آؤٹ مواد کو اپنے ڈیفالٹ سلاٹ میں لپیٹ دیتے ہیں۔

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

## جزائر

سرور موڈ میں، ایک Vue جز ایک `.nexy` فائل میں درآمد کیا گیا ایک جزیرہ ہے۔

### درآمد کرنا

`.nexy` فائل کے فرنٹ میٹر میں اجزاء درآمد کریں:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.vue" import Counter
---
<Counter start=3 />
```

### ہائیڈریشن کی ہدایات

جزیرہ ہائیڈریٹ ہونے پر کنٹرول کرنے کے لیے `directive` سہارے کا استعمال کریں:

- `client:load` (پہلے سے طے شدہ): فوری طور پر
- `client:idle`: جب براؤزر بیکار ہو۔
- `client:visible`: جب یہ منظر میں سکرول کرتا ہے۔
- `client:media`: جب میڈیا کا سوال مماثل ہو۔

## اعمال اور نیویگیشن

### کالنگ اعمال

ایکشن کال کی حالت کو منظم کرنے کے لیے `useAction` ہک کا استعمال کریں۔ Vue میں، واپس کی گئی حالت (`pending`، `data`، `error`) شمار شدہ ریف ہیں۔

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

### نیویگیشن

کلائنٹ سائڈ ٹرانزیشن کے لیے `Link` جزو کا استعمال کریں:

```vue
<template>
  <Link href="/about" active-class="active">About</Link>
</template>
```

پروگرامیٹک نیویگیشن کے لیے، `useRouter` ہک استعمال کریں:

```ts
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### یو آر ایل تک رسائی

تمام لوکیشن ہکس کمپیوٹیڈ ریفز واپس کرتے ہیں:

- `usePathname()`: موجودہ راستہ
- `useParams()`: متحرک طبقات
- `useSearchParams()`: استفسار کی تار
- `useLocation()`: مکمل مقام آبجیکٹ

## اگلے اقدامات

- [ملاحظات](../README.md): ان فارمیٹس کا موازنہ کریں جو صفحہ استعمال کر سکتا ہے۔
- [فرنٹ اینڈ](../../guides/frontend.md): Vite اور کلائنٹ کی تعمیر
