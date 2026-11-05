# اجزاء

Nexy مددگاروں کا ایک چھوٹا سیٹ برآمد کرتا ہے جو HTML سٹرنگز کو واپس کرتا ہے۔ ہر ایک کو `.nexy` ٹیمپلیٹ میں دو طریقوں سے استعمال کیا جاتا ہے: بطور کال Jinja، یا HTML طرز کے ٹیگ کے طور پر۔

## دو نحو، ایک فنکشن

```nexy filename="src/routes/index.nexy"
---
from nexy import Audio
---
{{ Audio("/theme.mp3", controls=True) }}

<Audio src="/theme.mp3" controls=True />
```

دونوں لائنیں ایک ہی مارک اپ تیار کرتی ہیں:

```html
<audio preload="metadata" controls><source src="/theme.mp3" type="audio/mp3" /></audio>
```

کمپائلر `<Audio ... />` سے `{{ Audio(...) }}` کو دوبارہ لکھتا ہے، لہذا ٹیگ فارم دوسرا API نہیں ہے: اوصاف فنکشن کے کلیدی الفاظ کے دلائل ہیں۔

## ٹیگ فارم کے قواعد

| ٹیگ میں | بن جاتا ہے۔ |
|---|---|
| `<Audio src="/a.mp3" />` | `Audio(src="/a.mp3")` |
| `controls=True` | `controls=True`، ایک حقیقی بولین |
| `width=640` | `width=640`، ایک عدد |
| `src="{{ url }}"` | `src=(url)`، Jinja میں تشخیص |
| کوئی اور `value` | `"value"`، ایک تار |

- ٹیگ کو ایک بڑے حروف سے شروع ہونا چاہیے اور فرنٹ میٹر میں درآمد کیا جانا چاہیے۔ ورنہ مرتب کرنے والا اٹھاتا ہے `Missing Import: <Name> used but not declared.`
- ٹیگ فارم **خود بند** ہے۔ `<Audio src="/a.mp3" />` اور `{{ Audio("/a.mp3") }}` برابر ہیں۔ مددگار ٹیگ کے اندر بچوں کو لکھنا تعاون یافتہ نہیں ہے۔
- ایک ننگا ایچ ٹی ایم ایل وصف یہاں بولین نہیں ہے: `controls` بن جاتا ہے `controls=""`، ​​جو کہ غلط ہے۔ لکھیں `controls=True`۔

> [!NOTE]
> `class_name` سی ایس ایس کلاسز کے لیے دستاویزی مطلوبہ لفظ ہے۔ اضافی مطلوبہ الفاظ کے دلائل HTML صفات بن جاتے ہیں، اس لیے `class="nav"` بھی آؤٹ پٹ تک پہنچ جاتے ہیں۔

## تصویر

```nexy
---
from nexy import Image
---
{{ Image("/logo.png", alt="Logo", width=128, height=32) }}

<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

`Image(src, alt="", width=None, height=None, loading="lazy", class_name=None, **attrs)` ڈیفالٹ سست لوڈنگ کے ساتھ ایک `<img>` رینڈر کرتا ہے۔

## لنک

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` کلائنٹ راؤٹر کے ذریعہ سنبھالا ہوا ایک `<a data-nexy-link>` پیش کرتا ہے۔ `prefetch=True` کے ساتھ، لنک کو منڈانے یا چھونے سے `window.__nexy_prefetch` کے ذریعے ہدف گرم ہوجاتا ہے۔

> [!NOTE]
> ٹیگ فارم لیبل کو بطور `children` لیتا ہے، عنصر کے مواد کے طور پر نہیں: `<Link href="/about" children="About" />`۔ کسی لنک کے اندر مارک اپ ڈالنے کے لیے کال فارم کو `children=` یا `.nexy` جز کے ساتھ استعمال کریں جو کہ `<Slot />` کو رینڈر کرتا ہے۔

