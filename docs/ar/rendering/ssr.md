# SSR (عرض الخادم)

## التعريف

SSR هو الإعداد الافتراضي: يعرض الخادم الصفحة بتنسيق HTML لكل طلب. لا شيء يمكّنه، ولا توجد علامة تطفئه - يتم عرض مشروع وضع الخادم عند كل طلب ما لم تعلن الصفحة عن `revalidate`.

## كيف يعمل

<!-- router:fbr,custom -->
| ملف الطريق | ما الذي ينتج HTML | متى |
|---|---|---|
| `.nexy` | الوحدة Python المترجمة، من خلال Jinja2 | كل طلب |
| `.md` | Markdown، ثم أقرب تخطيط | كل طلب |
| `.mdx`، `.tsx`، `.vue`، `.svelte` | الإطار المقدم في Node | عند الإنشاء عندما لا يكون للمسار أي تخطيط، وإلا في المتصفح |
| `.py` | لا شيء: يقوم بإرجاع JSON أو `Response` | - |

صفحة Markdown ومعالج جنبًا إلى جنب في نفس المشروع:

```md filename="src/routes/changelog.md"
# Changelog

Rendered to HTML on every request, then wrapped in the nearest layout.
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```

المسار المكون هو الحالة الوحيدة التي تحتاج إلى جملة ثانية. في الإنتاج، يتم تقديم مسار المكون **بدون** تخطيطًا مع HTML الذي تم إنتاجه عند الإنشاء، ويقوم المكون بترطيبه. مع التخطيط، أو قيد التطوير، تكون الحاوية فارغة ويتم عرض المكون في المتصفح - تصبح الصفحة بعد ذلك عبارة عن غلاف يملأ نفسه.

المسار المكون للجدول، بدون تخطيط، لذلك يخدم الإنتاج HTML الخاص به من الإصدار:

```tsx filename="src/routes/pricing.tsx"
export default function Pricing() {
  return <h1>Pricing</h1>;
}
```
<!-- /router -->

<!-- router:modular -->
| تعود وحدة التحكم | ما الذي ينتج HTML | متى |
|---|---|---|
| `useViews("....nexy")` | الوحدة النمطية Python المترجمة، من خلال Jinja2 | كل طلب |
| `dict`، قائمة، نموذجا | لا شيء: FastAPI يجيب على JSON | - |

عرض ونقطة نهاية JSON، جنبًا إلى جنب في نفس الوحدة:

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

## تقديم دورة الحياة

<!-- router:fbr,custom -->
1. يصل الطلب إلى جهاز التوجيه المستند إلى الملف. تتم مطابقة المسار، ويتم إرسال المقاطع الديناميكية إلى الأنواع التي يعلنها المكون.

   ```اسم الملف nexy = "src/routes/orders/[id].nexy"
   ---
   المعرف: الدعامة [int]
   ---
   <h1>الطلب رقم {{ المعرف + 1000 }}</h1>
   ```

   `/orders/42` يعرض `Order #1042`؛ `/orders/abc` الإجابات `404`.
2. يعمل المكون. يتم تشغيل المستند الذي ينتظر على العقدة - وهو مستند العميل - في تجمع مؤشرات الترابط، لذلك لا يوقف حلقة الحدث.
3. الجسد متدفق كما `text/html`. المكون الذي ينتج قطعًا يقوم بدفقها أثناء تصنيعها.
4. يتلقى المتصفح HTML. هيدرات الجزر حسب [التوجيه](islands.md).

يتم تحويل الخطأ الذي يظهر أثناء العرض إلى صفحة بواسطة `errors.nexy` عندما يكون لدى المشروع صفحة: راجع [صفحات الخطأ](../routing/fbr/errors/README.md).
<!-- /router -->

<!-- router:modular -->
1. يصل الطلب إلى وحدة التحكم. يتم إرسال معلمات المسار الخاصة بها إلى الأنواع التي تعلن عنها الطريقة، وتمريرها إلى العرض:

   ```اسم ملف بايثون = "src/apps/order_controller.py"
   من وحدة تحكم الاستيراد nexy.decorators
   من nexy.hooks قم باستيراد useViews


   @Controller("/الطلبات/{id}")
   وحدة تحكم ترتيب الفئة:
       الحصول على مواطن غير متزامن (self، id: int):
           إرجاع useViews("src/apps/order_view.nexy"، context={"id": id})
   ```

   ```اسم الملف nexy = "src/apps/order_view.nexy"
   ---
   المعرف: الدعامة [int]
   ---
   <h1>الطلب رقم {{ المعرف + 1000 }}</h1>
   ```

   `/orders/42/` يعرض `Order #1042`؛ `/orders/abc/` الإجابات `404`.
