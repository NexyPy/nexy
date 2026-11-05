# ملفات الوسيطة

يقوم `middleware.py` في دليل المسارات بتغليف الطلبات التي يعالجها هذا الدليل. مثل التخطيطات و `dependencies.py`، يتم تجميع الملفات من المسارات من الجذر إلى الأسفل، والأبعد أولاً.

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request
from nexy.http import JSONResponse


async def middleware(request: Request, call_next):
    if request.headers.get("authorization") != "Bearer secret":
        return JSONResponse({"detail": "login required"}, status_code=401)
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

الدالة `async def middleware(request, call_next)`: توقيع FastAPI على `@app.middleware("http")`. اتصل بـ `await call_next(request)` للاستمرار في المسار، أو قم بإرجاع الرد للتوقف عند هذا الحد. رمز بعد تشغيل المكالمة في طريق الخروج ويمكن تغيير الرد.

## ما يغلفه

تنطبق البرامج الوسيطة على **المسارات التي يوجد ملفها في دليلها** أو أدناه، والصفحات ومعالجات واجهة برمجة التطبيقات على حد سواء، بما في ذلك مجموعات المسارات:

```text
src/routes/
├─ middleware.py             every route
├─ open.py                   root only
├─ admin/
│  ├─ middleware.py          /admin and everything below
│  └─ users/
│     ├─ middleware.py       /admin/users and below
│     └─ index.py            root > admin > users
└─ (shop)/
   ├─ middleware.py          only the routes in this group
   └─ cart.py                root > shop     (URL: /cart)
```

أما بالنسبة للطلب إلى `/admin/users` فالأمر هو `root`، `admin`، `users`، ثم الطريق. لا تحتوي المجموعة على عنوان URL خاص بها، لذا تتم مطابقتها من خلال المسار الذي يخدم الطلب، وليس من خلال عنوان URL.

عنوان URL الذي لا يطابق أي مسار (404) يتلقى فقط البرامج الوسيطة للأدلة التي ليست مجموعات، والتي يتم تحديدها بواسطة بادئة عنوان URL. `[slug]` يطابق مقطعًا واحدًا ويطابق `[...rest]` الباقي.

## ما لا التفاف

- عناوين URL للإطار والأصول: `/__nexy__/`، `/_nexy/`، `/public/`، `/assets/` و `/@...` (Vite).
- WebSocket المعالجات وعمر الخادم: طلبات HTTP فقط.
- الملفات في الدلائل التي تبدأ بـ `_` أو `.`.

## البرمجيات الوسيطة أو التبعيات أو الحراس

| استخدم | عندما |
|---|---|
| `middleware.py` | أنت بحاجة إلى **الاستجابة** أيضًا: الرؤوس، وعمليات إعادة التوجيه، والتوقيت، وقصر الدائرة الكهربائية لمنطقة بأكملها |
| [`dependencies.py`](../dependencies/README.md) | تحتاج إلى معلمات محللة أو لإدخال قيمة (المستخدم الحالي، جلسة قاعدة البيانات) |
| `@UseGuard` على المعالج | يحتاج مسار واحد إلى فحص إضافي |
| `useMiddlewares` في [الإعداد](../../../reference/config.md) | برنامج ASGI الوسيط للتطبيق بأكمله (CORS، GZip، الجلسات) |

تعمل ملفات البرامج الوسيطة **قبل** من التبعيات: لقد مرر الطلب كل `middleware.py` من أدلةه عند بدء التبعيات.

## القواعد

- يجب أن يحدد الملف `async def middleware(request, call_next)`. وإلا فإن Nexy يتوقف عند بدء التشغيل ويقوم بتسمية الملف.
- إنها وحدة Python عادية: قم باستيراد ما تحتاجه. يتم تحميله مرة واحدة، عند بدء تشغيل الخادم.
- إنه ليس طريقًا أبدًا: `/middleware` هو 404.
- يتم فحص المسار الأساسي على `request.scope["path"]`، وليس على `request.url.path` أو الرأس `Host` أبدًا: منذ CVE-2026-48710، يمكن أن يختلف كائن URL مع المسار الذي استقبله الخادم. انظر [الأمان](../../../reference/security.md).

## التكلفة

المشروع بدون أي `middleware.py` لا يدفع شيئًا: لم يتم تثبيت الطبقة. مع الملفات، تضيف كل برامج وسيطة متطابقة Starlette `BaseHTTPMiddleware`؛ احتفظ بها صغيرة.

## الخطوات التالية

- [الميراث](../inheritance.md)
- [التبعيات](../dependencies/README.md)
- [البرمجيات الوسيطة والأمن](../../../guides/middleware-and-security.md)
