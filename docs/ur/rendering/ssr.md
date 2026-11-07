# SSR (سرور رینڈرنگ)

## تعریف

SSR پہلے سے طے شدہ ہے: سرور ہر درخواست کے لیے صفحہ کو HTML میں پیش کرتا ہے۔ کوئی بھی چیز اسے فعال نہیں کرتی ہے، اور کوئی جھنڈا اسے بند نہیں کرتا ہے - ایک سرور موڈ پروجیکٹ ہر درخواست پر پیش کرتا ہے جب تک کہ صفحہ `revalidate` کا اعلان نہ کرے۔

## یہ کیسے کام کرتا ہے۔

<!-- router:fbr,custom -->
| روٹ فائل | جو HTML تیار کرتا ہے۔ | جب |
|---|---|---|
| `.nexy` | مرتب کردہ Python ماڈیول، Jinja2 کے ذریعے | ہر درخواست |
| `.md` | Markdown، پھر قریب ترین لے آؤٹ | ہر درخواست |
| `.mdx`، `.tsx`، `.vue`، `.svelte` | فریم ورک، نوڈ میں پیش کیا گیا ہے۔ | تعمیر پر جب روٹ کا کوئی لے آؤٹ نہ ہو، بصورت دیگر براؤزر میں |
| `.py` | کچھ نہیں: یہ JSON یا ایک `Response` لوٹاتا ہے | - |

ایک Markdown صفحہ اور ایک ہینڈلر، ایک ہی پروجیکٹ میں شانہ بشانہ:

```md filename="src/routes/changelog.md"
# Changelog

Rendered to HTML on every request, then wrapped in the nearest layout.
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```

ایک جزو کا راستہ ایک ایسا معاملہ ہے جس میں دوسری سزا کی ضرورت ہے۔ پیداوار میں، ایک جزو کا راستہ **بغیر** ایک لے آؤٹ کو تعمیر کے وقت تیار کردہ HTML کے ساتھ پیش کیا جاتا ہے، اور جزو اسے ہائیڈریٹ کرتا ہے۔ لے آؤٹ کے ساتھ، یا ترقی میں، کنٹینر خالی ہے اور جز براؤزر میں پیش کرتا ہے - صفحہ پھر ایک شیل ہے جو خود کو بھرتا ہے۔

ٹیبل کا جزو راستہ، بغیر کسی ترتیب کے، لہذا پروڈکشن اپنے HTML کو تعمیر سے پیش کرتی ہے:

```tsx filename="src/routes/pricing.tsx"
export default function Pricing() {
  return <h1>Pricing</h1>;
}
```
<!-- /router -->

<!-- router:modular -->
| ایک کنٹرولر واپس آتا ہے۔ | جو HTML تیار کرتا ہے۔ | جب |
|---|---|---|
| `useViews("....nexy")` | مرتب کردہ Python ماڈیول، Jinja2 کے ذریعے | ہر درخواست |
| ایک `dict`، ایک فہرست، ایک ماڈل | کچھ نہیں: FastAPI JSON کا جواب دیتا ہے۔ | - |

ایک منظر اور ایک JSON اختتامی نقطہ، ایک ہی ماڈیول میں شانہ بشانہ:

```nexy filename="src/apps/changelog_view.nexy"
<h1>Changelog</h1>
<p>Rendered to HTML on every request.</p>
```

```python filename="src/apps/site_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/changelog")
class ChangelogController:
    async def get(self):
        return useViews("src/apps/changelog_view.nexy")


@Controller("/api/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```
<!-- /router -->

## رینڈرنگ لائف سائیکل

<!-- router:fbr,custom -->
1. درخواست فائل پر مبنی روٹر تک پہنچ جاتی ہے۔ راستہ مماثل ہے، اور متحرک حصوں کو ان اقسام میں ڈالا جاتا ہے جس کا جزو اعلان کرتا ہے۔

   ```nexy filename="src/routes/orders/[id].nexy"
   ---
   id: prop[int]
   ---
   <h1>Order #{{ id + 1000 }}</h1>
   ```

   `/orders/42` رینڈرز `Order #1042`؛ `/orders/abc` جوابات `404`۔
2. جزو چلتا ہے۔ ایک جو نوڈ پر انتظار کرتا ہے - ایک کلائنٹ دستاویز - تھریڈ پول میں چلتا ہے، لہذا یہ ایونٹ لوپ کو اسٹال نہیں کرتا ہے۔
3. جسم کو `text/html` کے طور پر بہایا جاتا ہے۔ ایک جزو جس سے ٹکڑوں کی پیداوار ہوتی ہے وہ انہیں بناتا ہے۔
4. براؤزر HTML وصول کرتا ہے۔ جزائر ان کی [ہدایت](islands.md) کے مطابق ہائیڈریٹ ہوتے ہیں۔

رینڈرنگ کے دوران پیدا ہونے والی غلطی کو `errors.nexy` کے ذریعے صفحہ میں تبدیل کر دیا جاتا ہے جب پروجیکٹ میں ایک ہوتا ہے: دیکھیں [غلطی کے صفحات](../routing/fbr/errors/README.md)۔
<!-- /router -->

<!-- router:modular -->
1. درخواست کنٹرولر تک پہنچ جاتی ہے۔ اس کے راستے کے پیرامیٹرز ان اقسام میں ڈالے جاتے ہیں جن کا طریقہ بیان کرتا ہے، اور منظر پر منتقل کیا جاتا ہے:

   ```python filename="src/apps/order_controller.py"
   from nexy.decorators import Controller
   from nexy.hooks import useViews


   @Controller("/orders/{id}")
   class OrderController:
       async def get(self, id: int):
           return useViews("src/apps/order_view.nexy", context={"id": id})
   ```

   ```nexy filename="src/apps/order_view.nexy"
   ---
   id: prop[int]
   ---
   <h1>Order #{{ id + 1000 }}</h1>
   ```

   `/orders/42/` رینڈرز `Order #1042`؛ `/orders/abc/` جوابات `404`۔
