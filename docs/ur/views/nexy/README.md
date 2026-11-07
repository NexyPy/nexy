# .nexy فائلیں

ایک `.nexy` فائل ایک جزو ہے: اوپر Python، درمیان میں HTML، نیچے CSS۔

**اس سے پہلے کہ آپ شروع کریں:** ایک پروجیکٹ جسے [کوئیک اسٹارٹ](../../getting-started/quick-start.md) نے بنایا ہے۔ ایک `.nexy` فائل کو کسی تعمیراتی ترتیب کی ضرورت نہیں ہے: `nx dev` اسے محفوظ کرنے پر مرتب کرتا ہے۔

<!-- router:fbr,custom -->
```nexy filename="src/routes/blog/[slug].nexy"
---
from nexy import usePathname

slug: prop[str] = "untitled"
pathname = usePathname()
---
<article class="post">
  <h1>{{ slug }}</h1>
  <p>You are on {{ pathname }}</p>
</article>

<style>
  .post { max-width: 60ch; }
</style>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/blog/post_view.nexy"
---
from nexy import usePathname

slug: prop[str] = "untitled"
pathname = usePathname()
---
<article class="post">
  <h1>{{ slug }}</h1>
  <p>You are on {{ pathname }}</p>
</article>

<style>
  .post { max-width: 60ch; }
</style>
```

کنٹرولر اپنے راستے سے `slug` گزرتا ہے:

```python filename="src/apps/blog/post_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/blog/post_view.nexy", context={"slug": slug})
```
<!-- /router -->

## فرنٹ میٹر

دو `---` لائنوں کے درمیان ہر چیز Python ہے۔ جب اجزاء کو مرتب کیا جاتا ہے تو درآمدات حل ہوجاتی ہیں۔ باقی ہر درخواست کے لئے چلتا ہے، لہذا یہ درخواست کی حالت پڑھ سکتا ہے.

| کیا | مثال |
|---|---|
| ایک ماڈیول درآمد کریں۔ | `import json`، `from datetime import datetime` |
| ایک جزو درآمد کریں۔ | `from "@/components/card.nexy" import Card` |
| جائیداد کا اعلان کریں۔ | `title: prop[str] = "Default"` |
| ایک قدر کا حساب لگائیں۔ | `year = datetime.now().year` |
| درخواست پڑھیں | `pathname = usePathname()` |
| صفحہ کیش کریں (ISR) | `revalidate = 60` |

## پراپرٹیز

پراپرٹیز جزو کی API ہیں۔ `prop[type]` قسم کا اعلان کرتا ہے، `= value` ڈیفالٹ دیتا ہے۔ ڈیفالٹ کے بغیر پراپرٹی کو والدین کے ذریعہ پاس کرنا ضروری ہے۔

ایک عرف سے شروع ہونے والی درآمدات کو `useAliases` کے ذریعے حل کیا جاتا ہے۔ سیٹ اپ `nx new` نقشے `@` سے `src` تک لکھتا ہے، جس سے `@/components/card.nexy` کا مطلب `src/components/card.nexy` ہوتا ہے۔

## سانچہ

فرنٹ میٹر کے نیچے Jinja2 کے ساتھ HTML ہے۔ فرنٹ میٹر سے متغیرات اور خواص دائرہ کار میں ہیں۔

```html
{% for item in items %}
  <li>{{ item.name }}</li>
{% endfor %}

{% if user %}
  <p>Welcome, {{ user.name }}</p>
{% endif %}
```

آٹو اسکیپنگ **آف** ہے: ٹیمپلیٹس پروجیکٹ کا اپنا ایچ ٹی ایم ایل ہیں، اس لیے `{{ value }}` کو تحریری طور پر داخل کیا جاتا ہے۔ اپنے آپ کو `{{ value | e }}` کے ساتھ ناقابل اعتماد اقدار سے بچیں۔ `| safe` اس لیے کچھ نہیں بدلتا۔

