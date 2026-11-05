# الوسيطة والأمن

يعمل Nexy على FastAPI و Starlette، لذا تنطبق برمجياتهم الوسيطة. والمشترك منها سطر واحد في `nexyconfig.py`.

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

يتم تمرير كل قاموس `use*` كوسائط كلمات رئيسية إلى البرامج الوسيطة Starlette المطابقة: `CORSMiddleware`، `GZipMiddleware`، `TrustedHostMiddleware`، `SessionMiddleware`.

## الوسيطة الخاصة بك

```python filename="nexyconfig.py"
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` يأخذ دروس ASGI الوسيطة.

## HTTPS

قم بخدمة HTTPS مباشرةً باستخدام `useSslKeyfile` و `useSslCertfile`، أو قم بإنهاء TLS في وكيل عكسي وقم بتعيين `useHTTPSRedirect`. أثناء التطوير، يظل خادم التطوير Vite على استرجاع HTTP خلف أصل Nexy، لذلك لا يصل إليه TLS أبدًا.

## قائمة مرجعية الإنتاج

- `useDocs = False` إذا كان مخطط OpenAPI لا يجب أن يكون عامًا.
- `useTrustedHost` تم تعيينه على نطاقاتك لمنع هجمات رأس المضيف.
- `useCORS` بأصول صريحة، لا `["*"]` أبدًا مع بيانات الاعتماد.
- حقيقي `secret_key` لجلسات القراءة من البيئة.
- الدعائم التي تم تمريرها إلى مكونات العميل تم تجاوزها من خلال HTML بواسطة Nexy. لا تضع علامة على إدخال المستخدم `| safe` في القوالب.

## الحراس والتبعيات

تستخدم الحماية لكل مسار تبعيات FastAPI. ينطبق `dependencies.py` في دليل المسارات على كل شيء تحته: راجع [التبعيات](../routing/fbr/dependencies/README.md). في جهاز التوجيه المعياري، استخدم [`@UseGuard`](../routing/modular/guards-and-metadata.md).

## الخطوات التالية

- [التكوين](../reference/config.md): كل حقل برمجي وسيط
- [نشر](../deployment/README.md)
- [الأداء](../deployment/performance.md)
