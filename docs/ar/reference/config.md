# التكوين

التكوين هو فئة في `nexyconfig.py` في جذر المشروع. يقوم Nexy بتحميله من الدليل
يعمل في؛ يستخدم المشروع بدون الملف الإعدادات الافتراضية.

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

| الحقل | الافتراضي | المعنى |
|---|---|---|
| `usePort` | `3000` | منفذ لـ `dev` و `start` |
| `useHost` | `"0.0.0.0"` | عنوان الربط |
| `useSslKeyfile`، `useSslCertfile` | `None` | يخدم HTTPS مباشرة |
| `useDevTools` | `True` | يضيف شريط الأدوات `nexy dev` إلى كل صفحة (معلومات الصفحة، والمسارات، والأخطاء، والتكوين)؛ `False` يزيله. لم يسبق له مثيل في الإنتاج |
| `useWorkers` | `0` | يعمل على تشغيل `nx start`؛ `0` هو واحد لكل وحدة معالجة مركزية على Linux وmacOS، وواحد على Windows |
| `useCSR` | `False` | وضع التوجيه من جانب العميل؛ `.nexy` الطرق معطلة |

## الطرق

| الحقل | الافتراضي | المعنى |
|---|---|---|
| `useRouter` | `None` | مثيل أو فئة `APIRouter` مثبتة بجوار المسارات المستندة إلى الملف؛ `None` يعني المستند إلى الملف فقط |
| `excludeDirs` | `["templates", "extension", "docs"]` | تم تخطي الدلائل عند مسح المسارات |
| `useAliases` | `None` | استيراد الأسماء المستعارة، على سبيل المثال. `{"@": "src"}` (`@/components/Counter.tsx` يعني `src/components/Counter.tsx`)؛ `nx new` يكتب الذي اخترته، وفيت و`tsconfig.json` يتبعه |

## الواجهة الأمامية

| الحقل | الافتراضي | المعنى |
|---|---|---|
| `useFF` | `None` | مصنع إطار العميل: `react()`، `vue()`، `svelte()`، `solid()`، `preact()` |
| `useVite` | `True` | إنشاء حزم العملاء وخدمتها باستخدام Vite |
| `useMarkdownExtensions` | `[]` | ملحقات إضافية لعرض `.md`/`.mdx` |
| `useWatchExtensions` | `None` | ملحقات إضافية يشاهدها خادم التطوير |
| `useWatchExcludePatterns` | `None` | أنماط الكرة الأرضية التي يتجاهلها خادم التطوير |

> **من المفيد أن نعرف**: `NexyConfigModel` يعلن `useVite = False`؛ وقت التشغيل `Config` الافتراضي هو
> `True`.

## أسماء الملفات المحجوزة

يضيف كل حقل ملحقات إلى دور محجوز. `useLayoutExtensions = ["md"]` يجعل `layout.md`
محجوز، تمامًا مثل `layout.nexy`.

| الحقل | إضافة الامتدادات إلى |
|---|---|
| `useLayoutExtensions` | `layout.*` |
| `useNotFoundExtensions` | `notfound.*` |
| `useErrorsExtensions` | `errors.*` |
| `useForbiddenExtensions` | `forbidden.*` |
| `useUnauthorizedExtensions` | `unauthorized.*` |
| `useLoadingExtensions` | `loading.*` |

## وثائق واجهة برمجة التطبيقات

| الحقل | الافتراضي | المعنى |
|---|---|---|
| `useDocs` | `True` | يخدم مخطط OpenAPI والصفحة المرجعية الخاصة به |
| `useDocsUrl` | `"/docs"` | مسار الصفحة المرجعية لواجهة برمجة التطبيقات |
| `useRedocsUrl` | `"/redocs"` | تم الإعلان عنه ولكن لم يتم تثبيت أي طريق |
| `useTitle` | `"Nexy App"` | عنوان OpenAPI وعنوان الصفحة (`"Nexy"` في `NexyConfigModel`) |

## الوسيطة

| الحقل | الافتراضي | المعنى |
|---|---|---|
| `useMiddlewares` | `[]` | فئات البرمجيات الوسيطة ASGI |
| `useCORS` | `None` | كوارج لـ `CORSMiddleware` |
| `useGZip` | `None` | كوارج لـ `GZipMiddleware` |
| `useTrustedHost` | `None` | كوارج لـ `TrustedHostMiddleware` |
| `useSession` | `None` | كوارج لـ `SessionMiddleware` |
| `useAuth` | `None` | تكوين البرامج الوسيطة للمصادقة |
| `useHTTPSRedirect` | `False` | إعادة توجيه HTTP إلى HTTPS |

##  تخفيض السعر

| الحقل | الافتراضي | المعنى |
|---|---|---|
| `useTocDepth` | `"2-6"` | مستويات العناوين المدرجة في جدول المحتويات |
| `useTocTitle` | `"Table of Contents"` | عنوان جدول المحتويات |
| `useTocAuto` | `True` | إنشاء جدول محتويات صفحات Markdown |

## المسارات خارج شجرة الملفات

أنشئ FastAPI `APIRouter` وقم بتثبيته باستخدام `useRouter`. يتم تقديمه بجانب المستند إلى الملف
الطرق:

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

## أعلن ولم يقرأ بعد

هذه الحقول موجودة في `NexyConfigModel` ولكن لا يوجد كود يستهلكها. إعدادها ليس له أي تأثير:

`useViteDevUrl`، `useRTL`.

## الخطوات التالية

- [i18n](../guides/i18n.md): التدويل
- [الواجهة الأمامية](../guides/frontend.md): `useFF` وبناء العميل
-  [النشر](../deployment/README.md)]: خيارات الإنتاج