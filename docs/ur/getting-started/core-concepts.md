# بنیادی تصورات

باقی دستاویزات جو الفاظ استعمال کرتے ہیں - راستہ، صفحہ، منظر، جزو، ہینڈلر، اختتامی نقطہ - ہر ایک ایک لائن میں، صفحہ کے لنک کے ساتھ جو گہرائی تک جاتا ہے۔ Nexy میں نئے ہیں؟ [Nexy کیا ہے؟](what-is-nexy.md) سے شروع کریں۔

## ان دستاویزات کو کیسے پڑھیں

| سطح | وہ سوال جس کا جواب دیتا ہے۔ | سے شروع کریں۔ |
|---|---|---|
| ایپلیکیشن فن تعمیر | کون سی پرت درخواست کا جواب دیتی ہے، اور کیا کرنے سے انکار کرتی ہے۔ | [Nexy کیسے کام کرتا ہے](how-nexy-works.md) |
| درخواست کا ڈھانچہ | کوڈ کہاں رہتا ہے، اور فائل کیا بنتی ہے۔ | [پروجیکٹ کا ڈھانچہ](project-structure.md) |
| پیش کش اور پیش کش | قاری کیا دیکھتا ہے، اور HTML کون تیار کرتا ہے۔ | [آراء](../views/README.md)، [رینڈرنگ](../rendering/README.md) |
| درخواست کا تعامل | قاری کیا کرتا ہے، اور جواب میں کیا چلتا ہے۔ | [اعمال ](../guides/actions.md) |

سطحوں کو اس ترتیب میں ایک بار پڑھا جاتا ہے۔ اس کے بعد، آپ کو جس صفحہ کی ضرورت ہے وہ ایک تلاش ہے، نہ کہ کورس۔

## ایپلیکیشن فن تعمیر

یہ فیصلہ کرنے کے تین طریقے کہ کون سا کوڈ یو آر ایل کا جواب دیتا ہے۔ وہ متبادل ہیں، پرتیں نہیں:

- **فائل پر مبنی روٹنگ (FBR)**: `src/routes/` کے تحت فائل ایک روٹ ہے۔ پہلے سے طے شدہ۔
- **ماڈیولر راؤٹر**: NestJS طرز کے کوڈ بیس کے لیے `src/apps/` کے تحت کنٹرولرز اور ماڈیولز، ڈیکوریٹرز کے ساتھ اعلان کردہ۔
- **حسب ضرورت روٹر**: ایک موجودہ FastAPI `APIRouter` ایپلی کیشن میں شامل ہے۔

انتخاب `nexyconfig.py` کی ایک سطر ہے۔ فائل پر مبنی روٹنگ کو کسی کی ضرورت نہیں ہے: بغیر `useRouter`، Nexy پڑھتا ہے `src/routes/`۔

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule  # modular: the root module of src/apps/
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.legacy import api  # an APIRouter you already have


class NexyConfig(NexyConfigModel):
    useRouter = api  # custom: your router, included as it is
