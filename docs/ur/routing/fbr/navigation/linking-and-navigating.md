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

| فریم ورک | درآمد کریں۔ |
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

| Prop | مطلب |
|---|---|
| `href` | پروجیکٹ کا راستہ (ٹائپو ایک قسم کی غلطی ہے)، اختیاری طور پر `?query` یا `#fragment`، یا ایک بیرونی URL کے ساتھ۔ |
| `replace` | تاریخ کے اندراج کو شامل کرنے کے بجائے تبدیل کریں۔ |
| `scroll` | `false` نیویگیٹ کرنے کے بعد اسکرول پوزیشن کو برقرار رکھتا ہے۔ طے شدہ: `true`۔ |
| `prefetch` | `'intent'` (پہلے سے طے شدہ) صفحہ کو ہوور، فوکس یا ٹچ پر لوڈ کرتا ہے۔ `'viewport'` جب لنک اسکرول کرتا ہے `false` کبھی نہیں۔ |
| `activeClassName` | کلاس میں شامل کیا گیا جب کہ لنک موجودہ صفحہ یا اس کے نیچے کسی صفحے پر اشارہ کرتا ہے (`activeClass` Vue اور Svelte میں)۔ |
| `exact` | صرف عین صفحہ پر فعال۔ |

موجودہ صفحہ پر اشارہ کرنے والا لنک بھی `aria-current="page"` ملتا ہے۔

## کانٹے

مقام ہر فریم ورک میں، اس فریم ورک کے محاورے میں دستیاب ہے۔ پہلے کے دوران، سرور سائیڈ درخواست کے URL کے ساتھ ہکس کا جواب پیش کرتا ہے، اس لیے صفحہ بغیر مماثلت کے ہائیڈریٹ ہوتا ہے۔

| | React، Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| راستہ | `usePathname()` | `usePathname()` ایک رسائیر لوٹاتا ہے۔ | `usePathname()` ایک حوالہ دیتا ہے۔ | `$pathname` اسٹور |
| روٹ پیرامز | `useParams()` | `useParams()` رسائی کنندہ | `useParams()` حوالہ | `$params` اسٹور |
| استفسار | `useSearchParams()` | `useSearchParams()` رسائی کنندہ | `useSearchParams()` حوالہ | `$searchParams` اسٹور |
| سب کچھ | `useLocation()` | `useLocation()` رسائی کنندہ | `useLocation()` حوالہ | `$location` اسٹور |
| نیویگیٹ کریں۔ | `useRouter()` | `useRouter()` | `useRouter()` | `router` |
| پرواز میں نیویگیشن | `useTransition()` | `useTransition()` رسائی کنندہ | `useTransition()` حوالہ | `useTransition()` اسٹور |
| ایک راستہ ملائیں | `useMatch(path?)` | `useMatch(path?)` رسائی کنندہ | `useMatch(path?)` حوالہ | `useMatch(path?)` اسٹور |
| جانے سے پہلے پوچھ لیں۔ | `useBlocker(dirty)` | `useBlocker(dirty())` میں `createEffect` | `useBlocker(dirtyRef)` | `useBlocker(dirty)` میں `$effect` |

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

## لوڈنگ حالت `useTransition` کے ساتھ دکھائیں

`useTransition()` بتاتا ہے کہ آیا کلائنٹ نیویگیشن پرواز میں ہے۔ `pending` کلک سے اگلا صفحہ ظاہر ہونے تک `true` ہے، اور `next` وہ مقام ہے جہاں یہ جا رہا ہے۔ صفحہ کے دکھائے جانے کے بعد، جب نیویگیشن رک جاتی ہے، یا جب کوئی نیا اس کی جگہ لے لیتا ہے تو یہ واپس `{ pending: false, next: null }` پر چلا جاتا ہے۔

```tsx
import { useTransition } from "@nexy/client";

export default function Progress() {
  const { pending, next } = useTransition();
  return pending ? <p role="status">Loading {next?.pathname}</p> : null;
}
```

## ایک راستے کو `useMatch` سے جوڑیں

`useMatch(path)` بتاتا ہے کہ آیا `path` کلائنٹ کے راستے سے میل کھاتا ہے۔ یہ `{ match, found }` لوٹتا ہے، جہاں `match` راستے `file` کو رکھتا ہے، اس کا `layouts` اور اس کا `params`، یا ہے `null`۔ راستے کے بغیر یہ موجودہ صفحہ سے میل کھاتا ہے اور ہر نیویگیشن کی پیروی کرتا ہے۔ سرور رینڈر کے دوران ابھی تک کوئی راؤٹر نہیں ہے، اس لیے `match` ہے `null` اور `found` ہے `false`۔

```tsx
import { useMatch } from "@nexy/client";

export default function Breadcrumb() {
  const { match } = useMatch();
  return match?.params.id ? <span>User {match.params.id}</span> : null;
}
```

## ایک صفحہ پکڑو جو `ErrorBoundary` کے ساتھ ناکام ہو

`ErrorBoundary` اپنے بچوں کے بجائے فال بیک دکھاتا ہے جب ان میں سے کوئی پھینکتا ہے جب یہ براؤزر میں رینڈر ہوتا ہے۔ فال بیک کو غلطی اور `reset` موصول ہوتی ہے، جو بچوں کو دوبارہ پیش کرتی ہے۔

