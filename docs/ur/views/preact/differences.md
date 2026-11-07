# Preact

Nexy سرور پر Preact 10 اجزاء پیش کرتا ہے، پھر Preact انہیں براؤزر میں لے جاتا ہے۔ صفحات، ترتیب، جزیرے اور اعمال ہر فریم ورک میں ایک جیسے ہیں: یہ صفحہ سیٹ اپ کا احاطہ کرتا ہے، پھر وہ حصے جو [مشترکہ معاہدوں](../frontend/pages.md) سے مختلف ہوتے ہیں۔

<!-- router:fbr,custom -->
| موڈ | `nexyconfig.py` | صفحات ہیں۔ | Preact ہے۔ |
|---|---|---|---|
| سرور (پہلے سے طے شدہ) | `useCSR = False` | `.nexy` فائلیں | [جزائر](../../rendering/islands.md) ان صفحات کے اندر |
| کلائنٹ | `useCSR = True` | `.tsx` فائلیں | پورا صفحہ، [لے آؤٹس](../frontend/layouts.md) اور کلائنٹ روٹر کے ساتھ |
<!-- /router -->

<!-- router:modular -->
ماڈیولر راؤٹر کے ساتھ، Preact اجزاء [جزیرے](../../rendering/islands.md) ہوتے ہیں `.nexy` ویوز کے اندر ایک کنٹرولر واپس آتا ہے: کوئی صفحہ فائل نہیں ہے اور کوئی کلائنٹ راؤٹر نہیں ہے۔
<!-- /router -->

## ایک پروجیکٹ شروع کریں۔

<!-- router:fbr,custom -->
```bash
nx new my-app --template web-fbr-preact
```
<!-- /router -->

<!-- router:modular -->
```bash
nx new my-app --template web-modular-preact
```
<!-- /router -->

ٹیمپلیٹ ایک سرور موڈ پروجیکٹ ہے جس میں Preact جزائر ہیں۔ اس کے بجائے اشارے کا جواب دینے کے لیے بغیر کسی ٹیمپلیٹ کے `nx new my-app` چلائیں: روٹر، پروجیکٹ کی قسم، آیا کلائنٹ سائیڈ روٹنگ استعمال کرنا ہے، پھر فریم ورک۔

## موجودہ پروجیکٹ میں Preact کو فعال کریں۔

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

`nx new` اس فائل کو لکھتے ہیں۔ Nexy خود `__nexy__/vite.ts` لکھتا ہے، اس لیے اس میں ترمیم نہ کریں۔

| پیکج | نسخہ `nx new` لکھتے ہیں۔ |
|---|---|
| `preact` | `^10.25.4` |
| `@preact/preset-vite` | `^2.10.1` (دیو انحصار) |
| `preact-render-to-string` | `^6.7.0` (دیو انحصار، سرور پر پیش کرتا ہے) |

## لکھیں Preact

A Preact جز ایک React طرز کا فنکشن ہے۔ اختلافات جو یہاں اہم ہیں:

```tsx filename="src/components/Counter.tsx"
import { useState } from "preact/hooks";

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start);
  return <button class="counter" onClick={() => setCount(count + 1)}>{count}</button>;
}
```

- ہکس `preact/hooks` سے آتے ہیں، جیسے `ComponentChildren` `preact` سے۔
- HTML اوصاف لکھیں: `class`، `for`، `charset`۔ `Link` اپنی کلاسیں `class` سے پڑھتا ہے۔

## قواعد

