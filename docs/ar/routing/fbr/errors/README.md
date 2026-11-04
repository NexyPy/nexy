# صفحات الخطأ

يجب أن يتم الرد على الطلب الذي يفشل مثل بقية موقعك: صفحة بكلماتك الخاصة لـ
زائر، نفس فشل JSON لعميل API. يجيب Nexy على كليهما، ويستبدل كل منهما ملف واحد
إجابة.

هذه الصفحة هي الخريطة: أي ملف يجيب على أي حالة، وكيفية إنشاء ملفك الأول. صفحات
مجلد الحصول على [صفحتهم الخاصة](folder-pages.md).

## فشل واحد وإجابتان

```diagram filename="من يجيب على طلب فاشل"
a request that fails
      │
      ├── a browser (Accept: text/html)              ──►  an HTML page
      └── an API client (Accept: application/json)   ──►  {"detail": "…"}  with the same status

the HTML page
      ├── the deepest folder of the URL that holds a file   ──►  your file
      └── no folder of the chain holds one                 ──►  the built-in page
```

## صفحتك الأولى

أنشئ `src/routes/notfound.nexy` واكتب ما يجب على الزائر قراءته:

```nexy filename="src/routes/notfound.nexy"
---
title: Page not found
---
<h1>Page not found</h1>
<p>The page moved or never existed. <a href="/">Back home</a>.</p>
```

احفظ واطلب عنوان URL الذي لا يخدم أي شيء:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/nowhere
# HTTP/1.1 404 Not Found
```

الملف الموجود في جذر المسارات يجيب على المشروع بأكمله؛ نسخة في مجلد تجيب على هذا المجلد فقط
و[يبقي الباقي كما هو](folder-pages.md). بدون أي ملف، يقدم Nexy تصميمه المدمج
الصفحة.

## أي ملف يجيب

| الملف | الإجابات |
|---|---|
| `notfound.nexy` | `404` لدليلها |
| `errors.nexy` | `500` لدليلها |
| `forbidden.nexy` | `403` لدليلها |
| `unauthorized.nexy` | `401` لدليلها |
| `loading.nexy` | محفوظة؛ لا يوجد تأثير وقت التشغيل حتى الآن |

| الحالة | الجواب |
|---|---|
| لا يوجد طريق مطابق | `404` |
| لا يمكن تحويل المقطع الديناميكي إلى التعليق التوضيحي الخاص به | `404` |
| استثناء لم تتم معالجته، في صفحة أو معالج API | `500` |
| `raise HTTPException(status_code=403)` | الحالة التي قمت برفعها، مثل HTML أو JSON |
| `notFound()`، `forbidden()`، `unauthorized()` | `404`، `403`، `401`، من أي مكان في طلب |
| `redirect()`، `permanentRedirect()` | إعادة توجيه حقيقية بدون صفحة خطأ |

## اترك صفحة أو إجابة من الكود

`redirect`، `permanentRedirect`، `notFound`، `forbidden` و `unauthorized` يرفعون استثناء HTTP،
لذلك يعمل نفس الاستدعاء في صفحة `.nexy`، ومعالج API، ووحدة تحكم معيارية، وحارس و
`dependencies.py`. لديهم نفس الأسماء على العميل (`@nexy/client`).

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound, redirect

from src.posts import find

slug: prop[str]
post = find(slug)
if post is None:
    notFound()
if post.moved_to:
    redirect(post.moved_to)
---
<h1>{{ post.title }}</h1>
```

| اتصل | رد |
|---|---|
| `redirect(url)` | `307`؛ `redirect(url, status=303)` يحول POST إلى GET بعد النموذج |
| `permanentRedirect(url)` | `308`؛ المتصفحات ومحركات البحث تتذكره |
| `notFound(detail=None)` | `404`: صفحة `notfound`، أو JSON لعميل API |
| `forbidden(detail=None)` | `403`: الزائر معروف ولكن قد لا يرى هذا |
| `unauthorized(detail=None, scheme=None)` | `401`؛ `scheme="Bearer"` يضيف `WWW-Authenticate` |

إعادة توجيه الإجابات برأس `Location` وبدون صفحة، أيضًا إلى عميل API. بناء
الوجهة من القيم التي تثق بها: أ `redirect(request.query_params["next"])` يرسل الزوار
أينما يقول الرابط. تم رفض الوجهة التي تحتوي على فاصل أسطر.

يقوم الحارس بحماية مجلد كامل:

```python filename="src/routes/private/dependeency.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

## HTML أو JSON

يجيب نفس الاستثناء بشكل مختلف اعتمادًا على من يسأل:

- يحصل المتصفح (`Accept: text/html`) على صفحة HTML. تم حذف التفاصيل من HTML، لذلك تم إنشاء رسالة
  من إدخال المستخدم لا يمكن إدخال العلامات.
- العميل الذي يطلب JSON وليس صفحة (`Accept: application/json`) يحصل على
  `{"detail": "..."}` بنفس رمز الحالة.

```python filename="src/routes/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=403, detail="Out of range")
    return {"id": id}
```

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!ملاحظة]
> عميل يرسل `Accept: */*` (الافتراضي لـ `curl` والعديد من HTTP
> المكتبات) تتلقى صفحة HTML. اضبط `Accept: application/json` لأخطاء JSON.

## الاستثناءات غير المعالجة

استثناء هو أنه لا يتم تسجيل أي شيء تتم معالجته مرة واحدة، باستثناء مصدره و
رمز حوله، والرد وفقا للوضع.

| | `nx dev` | `nx start` |
|---|---|---|
| المتصفح | صفحة تحتوي على الخطأ، وأسطر التعليمات البرمجية التي رفعتها والتتبع الكامل | صفحة `500` المضمنة (أو `errors.nexy`) مع مرجع |
| عميل JSON | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| سجل الخادم | الاستثناء وأسطر التعليمات البرمجية الخاصة بك | الاستثناء والتتبع بالكامل، بنفس المرجع |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

المرجع هو ثمانية أحرف جديدة لكل فشل. يمكن للزائر أن يقتبسها، وتجد
التتبع من خلال البحث في السجل عنه. ولا يصل الاستثناء ولا الكود إلى الزائر
الإنتاج. يستبدل `errors.nexy` المخصص الصفحة فقط؛ يبقى خط السجل.

## أخطاء في التحقق

رأس مفقود أو معلمة استعلام أو حقل نص يجيب `422` بنص JSON الخاص بـ FastAPI، لكل
العميل. انظر [التصديق والأخطاء](../handlers/validation-and-errors.md).

## الخطوات التالية

- [صفحات الخطأ لكل مجلد](folder-pages.md): 404 أو 403 أو 401 خاصة بك في مجلد واحد
- [الطرق الديناميكية](../pages/dynamic-routes.md)
-  مسارات واجهة برمجة التطبيقات](../handlers/README.md)
- [الاختبار](../../../guides/testing.md)