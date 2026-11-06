# هيكل المشروع

كل ملف في مشروع Nexy له وظيفة واحدة، ويعتمد مكان انتقاله على جهاز التوجيه: `src/routes/` للتوجيه المستند إلى الملف، `src/apps/` لجهاز التوجيه المعياري.

## المستوى الأعلى

<!-- router:fbr -->
```text
my-app/
├─ src/
│  ├─ routes/            every file is a route
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

لاختيار مجلد، اسأل ما هو الملف:

- **شيء يمكن للمتصفح فتحه** - طريق: `src/routes/`.
- **قطعة تستخدم بعدة طرق** - مكون أو وحدة نمطية: `src/components/`، `src/`.
- **ملف قدم كما هو** - `public/`.
- **تم إنشاؤه** - `__nexy__/`; لا تقم بتحريره أبدًا.

> [!WARNING]
> `src/routes/` يتم مسحه: يصبح المساعد الموجود هناك طريقًا. ضع مساعداً ليس طريقاً خارج `src/routes/`، أو ابدأ اسمه بـ `_`.
<!-- /router -->

<!-- router:modular -->
```text
my-app/
├─ src/
│  ├─ apps/              controllers, modules and their views
│  │  ├─ app_module.py   the root module, given to useRouter
│  │  ├─ app_controller.py
│  │  ├─ app_view.nexy   a view a controller returns
│  │  ├─ layout.nexy     the frame the controllers pass their view to
│  │  └─ users/          one folder per feature: controller, module, service, model
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = AppModule
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

لاختيار مجلد، اسأل ما هو الملف:

- **عنوان URL** - طريقة وحدة التحكم في `src/apps/`، المسجلة بواسطة الوحدة النمطية الخاصة بها.
- **صفحة** - عرض `.nexy` بجوار وحدة التحكم الخاصة بها، تم إرجاعها بـ `useViews`.
- **قطعة تستخدم بعدة وجهات نظر** - `src/components/`.
- **ملف قدم كما هو** - `public/`.
- **تم إنشاؤه** - `__nexy__/`; لا تقم بتحريره أبدًا.
<!-- /router -->

<!-- router:custom -->
```text
my-app/
├─ src/
│  ├─ legacy/            the FastAPI router you include
│  │  └─ api.py          router = APIRouter(prefix="/api")
│  ├─ routes/            pages and route files, served next to it
│  │  └─ index.nexy      → /
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = router
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

لاختيار مجلد، اسأل ما هو الملف:

- **مسار التطبيق المضمن** - حيث هو موجود بالفعل، هنا `src/legacy/`.
- **صفحة أو مسار جديد** - `src/routes/`، بجوار جهاز التوجيه المتضمن.
- **ملف قدم كما هو** - `public/`.
- **تم إنشاؤه** - `__nexy__/`; لا تقم بتحريره أبدًا.
<!-- /router -->

<!-- router:fbr,custom -->
## `src/routes/`

يصبح كل ملف مسارًا، باستثناء الأسماء المحجوزة أدناه. مسار الملف مطروحًا منه الامتداد هو عنوان URL - راجع [التوجيه المستند إلى الملف](../routing/fbr/README.md).

| ملف | الدور |
|---|---|
| `layout.nexy` | يلتف صفحات الأخوة والأبناء |
| `errors.nexy` | 500 صفحة للدليل |
| `notfound.nexy` | 404 صفحة للدليل |
| `dependencies.py` | تبعيات FastAPI مشتركة للدليل |
| `__init__.py` | Python علامة الحزمة |
| `loading.nexy` | محجوز - مستبعد من المسارات، ولكن ليس له تأثير وقت التشغيل حتى الآن |

كل اسم صفحة موجود أيضًا لكل إطار عمل. مع تكوين `react()`، يتم حجز `layout.jsx` و `layout.tsx` تمامًا مثل `layout.nexy`. وقد بنيت القوائم في `nexy/core/config.py` (`LAYOUT_FILE_NAMES`، `ERROR_FILE_NAMES`، `NOTFOUND_FILE_NAMES`، `LOADING_FILE_NAMES`).

> [!NOTE]
> يتم تثبيت `notfound.nexy` و `errors.nexy` فقط عند وجود نسخة في جذر المسارات. ثم تقوم النسخة الموجودة في دليل فرعي بتحسين الصفحة لتلك البادئة.
<!-- /router -->

<!-- router:modular -->
## `src/apps/`

تجيب وحدة التحكم على عناوين URL، وتجمع الوحدة وحدات التحكم والموفرين، ويتم تركيب الوحدة الجذرية مع `useRouter` في `nexyconfig.py`:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller()
class AppController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/app_view.nexy")})
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    useAliases = {"@": "src"}  # the views import @/components/...
```

لا يوجد ملف في `src/apps/` يمثل مسارًا باسمه: فقط وحدات التحكم التي تسردها الوحدة النمطية هي التي تجيب. انظر [التوجيه المعياري](../routing/modular/README.md).
<!-- /router -->

## `public/`

يتم تقديم الملفات هنا من جذر الموقع: `/favicon.ico`، `/robots.txt`، الصور، الخطوط.

## `__nexy__/`

أنشئ بواسطة `nx build` (وبواسطة `nx dev` للأجزاء التي يحتاجها). أنه يحتوي على:

- الملفات `.nexy` المجمعة، كحزمة Python (`__nexy__/src/...`)؛
- نقاط دخول العميل التي تم إنشاؤها (`main.ts`، `vite.ts`، `*.auto.ts`)؛
- `client/` بعد Vite البناء - الأصول، البيان، HTML المعروض مسبقًا؛
- `build-cache.json`.

تعامل مع الدليل بأكمله على أنه يمكن التخلص منه: احذفه وأعد بنائه. يؤدي تحريره يدويًا إلى فقدان التغيير في البنية التالية. أضفه إلى `.gitignore`.

## الخطوات التالية

<!-- router:fbr -->
- [التوجيه المستند إلى الملف](../routing/fbr/README.md): كيف يصبح المسار عنوان URL
<!-- /router -->
<!-- router:modular -->
- [التوجيه المعياري](../routing/modular/README.md): وحدات التحكم والوحدات والموفرين
<!-- /router -->
<!-- router:custom -->
- [التوجيه المخصص](../routing/custom/README.md): يتضمن جهاز توجيه موجود FastAPI
<!-- /router -->
- [التكوين ](../reference/config.md): كل خيار المشروع
- [الواجهة الأمامية](../guides/frontend.md): Vite والتصميم وبناء العميل