2. يتم تشغيل العرض، ويقوم `useViews` بإرجاع HTML الخاص به كاستجابة.
3. يتلقى المتصفح HTML. هيدرات الجزر حسب [التوجيه](islands.md).

يتم الرد على الخطأ الذي يظهر أثناء العرض باستخدام صفحة الخطأ الافتراضية.
<!-- /router -->

## متى تستخدم

- تعرض الصفحة شيئًا يملكه القارئ: جلسة، حساب، عربة.
- يجب أن تكون البيانات جديدة عند كل تحميل.
- يجب أن يكون المحتوى بتنسيق HTML لبرامج الزحف التي لا تعمل JavaScript.
- الصفحة رخيصة الثمن: استعلام واحد، قالب واحد.

الحالة الأولى، صفحة تحية للقارئ من الجلسة. `useSession` يقرأ جلسة `useSession` في `nexyconfig.py`، والتي بدونها يفشل:

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

## التكوين

<!-- router:fbr,custom -->
لا شيء. هناك طريقان، وليس لديهم نفس الحبوب:

| لترك SSR ل | افعل هذا | الحبوب |
|---|---|---|
| صفحة واحدة، مع ذاكرة التخزين المؤقت | `revalidate = 60` في مقدمتها → [ISR](isr.md) | الصفحة |
| المشروع بأكمله، توجيه العميل | `useCSR = True` في `nexyconfig.py` → [المسؤولية الاجتماعية للشركات](csr.md) | مشروع |

التبديل على مستوى المشروع، في `nexyconfig.py`. يحتاج وضع العميل إلى إطار عمل العميل:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```
<!-- /router -->

<!-- router:modular -->
لا شيء. يتم تقديم كل عرض ترجعه وحدة التحكم عند كل طلب: [ISR](isr.md) و [CSR](csr.md) هما وضعان لجهاز التوجيه المستند إلى الملف.
<!-- /router -->

## مثال

<!-- router:fbr,custom -->
```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` يقوم بتشغيل هذا القالب مرة واحدة، مع ضبط `slug` على `hello`. الطلب الثاني يقوم بتشغيله مرة أخرى: لا يتم الاحتفاظ بأي شيء بين الاثنين. سلسلة الاستعلام ليست دعامة - اقرأها باستخدام الخطافات في [التنقل](../routing/fbr/navigation/hooks.md).
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

`GET /blog/hello/` يقوم بتشغيل هذا العرض مرة واحدة، مع ضبط `slug` على `hello`. الطلب الثاني يقوم بتشغيله مرة أخرى: لا يتم الاحتفاظ بأي شيء بين الاثنين. سلسلة الاستعلام ليست دعامة - اقرأها باستخدام `useSearchParams`.
<!-- /router -->

## القيود

- **عرض واحد لكل طلب.** زائران في نفس الثانية يدفع كل منهما ثمن العرض والاستعلامات التي تقف وراءه.
- **لا توجد ذاكرة تخزين مؤقت.** لا توجد ذاكرة تخزين مؤقت للاستجابة المشتركة لتدفئة: مع مسارات الملفات، يضيف [ISR](isr.md) واحدًا لكل عنوان URL.
- **يساعد الدفق فقط المكون الذي ينتج.** لا يزال الاستعلام البطيء الموجود أعلى الصفحة يؤخر البايت الأول.
- **لا يوجد إخراج ثابت.** في وضع الخادم، لا يتم تجميد أي شيء عند الإنشاء: لا يوجد وضع SSG، ولا يوجد أمر تصدير. انظر [التقديم](README.md).
- **تم إيقاف ميزة الهروب التلقائي** في `.nexy` القوالب. الهروب من القيم غير الموثوق بها مع `| e`.

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

## الخطوات التالية

<!-- router:fbr,custom -->
- [ISR](isr.md): قم بتخزين هذه الصفحة لكل عنوان URL
<!-- /router -->
- [الجزر](islands.md): احتفظ بـ SSR واجعل عنصر واجهة مستخدم واحدًا تفاعليًا
<!-- router:fbr,custom -->
- [CSR](csr.md): التنقل اليدوي إلى المتصفح
<!-- /router -->
- [الأداء](../deployment/performance.md)