2. ویو چلتا ہے، اور `useViews` جواب کے طور پر اپنا HTML واپس کرتا ہے۔
3. براؤزر HTML وصول کرتا ہے۔ جزائر ان کی [ہدایت](islands.md) کے مطابق ہائیڈریٹ ہوتے ہیں۔

رینڈرنگ کے دوران پیدا ہونے والی غلطی کا جواب ڈیفالٹ ایرر پیج کے ساتھ دیا جاتا ہے۔
<!-- /router -->

## کب استعمال کرنا ہے۔

- صفحہ کچھ ایسی چیز دکھاتا ہے جو قاری کے پاس ہے: ایک سیشن، ایک اکاؤنٹ، ایک کارٹ۔
- ڈیٹا ہر بوجھ پر تازہ ہونا چاہیے۔
- مواد ان کرالروں کے لیے HTML میں ہونا چاہیے جو نہیں چلتے JavaScript۔
- صفحہ پیش کرنے کے لیے سستا ہے: ایک سوال، ایک ٹیمپلیٹ۔

پہلی صورت، ایک صفحہ جو قاری کو سیشن سے سلام کرتا ہے۔ `useSession` `nexyconfig.py` میں `useSession` کا سیشن پڑھتا ہے، جس کے بغیر یہ ناکام ہوجاتا ہے:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me"}
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/account.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/account_view.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

## کنفیگریشن

<!-- router:fbr,custom -->
کوئی نہیں۔ دو راستے ہیں، اور ان کے پاس ایک ہی اناج نہیں ہے:

| کے لیے ایس ایس آر چھوڑنے کے لیے | یہ کرو | اناج |
|---|---|---|
| ایک صفحہ، ایک کیشے کے ساتھ | `revalidate = 60` اس کے فرنٹ میٹر میں → [ISR](isr.md) | صفحہ |
| پورا پروجیکٹ، کلائنٹ روٹڈ | `useCSR = True` میں `nexyconfig.py` → [CSR](csr.md) | پروجیکٹ |

پروجیکٹ وسیع سوئچ، `nexyconfig.py` میں۔ کلائنٹ موڈ کو کلائنٹ فریم ورک کی ضرورت ہے:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```
<!-- /router -->

<!-- router:modular -->
کوئی نہیں۔ کنٹرولر کی واپسی کا ہر منظر ہر درخواست پر پیش کیا جاتا ہے: [ISR](isr.md) اور [CSR](csr.md) فائل پر مبنی روٹر کے موڈ ہیں۔
<!-- /router -->

## مثال

<!-- router:fbr,custom -->
```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` اس سانچے کو ایک بار چلاتا ہے، `slug` کو `hello` پر سیٹ کرتا ہے۔ دوسری درخواست اسے دوبارہ چلاتی ہے: دونوں کے درمیان کچھ نہیں رکھا جاتا ہے۔ استفسار کی تار کوئی سہارا نہیں ہے - اسے [نیویگیشن](../routing/fbr/navigation/hooks.md) میں ہکس کے ساتھ پڑھیں۔
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/blog_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/post_view.nexy", context={"slug": slug})
```

```nexy filename="src/apps/post_view.nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello/` اس منظر کو ایک بار چلاتا ہے، `slug` کو `hello` پر سیٹ کرتا ہے۔ دوسری درخواست اسے دوبارہ چلاتی ہے: دونوں کے درمیان کچھ نہیں رکھا جاتا ہے۔ استفسار کی تار کوئی سہارا نہیں ہے - اسے `useSearchParams` کے ساتھ پڑھیں۔
<!-- /router -->

## حدود

- **فی ایک رینڈر درخواست** ایک ہی سیکنڈ میں دو زائرین رینڈر اور اس کے پیچھے سوالات کے لیے ادائیگی کرتے ہیں۔
- **نہیں کیشے** گرم کرنے کے لیے کوئی مشترکہ رسپانس کیش نہیں ہے: فائل روٹس کے ساتھ، [ISR](isr.md) فی یو آر ایل، ایک کا اضافہ کرتا ہے۔
- **سٹریمنگ صرف اس جزو کی مدد کرتا ہے۔ پیداوار** صفحہ کے اوپری حصے میں ایک سست سوال اب بھی پہلے بائٹ میں تاخیر کرتا ہے۔
- **کوئی جامد نہیں۔ آؤٹ پٹ** سرور موڈ میں تعمیر میں کچھ بھی منجمد نہیں ہوتا ہے: کوئی SSG موڈ نہیں ہے، اور کوئی برآمد کمانڈ نہیں ہے۔ دیکھیں [ترجمہ ](README.md)۔
- **`.nexy` ٹیمپلیٹس میں آٹو اسکیپنگ بند ہے**۔ `| e` کے ساتھ ناقابل اعتماد اقدار سے بچیں۔

<!-- router:fbr,custom -->
```nexy filename="src/routes/search.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/search_view.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

## اگلے اقدامات

<!-- router:fbr,custom -->
- [ISR](isr.md): اس صفحہ کو فی یو آر ایل کیش کریں۔
<!-- /router -->
- [جزائر](islands.md): SSR کو برقرار رکھیں اور ایک ویجیٹ کو انٹرایکٹو بنائیں
<!-- router:fbr,custom -->
- [CSR](csr.md): براؤزر پر ہینڈ نیویگیشن
<!-- /router -->
- [کارکردگی ](../deployment/performance.md)