| فریم ورک | درآمد کریں۔ | فال بیک |
|---|---|---|
| React، Preact، Solid | `import { ErrorBoundary } from "@nexy/client"` | `fallback={(error, reset) => ...}` |
| Vue | `import { ErrorBoundary } from "@nexy/client"` | ایک `fallback` فنکشن prop؛ بچے پہلے سے طے شدہ سلاٹ میں جاتے ہیں۔ |
| Svelte | `import ErrorBoundary from "@nexy/ErrorBoundary.svelte"` | ایک `fallback` کا ٹکڑا |

```tsx
import { ErrorBoundary } from "@nexy/client";

<ErrorBoundary fallback={(error, reset) => <button onClick={reset}>{error.message}: retry</button>}>
  <Dashboard />
</ErrorBoundary>
```

```svelte
<ErrorBoundary>
  {#snippet fallback(error, reset)}
    <button onclick={reset}>{error.message}: retry</button>
  {/snippet}
  <Dashboard />
</ErrorBoundary>
```

یہ نہیں پکڑتا:

- ایک غلطی بعد میں پھینکی گئی، ایونٹ ہینڈلر، ٹائمر یا وعدہ میں: اسے پکڑو جہاں یہ ہوتا ہے۔ Vue اس کے اپنے ایونٹ ہینڈلرز کے لیے مستثنیٰ ہے، جن کی غلطیاں حد تک پہنچ جاتی ہیں۔
- ایک صفحہ جو روٹر لوڈ نہیں کر سکتا: براؤزر اس کے بجائے سرور سے پوچھتا ہے (دیکھیں [روٹر کیا کرتا ہے](#what-the-router-does))۔

## غیر محفوظ شدہ تبدیلیوں کے ساتھ صفحہ چھوڑنے سے پہلے پوچھیں۔

`useBlocker(dirty, message?)` آنے والے سے جانے سے پہلے پوچھتا ہے جب کہ `dirty` سچ ہے: ایک لنک، ایک `router.push`، پیچھے اور آگے کے بٹن، ایک دوبارہ لوڈ اور ایک بند ٹیب۔ ایک کلائنٹ نیویگیشن دکھاتا ہے `message` میں `confirm()`: ہاں جاری ہے، صفحہ پر نہیں رہتا۔ دوبارہ لوڈ یا بند ٹیب براؤزر کا اپنا سوال دکھاتا ہے، جسے کوئی صفحہ لفظ نہیں دے سکتا۔ ایک پیغام کے بغیر، سوال یہ ہے کہ "آپ کے پاس غیر محفوظ شدہ تبدیلیاں ہیں۔ اس صفحہ کو چھوڑ دیں؟"۔

```tsx
import { useState } from "react";
import { useBlocker } from "@nexy/client";

export default function Editor() {
  const [text, setText] = useState("");
  const [saved, setSaved] = useState("");
  useBlocker(text !== saved, "Your draft is not saved. Leave anyway?");
  return (
    <form onSubmit={(event) => (event.preventDefault(), setSaved(text))}>
      <textarea value={text} onChange={(event) => setText(event.target.value)} />
      <button>Save</button>
    </form>
  );
}
```

ہر فریم ورک کے محاورے میں جھنڈا پڑھا جاتا ہے جہاں یہ تبدیل ہوتا ہے:

| فریم ورک | پرچم کی پیروی کریں۔ |
|---|---|
| React، Preact | ہر رینڈر پر `useBlocker(dirty)` |
| Vue | `useBlocker(dirty)` `dirty` کے ساتھ ریف یا ایک کمپیوٹیڈ |
| Solid | `createEffect(() => useBlocker(dirty()))` |
| Svelte | `$effect(() => useBlocker(dirty))` |

`useBlocker` اس فیصلے کے لیے ایک فنکشن بھی لیتا ہے جو اس بات پر منحصر ہوتا ہے کہ وزیٹر کہاں جاتا ہے۔ یہ اگلا مقام اور موجودہ مقام حاصل کرتا ہے، اور رہنے کی وجہ (سٹرنگ) واپس کرتا ہے، یا آگے جانے کے لیے کچھ نہیں:

```tsx
useBlocker((next) => (next.pathname.startsWith("/admin") ? "Admins only" : undefined));
```

ایک فنکشن خود سے نہیں پوچھتا ہے اور دوبارہ لوڈ نہیں رکھتا ہے۔ پوچھنے کے لیے اس میں `confirm()` کو کال کریں۔

## `Image`

`Image` ایک `<img>` پیش کرتا ہے جو پہلے سے سست ہے اور جب اس کا سائز معلوم ہوتا ہے تو ترتیب کو تبدیل نہیں کرتا ہے۔

| فریم ورک | درآمد کریں۔ |
|---|---|
| React، Preact، Solid، Vue | `import { Image } from "@nexy/client"` |
| Svelte | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` درکار ہے۔ آرائشی تصویر کے لیے `alt=""` کا استعمال کریں۔ جب یہ غائب ہو تو Nexy ایک بار خبردار کرتا ہے۔
- دونوں `width` اور `height` کے ساتھ، اوصاف براؤزر کو پہلو کا تناسب دیتے ہیں اور تصویر سیال رہتی ہے (`height: auto; max-width: 100%`)۔
- `priority` تصویر کو اب اعلی ترجیح پر لوڈ کرتا ہے، اس کے لیے جو آمد پر نظر آتا ہے۔
- `fill` `width` اور `height` کو نظر انداز کرتے ہوئے، تصویر کو اپنے پوزیشن والے والدین کا احاطہ کرتا ہے۔
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
