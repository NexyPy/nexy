# المفاهيم الأساسية

الكلمات التي تستخدمها بقية المستندات - المسار، الصفحة، العرض، المكون، المعالج، نقطة النهاية - كل منها في سطر واحد، مع رابط للصفحة يتعمق أكثر. هل أنت جديد في نيكسي؟ ابدأ بـ [ما هو النكسي؟](what-is-nexy.md).

## كيفية قراءة هذه المستندات

| المستوى | السؤال الذي يجيب عليه | ابدأ بـ |
|---|---|---|
| بنية التطبيق | أي طبقة تجيب على الطلب، وما ترفض القيام به | [كيف يعمل نيكسي](how-nexy-works.md) |
| هيكل التطبيق | أين يعيش الكود، وما هو الملف | [هيكل المشروع](project-structure.md) |
| التقديم والتقديم | ما يراه القارئ ومن ينتج HTML | [المشاهدات](../views/README.md)، [العرض](../rendering/README.md) |
| تفاعل التطبيق | ما يفعله القارئ، وما يجري ردا على ذلك | [الإجراءات](../guides/actions.md) |

تتم قراءة المستويات بهذا الترتيب مرة واحدة. بعد ذلك، الصفحة التي تحتاجها هي صفحة بحث وليست دورة تدريبية.

## بنية التطبيق

ثلاث طرق لتحديد الرمز الذي يجيب على عنوان URL. إنها بدائل وليست طبقات:

- **التوجيه المستند إلى الملف (FBR)**: الملف الموجود ضمن `src/routes/` هو مسار. الافتراضي.
- **جهاز التوجيه المعياري**: وحدات التحكم والوحدات ضمن `src/apps/`، المُعلن عنها باستخدام أدوات الديكور، لقاعدة تعليمات برمجية على طراز NestJS.
- **جهاز التوجيه المخصص**: موجود FastAPI `APIRouter` موجود في التطبيق.

والاختيار هو سطر واحد من الصنف `NexyConfig` في `nexyconfig.py`.

<!-- router:fbr -->
لا يحتاج التوجيه المستند إلى الملف إلى سطر: بدون `useRouter`، يقرأ Nexy `src/routes/`.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    pass  # file-based: no useRouter, the files of src/routes/ are the routes
```
<!-- /router -->

<!-- router:modular -->
جهاز التوجيه المعياري هو الوحدة الجذرية لـ `src/apps/`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule  # modular: the root module of src/apps/
```
<!-- /router -->

<!-- router:custom -->
جهاز التوجيه المخصص هو `APIRouter` لديك بالفعل:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import api  # an APIRouter you already have


class NexyConfig(NexyConfigModel):
    useRouter = api  # custom: your router, included as it is
```
<!-- /router -->

اختيار واحد من الثلاثة هو قرار واحد. اختيار إطار عمل للواجهة الأمامية هو أمر آخر منفصل: راجع [اختر جهاز توجيه](../routing/README.md) و[طرق العرض](../views/README.md).

## هيكل التطبيق

خمسة مفاهيم عادة ما يدمجها القارئ القادم من Next.js في فكرة واحدة. إنهما ليسا نفس الشيء، والفرق يفسر معظم الأسئلة "لماذا لا تعرض صفحتي".

| فكرة | ما هو عليه | ما هو ليس كذلك |
|---|---|---|
| **الطريق** | نمط عنوان URL، الناتج عن مسار الملف | ملف: يمكن لملف واحد الإجابة على عدة عناوين URL (`[slug]`) |
| **الصفحة** | ملف مسار يعرض طريقة عرض: `.nexy`، `.md`، `.mdx`، `.tsx`، `.vue`، `.svelte` | نقطة النهاية: فهي تجيب على مستند، وليس على البيانات |
| **عرض** | ما الذي ينتج نص الصفحة: Jinja2 و Python، أو Markdown، أو مكون العميل | المسار: نفس العرض يمكن أن يخدم عدة صفحات |
| **المكون** | قطعة قابلة لإعادة الاستخدام تستوردها الصفحة | المسار: في وضع الخادم، لا يتم تقديم المكون بمفرده أبدًا |
| **معالج المسار** | وظيفة ملف المسار `.py`، المسمى على اسم طريقة HTTP (`GET`، `POST`، …) | صفحة: تقوم بإرجاع JSON أو ملف أو `Response` |
| **نقطة النهاية** | الزوج (URL، الطريقة) الذي يجيب عليه المعالج | المعالج: يمكن لملف واحد الإجابة على عدة نقاط نهاية |

في جملة واحدة: **الصفحة هي ملف توجيه، والعرض هو ما يعرضه، والمكون هو ما تعيد الصفحة استخدامه، والمعالج يجيب على نقطة النهاية.**

<!-- router:fbr -->
الخمسة في مشروع واحد صغير:

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

يمثل الجزء الأمامي والقالب الموجود أسفله عرض الصفحة؛ `Like` هو المكون الذي يعيد استخدامه.

```python filename="src/routes/api/posts.py"
async def GET():  # the endpoint GET /api/posts
    return {"posts": []}