```

تین میں سے کسی ایک کا انتخاب کرنا ایک فیصلہ ہے۔ فرنٹ اینڈ فریم ورک کا انتخاب ایک اور ہے، الگ الگ: دیکھیں [روٹر کا انتخاب کریں](../routing/README.md) اور [دیکھے](../views/README.md)۔

## درخواست کا ڈھانچہ

پانچ تصورات جو کہ Next.js سے آنے والا قاری عموماً ایک میں ضم ہوجاتا ہے۔ وہ ایک ہی چیز نہیں ہیں، اور فرق زیادہ تر سوالات کی وضاحت کرتا ہے "میرا صفحہ کیوں پیش نہیں کر رہا ہے"۔

| تصور | یہ کیا ہے | یہ کیا نہیں ہے۔ |
|---|---|---|
| **راستہ** | ایک URL پیٹرن، جو ایک فائل کے راستے سے تیار ہوتا ہے۔ | ایک فائل: ایک فائل کئی یو آر ایل کا جواب دے سکتی ہے (`[slug]`) |
| **صفحہ** | ایک روٹ فائل جو ایک منظر پیش کرتی ہے: `.nexy`، `.md`، `.mdx`، `.tsx`، `.vue`، `.svelte` | ایک اختتامی نقطہ: یہ ایک دستاویز کا جواب دیتا ہے، ڈیٹا نہیں۔ |
| **دیکھیں** | صفحہ کا باڈی کیا بناتا ہے: Jinja2 اور Python، Markdown، یا کلائنٹ کا جزو | ایک راستہ: ایک ہی منظر کئی صفحات کی خدمت کرسکتا ہے۔ |
| **جزو** | دوبارہ قابل استعمال ٹکڑا ایک صفحہ درآمد کرتا ہے۔ | ایک راستہ: سرور موڈ میں ایک جزو کبھی بھی خود سے پیش نہیں ہوتا ہے۔ |
| **روٹ ہینڈلر** | ایک `.py` روٹ فائل کا فنکشن، جس کا نام HTTP طریقہ (`GET`، `POST`، …) | ایک صفحہ: یہ JSON، ایک فائل یا ایک `Response` لوٹاتا ہے |
| **اختتامی نقطہ** | جوڑا (URL، طریقہ) جس کا ہینڈلر جواب دیتا ہے۔ | ایک ہینڈلر: ایک فائل کئی اختتامی نکات کا جواب دے سکتی ہے۔ |

ایک جملے میں: **ایک صفحہ ایک روٹ فائل ہے، ایک منظر وہ ہے جو اسے پیش کرتا ہے، ایک جزو وہ ہے جسے صفحہ دوبارہ استعمال کرتا ہے، ایک ہینڈلر ایک اختتامی نقطہ کا جواب دیتا ہے۔**

تمام پانچ ایک چھوٹے پروجیکٹ میں:

```text
src/
├─ routes/
│  ├─ blog/[slug].nexy    a route (/blog/{slug}) whose file is a page
│  └─ api/posts.py        a route whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```nexy filename="src/routes/blog/[slug].nexy"
---
from "@/components/Like.tsx" import Like

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Like post="{{ slug }}" />
```

فرنٹ میٹر اور اس کے نیچے کا سانچہ صفحہ کا منظر ہے۔ `Like` وہ جزو ہے جسے یہ دوبارہ استعمال کرتا ہے۔

```python filename="src/routes/api/posts.py"
async def GET():  # the endpoint GET /api/posts
    return {"posts": []}


async def POST():  # the endpoint POST /api/posts
    return {"created": True}
```

دو مزید الفاظ جو ہر جگہ واپس آتے ہیں:

- **لے آؤٹ**: ایک `layout.*` فائل جو اپنے فولڈر کے نیچے صفحات کو سمیٹتی ہے۔ جڑ HTML دستاویز کا مالک ہے۔ دیکھیں [لے آؤٹ](../routing/fbr/layouts/README.md)۔
- **انحصار**: ایک فنکشن جو ہینڈلر سے پہلے چلتا ہے، فی روٹ یا فی فولڈر لاگو ہوتا ہے۔ دیکھیں [انحصار](../routing/fbr/dependencies/README.md)۔

## پیش کش اور پیش کش

دو آزاد فیصلے، اکثر الجھ جاتے ہیں:

- **فارمیٹ** فیصلہ کرتا ہے کہ کون سی فائل صفحہ کو رینڈر کرتی ہے: [ملاحظات](../views/README.md)۔
- **موڈ** فیصلہ کرتا ہے کہ ایچ ٹی ایم ایل کون تیار کرتا ہے اور کب: [رینڈرنگ](../rendering/README.md)۔

| تصور | ایک لائن |
|---|---|
| سرور موڈ | سرور `.nexy` اور `.md` صفحات پیش کرتا ہے۔ اجزاء جزیرے ہیں ([موڈز](../routing/fbr/modes.md)) |
| کلائنٹ موڈ | `useCSR = True`: فریم ورک فائلیں راستے ہیں، اور نیویگیشن براؤزر میں ہوتی ہے۔ |
| SSR، ISR، CSR، جزائر | چار رینڈرنگ موڈز، فی صفحہ طے کیا گیا سوائے CSR کے، جو فی پروجیکٹ ہے ([رینڈرنگ](../rendering/README.md)) |
| ہائیڈریشن | HTML کے ساتھ ایک فریم ورک منسلک کرنے والا براؤزر پہلے ہی بھیجے ہوئے سرور ([جزیرے](../rendering/islands.md)) |
| سہارے | وہ اقدار جو والدین کسی جزو کو منتقل کرتے ہیں، `name: prop[type]` کا اعلان `.nexy` فائل میں کیا جاتا ہے ([.nexy فائلز](../views/nexy/README.md)) |