- **فی پروجیکٹ ایک فریم ورک** `useFF` بالکل ایک فریم ورک لیتا ہے۔ `useFF = [preact(), react()]` شروع ہونے پر سرور کو روکتا ہے۔ `useFF = preact()` کے ساتھ، ہر `.tsx` فائل Preact ہے۔
<!-- router:fbr,custom -->
- **صفحات ہیں۔ `.tsx`** `src/routes/` کے تحت صرف ایک `.tsx` فائل ایک صفحہ بنتی ہے۔ `.jsx` ایک جز کے لیے ٹھیک ہے۔
- **اجزاء باہر رہتے ہیں `src/routes/`**، عام طور پر `src/components/` میں، اس لیے وہ صفحات نہیں ہیں۔
- **سرور موڈ پراجیکٹ میں کوئی `.tsx` صفحہ** نہیں ہوتا، اور کلائنٹ موڈ پروجیکٹ میں کوئی `.nexy` صفحہ نہیں ہوتا: Nexy شروع کرنے سے انکار کرتا ہے اور فائل کو نام دیتا ہے۔ دیکھیں [موڈز](../../routing/fbr/modes.md)۔
<!-- /router -->
<!-- router:modular -->
- **اجزاء `src/components/`** میں رہتے ہیں، اور ایک منظر انہیں جزیروں کے طور پر درآمد کرتا ہے۔
<!-- /router -->
- **ایک `.mdx` صفحہ سے درآمد کرتا ہے۔ `"preact"`.** Nexy ایک `.mdx` فائل کو Preact کے ساتھ مرتب کرتا ہے جب وہ اس درآمد کو دیکھتا ہے، مثال کے طور پر `import { h } from "preact"`، اور دوسری صورت میں React کے ساتھ۔ دیکھیں [Markdown اور MDX](../nexy/markdown.md)۔

<!-- router:fbr,custom -->
## صفحات

کلائنٹ موڈ میں (`useCSR = True`)، صفحہ ایک `.tsx` فائل ہے۔

### صفحہ کا جزو

ایک صفحہ فائل کا ڈیفالٹ ایکسپورٹ ہوتا ہے۔ اگر کوئی ڈیفالٹ ایکسپورٹ موجود نہیں ہے، تو Nexy پہلی نامزد ایکسپورٹ کو چنتا ہے۔

```tsx filename="src/routes/index.tsx"
export default function Home() {
  return <h1>Hello</h1>;
}
```

### متحرک طبقات

URL پیرامیٹرز `useParams` ہک کے ذریعے دستیاب ہیں:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

## لے آؤٹ

### عمل درآمد

روٹ لے آؤٹ دستاویز کے شیل کی وضاحت کرتا ہے۔ نیسٹڈ لے آؤٹ مواد کو لپیٹ دیتے ہیں۔

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
<!-- /router -->

## جزائر

سرور موڈ میں، ایک Preact جز میں درآمد کیا جاتا ہے۔ `.nexy` فائل ایک جزیرہ ہے۔

### درآمد کرنا

`.nexy` فائل کے فرنٹ میٹر میں اجزاء درآمد کریں:

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```
<!-- /router -->

### ہائیڈریشن کی ہدایات

جزیرہ ہائیڈریٹ ہونے پر کنٹرول کرنے کے لیے `directive` سہارے کا استعمال کریں:

- `client:load` (پہلے سے طے شدہ): فوری طور پر
- `client:idle`: جب براؤزر بیکار ہو۔
- `client:visible`: جب یہ منظر میں سکرول کرتا ہے۔
- `client:media`: جب میڈیا کا سوال مماثل ہو۔

## اعمال اور نیویگیشن

### کالنگ اعمال

ایکشن کال کی حالت کو منظم کرنے کے لیے `useAction` ہک کا استعمال کریں:

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const { run, pending, error, data } = useAction(add_todo);
// ...
<button onClick={() => run({ title: "New Task" })}>Add</button>
```

### نیویگیشن

کلائنٹ سائڈ ٹرانزیشن کے لیے `Link` جز کا استعمال کریں۔ نوٹ کریں کہ Preact `className` کی بجائے `class` استعمال کرتا ہے:

```tsx
import { Link } from "@nexy/client";

<Link href="/about" class="nav" activeClassName="active">About</Link>
```

پروگرامیٹک نیویگیشن کے لیے، `useRouter` ہک استعمال کریں:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### URL تک رسائی

- `usePathname()`: موجودہ راستہ
- `useParams()`: متحرک طبقات
- `useSearchParams()`: استفسار کی تار
- `useLocation()`: مکمل مقام آبجیکٹ

## اگلے اقدامات

- [آراء](../README.md): ان فارمیٹس کا موازنہ کریں جو صفحہ استعمال کر سکتا ہے۔
- [فرنٹ اینڈ ](../../guides/frontend.md): Vite اور کلائنٹ کی تعمیر
