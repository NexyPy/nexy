# لنک کرنا اور نیویگیٹ کرنا

کلائنٹ روٹنگ (`useCSR = True`) کے ساتھ، دو صفحات کے درمیان ایک لنک دستاویز کو دوبارہ لوڈ کرنے کے بجائے براؤزر میں صفحہ کو تبدیل کرتا ہے۔ ترتیب اپنی حالت برقرار رکھتی ہے۔

## سادہ لنکس پہلے ہی کام کر رہے ہیں۔

آپ کے پروجیکٹ کے صفحہ پر ہر `<a href>` کلائنٹ پر تشریف لے جاتا ہے، جس میں کوئی جز اور کوئی مارکر نہیں:

```html
<a href="/about">About</a>
```

ایک لنک براؤزر پر چھوڑ دیا جاتا ہے، اور صفحہ کو عام طور پر لوڈ کرتا ہے، جب:

- ایک موڈیفائر کلید رکھی ہوئی ہے، یا بٹن اہم نہیں ہے۔
- اس میں `target` (`_self` کے علاوہ)، `download`، `rel="external"` یا `data-nexy-reload`؛
- `href` ایک اور اصل ہے، ایک `mailto:` یا `tel:` لنک، یا صرف ایک `#fragment`؛
- راستہ کسی کلائنٹ کے راستے سے میل نہیں کھاتا، لہذا سرور اس کا جواب دیتا ہے۔

## `Link`

`Link` وہی اینکر ہے جس کے ساتھ کوئی سادہ نہیں کر سکتا: اس کا `href` آپ کے راستوں کے خلاف چیک کیا جاتا ہے، یہ ہدف والے صفحے کو گرم کرتا ہے، اور یہ جانتا ہے کہ یہ کب موجودہ صفحہ پر اشارہ کرتا ہے۔ جب آپ `nx dev` یا `nx build` چلاتے ہیں تو Nexy آپ کے فریم ورک کا `Link` `__nexy__/src` میں تیار کرتا ہے۔

| فریم ورک | درآمد |
|---|---|
| React، Preact، Solid، Vue | `import { Link } from "@nexy/client"` |
| Svelte | `import Link from "@nexy/Link.svelte"` |

```tsx
import { Link } from "@nexy/client";

export default function Nav() {
  return (
    <Link href="/dashboard" activeClassName="on">
      Dashboard
    </Link>
  );
}
```

| پروپ | معنی |
|---|---|
| `href` | پروجیکٹ کا راستہ (ٹائپو ایک قسم کی غلطی ہے)، اختیاری طور پر `?query` یا `#fragment`، یا ایک بیرونی URL کے ساتھ۔ |
| `replace` | تاریخ کے اندراج کو شامل کرنے کے بجائے بدل دیں۔ |
| `scroll` | `false` نیویگیٹ کرنے کے بعد اسکرول پوزیشن کو برقرار رکھتا ہے۔ طے شدہ: `true`۔ |
| `prefetch` | `'intent'` (پہلے سے طے شدہ) صفحہ کو ہوور، فوکس یا ٹچ پر لوڈ کرتا ہے۔ `'viewport'` جب لنک اسکرول کرتا ہے `false` کبھی نہیں۔ |
| `activeClassName` | کلاس میں شامل کیا گیا جب کہ لنک موجودہ صفحہ یا اس کے نیچے کسی صفحے پر اشارہ کرتا ہے (`activeClass` Vue اور Svelte میں)۔ |
| `exact` | صرف عین صفحہ پر فعال۔ |

موجودہ صفحہ پر اشارہ کرنے والا لنک بھی `aria-current="page"` ملتا ہے۔

## کانٹے

مقام ہر فریم ورک میں، اس فریم ورک کے محاورے میں دستیاب ہے۔ پہلے کے دوران، سرور سائیڈ درخواست کے URL کے ساتھ ہکس کا جواب پیش کرتا ہے، اس لیے صفحہ بغیر مماثلت کے ہائیڈریٹ ہوتا ہے۔

