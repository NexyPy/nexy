# التكوين

التكوين هو فئة في `nexyconfig.py` في جذر المشروع. يقوم Nexy بتحميله من الدليل الذي يعمل فيه؛ يستخدم المشروع بدون الملف الإعدادات الافتراضية.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    usePort = 3000
    useTitle = "My App"
    useAliases = {"@": "src"}
```

## الخادم

| الميدان | الافتراضي | معنى |
|---|---|---|
| `usePort` | `3000` | منفذ لـ `dev` و `start` |
| `useHost` | `"0.0.0.0"` | ربط العنوان |
| `useSslKeyfile`، `useSslCertfile` | `None` | خدمة HTTPS مباشرة |
| `useDevTools` | `True` | يضيف شريط الأدوات `nexy dev` إلى كل صفحة (معلومات الصفحة، والمسارات، والأخطاء، والتكوين)؛ `False` يزيله. لا يوجد أبدا في الإنتاج |
| `useHealth` | `False` | يخدم `GET /health/live` و `GET /health/ready` لموازنات التحميل وتحقيقات Kubernetes؛ راجع [نشر](../deployment/README.md#built-in-endpoints) |
| `useMaxBodySize` | `1048576` | أكبر نص طلب يقرأه العامل، بالبايت (1 ميجابايت)؛ الأكبر هو `413`، و `0` يطفئ الحد. ارفعه إلى المسار الذي يأخذ تحميلات الملفات |
| `useSiteUrl` | `None` | الأصل العام للموقع، مثل `"https://example.com"`؛ بمجرد ضبطه، يخدم Nexy `/sitemap.xml` و `/robots.txt`. راجع [خريطة الموقع وملف robots.txt](../guides/sitemap.md) |
| `useWorkers` | `0` | تشغيل العمليات `nx start`؛ `0` هو واحد لكل وحدة معالجة مركزية على Linux وmacOS، وواحد على Windows |
| `useCSR` | `False` | وضع التوجيه من جانب العميل؛ `.nexy` الطرق معطلة |
| `useBasePath` | `None` | البادئة العامة للتطبيق بأكمله، مثل `"/app"`؛ الطلبات خارجها تجيب على 404، والروابط التي تم إنشاؤها ومسارات العميل ونداءات الإجراء والأصول تحمل البادئة. راجع [نشر](../deployment/README.md#serve-under-a-sub-path) |
| `useImageWidths` | `[320, 640, 960, 1280]` | عروض البكسل `nx build` تولد للصور المحلية؛ يحتاج التحويل إلى `Pillow`، وبدونه تحتفظ الصور بعنوان URL الأصلي الخاص بها. انظر [الصورة](../routing/fbr/navigation/linking-and-navigating.md#image) |
| `useISRCache` | `None` | مخزن ISR: `None` أو `"memory"` لعملية واحدة، `"file"` لمضيف واحد، `"redis"` لعدة عاملين، تعيين مع `type` والخيارات، أو كائن مع `get`، `set` و `invalidate`. انظر [ISR](../rendering/isr.md#choose-a-store) |

## قاعدة البيانات

| الميدان | الافتراضي | معنى |
|---|---|---|
| `useORM` | `None` | ORM للمشروع: `"SQLModel"`، `"SQLAlchemy"` أو `"Tortoise-ORM"`. `nx new` يكتبه، و `nx migrate` ينتقي منه Alembic أو Aerich منه؛ بدونه، `nx migrate` يأخذ أول ORM مثبتًا. انظر [قواعد البيانات](../guides/databases.md#migrations) |

## الطرق

| الميدان | الافتراضي | معنى |
|---|---|---|
| `useRouter` | `None` | `APIRouter` مثيل أو فئة مثبتة بجوار المسارات المستندة إلى الملف؛ `None` يعني المستند إلى الملف فقط |
| `excludeDirs` | `["templates", "extension", "docs"]` | تم تخطي الدلائل عند مسح المسارات |
| `useAliases` | `None` | استيراد الأسماء المستعارة، على سبيل المثال `{"@": "src"}` (`@/components/Counter.tsx` يعني `src/components/Counter.tsx`)؛ `nx new` يكتب الذي اخترته، ويتبعه Vite و `tsconfig.json` |

## الواجهة الأمامية

| الميدان | الافتراضي | معنى |
|---|---|---|
| `useFF` | `None` | مصنع إطار العميل: `react()`، `vue()`، `svelte()`، `solid()`، `preact()` |
| `useVite` | `True` | بناء وتقديم حزم العملاء مع Vite |
| `useMarkdownExtensions` | `[]` | ملحقات إضافية للعرض `.md`/`.mdx` |
| `useWatchExtensions` | `None` | ملحقات إضافية يشاهدها خادم التطوير |
| `useWatchExcludePatterns` | `None` | أنماط الكرة الأرضية التي يتجاهلها خادم التطوير |

> **من المفيد معرفة**: `NexyConfigModel` يعلن `useVite = False`؛ وقت التشغيل `Config` الافتراضي هو `True`.

## أسماء الملفات المحجوزة

يضيف كل حقل ملحقات إلى دور محجوز. `useLayoutExtensions = ["md"]` يجعل `layout.md` محجوزاً، مثل `layout.nexy` تماماً.

| الميدان | يضيف ملحقات إلى |
|---|---|
| `useLayoutExtensions` | `layout.*` |
| `useNotFoundExtensions` | `notfound.*` |
| `useErrorsExtensions` | `errors.*` |
| `useForbiddenExtensions` | `forbidden.*` |
| `useUnauthorizedExtensions` | `unauthorized.*` |
| `useLoadingExtensions` | `loading.*` |

## وثائق واجهة برمجة التطبيقات

| الميدان | الافتراضي | معنى |
|---|---|---|
| `useDocs` | `"dev"` | حيث يتم تقديم الصفحة المرجعية Scalar و `/openapi.json`: `"dev"` على `nx dev` فقط، `True` في الإنتاج أيضًا (يسرد المخطط كل مسار وإجراء خادم)، `False` في أي مكان |
| `useDocsUrl` | `"/docs"` | مسار الصفحة المرجعية لواجهة برمجة التطبيقات |
| `useRedocsUrl` | `"/redocs"` | تم الإعلان عنه ولكن لم يتم تثبيت أي طريق |
| `useTitle` | `"Nexy App"` | OpenAPI العنوان وعنوان الصفحة (`"Nexy"` في `NexyConfigModel`) |

### مجاناً `/docs` لصفحة من المشروع

يجيب مرجع واجهة برمجة التطبيقات (API) على `/docs` قبل أي مسار، لذلك لا يتم عرض `src/routes/docs.nexy` أو `src/routes/docs/[[...slug]].nexy` هناك أبدًا. `nx dev` و `nx start` تسمية مثل هذه الصفحة عند بدء التشغيل. انقل المرجع بـ `useDocsUrl`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useDocsUrl = "/api-reference"
```