> [!NOTE]
> لپیٹ JavaScript جس میں `{{` یا `{%` `{% raw %}...{% endraw %}` میں ہو۔ فریم ورک جیسے Vue اور Svelte ایک ہی منحنی خطوط وحدانی استعمال کرتے ہیں۔

## اجزاء

کوئی بھی درآمد شدہ کال ایبل جس کا نام بڑے حروف سے شروع ہوتا ہے اسے بطور ٹیگ استعمال کیا جا سکتا ہے۔ مرتب کرنے والا اسے Jinja کال پر دوبارہ لکھتا ہے: اوصاف کلیدی الفاظ کے دلائل بن جاتے ہیں۔

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/card.nexy" import Card
from nexy import Audio
---
<Card title="Hello">
  <p>Child content</p>
</Card>

<Audio src="/theme.mp3" controls=True />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/card.nexy" import Card
from nexy import Audio
---
<Card title="Hello">
  <p>Child content</p>
</Card>

<Audio src="/theme.mp3" controls=True />
```
<!-- /router -->

آخری سطر بالکل `{{ Audio("/theme.mp3", controls=True) }}` ہے۔ دونوں نحو بلٹ ان `Image`، `Link`، `Audio` اور `Video` مددگاروں کے لیے درست ہیں - دیکھیں [اجزاء](components.md#two-syntaxes-one-function)۔

بچوں کو چائلڈ کمپوننٹ کے اندر `<Slot />` (کیپٹل S) کے ذریعے اور ایک لے آؤٹ کے اندر `{{ children }}` کے ذریعے پیش کیا جاتا ہے۔

انتساب کے اندر Jinja کے ساتھ ایک حسابی قدر پاس کریں: `<Icon path="{{ icon }}" size="{{ size }}" />`۔ ایک ننگا نام جیسا کہ `path=icon` متن `icon` ہے، متغیر نہیں۔ کسی جزو کو سی ایس ایس کلاس دینے کے لیے، ایک `class_name` پروپ کا اعلان کریں: `class` ایک Python کلیدی لفظ ہے۔

> [!NOTE]
> ایک مددگار ٹیگ ہمیشہ خود بند ہوتا ہے۔ مواد کو `Link` کو منتقل کرنا اس کے `children` دلیل (`<Link href="/about" children="About" />`) سے ہوتا ہے، عنصر کے مواد سے نہیں۔

## طرزیں

`<style>` بلاکس اس صفحہ کے ساتھ خارج ہوتے ہیں جو ان کا اعلان کرتا ہے۔ ان کا دائرہ کار نہیں ہے: دو اجزاء میں استعمال ہونے والی کلاس کا نام ایک کلاس ہے۔ اپنی کلاسوں کا سابقہ ​​یا نام کی جگہ۔

## قواعد جو وقت بچاتے ہیں۔

- فی فائل ایک جزو۔ پاسکل کیس (`CopyChip.nexy`) میں فائل کا نام جزو کا نام ہے۔ ایک `.nexy` جزو کو Python ماڈیول کے طور پر درآمد کیا جاتا ہے: نام میں ایک ہائفن (`copy-chip.nexy`) مرتب نہیں ہوتا ہے۔
- پرپس کو استعمال کرنے سے پہلے ان کا اعلان کریں: ایک غیر اعلان شدہ متغیر خالی سٹرنگ کے طور پر پیش کرتا ہے، کیونکہ Jinja2 کا غیر وضاحتی یہاں خاموش ہے۔
- افعال کے اندر ضمنی اثرات رکھیں - ہر درخواست پر فرنٹ میٹر دوبارہ چلتا ہے۔

## اگلے اقدامات

- [Markdown اور MDX](markdown.md): مواد کے صفحات
- [ISR](../../rendering/isr.md): فی راستہ ایک صفحہ کیش کریں۔
- [CSR](../../rendering/csr.md): کلائنٹ سائیڈ رینڈرنگ
