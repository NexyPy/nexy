# جزائر اور ہائیڈریشن

## تعریف

ایک جزیرہ کلائنٹ کا جزو ہے - React، Vue، Svelte، Solid یا Preact - ایک `.nexy` صفحہ میں درآمد کیا جاتا ہے۔ سرور اپنا HTML پیش کرتا ہے۔ براؤزر اس ایک جزو کو انٹرایکٹو بناتا ہے۔ باقی صفحہ HTML ہی رہتا ہے۔

جزائر سرور موڈ میں موجود ہیں۔ کلائنٹ موڈ میں اجزاء *ہیں* صفحات: دیکھیں [CSR](csr.md)۔

## یہ کیسے کام کرتا ہے۔

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter directive="client:visible" />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter directive="client:visible" />
```
<!-- /router -->

Nexy تعمیراتی وقت پر جز کو رینڈر کرتا ہے، اس کا HTML اسٹور کرتا ہے، اور اسے صفحہ کے اندر رکھتا ہے۔ صفحہ کا جواب اس HTML کے علاوہ `props` کو JSON وصف کے طور پر رکھتا ہے۔ براؤزر میں، جزیرے کا رن ٹائم جزو کو لوڈ کرتا ہے اور کنٹینر پر قبضہ کر لیتا ہے۔

`directive` فیصلہ کرتا ہے کہ **جب** ایسا ہوتا ہے۔ ایک کے بغیر، اس کا رن ٹائم تیار ہوتے ہی جزیرہ ہائیڈریٹ ہو جاتا ہے۔

## رینڈرنگ لائف سائیکل

1. تعمیر میں، کلائنٹ کے ہر جزو کو HTML میں پیش کیا جاتا ہے اور `__nexy__/client/static/` کے تحت لکھا جاتا ہے: ایک بار اس کے اپنے ڈیفالٹس کے ساتھ، اور ایک بار فی لٹریل `props` ایک `.nexy` فائل اسے دیتی ہے۔
2. ایک درخواست `.nexy` صفحہ کو پیش کرتی ہے۔ جزیرے کا HTML ٹیگ کی جگہ داخل کیا گیا ہے۔
3. جواب میں HTML، `props`، اور ہدایت کو بطور اوصاف شامل کیا جاتا ہے۔
4. براؤزر میں، ہدایت کے مطابق رن ٹائم شیڈول ہائیڈریشن کرتا ہے۔
5. ہائیڈریشن جامد ایچ ٹی ایم ایل کو لائیو جزو سے بدل دیتا ہے۔ باقی صفحہ اچھوت ہے۔

ترقی میں کوئی تعمیراتی اسنیپ شاٹ نہیں ہے: کنٹینر خالی ہے اور جز براؤزر میں رینڈر ہوتا ہے۔ صفحہ ایک جیسا لگتا ہے، لیکن پہلا پینٹ پیداوار سے مختلف ہے۔

## کب استعمال کرنا ہے۔

- ایسا صفحہ جو زیادہ تر مواد پر مشتمل ہوتا ہے اور اس میں ایک یا دو متعامل مقامات ہوتے ہیں۔
- ایک ویجیٹ جو کرالر کے لیے HTML میں موجود ہونا چاہیے اور پھر بھی کام کرتا ہے۔
- ایک ایسا جزو جس کو براؤزر کی ضرورت ہے لیکن پورے صفحے کو کلائنٹ رینڈرنگ میں نہیں گھسیٹنا چاہیے۔

## کنفیگریشن

| ہدایت | ہائیڈریٹس |
|---|---|
| کوئی نہیں، یا `client:load` | فوری طور پر |
| `client:idle` | جب براؤزر بیکار ہو (`requestIdleCallback`، 2 s ٹائم آؤٹ) |
| `client:visible` | جب جزیرہ ویو پورٹ میں داخل ہوتا ہے، 200 px جلد |
| `client:media` | جب ایک میڈیا سوال مماثل ہے؛ اسے `media` کے ساتھ مقرر کریں |

```nexy
<Chart directive="client:media" media="(min-width: 768px)" />
```

`client:media` ڈیفالٹ `(min-width: 768px)` پر ہوتا ہے جب `media` غیر حاضر ہوتا ہے، اور ایک بار ہائیڈریٹ ہوتا ہے۔ `IntersectionObserver` کے بغیر براؤزر پر، `client:visible` واپس بیکار ہوجاتا ہے۔

`directive` اور `media` Nexy کی طرف سے استعمال کیا جاتا ہے: وہ آپ کے اجزاء میں منتقل نہیں ہوتے ہیں۔

## مثال

```tsx filename="src/components/Counter.tsx"
import { useState } from "react"

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Count</h1>
<Counter start=3 directive="client:idle" />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Count</h1>
<Counter start=3 directive="client:idle" />
```
<!-- /router -->

## حدود

- **`client:only` کبھی نہیں۔ ہائیڈریٹس** یہ قبول کیا جاتا ہے، لیکن رن ٹائم اسے چھوڑ دیتا ہے، لہذا سرور HTML غیر فعال رہتا ہے۔ کلائنٹ روٹ ([CSR](csr.md)) کا استعمال کریں جب کوئی جزو سرور پر رینڈر نہیں کر سکتا۔
- **`client:manual` کوئی عوامی نہیں ہے۔ محرک** اسے خود بخود بھی چھوڑ دیا جاتا ہے، اور جو ہینڈل اسے دوبارہ شروع کرتا ہے وہ اندرونی ہے۔
- **`props` JSON ہونا ضروری ہے۔** وہ `json.dumps` کے ساتھ سیریلائز کیے گئے ہیں۔ ایک قدر جسے سیریلائز نہیں کیا جا سکتا، گرا دیا جاتا ہے، اور جزیرے کو موصول ہوتا ہے `{}` - خاموشی سے۔
- **ایک جزیرہ مشترکہ کے ساتھ کلائنٹ کا جزو نہیں ہے۔ ریاست** دو جزیرے ریاست کا اشتراک اس طریقہ کار کے بغیر نہیں کرتے جو آپ خود شامل کرتے ہیں۔
- **جزیرے کی طرف سے دوبارہ پیش نہیں کیا گیا ہے۔ سرور** اس کا ایچ ٹی ایم ایل تعمیر کا اسنیپ شاٹ ہے، اس کے علاوہ جو بھی جزو ہائیڈریٹ ہونے کے بعد کرتا ہے۔
- **صرف لغوی `props` سرور تک پہنچتا ہے۔ ایچ ٹی ایم ایل** `<Counter label="clicks" step="2" />` کو ان `props` کے ساتھ پیش کردہ اسنیپ شاٹ ملتا ہے۔ درخواست کے وقت ایک `prop` حساب کیا گیا (`label="{{ name }}"`)، ایک اسپریڈ (`{{ ...props }}`) یا ٹیگز کے درمیان بچوں کو تعمیر کے وقت معلوم نہیں کیا جاسکتا: وہ جزیرہ اسنیپ شاٹ کو اس وقت تک دکھاتا ہے جب تک کہ یہ ہائیڈریٹ نہ ہوجائے۔
- **جزائر کا ایک صفحہ اس میں ایک CSR صفحہ ہے۔ بھیس** اگر ہر بلاک کو ایک دوسرے سے بات کرنے کی ضرورت ہے، تو اس کے بجائے کلائنٹ موڈ منتخب کریں۔

## اگلے اقدامات

- [رینڈرنگ ](README.md): چار طریقے
- [اجزاء](../views/nexy/components.md): ایک `.nexy` صفحہ کیسے درآمد کرتا ہے۔
- [React](../views/react/differences.md), [Vue](../views/vue/differences.md), [Svelte](../views/svelte/differences.md), [Solid](../views/solid/differences.md), [Preact](../views/preact/differences.md)