async def POST():  # the endpoint POST /api/posts
    return {"created": True}
```

<!-- /router -->

<!-- router:modular -->
مع جهاز التوجيه المعياري، المسار هو مسار وحدة التحكم، والمعالج هو أحد أساليبه، والذي سمي على اسم فعل HTTP:

```text
src/
├─ apps/
│  ├─ app_module.py       the root module: lists the controllers
│  └─ posts_controller.py a route (/api/posts) whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```python filename="src/apps/posts_controller.py"
from nexy.decorators import Controller


@Controller("/api/posts")
class PostsController:
    async def get(self) -> dict:  # the endpoint GET /api/posts
        return {"posts": []}

    async def post(self) -> dict:  # the endpoint POST /api/posts
        return {"created": True}
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .posts_controller import PostsController


@Module()
class AppModule:
    controllers = [PostsController]
```

لا تزال الصفحة ملفًا لـ `src/routes/`، أو طريقة عرض ترجعها وحدة التحكم بـ `useViews`.
<!-- /router -->

<!-- router:custom -->
مع جهاز التوجيه المخصص، المسار هو مسار `APIRouter` الخاص بك، والمعالج هو الوظيفة التي يسجلها الديكور الخاص به:

```python filename="src/legacy.py"
from fastapi import APIRouter

api = APIRouter()


@api.get("/api/posts")  # the endpoint GET /api/posts
async def list_posts():
    return {"posts": []}


@api.post("/api/posts")  # the endpoint POST /api/posts
async def create_post():
    return {"created": True}
```

لا تزال الصفحات عبارة عن ملفات `src/routes/`: تجيب الصفحة `.nexy` بجوار المسارات المضمنة.
<!-- /router -->

كلمتان أخريان تعودان في كل مكان:

- **التخطيط**: ملف `layout.*` يغلف الصفحات الموجودة أسفل المجلد الخاص به؛ يمتلك الجذر مستند HTML. انظر [التخطيطات](../routing/fbr/layouts/README.md).
- **التبعية**: دالة يتم تشغيلها قبل المعالج، ويتم تطبيقها لكل مسار أو لكل مجلد. انظر [التبعيات](../routing/fbr/dependencies/README.md).

## التقديم والتقديم

قراران مستقلان، غالبًا ما يتم الخلط بينهما:

- **يحدد التنسيق** الملف الذي يعرض الصفحة: [المشاهدات](../views/README.md).
- **يحدد الوضع** من يقوم بإنتاج HTML ومتى: [العرض](../rendering/README.md).

| فكرة | سطر واحد |
|---|---|
| وضع الخادم | يعرض الخادم `.nexy` و `.md` صفحة؛ المكونات هي جزر ([الأوضاع](../routing/fbr/modes.md)) |
| وضع العميل | `useCSR = True`: ملفات الإطار هي المسارات، ويتم التنقل في المتصفح |
| SSR، ISR، CSR، الجزر | أربعة أوضاع عرض، يتم تحديدها لكل صفحة باستثناء CSR، والتي تكون لكل مشروع ([العرض](../rendering/README.md)) |
| الترطيب | المتصفح الذي يقوم بإرفاق إطار عمل بـ HTML الذي أرسله الخادم بالفعل ([الجزر](../rendering/islands.md)) |
| الدعائم | القيم التي يمررها أحد الوالدين إلى المكون، المعلن عنها `name: prop[type]` في ملف `.nexy` ([ملفات .nexy](../views/nexy/README.md)) |

صفحة في وضع الخادم بجزيرة واحدة: يعرض الخادم الصفحة، ويقوم المتصفح بترطيب المخطط فقط عند تمريره إلى العرض.

<!-- router:fbr,custom -->
```nexy filename="src/routes/sales.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Sales</h1>
<Chart directive="client:visible" />
```
<!-- /router -->