## آڈیو اور ویڈیو

```nexy
---
from nexy import Audio, Video
---
{{ Audio("/theme.mp3", controls=True) }}
{{ Video("/demo.mp4", width=640, height=360, muted=True, sources=["/demo.webm", "/demo.mp4"]) }}

<Audio src="/theme.mp3" controls=True />
<Video src="/demo.mp4" width=640 height=360 muted=True />
```

`Audio(src, controls=True, autoplay=False, loop=False, muted=False, preload="metadata", class_name=None, sources=None, **attrs)` اور `Video(src, width=None, height=None, ...)` مقامی کھلاڑیوں کو پیش کرتے ہیں۔ `sources` ہر ایکسٹینشن سے اخذ کردہ MIME قسم کے ساتھ `<source>` ٹیگز شامل کرتا ہے۔

## ایک جزو جسے آپ خود لکھتے ہیں۔

دوبارہ قابل استعمال `.nexy` جزو `src/components/` کے تحت فائل ہے: Python اوپر پر، HTML نیچے۔ یہ کسی دوسرے Python ماڈیول کی طرح درآمد کیا جاتا ہے۔

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
tone: prop[str] = "neutral"
---
<article class="card card-{{ tone }}">
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/routes/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest notes" tone="warm">
  <p>Everything published this week.</p>
</Card>
```

`title` کوئی ڈیفالٹ نہیں ہے، لہذا صفحہ اسے پاس کرنا ضروری ہے؛ `tone` واپس `"neutral"` پر آتا ہے۔ ٹیگز کے درمیان مارک اپ `<Slot />` (کیپٹل ایس) کے اندر آتا ہے۔ پرپس، سلاٹس اور ٹیگ فارم کے قواعد کے لیے [.nexy فائلز](README.md#components) دیکھیں۔

## کلائنٹ کا جزو درآمد کرنا

ایک `.nexy` فائل سے، راستے کے ذریعے ایک فریم ورک جزو درآمد کریں؛ کمپائلر اسے کلائنٹ پر ماؤنٹ کرتا ہے اور صفات کو پرپس کے طور پر پاس کرتا ہے:

```nexy
---
from "@/components/Counter.tsx" import Counter
---
<Counter start="0" />
```

`Import(path, framework, symbol)` Python میں بھی ایسا ہی کرتا ہے:

```python
from nexy import Import

counter = Import("@/components/Counter.tsx", "react", "Counter")
html = counter(start=0)
```

وہی درآمدی ترکیب `.json`، `.css` اور تصویری فائلوں کو ان کے یو آر ایل میں حل کرتی ہے۔

## سانچہ اور Vite

`Template().render(path, context)` ایک ٹیمپلیٹ فائل (Jinja2، یا Markdown کو `.md` راستوں کے لیے HTML میں رینڈر کرتا ہے۔ `Template().invalidate(path)` اسے کیشے سے گرا دیتا ہے۔

`Vite()` موجودہ موڈ کے لیے کلائنٹ ٹیگز واپس کرتا ہے: ترقی میں HMR اسکرپٹ، پیداوار میں کلائنٹ کا بنڈل۔ Nexy اسے ہر صفحے کے لیے کال کرتا ہے۔ آپ کو شاذ و نادر ہی براہ راست اس کی ضرورت ہے۔

## ابھی تک نافذ نہیں ہوا۔

`Form` اور `Script` بغیر کسی رویے کے برآمد شدہ پلیس ہولڈرز ہیں۔ ان پر بھروسہ نہ کریں۔

## اگلے اقدامات

- [.nexy فائلیں](README.md): جہاں یہ مددگار استعمال ہوتے ہیں۔
- [React](../react/differences.md): اجزاء کی درآمد `.tsx`
- [فرنٹ اینڈ](../../guides/frontend.md): کلائنٹ کے اجزاء کیسے بنڈل ہوتے ہیں۔
