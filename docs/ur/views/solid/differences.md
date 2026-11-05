# Solid

Nexy سرور پر Solid 1.9 اجزاء پیش کرتا ہے، پھر Solid انہیں براؤزر میں لے جاتا ہے۔ صفحات، ترتیب، جزیرے اور اعمال ہر فریم ورک میں ایک جیسے ہیں: یہ صفحہ سیٹ اپ کا احاطہ کرتا ہے، پھر وہ حصے جو [مشترکہ معاہدوں](../frontend/pages.md) سے مختلف ہوتے ہیں۔

| موڈ | `nexyconfig.py` | صفحات ہیں | Solid ہے |
|---|---|---|---|
| سرور (پہلے سے طے شدہ) | `useCSR = False` | `.nexy` فائلیں | [جزیرے](../../rendering/islands.md) ان صفحات کے اندر |
| کلائنٹ | `useCSR = True` | `.tsx` فائلیں | پورا صفحہ، [لے آؤٹس](../frontend/layouts.md) اور کلائنٹ روٹر کے ساتھ |

## ایک پروجیکٹ شروع کریں۔

```bash
nx new my-app --template web-fbr-solid
```

ٹیمپلیٹ ایک سرور موڈ پروجیکٹ ہے جس میں Solid جزائر ہیں۔ اس کی بجائے اشارے کا جواب دینے کے لیے بغیر کسی ٹیمپلیٹ کے `nx new my-app` چلائیں: روٹر، پروجیکٹ کی قسم، آیا کلائنٹ سائیڈ روٹنگ استعمال کرنا ہے، پھر فریم ورک۔

## موجودہ پروجیکٹ میں Solid کو فعال کریں۔

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

کلائنٹ موڈ میں لکھیں `solid({ ssr: true })`: Solid سرور اور براؤزر کے لیے ایک جزو کو مختلف طریقے سے مرتب کرتا ہے، اور کلائنٹ موڈ کو دونوں کی ضرورت ہوتی ہے۔ `nx new` اس فائل کو لکھتے ہیں۔ Nexy خود `__nexy__/vite.ts` لکھتا ہے، اس لیے اس میں ترمیم نہ کریں۔

| پیکیج | ورژن `nx new` لکھتا ہے |
|---|---|
| `solid-js` | `^1.9.12` |
| `vite-plugin-solid` | `^2.11.0` (دیو انحصار) |

## اشاروں میں سوچیں۔

ایک Solid جزو کا فنکشن **ایک بار** چلتا ہے۔ بعد میں جو تبدیلیاں ہوتی ہیں اسے سگنل کے ذریعے پڑھا جاتا ہے، اور صرف وہ تاثرات جو اسے پڑھتے ہیں اپ ڈیٹ ہوتے ہیں:

```tsx filename="src/components/Counter.tsx"
import { createSignal } from "solid-js";

export default function Counter(props: { start?: number }) {
  const [count, setCount] = createSignal(props.start ?? 0);
  return <button onClick={() => setCount(count() + 1)}>{count()}</button>;
}
```

- سگنل کو کال کریں، `count()`، JSX کے اندر، اس کے اوپر متغیر میں نہیں۔
- پروپس کو بطور `props.start` پڑھیں۔ ڈیسٹرکچرنگ `{ start }` قیمت کو ایک بار پڑھتا ہے اور اپ ڈیٹس کو کھو دیتا ہے۔
- Solid HTML کی خصوصیات لکھتا ہے: `class`، `for`، `charset`، `className` نہیں۔

## قواعد

- **فی پروجیکٹ ایک فریم ورک** `useFF` بالکل ایک فریم ورک لیتا ہے۔ `useFF = [solid(), react()]` شروع ہونے پر سرور کو روکتا ہے۔ `useFF = solid()` کے ساتھ، ہر `.tsx` فائل Solid ہے۔
- **صفحات ہیں۔ `.tsx`** `src/routes/` کے تحت صرف ایک `.tsx` فائل ایک صفحہ بنتی ہے۔ `.jsx` ایک جز کے لیے ٹھیک ہے۔
- **اجزاء باہر رہتے ہیں `src/routes/`**، عام طور پر `src/components/` میں، اس لیے وہ صفحات نہیں ہیں۔
- **سرور موڈ پروجیکٹ کا کوئی `.tsx` صفحہ** نہیں ہوتا، اور کلائنٹ موڈ پروجیکٹ کا کوئی `.nexy` صفحہ نہیں ہوتا: Nexy شروع کرنے سے انکار کرتا ہے اور فائل کو نام دیتا ہے۔ دیکھیں [موڈز](../../routing/fbr/modes.md)۔
- **کوئی `.mdx` Solid کے ساتھ** MDX React یا Preact میں مرتب کرتا ہے؛ `.md` صفحات کام کرتے ہیں۔

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

یو آر ایل پیرامیٹرز `useParams` ہک کے ذریعے دستیاب ہیں، جو ایک رسائیر کو واپس کرتا ہے:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const params = useParams<{ slug: string }>();
  return <h1>{params().slug}</h1>;
}
```

## لے آؤٹ

### عمل درآمد

روٹ لے آؤٹ دستاویز کے شیل کی وضاحت کرتا ہے۔ نیسٹڈ لے آؤٹ مواد کو لپیٹ دیتے ہیں۔

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

تباہ نہ کریں `props.children`، جیسا کہ Solid اسے سستی سے پڑھتا ہے۔

## جزائر

سرور موڈ میں، ایک Solid جز ایک `.nexy` فائل میں درآمد کیا گیا جزیرہ ہے۔

### درآمد کرنا

`.nexy` فائل کے فرنٹ میٹر میں اجزاء درآمد کریں:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```

### ہائیڈریشن کی ہدایات

جزیرہ ہائیڈریٹ ہونے پر کنٹرول کرنے کے لیے `directive` سہارے کا استعمال کریں:

- `client:load` (پہلے سے طے شدہ): فوری طور پر
- `client:idle`: جب براؤزر بیکار ہو۔
- `client:visible`: جب یہ منظر میں طومار کرتا ہے۔
- `client:media`: جب میڈیا کا استفسار ملتا ہے۔

## اعمال اور نیویگیشن

### کالنگ اعمال

ایکشن کال کی حالت کو منظم کرنے کے لیے `useAction` ہک کا استعمال کریں۔ Solid میں، یہ ایکسیسرز کو واپس کرتا ہے (انہیں فنکشن کہتے ہیں)۔

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const save = useAction(add_todo);
// ...
<button disabled={save.pending()}>Add</button>
```

### نیویگیشن

کلائنٹ سائیڈ ٹرانزیشن کے لیے `Link` جز کا استعمال کریں:

```tsx
import { Link } from "@nexy/client";

<Link href="/about">About</Link>
```

پروگرامیٹک نیویگیشن کے لیے، `useRouter` ہک استعمال کریں:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### یو آر ایل تک رسائی

تمام لوکیشن ہکس واپس آنے والے ایکسیسرز:

- `usePathname()`: موجودہ راستہ
- `useParams()`: متحرک طبقات
- `useSearchParams()`: استفسار کی تار
- `useLocation()`: مکمل مقام آبجیکٹ

## اگلے اقدامات

- [ملاحظات](../README.md): ان فارمیٹس کا موازنہ کریں جو صفحہ استعمال کر سکتا ہے۔
- [فرنٹ اینڈ](../../guides/frontend.md): Vite اور کلائنٹ کی تعمیر