أو قم بإيقاف تشغيله باستخدام `useDocs = False`، والذي يتوقف أيضًا عن الخدمة `/openapi.json`. أثناء تشغيل المرجع، احتفظ بمسارات المشروع بعيدًا عن هذا المسار.

## الوسيطة

| الميدان | الافتراضي | معنى |
|---|---|---|
| `useMiddlewares` | `[]` | فئات البرمجيات الوسيطة ASGI |
| `useCORS` | `None` | كوارج ل `CORSMiddleware` |
| `useGZip` | `None` | كوارج ل `GZipMiddleware` |
| `useTrustedHost` | `None` | كوارج ل `TrustedHostMiddleware` |
| `useSession` | `None` | كوارج ل `SessionMiddleware` |
| `useAuth` | `None` | تكوين البرامج الوسيطة للمصادقة |
| `useHTTPSRedirect` | `False` | إعادة توجيه HTTP إلى HTTPS |

## Markdown

| الميدان | الافتراضي | معنى |
|---|---|---|
| `useTocDepth` | `"2-6"` | مستويات العناوين المدرجة في جدول المحتويات |
| `useTocTitle` | `"Table of Contents"` | عنوان جدول المحتويات |
| `useTocAuto` | `True` | إنشاء جدول محتويات لـ Markdown صفحة |

## الطرق خارج شجرة الملفات

قم ببناء FastAPI `APIRouter` وتركيبه بـ `useRouter`. يتم تقديمه بجوار المسارات المستندة إلى الملف:

```python filename="nexyconfig.py"
from fastapi import APIRouter
from nexy.core.models import NexyConfigModel

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


class NexyConfig(NexyConfigModel):
    useRouter = router
```

تتم قراءة الإعدادات الافتراضية أعلاه من `nexy/core/config.py`.

## أعلن، لم يقرأ بعد

هذه الحقول موجودة في `NexyConfigModel` ولكن لا يوجد كود يستهلكها. إعدادها ليس له أي تأثير:

`useViteDevUrl`، `useRTL`.

## الخطوات التالية

- [i18n](../guides/i18n.md): التدويل
- [الواجهة الأمامية](../guides/frontend.md): `useFF` وبناء العميل
- [النشر](../deployment/README.md): خيارات الإنتاج
