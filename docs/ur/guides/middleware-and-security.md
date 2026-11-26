# مڈل ویئر اور سیکیورٹی

Nexy FastAPI اور Starlette پر چلتا ہے، لہذا ان کا مڈل ویئر لاگو ہوتا ہے۔ عام والے `nexyconfig.py` میں ایک لائن ہیں۔

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {
        "allow_origins": ["https://app.example.com"],
        "allow_methods": ["GET", "POST"],
        "allow_credentials": True,
    }
    useGZip = {"minimum_size": 1000}
    useTrustedHost = {"allowed_hosts": ["example.com", "*.example.com"]}
    useHTTPSRedirect = True
    useSession = {"secret_key": "change-me"}
```

ہر `use*` لغت کو مطلوبہ الفاظ کے دلائل کے طور پر مماثل Starlette مڈل ویئر کے لیے پاس کیا جاتا ہے: `CORSMiddleware`، `GZipMiddleware`، `TrustedHostMiddleware`، `SessionMiddleware`۔

## آپ کا اپنا مڈل ویئر

```python filename="nexyconfig.py"
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` ASGI مڈل ویئر کی کلاس لیتا ہے۔

## شرح کو محدود کرنا

`useRateLimit` کلائنٹ کے ایڈریس کا جواب `429 Too Many Requests` دیتا ہے جو `per` سیکنڈ کی ایک ونڈو میں `requests` سے زیادہ درخواستیں بھیجتا ہے۔

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useRateLimit = {"requests": 60, "per": 60, "paths": ["/api/", "/_nx_"]}
```

Nexy اس بات کی ضمانت دیتا ہے کہ حد سے زیادہ درخواست کو `Retry-After` ہیڈر کے ساتھ ایک `429` ملتا ہے، جو ونڈو میں باقی رہ جاتے ہیں، اور کبھی بھی آپ کے راستوں، اعمال یا مڈل ویئر تک نہیں پہنچتے ہیں۔

Nexy اس بات کی ضمانت دیتا ہے کہ `useRateLimit` کے بغیر کوئی شرح کی حد مڈل ویئر کو شامل نہیں کیا جائے گا۔

Nexy اس بات کی ضمانت دیتا ہے کہ `useHealth` تحقیقات کبھی محدود نہیں ہوتیں۔

`paths` اختیاری ہے: اس کے بغیر ہر راستہ محدود ہے۔ سرور کے اعمال `/_nx_` کے تحت پیش کیے جاتے ہیں، تاکہ یہ سابقہ ​​ان سب کو محدود کر دے۔

ونڈو کو تمام کلائنٹس کے ذریعہ طے کیا گیا ہے اور اس کا اشتراک کیا گیا ہے: گنتی `per` سیکنڈ کے ہر ایک سے دوبارہ شروع ہوتی ہے۔ لہذا ایک کلائنٹ ونڈو کے کنارے پر دو بار `requests` بھیج سکتا ہے۔

شمار ہر کارکن کی یاد میں رہتا ہے۔ اوپر والے `useWorkers` کے ساتھ، ایک کلائنٹ ہر کارکن کو `requests` بھیج سکتا ہے، اور سرور کے دوبارہ شروع ہونے پر گنتی دوبارہ شروع ہو جاتی ہے۔

کلائنٹ کا پتہ وہی ہے جو یوویکورن درخواست دیتا ہے۔ اسی مشین پر ایک ریورس پراکسی کے پیچھے، یوویکورن اسے `X-Forwarded-For` سے پڑھتا ہے؛ دوسری مشین پر پراکسی کے لیے، اس کا پتہ `FORWARDED_ALLOW_IPS` ماحولیاتی متغیر میں درج کریں، یا ہر کلائنٹ پراکسی کا پتہ شیئر کرتا ہے۔

آپ کی درخواست متعدد کارکنوں یا سرورز کے اشتراک کردہ حد کے لیے ذمہ دار ہے: ایک ریورس پراکسی یا اسٹور جیسے Redis۔

## HTTPS

HTTPS کو براہ راست `useSslKeyfile` اور `useSslCertfile` کے ساتھ پیش کریں، یا TLS کو ریورس پراکسی پر ختم کریں اور `useHTTPSRedirect` سیٹ کریں۔ ترقی میں Vite دیو سرور Nexy اصل کے پیچھے لوپ بیک HTTP پر رہتا ہے، لہذا TLS کبھی بھی اس تک نہیں پہنچتا۔

## پروڈکشن چیک لسٹ

- `useDocs = False` اگر OpenAPI اسکیما کو عوامی نہیں ہونا چاہئے۔
- `useTrustedHost` میزبان ہیڈر حملوں کو روکنے کے لیے، آپ کے ڈومینز پر سیٹ کریں۔
- `useCORS` واضح ماخذ کے ساتھ، کبھی بھی `["*"]` اسناد کے ساتھ۔
- سیشنز کے لیے ایک حقیقی `secret_key`، ماحول سے پڑھیں۔
- Props کلائنٹ کے اجزاء کو منتقل کیا جاتا ہے جو Nexy کے ذریعہ HTML سے بچ جاتا ہے۔ ٹیمپلیٹس میں صارف کے ان پٹ `| safe` کو نشان زد نہ کریں۔

## محافظ اور انحصار

فی روٹ تحفظ FastAPI انحصار استعمال کرتا ہے۔ روٹس ڈائرکٹری میں ایک `dependencies.py` اس کے نیچے ہر چیز پر لاگو ہوتا ہے: دیکھیں [انحصار](../routing/fbr/dependencies/README.md)۔ ماڈیولر راؤٹر میں [`@UseGuard`](../routing/modular/guards-and-metadata.md) کا استعمال کریں۔

## اگلے اقدامات

- [کنفیگ ](../reference/config.md): ہر مڈل ویئر فیلڈ
- [تعیناتی ](../deployment/README.md)
- [کارکردگی ](../deployment/performance.md)
