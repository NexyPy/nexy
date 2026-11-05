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

## HTTPS

HTTPS کو براہ راست `useSslKeyfile` اور `useSslCertfile` کے ساتھ پیش کریں، یا TLS کو ریورس پراکسی پر ختم کریں اور `useHTTPSRedirect` سیٹ کریں۔ ترقی میں Vite دیو سرور Nexy اصل کے پیچھے لوپ بیک HTTP پر رہتا ہے، لہذا TLS کبھی بھی اس تک نہیں پہنچتا۔

## پروڈکشن چیک لسٹ

- `useDocs = False` اگر OpenAPI اسکیما عوامی نہیں ہونا چاہئے۔
- `useTrustedHost` میزبان ہیڈر حملوں کو روکنے کے لیے، آپ کے ڈومینز پر سیٹ کریں۔
- `useCORS` واضح ماخذ کے ساتھ، کبھی بھی `["*"]` اسناد کے ساتھ۔
- سیشنز کے لیے ایک حقیقی `secret_key`، ماحول سے پڑھیں۔
- کلائنٹ کے اجزاء کو بھیجے گئے پروپس Nexy کے ذریعہ HTML سے بچ گئے ہیں۔ ٹیمپلیٹس میں صارف کے ان پٹ `| safe` کو نشان زد نہ کریں۔

## محافظ اور انحصار

فی روٹ تحفظ FastAPI انحصار استعمال کرتا ہے۔ روٹس ڈائرکٹری میں ایک `dependencies.py` اس کے نیچے ہر چیز پر لاگو ہوتا ہے: دیکھیں [انحصار](../routing/fbr/dependencies/README.md)۔ ماڈیولر راؤٹر میں [`@UseGuard`](../routing/modular/guards-and-metadata.md) کا استعمال کریں۔

## اگلے اقدامات

- [کنفیگ ](../reference/config.md): ہر مڈل ویئر فیلڈ
- [تعیناتی ](../deployment/README.md)
- [کارکردگی ](../deployment/performance.md)
