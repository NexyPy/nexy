# ترتیب

کنفیگریشن پروجیکٹ کی جڑ میں `nexyconfig.py` میں ایک کلاس ہے۔ Nexy اسے اس ڈائریکٹری سے لوڈ کرتا ہے جس میں یہ چلتی ہے۔ فائل کے بغیر ایک پروجیکٹ ڈیفالٹس کا استعمال کرتا ہے۔

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    usePort = 3000
    useTitle = "My App"
    useAliases = {"@": "src"}
```

## سرور

| فیلڈ | ڈیفالٹ | معنی |
|---|---|---|
| `usePort` | `3000` | بندرگاہ `dev` اور `start` |
| `useHost` | `"0.0.0.0"` | پتہ کا پابند |
| `useSslKeyfile`، `useSslCertfile` | `None` | HTTPS کو براہ راست پیش کرتے ہیں |
| `useDevTools` | `True` | ٹول بار `nexy dev` ہر صفحہ میں اضافہ کرتا ہے (صفحہ کی معلومات، راستے، غلطیاں، تشکیل)؛ `False` اسے ہٹاتا ہے۔ پیداوار میں کبھی موجود نہیں |
| `useWorkers` | `0` | عمل `nx start` رنز؛ `0` لینکس اور میک او ایس پر ایک فی سی پی یو ہے، ونڈوز پر ایک |
| `useCSR` | `False` | کلائنٹ سائیڈ روٹنگ موڈ؛ `.nexy` راستے غیر فعال ہیں |

## راستے

| فیلڈ | ڈیفالٹ | معنی |
|---|---|---|
| `useRouter` | `None` | ایک `APIRouter` مثال یا کلاس فائل پر مبنی راستوں کے ساتھ نصب؛ `None` کا مطلب صرف فائل پر مبنی ہے |
| راستوں کو اسکین کرتے وقت `excludeDirs` | `["templates", "extension", "docs"]` | ڈائریکٹریز کو چھوڑ دیا گیا |
| `useAliases` | `None` | عرفی نام درآمد کریں، جیسے `{"@": "src"}` (`@/components/Counter.tsx` کا مطلب ہے `src/components/Counter.tsx`)؛ `nx new` جسے آپ نے منتخب کیا ہے لکھتا ہے، اور Vite اور `tsconfig.json` اس کی پیروی کرتا ہے |

## فرنٹ اینڈ

| فیلڈ | ڈیفالٹ | معنی |
|---|---|---|
| `useFF` | `None` | کلائنٹ فریم ورک فیکٹری: `react()`، `vue()`، `svelte()`، `solid()`، `preact()` |
| `useVite` | `True` | Vite | کے ساتھ کلائنٹ بنڈل بنائیں اور پیش کریں۔
| `useMarkdownExtensions` | `[]` | اضافی ایکسٹینشنز `.md`/`.mdx` رینڈرنگ |
| `useWatchExtensions` | `None` | اضافی ایکسٹینشن دیو سرور دیکھتا ہے |
| `useWatchExcludePatterns` | `None` | گلوب پیٹرن جنہیں دیو سرور نظر انداز کرتا ہے |

> **جاننا اچھا ہے**: `NexyConfigModel` اعلان کرتا ہے `useVite = False`؛ رن ٹائم `Config` ڈیفالٹ `True` ہے۔

## محفوظ فائل کے نام

ہر فیلڈ ایک مخصوص کردار میں توسیعات کا اضافہ کرتا ہے۔ `useLayoutExtensions = ["md"]` `layout.md` کو مخصوص بناتا ہے، بالکل `layout.nexy` کی طرح۔

| فیلڈ | ایکسٹینشنز کو | میں شامل کرتا ہے۔
|---|---|
| `useLayoutExtensions` | `layout.*` |
| `useNotFoundExtensions` | `notfound.*` |
| `useErrorsExtensions` | `errors.*` |
| `useForbiddenExtensions` | `forbidden.*` |
| `useUnauthorizedExtensions` | `unauthorized.*` |
| `useLoadingExtensions` | `loading.*` |

## API دستاویزات

| فیلڈ | ڈیفالٹ | معنی |
|---|---|---|
| `useDocs` | `True` | OpenAPI اسکیما اور اس کے اسکیلر حوالہ صفحہ | کی خدمت کریں۔
| `useDocsUrl` | `"/docs"` | API حوالہ صفحہ کا راستہ |
| `useRedocsUrl` | `"/redocs"` | اعلان کیا گیا لیکن کوئی راستہ نہیں لگایا گیا |
| `useTitle` | `"Nexy App"` | OpenAPI عنوان اور صفحہ کا عنوان (`"Nexy"` `NexyConfigModel`] میں) |

## مڈل ویئر

| فیلڈ | ڈیفالٹ | معنی |
|---|---|---|
| `useMiddlewares` | `[]` | ASGI مڈل ویئر کلاسز |
| `useCORS` | `None` | `CORSMiddleware` |
| `useGZip` | `None` | `GZipMiddleware` |
| `useTrustedHost` | `None` | `TrustedHostMiddleware` |
| `useSession` | `None` | `SessionMiddleware` |
| `useAuth` | `None` | توثیق مڈل ویئر کی تشکیل |
| `useHTTPSRedirect` | `False` | HTTPS کو HTTPS |

## Markdown

| فیلڈ | ڈیفالٹ | معنی |
|---|---|---|
| `useTocDepth` | `"2-6"` | عنوانات کی سطح مندرجات کے جدول میں شامل ہیں |
| `useTocTitle` | `"Table of Contents"` | TOC عنوان |
| `useTocAuto` | `True` | Markdown صفحات | کے لیے مندرجات کا جدول تیار کریں۔

## فائل ٹری سے باہر کے راستے

ایک FastAPI `APIRouter` بنائیں اور اسے `useRouter` کے ساتھ چڑھائیں۔ یہ فائل پر مبنی راستوں کے آگے پیش کیا جاتا ہے:

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

اوپر ڈیفالٹس `nexy/core/config.py` سے پڑھے جاتے ہیں۔

## اعلان کیا، ابھی پڑھا نہیں۔

یہ فیلڈز `NexyConfigModel` میں موجود ہیں لیکن کوئی کوڈ انہیں استعمال نہیں کرتا۔ ان کی ترتیب کا کوئی اثر نہیں ہے:

`useViteDevUrl`، `useRTL`۔

## اگلے اقدامات

- [i18n](../guides/i18n.md): بین الاقوامی کاری
- [فرنٹ اینڈ](../guides/frontend.md): `useFF` اور کلائنٹ کی تعمیر
- [تعینات](../deployment/README.md): پیداوار کے اختیارات