<!-- router:modular -->
تظهر الجزيرة في العرض، وتقوم وحدة التحكم بإرجاع العرض:

```nexy filename="src/apps/sales_view.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Sales</h1>
<Chart directive="client:visible" />
```

```python filename="src/apps/sales_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/sales")
class SalesController:
    async def get(self):
        return useViews("src/apps/sales_view.nexy")
```
<!-- /router -->

## تفاعل التطبيق

| فكرة | سطر واحد |
|---|---|
| العمل | دالة Python تم وضع علامة `@Action` عليها، بمثابة `POST`، قابلة للاستدعاء من نموذج أو كدالة مكتوبة ([إجراءات](../guides/actions.md)) |
| النموذج | نموذج HTML ينشر إلى إجراء، مع عودة أخطاء التحقق من الصحة إلى الصفحة ([الإجراءات](../guides/actions.md)) |
| الملاحة | الروابط التي تجلب مسبقًا، والخطافات التي تقرأ المسار والاستعلام وملفات تعريف الارتباط والجلسة ([الخطافات](../routing/fbr/navigation/hooks.md)) |
| جلب البيانات | تتم بواسطة الصفحة أو المعالج الذي يحتاج إليها؛ لا يقوم Nexy بشحن طبقة بيانات العميل ([معالجات](../routing/fbr/handlers/README.md)) |

الإجراء والنموذج الذي يتم النشر إليه، والذي يعمل قبل تحميل أي برنامج نصي:

```python filename="src/actions/newsletter.py"
from nexy.decorators import Action


@Action
async def subscribe(email: str) -> bool:
    return True
```

<!-- router:fbr,custom -->
```html filename="src/routes/index.nexy"
<form method="post" action="{{ __actions_path['subscribe'] }}">
  <input name="email" type="email">
  <button type="submit">Subscribe</button>
</form>
```
<!-- /router -->

<!-- router:modular -->
```html filename="src/apps/home_view.nexy"
<form method="post" action="{{ __actions_path['subscribe'] }}">
  <input name="email" type="email">
  <button type="submit">Subscribe</button>
</form>
```
<!-- /router -->

## ما لا يفعله نيكي

المصادقة والترخيص وقاعدة البيانات والتدويل والوظائف الأساسية والبريد الإلكتروني والمدفوعات والبحث هي **مسؤولية تطبيقك**، وليست مسؤولية إطار العمل. يعطي Nexy نقاط الامتداد ويقول مكان توصيل كل واحدة منها: راجع [ما يتركه Nexy لك](how-nexy-works.md#what-nexy-leaves-to-you).

<!-- router:fbr -->
المصادقة، على سبيل المثال، يتم توصيلها بتبعية المجلد الذي تحميه. يقوم Nexy بتشغيله قبل كل طريق أدناه؛ من هو المستخدم يبقى قرارك:

```python filename="src/routes/account/dependeency.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```
<!-- /router -->

<!-- router:modular -->
على سبيل المثال، يتم توصيل المصادقة بوحدة حماية على وحدة التحكم التي تحميها. يقوم Nexy بتشغيله قبل كل معالج للفئة؛ من هو المستخدم يبقى قرارك:

```python filename="src/apps/account_controller.py"
from nexy import unauthorized
from nexy.decorators import Controller, UseGuard
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


@Controller("/account")
@UseGuard(require_login)
class AccountController:
    async def get(self) -> dict:
        return {"ok": True}
```
<!-- /router -->

<!-- router:custom -->
المصادقة، على سبيل المثال، يتم توصيلها بتبعية جهاز التوجيه الذي تحميه، كما في FastAPI؛ من هو المستخدم يبقى قرارك:

```python filename="src/account.py"
from fastapi import APIRouter, Depends

from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


api = APIRouter(prefix="/account", dependencies=[Depends(require_login)])
```
<!-- /router -->

السبب ليس البساطة في حد ذاتها: إن إطار العمل الذي يختار ORM الخاص بك أو مكتبة المصادقة الخاصة بك قد قرر شيئًا لا يمكن لأحد أن يقرره إلا تطبيقك.

## الخطوات التالية

- [هيكل المشروع](project-structure.md): كل مجلد وملف للمشروع
- [المعجم](../reference/glossary.md): الكلمات نفسها في فهرس أبجدي واحد
- [كيف يعمل Nexy](how-nexy-works.md): الطبقات، ومن يبني ماذا، وماذا يترك لك Nexy
