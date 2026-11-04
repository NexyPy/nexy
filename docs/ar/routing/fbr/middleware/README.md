# ملفات البرامج الوسيطة

يقوم `middleware.py` في دليل المسارات بتغليف الطلبات التي يعالجها هذا الدليل. مثل التخطيطات و
`dependencies.py`، يتم تكديس الملفات من المسارات الجذرية إلى الأسفل، والأبعد أولاً.

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

الوظيفة هي `async def middleware(request, call_next)`: توقيع FastAPI
`@app.middleware("http")`. اتصل بـ `await call_next(request)` للاستمرار في المسار، أو العودة أ
رد للتوقف عند هذا الحد. رمز بعد تشغيل المكالمة في طريق الخروج ويمكن تغيير الرد.

##  ما يغلفه

تنطبق البرامج الوسيطة على **المسارات التي يوجد ملفها في دليلها** أو أدناه، والصفحات وواجهة برمجة التطبيقات (API)
معالجات على حد سواء، وشملت مجموعات الطريق:

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

بالنسبة للطلب إلى `/admin/users` فالأمر هو `root`، `admin`، `users`، ثم الطريق. مجموعة ليس لها
عنوان URL خاص به، بحيث تتم مطابقته من خلال المسار الذي يخدم الطلب، وليس من خلال عنوان URL.

عنوان URL الذي لا يتطابق مع أي مسار (404) يتلقى فقط البرامج الوسيطة للأدلة التي ليست مجموعات،
تم تحديده بواسطة بادئة URL. `[slug]` يطابق مقطعًا واحدًا ويطابق `[...rest]` الباقي.

##  ما لا يلف

- عناوين URL للإطار والأصول: `/__nexy__/`، `/_nexy/`، `/public/`، `/assets/` و `/@...` (Vite).
- معالجات WebSocket وعمر الخادم: طلبات HTTP فقط.
- الملفات الموجودة في المجلدات تبدأ بـ `_` أو `.`.

## البرمجيات الوسيطة أو التبعيات أو الحراس

| استخدم | عندما |
|---|---|
| `middleware.py` | أنت بحاجة إلى **الاستجابة** أيضًا: الرؤوس، وعمليات إعادة التوجيه، والتوقيت، وقصر الدائرة الكهربائية لمنطقة بأكملها |
| [`dependencies.py`](../dependencies/README.md) | تحتاج إلى معلمات تحليلية أو لإدخال قيمة (المستخدم الحالي، جلسة قاعدة البيانات) |
| `@UseGuard` على معالج | يحتاج مسار واحد إلى فحص إضافي |
| `useMiddlewares` في [config](../../../reference/config.md) | برنامج ASGI الوسيط للتطبيق بأكمله (CORS، GZip، الجلسات) |

تعمل ملفات البرامج الوسيطة ** قبل تبعيات **: لقد مر الطلب بكل `middleware.py` من ملفاته
الدلائل عند بدء التبعيات.

## القواعد

- يجب أن يحدد الملف `async def middleware(request, call_next)`. وإلا فإن Nexy يتوقف عند بدء التشغيل و
  يسمي الملف.
- إنها وحدة بايثون عادية: قم باستيراد ما تحتاجه. يتم تحميله مرة واحدة، عند بدء تشغيل الخادم.
- ليس طريقًا أبدًا: `/middleware` هو 404.
- يتم فحص المسار الأساسي على `request.scope["path"]`، وليس على `request.url.path` أو رأس `Host` أبدًا: منذ
  CVE-2026-48710 يمكن أن يختلف كائن URL مع المسار الذي يتلقاه الخادم. انظر
  [الأمن](../../../reference/security.md).

## التكلفة

المشروع بدون أي `middleware.py` لا يدفع شيئًا: لم يتم تثبيت الطبقة. مع ملفات كل
تضيف البرامج الوسيطة المطابقة Starlette `BaseHTTPMiddleware`; احتفظ بها صغيرة.

## الخطوات التالية

- [الميراث](../inheritance.md)
- [التبعيات](../dependencies/README.md)
-  [البرمجيات الوسيطة والأمن](../../../guides/middleware-and-security.md)