ایک جزیرے کے ساتھ سرور موڈ کا صفحہ: سرور صفحہ کو رینڈر کرتا ہے، براؤزر صرف اس وقت چارٹ کو ہائیڈریٹ کرتا ہے جب وہ منظر میں اسکرول کرتا ہے۔

```nexy filename="src/routes/sales.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Sales</h1>
<Chart directive="client:visible" />
```

## درخواست کا تعامل

| تصور | ایک لائن |
|---|---|
| ایکشن | ایک Python فنکشن نشان زد `@Action`، ایک `POST` کے طور پر پیش کیا گیا، فارم سے کال کیا جا سکتا ہے یا ٹائپ شدہ فنکشن کے طور پر ([ایکشنز](../guides/actions.md)) |
| فارم | ایک ایچ ٹی ایم ایل فارم جو ایک ایکشن پر پوسٹ کرتا ہے، توثیق کی غلطیوں کے ساتھ صفحہ پر واپس آتا ہے ([ایکشن](../guides/actions.md)) |
| نیویگیشن | لنکس جو پہلے سے تیار کرتے ہیں، اور ہکس جو راستے، استفسار، کوکیز اور سیشن کو پڑھتے ہیں ([ہکس](../routing/fbr/navigation/hooks.md)) |
| ڈیٹا بازیافت کرنا | صفحہ یا ہینڈلر کے ذریعہ کیا گیا ہے جس کی ضرورت ہے۔ Nexy بغیر کلائنٹ کی ڈیٹا لیئر بھیجتا ہے ([ہینڈلر](../routing/fbr/handlers/README.md)) |

ایک عمل اور فارم جو اس پر پوسٹ کرتا ہے، جو کسی بھی اسکرپٹ کے لوڈ ہونے سے پہلے کام کرتا ہے:

```python filename="src/actions/newsletter.py"
from nexy.decorators import Action


@Action
async def subscribe(email: str) -> bool:
    return True
```

```html filename="src/routes/index.nexy"
<form method="post" action="{{ __actions_path['subscribe'] }}">
  <input name="email" type="email">
  <button type="submit">Subscribe</button>
</form>
```

## Nexy کیا نہیں کرتا

توثیق، اجازت، ڈیٹا بیس، بین الاقوامی کاری، پس منظر کی ملازمتیں، ای میل، ادائیگیاں اور تلاش **آپ کی درخواست کی ذمہ داری** ہیں، فریم ورک کی نہیں۔ Nexy ایکسٹینشن پوائنٹ دیتا ہے اور کہتا ہے کہ ہر ایک کو کہاں سے لگانا ہے: دیکھیں [Nexy آپ کے لیے کیا چھوڑتا ہے](how-nexy-works.md#what-nexy-leaves-to-you)۔

توثیق، مثال کے طور پر، اس فولڈر کے انحصار میں پلگ ان کی حفاظت کرتا ہے۔ Nexy اسے نیچے کے ہر راستے سے پہلے چلاتا ہے۔ صارف کون ہے آپ کا فیصلہ برقرار ہے:

```python filename="src/routes/account/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

وجہ اس کی اپنی خاطر minimalism نہیں ہے: ایک فریم ورک جو آپ کے ORM یا آپ کی auth لائبریری کو چنتا ہے اس نے کچھ فیصلہ کیا ہے جس کا فیصلہ صرف آپ کی درخواست ہی کر سکتی ہے۔

## اگلے اقدامات

- [پروجیکٹ کا ڈھانچہ ](project-structure.md): پروجیکٹ کا ہر فولڈر اور فائل
- [لغت ](../reference/glossary.md): ایک ہی الفاظ، ایک حروف تہجی کے اشاریہ میں
- [کس طرح Nexy کام](how-nexy-works.md): پرتیں، کون کیا بناتا ہے، اور کیا Nexy آپ کے لیے چھوڑتا ہے۔
