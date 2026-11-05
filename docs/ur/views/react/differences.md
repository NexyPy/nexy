# React

Nexy سرور پر React 19 اجزاء پیش کرتا ہے، پھر React انہیں براؤزر میں ہائیڈریٹ کرتا ہے۔ صفحات، ترتیب، جزیرے اور اعمال ہر فریم ورک میں ایک جیسے ہیں: یہ صفحہ سیٹ اپ کا احاطہ کرتا ہے، پھر وہ حصے جو [مشترکہ معاہدوں](../frontend/pages.md) سے مختلف ہوتے ہیں۔

| موڈ | `nexyconfig.py` | صفحات ہیں | React ہے |
|---|---|---|---|
| سرور (پہلے سے طے شدہ) | `useCSR = False` | `.nexy` فائلیں | [جزیرے](../../rendering/islands.md) ان صفحات کے اندر |
| کلائنٹ | `useCSR = True` | `.tsx` فائلیں | پورا صفحہ، [لے آؤٹس](../frontend/layouts.md) اور کلائنٹ روٹر کے ساتھ |

## ایک پروجیکٹ شروع کریں۔

```bash
nx new my-app --template web-fbr-react
```

ٹیمپلیٹ ایک سرور موڈ پروجیکٹ ہے جس میں React جزائر ہیں۔ اس کی بجائے اشارے کا جواب دینے کے لیے بغیر کسی ٹیمپلیٹ کے `nx new my-app` چلائیں: روٹر، پروجیکٹ کی قسم، آیا کلائنٹ سائیڈ روٹنگ استعمال کرنا ہے، پھر فریم ورک۔

## موجودہ پروجیکٹ میں React کو فعال کریں۔

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

`nx new` اس فائل کو لکھتے ہیں۔ Nexy خود `__nexy__/vite.ts` لکھتا ہے، اس لیے اس میں ترمیم نہ کریں۔

| پیکیج | ورژن `nx new` لکھتا ہے |
|---|---|
| `react`، `react-dom` | `^19.2.5` |
| `@vitejs/plugin-react` | `^5.2.0` |
| `@types/react`، `@types/react-dom` | دیو انحصار |

## قواعد

- **فی پروجیکٹ ایک فریم ورک** `useFF` بالکل ایک فریم ورک لیتا ہے۔ `useFF = [react(), vue()]` شروع ہونے پر سرور کو روکتا ہے۔
- **صفحات `.tsx`[** React کی ملکیت `.tsx` اور `.jsx` اجزاء کے لیے ہیں، لیکن `src/routes/` کے تحت صرف ایک `.tsx` فائل ایک صفحہ بنتی ہے۔
- **اجزاء باہر رہتے ہیں `src/routes/`**، عام طور پر `src/components/` میں، اس لیے وہ صفحات نہیں ہیں۔
- **سرور موڈ پروجیکٹ کا کوئی `.tsx` صفحہ** نہیں ہوتا، اور کلائنٹ موڈ پروجیکٹ کا کوئی `.nexy` صفحہ نہیں ہوتا: Nexy شروع کرنے سے انکار کرتا ہے اور فائل کو نام دیتا ہے۔ [طریقوں](../../routing/fbr/modes.md) کو دیکھیں۔

## صفحات

کلائنٹ موڈ (`useCSR = True`) میں، صفحہ ایک `.tsx` فائل ہے۔

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

روٹ لے آؤٹ دستاویز کے شیل کی وضاحت کرتا ہے۔ نیسٹڈ لے آؤٹ مواد کو اپنے نیچے سمیٹتے ہیں۔

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

## جزائر

سرور موڈ میں، ایک React جز میں درآمد کیا جاتا ہے۔ `.nexy` فائل ایک جزیرہ ہے۔

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

کلائنٹ سائڈ ٹرانزیشن کے لیے `Link` جز کا استعمال کریں:

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

- `usePathname()`: موجودہ راستہ
- `useParams()`: متحرک طبقات
- `useSearchParams()`: استفسار کی تار
- `useLocation()`: مکمل مقام آبجیکٹ

## اگلے اقدامات

- [ملاحظات](../README.md): ان فارمیٹس کا موازنہ کریں جو صفحہ استعمال کر سکتا ہے۔
- [فرنٹ اینڈ](../../guides/frontend.md): Vite اور کلائنٹ کی تعمیر
