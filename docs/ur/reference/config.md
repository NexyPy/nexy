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

| میدان | طے شدہ | مطلب |
|---|---|---|
| `usePort` | `3000` | `dev` اور `start` کے لیے بندرگاہ |
| `useHost` | `"0.0.0.0"` | پتہ باندھنا |
| `useSslKeyfile`، `useSslCertfile` | `None` | HTTPS کو براہ راست پیش کریں۔ |
| `useDevTools` | `True` | ٹول بار `nexy dev` ہر صفحہ میں اضافہ کرتا ہے (صفحہ کی معلومات، راستے، غلطیاں، تشکیل)؛ `False` اسے ہٹاتا ہے۔ پروڈکشن میں کبھی موجود نہ ہوں۔ |
| `useWorkers` | `0` | عمل `nx start` چلتا ہے؛ `0` لینکس اور میک او ایس پر ایک فی سی پی یو ہے، ونڈوز پر ایک |
| `useCSR` | `False` | کلائنٹ سائڈ روٹنگ موڈ؛ `.nexy` راستے غیر فعال ہیں۔ |

## راستے

| میدان | طے شدہ | مطلب |
|---|---|---|
| `useRouter` | `None` | ایک `APIRouter` مثال یا کلاس فائل پر مبنی راستوں کے ساتھ لگائی گئی ہے۔ `None` کا مطلب صرف فائل پر مبنی ہے۔ |
| `excludeDirs` | `["templates", "extension", "docs"]` | راستوں کو اسکین کرتے وقت ڈائریکٹریز کو چھوڑ دیا گیا۔ |
| `useAliases` | `None` | عرفی نام درآمد کریں، جیسے `{"@": "src"}` (`@/components/Counter.tsx` کا مطلب ہے `src/components/Counter.tsx`)؛ `nx new` جسے آپ نے منتخب کیا ہے لکھتا ہے، اور Vite اور `tsconfig.json` اس کی پیروی کرتا ہے |

## فرنٹ اینڈ

| میدان | طے شدہ | مطلب |
|---|---|---|
| `useFF` | `None` | کلائنٹ فریم ورک فیکٹری: `react()`، `vue()`، `svelte()`، `solid()`، `preact()` |
| `useVite` | `True` | Vite کے ساتھ کلائنٹ بنڈل بنائیں اور پیش کریں |
| `useMarkdownExtensions` | `[]` | `.md`/`.mdx` رینڈرنگ کے لیے اضافی ایکسٹینشنز |
| `useWatchExtensions` | `None` | اضافی ایکسٹینشنز جو ڈیو سرور دیکھتا ہے۔ |
| `useWatchExcludePatterns` | `None` | گلوب پیٹرن جنہیں ڈیو سرور نظر انداز کرتا ہے۔ |

> **جاننا اچھا ہے**: `NexyConfigModel` اعلان کرتا ہے `useVite = False`؛ رن ٹائم `Config` ڈیفالٹ `True` ہے۔

## محفوظ فائل کے نام

ہر فیلڈ ایک مخصوص کردار میں توسیعات کا اضافہ کرتا ہے۔ `useLayoutExtensions = ["md"]` `layout.md` کو مخصوص بناتا ہے، بالکل `layout.nexy` کی طرح۔

| میدان | میں توسیعات شامل کرتا ہے۔ |
|---|---|
| `useLayoutExtensions` | `layout.*` |
| `useNotFoundExtensions` | `notfound.*` |
| `useErrorsExtensions` | `errors.*` |
| `useForbiddenExtensions` | `forbidden.*` |
| `useUnauthorizedExtensions` | `unauthorized.*` |
| `useLoadingExtensions` | `loading.*` |

## API دستاویزات

| میدان | طے شدہ | مطلب |
|---|---|---|
| `useDocs` | `True` | OpenAPI اسکیما اور اس کے اسکیلر حوالہ صفحہ کی خدمت کریں۔ |
| `useDocsUrl` | `"/docs"` | API حوالہ صفحہ کا راستہ |
| `useRedocsUrl` | `"/redocs"` | اعلان کیا گیا ہے لیکن کوئی راستہ نہیں لگایا گیا ہے۔ |
| `useTitle` | `"Nexy App"` | OpenAPI عنوان اور صفحہ کا عنوان (`"Nexy"` `NexyConfigModel` میں) |

## مڈل ویئر

| میدان | طے شدہ | مطلب |
|---|---|---|
| `useMiddlewares` | `[]` | ASGI مڈل ویئر کلاسز |
| `useCORS` | `None` | `CORSMiddleware` کے لیے kwargs |
| `useGZip` | `None` | `GZipMiddleware` کے لیے کوارگز |
| `useTrustedHost` | `None` | `TrustedHostMiddleware` کے لیے kwargs |
| `useSession` | `None` | `SessionMiddleware` کے لیے کوارگز |
| `useAuth` | `None` | توثیق مڈل ویئر کی تشکیل |
| `useHTTPSRedirect` | `False` | HTTP کو HTTPS پر ری ڈائریکٹ کریں۔ |

## Markdown

| میدان | طے شدہ | مطلب |
|---|---|---|
| `useTocDepth` | `"2-6"` | مندرجات کے جدول میں سرخی کی سطحیں شامل ہیں۔ |
| `useTocTitle` | `"Table of Contents"` | TOC عنوان |
| `useTocAuto` | `True` | Markdown صفحات کے لیے مندرجات کا جدول تیار کریں۔ |

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
