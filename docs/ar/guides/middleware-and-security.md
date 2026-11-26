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

## الحد من المعدل

`useRateLimit` يجيب `429 Too Many Requests` على عنوان العميل الذي يرسل أكثر من `requests` طلب في نافذة واحدة مدتها `per` ثانية.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useRateLimit = {"requests": 60, "per": 60, "paths": ["/api/", "/_nx_"]}
```

يضمن Nexy أن الطلب الذي يتجاوز الحد سيحصل على `429` برأس `Retry-After`، والثواني المتبقية في النافذة، ولن يصل أبدًا إلى مساراتك أو إجراءاتك أو برامجك الوسيطة.

يضمن Nexy أنه بدون `useRateLimit` لا تتم إضافة أي برامج وسيطة ذات حد للمعدل.

يضمن Nexy أن مجسات `useHealth` ليست محدودة أبدًا.

`paths` اختيارية: بدونها كل طريق محدود. يتم تقديم إجراءات الخادم ضمن `/_nx_`، بحيث تحدد هذه البادئة جميعها.

تم إصلاح النافذة ومشاركتها من قبل جميع العملاء: تبدأ عمليات التعداد مرة أخرى عند كل مضاعفات `per` ثانية. وبالتالي يمكن للعميل إرسال ما يصل إلى مرتين `requests` عبر حافة النافذة.

التهم تعيش في ذاكرة كل عامل. مع وجود `useWorkers` فوق واحد، يمكن للعميل إرسال `requests` إلى كل عامل، وتبدأ عمليات العد مرة أخرى عند إعادة تشغيل الخادم.

عنوان العميل هو العنوان الوحيد الذي يقدمه uvicorn للطلب. خلف الوكيل العكسي على نفس الجهاز، يقرأه uvicorn من `X-Forwarded-For`؛ بالنسبة للوكيل الموجود على جهاز آخر، قم بإدراج عنوانه في متغير البيئة `FORWARDED_ALLOW_IPS`، أو يشارك كل عميل عنوان الوكيل.

تطبيقك مسؤول عن الحد المشترك بين العديد من العاملين أو الخوادم: وكيل عكسي أو متجر مثل Redis.

## HTTPS

قم بخدمة HTTPS مباشرة مع `useSslKeyfile` و `useSslCertfile`، أو قم بإنهاء TLS في وكيل عكسي وقم بتعيين `useHTTPSRedirect`. أثناء التطوير، يظل خادم التطوير Vite على استرجاع HTTP خلف أصل Nexy، لذلك لا يصل إليه TLS أبدًا.

## قائمة مرجعية الإنتاج

- `useDocs = False` إذا كان مخطط OpenAPI لا يجب أن يكون عامًا.
- `useTrustedHost` تم تعيينه على نطاقاتك لمنع هجمات رأس المضيف.
- `useCORS` بأصول صريحة، أبدًا `["*"]` مع بيانات الاعتماد.
- حقيقي `secret_key` لجلسات القراءة من البيئة.
- Props تم تمريرها إلى مكونات العميل والتي تم تجاوزها بـ HTML بواسطة Nexy. لا تضع علامة على إدخال المستخدم `| safe` في القوالب.

## الحراس والتبعيات

تستخدم الحماية لكل مسار تبعيات FastAPI. ينطبق `dependencies.py` في دليل المسارات على كل شيء تحته: راجع [التبعيات](../routing/fbr/dependencies/README.md). في جهاز التوجيه المعياري، استخدم [`@UseGuard` ](../routing/modular/guards-and-metadata.md).

## الخطوات التالية

- [التكوين](../reference/config.md): كل حقل برمجي وسيط
- [نشر](../deployment/README.md)
- [الأداء](../deployment/performance.md)