| | React، Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| راستہ | `usePathname()` | `usePathname()` ایک رسائیر لوٹاتا ہے | `usePathname()` ریف | `$pathname` اسٹور |
| روٹ پیرامز | `useParams()` | `useParams()` ایکسیسر | `useParams()` ریف | `$params` اسٹور |
| استفسار | `useSearchParams()` | `useSearchParams()` رسائی کنندہ | `useSearchParams()` حوالہ | `$searchParams` اسٹور |
| ہر چیز | `useLocation()` | `useLocation()` ایکسیسر | `useLocation()` ریفری | `$location` اسٹور |
| تشریف لے جائیں | `useRouter()` | `useRouter()` | `useRouter()` | `router` |

استفسار ایک `URLSearchParams` ہے۔ `useRouter()` اور `router` دیں `push(href)`، `replace(href)`، `back()`، `forward()`، `refresh()` اور `prefetch(href)`؛ `push` اور `replace` قبول کرتے ہیں `{ scroll: false }`۔

```tsx
import { useParams, useRouter, useSearchParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  const tab = useSearchParams().get("tab") ?? "profile";
  const router = useRouter();
  return <button onClick={() => router.push(`/users/${id}?tab=posts`)}>{tab}</button>;
}
```

## `Image`

`Image` ایک `<img>` کو پیش کرتا ہے جو پہلے سے طے شدہ طور پر سست ہے اور جب اس کا سائز معلوم ہوتا ہے تو ترتیب کو تبدیل نہیں کرتا ہے۔

| فریم ورک | درآمد |
|---|---|
| React، Preact، Solid، Vue | `import { Image } from "@nexy/client"` |
| Svelte | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` درکار ہے۔ آرائشی تصویر کے لیے `alt=""` کا استعمال کریں۔ جب یہ غائب ہو تو Nexy ایک بار خبردار کرتا ہے۔
- `width` اور `height` دونوں کے ساتھ، اوصاف براؤزر کو پہلو کا تناسب دیتے ہیں اور تصویر سیال رہتی ہے (`height: auto; max-width: 100%`)۔
- `priority` تصویر کو اب اعلی ترجیح پر لوڈ کرتا ہے، اس کے لیے جو آمد پر نظر آتا ہے۔
- `fill` `width` اور `height` کو نظر انداز کرتے ہوئے، تصویر کو اس کے پوزیشن والے والدین کا احاطہ کرتا ہے۔
- `sizes` اور `srcSet` سے گزرتے ہیں۔ Nexy تصاویر کا سائز تبدیل یا تبدیل نہیں کرتا ہے۔

## ایک `.nexy` صفحہ سے لنک

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` رینڈرز `<a href="/about" data-nexy-link="true">`۔ ہر وصف اور `href` HTML سے بچ گئے ہیں۔

## روٹر کیا کرتا ہے۔

نیویگیشن پر، راؤٹر:

1. کلائنٹ کے راستوں (`.tsx`، `.jsx`، `.vue`، `.svelte`) کے خلاف راستے سے میل کھاتا ہے؛
2. صفحہ اور اس کے [لے آؤٹس](../layouts/README.md) **پہلے** کو درآمد اور پیش کرتا ہے، اور تب ہی یو آر ایل کو `history.pushState` کے ساتھ منتقل کرتا ہے، اس لیے ایڈریس بار کبھی بھی ایسا صفحہ نہیں دکھاتا ہے جو ناکام ہوا ہو۔
3. `document` پر ایک `nexy:navigated` واقعہ بھیجتا ہے۔
4. سب سے اوپر، یا `#fragment` ہدف تک سکرول کرتا ہے۔

ایک نئی نیویگیشن ایک پرانی کو منسوخ کر دیتی ہے جو اب بھی پیش کر رہا ہے۔ اگر کوئی صفحہ رینڈر نہیں کر سکتا تو براؤزر اس کے بجائے سرور سے پوچھتا ہے۔ پیچھے اور آگے کے بٹن اس اندراج کے صفحہ کو رینڈر کرتے ہیں اور اس کی اسکرول پوزیشن کو بحال کرتے ہیں۔

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

روٹر صرف کلائنٹ روٹس والے پروجیکٹ میں شروع ہوتا ہے، لہذا سرور کے ذریعے پیش کردہ پروجیکٹ براؤزر کے اپنے بیک بٹن اور اسکرول کی بحالی کو برقرار رکھتا ہے۔

## اگلے اقدامات

- [لے آؤٹ](../layouts/README.md)
- [CSR](../../../rendering/csr.md)
- [اجزاء](../../../views/nexy/components.md)
