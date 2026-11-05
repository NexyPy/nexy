# Svelte

Nexy سرور پر Svelte 5 اجزاء پیش کرتا ہے، پھر Svelte انہیں براؤزر میں لے جاتا ہے۔ صفحات، ترتیب، جزیرے اور اعمال ہر فریم ورک میں ایک جیسے ہیں: یہ صفحہ سیٹ اپ کا احاطہ کرتا ہے، پھر وہ حصے جو [مشترکہ معاہدوں](../frontend/pages.md) سے مختلف ہوتے ہیں۔

| موڈ | `nexyconfig.py` | صفحات ہیں | Svelte ہے |
|---|---|---|---|
| سرور (پہلے سے طے شدہ) | `useCSR = False` | `.nexy` فائلیں | [جزیرے](../../rendering/islands.md) ان صفحات کے اندر |
| کلائنٹ | `useCSR = True` | `.svelte` فائلیں | پورا صفحہ، [لے آؤٹس](../frontend/layouts.md) اور کلائنٹ روٹر کے ساتھ |

## ایک پروجیکٹ شروع کریں۔

```bash
nx new my-app --template web-fbr-svelte
```

ٹیمپلیٹ ایک سرور موڈ پروجیکٹ ہے جس میں Svelte جزائر ہیں۔ اس کی بجائے اشارے کا جواب دینے کے لیے بغیر کسی ٹیمپلیٹ کے `nx new my-app` چلائیں: روٹر، پروجیکٹ کی قسم، آیا کلائنٹ سائیڈ روٹنگ استعمال کرنا ہے، پھر فریم ورک۔

## موجودہ پروجیکٹ میں Svelte کو فعال کریں۔

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

`nx new` اس فائل کو لکھتے ہیں۔ Nexy خود `__nexy__/vite.ts` لکھتا ہے، اس لیے اس میں ترمیم نہ کریں۔

| پیکیج | ورژن `nx new` لکھتا ہے |
|---|---|
| `svelte` | `^5.20.2` |
| `@sveltejs/vite-plugin-svelte` | `^5.0.0` |

## قواعد

- **Svelte 5** اجزاء رنس کا استعمال کرتے ہیں: `$props()`، `$state()`، اور بچوں کے لیے ٹکڑے
- **فی پروجیکٹ ایک فریم ورک** `useFF` بالکل ایک فریم ورک لیتا ہے۔ `useFF = [svelte(), vue()]` شروع ہونے پر سرور کو روکتا ہے۔
- **ایک جزو فی فائل** آپ جس نام کے تحت `.svelte` فائل درآمد کرتے ہیں وہ صرف وہی ٹیگ ہے جو آپ لکھتے ہیں۔
- **اجزاء باہر رہتے ہیں `src/routes/`**، عام طور پر `src/components/` میں، اس لیے وہ صفحات نہیں ہیں۔
- **سرور موڈ پروجیکٹ کا کوئی `.svelte` صفحہ** نہیں ہوتا، اور کلائنٹ موڈ پروجیکٹ کا کوئی `.nexy` صفحہ نہیں ہوتا: Nexy شروع کرنے سے انکار کرتا ہے اور فائل کو نام دیتا ہے۔ [طریقوں](../../routing/fbr/modes.md) کو دیکھیں۔

## صفحات

کلائنٹ موڈ (`useCSR = True`) میں، صفحہ ایک `.svelte` فائل ہے۔

### صفحہ کا جزو

صفحہ `.svelte` فائل کے اسکرپٹ بلاک کے ذریعہ بیان کردہ جزو ہے۔

```svelte filename="src/routes/index.svelte"
<script lang="ts">
</script>

<h1>Hello</h1>
```

### متحرک طبقات

یو آر ایل پیرامیٹرز `$props()` رن کے ذریعے سہارے کے طور پر صفحہ تک پہنچتے ہیں:

```svelte filename="src/routes/blog/[slug].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

متبادل طور پر، کسی بھی جزو میں `$params` اسٹور سے `@nexy/client` کا استعمال کریں۔

## لے آؤٹ

### عمل درآمد

روٹ لے آؤٹ دستاویز کے شیل کی وضاحت کرتا ہے۔ نیسٹڈ لے آؤٹ `children` کے ٹکڑوں کا استعمال کرتے ہوئے مواد کو سمیٹتے ہیں۔

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

## جزائر

سرور موڈ میں، ایک Svelte جز ایک `.nexy` فائل میں درآمد کیا گیا جزیرہ ہے۔

### درآمد کرنا

`.nexy` فائل کے فرنٹ میٹر میں اجزاء درآمد کریں:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.svelte" import Counter
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

ایکشن کال کی حالت کو منظم کرنے کے لیے `useAction` ہک کا استعمال کریں۔ Svelte میں، یہ ایک اسٹور لوٹاتا ہے (`$` کے ساتھ پڑھیں)۔

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

### نیویگیشن

کلائنٹ سائڈ ٹرانزیشن کے لیے `Link` جزو کا استعمال کریں:

```svelte
<script lang="ts">
  import Link from "@nexy/Link.svelte";
</script>

<Link href="/about" activeClass="active">About</Link>
```

پروگرامیٹک نیویگیشن کے لیے، `router` آبجیکٹ `@nexy/client` سے استعمال کریں:

```ts
import { router } from "@nexy/client";

router.push("/dashboard");
```

### یو آر ایل تک رسائی

تمام مقام کا ڈیٹا اسٹورز کے طور پر فراہم کیا جاتا ہے:

- `$pathname`: موجودہ راستہ
- `$params`: متحرک طبقات
- `$searchParams`: استفسار کی تار
- `$location`: مکمل مقام آبجیکٹ

## اگلے اقدامات

- [ملاحظات](../README.md): ان فارمیٹس کا موازنہ کریں جو صفحہ استعمال کر سکتا ہے۔
- [فرنٹ اینڈ](../../guides/frontend.md): Vite اور کلائنٹ کی تعمیر
