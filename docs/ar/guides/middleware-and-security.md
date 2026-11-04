# البرمجيات الوسيطة والأمن

يعمل Nexy على FastAPI وStarlette، لذا تنطبق برامجهم الوسيطة. المشتركة هي سطر واحد في
`nexyconfig.py`.

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

يتم تمرير كل قاموس `use*` كوسائط كلمات رئيسية إلى برنامج Starlette الوسيط المطابق:
`CORSMiddleware`، `GZipMiddleware`، `TrustedHostMiddleware`، `SessionMiddleware`.

## الوسيطة الخاصة بك

```python filename="nexyconfig.py"
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` يأخذ دروس ASGI الوسيطة.

## HTTPS

قم بخدمة HTTPS مباشرةً باستخدام `useSslKeyfile` و`useSslCertfile`، أو قم بإنهاء TLS عبر وكيل عكسي
وتعيين `useHTTPSRedirect`. أثناء التطوير، يظل خادم Vite dev على استرجاع HTTP خلف
أصل Nexy، لذلك لا يصل إليه TLS أبدًا.

## قائمة مرجعية للإنتاج

- `useDocs = False` إذا لم يكن مخطط OpenAPI عامًا.
-  `useTrustedHost` تم تعيينها على النطاقات الخاصة بك، لمنع هجمات رأس المضيف.
- `useCORS` بأصول صريحة، أبدًا `["*"]` مع بيانات الاعتماد.
- `secret_key` حقيقي للجلسات، اقرأها من البيئة.
- الدعائم التي تم تمريرها إلى مكونات العميل تم تجاوزها باستخدام HTML بواسطة Nexy. لا تضع علامة على إدخال المستخدم `| safe` في
  قوالب.

##  الحراسة والتبعيات

تستخدم الحماية لكل مسار تبعيات FastAPI. ينطبق `dependencies.py` في دليل الطرق على
كل ما تحته: انظر [التبعيات](../routing/fbr/dependencies/README.md). في استخدام جهاز التوجيه وحدات
[`@UseGuard`](../routing/modular/guards-and-metadata.md).

## الخطوات التالية

- [التكوين](../reference/config.md): كل حقل من حقول البرمجيات الوسيطة
-  [نشر](../deployment/README.md)
- [الأداء](../deployment/performance.md)