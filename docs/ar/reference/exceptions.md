# الاستثناءات والأخطاء

يمكن أن يفشل الطلب في أربعة أماكن، ويجيب Nexy على كل منها بشكل مختلف. هذه الصفحة هي الفهرس: ابحث عن الحالة التي تراها، ثم السطر الذي أنتجها، ثم الملف الذي يحدد النص.

> [!NOTE]
> هناك ثلاثة أشياء منفصلة وسهلة الخلط: **إجابة HTTP** (الحالة والنص)، و **صفحة الخطأ** (`notfound.nexy`، `errors.nexy`)، وسطر السجل **** (ما تقرأه في الوحدة الطرفية). لا يؤدي تغيير الصفحة إلى تغيير الحالة، ولا يؤدي تخصيص الصفحة إلى إخفاء السجل.

## النسخة القصيرة

| ماذا حدث | الحالة | يرى المتصفح | يرى عميل API |
|---|---|---|---|
| لا يوجد مسار يطابق عنوان URL | `404` | `notfound.nexy`، وإلا الصفحة المضمنة | `{"detail": "Not Found"}` |
| مقطع المسار لا يتناسب مع التعليق التوضيحي الخاص به | `404` | نفس الصفحة | `{"detail": "Not Found"}` |
| استعلام أو رأس أو ملف تعريف ارتباط أو حقل نص مفقود أو غير صالح | `422` | FastAPI جسم JSON | FastAPI جسم JSON |
| `notFound()` | `404` | الصفحة | `{"detail": ...}` |
| `unauthorized()` | `401` | الصفحة المضمنة | `{"detail": ...}` |
| `forbidden()` | `403` | الصفحة المضمنة | `{"detail": ...}` |
| `raise HTTPException(409, ...)` | `409` | الصفحة المضمنة | `{"detail": ...}` |
| استثناء شيء اشتعلت | `500` | `errors.nexy`، وإلا الصفحة المضمنة | `{"detail", "reference"}` |
| `redirect(url)` | `307` | الوجهة، لا الصفحة | الوجهة، لا أحد |
| `permanentRedirect(url)` | `308` | الوجهة، لا الصفحة | الوجهة |

عميل API هو طلب يطلب رأسه `Accept` JSON وليس صفحة:

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!WARNING]
> `curl` يرسل `Accept: */*` افتراضيًا، والذي يحصل على صفحة HTML. أضف `-H "Accept: application/json"` عند اختبار شكل JSON. تستمر المتصفحات في الحصول على الصفحات.

## من أين يأتي الفشل

```diagram filename="طلب واحد وأربعة مخارج"
Browser ──► Middleware ──► Router ──► Page or handler
                 │            │             │
                 │            │             ├─ return ───────────► 200
                 │            │             ├─ HTTPException ────► its status
                 │            │             └─ other exception ───► 500
                 │            └─ no match ────────────────────────► 404
                 └─ raises ──────────────────────────────────────► 500
```

| المرحلة | ما يمكن أن تفشل | الجواب |
|---|---|---|
| الوسيطة | جلسات `middleware.py`، CORS الخاصة بك | حالة الاستثناء، وإلا `500` |
| جهاز التوجيه | عنوان URL لا يطابق أي ملف | `404` |
| التحقق من الصحة | لا يمكن تحويل مقطع المسار | `404` |
| التحقق من الصحة | استعلام أو رأس أو ملف تعريف ارتباط أو حقل نص | `422` |
| الصفحة، المعالج، العمل، الحارس | `HTTPException` | حالتها |
| الصفحة، المعالج، العمل، الحارس | أي شيء آخر | `500` |

## غادر من أي مكان

`redirect`، `permanentRedirect`، `notFound`، `forbidden` و `unauthorized` يثير استثناء HTTP، لذلك يعمل نفس الاستدعاء في صفحة `.nexy`، ومعالج API، ووحدة تحكم نمطية، وحارس، و `dependencies.py` وإجراء.

<!-- router:fbr,custom -->
```python filename="src/routes/posts/[slug].py"
from nexy import notFound, redirect

from src.posts import find


async def GET(slug: str):
    post = find(slug)
    if post is None:
        notFound("No such post")
    if post.moved_to:
        redirect(post.moved_to)
    return post
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/posts/posts_by_slug_controller.py"
from nexy import notFound, redirect
from nexy.decorators import Controller

from src.posts import find


@Controller("/posts/{slug}")
class PostsBySlugController:
    async def get(self, slug: str):
        post = find(slug)
        if post is None:
            notFound("No such post")
        if post.moved_to:
            redirect(post.moved_to)
        return post
```

قم بإدراج وحدة التحكم في `controllers` من الوحدة الجذرية.
<!-- /router -->

| اتصل | الإجابة | متى |
|---|---|---|
| `notFound(detail=None)` | `404` | المورد غير موجود |
| `unauthorized(detail=None, scheme=None)` | `401` | يجب على الزائر تسجيل الدخول أولا |
| `forbidden(detail=None)` | `403` | الزائر معروف لكنه قد لا يرى ذلك |
| `redirect(url, status=307)` | `307` | أرسلهم إلى مكان آخر، مع الحفاظ على الطريقة |
| `redirect(url, status=303)` | `303` | بعد النموذج: الطلب التالي هو `GET` |
| `permanentRedirect(url)` | `308` | صفحة منقولة يجب أن تتذكرها محركات البحث |

قم ببناء الوجهة من القيم التي تثق بها. `redirect(request.query_params["next"])` يرسل الزوار أينما ذكر الرابط؛ إنها عملية إعادة توجيه مفتوحة. تم رفض الوجهة التي تحتوي على فاصل أسطر.

## التحقق من الصحة: 422 أو 404

يتم التحقق من صحة معلمات المعالج بواسطة FastAPI مقابل التعليقات التوضيحية الخاصة بها.

<!-- router:fbr,custom -->
```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/search/search_api_controller.py"
from nexy.decorators import Controller
from nexy.http import Header


@Controller("/api/search")
class SearchApiController:
    async def get(self, q: str, limit: int = 10, x_token: str = Header(...)):
        return {"q": q, "limit": limit}
```

قم بإدراج وحدة التحكم في `controllers` من الوحدة الجذرية.
<!-- /router -->

| مشكلة | الحالة | لماذا |
|---|---|---|
| استعلام أو رأس أو ملف تعريف ارتباط أو حقل نص مفقود أو غير صالح | `422` | وصل الطلب إلى المعالج، والبيانات خاطئة |
| مقطع مسار غير صالح (`/api/users/abc` لـ `id: int`) | `404` | لا يحتوي المجلد على مسار لرقم غير رقم، لذا فإن عنوان URL غير موجود |

الجسم `422` هو الشكل القياسي لـ FastAPI، لذلك يستمر العملاء ومجموعات SDK التي تم إنشاؤها في العمل:

```json
{"detail": [{"loc": ["query", "q"], "msg": "Field required", "type": "missing"}]}
```

بالنسبة للنموذج أو الإجراء، يتلقى العميل `ActionError` مع `status` و `detail`؛ يقوم `422` أيضًا بملء `error.fields` برسالة واحدة لكل حقل. انظر [الإجراءات](../guides/actions.md#errors-and-failures).

> [!TIP]
> التحقق من صحة التوقيع عندما تكون القاعدة حول حقل واحد (`limit: int = 10`). التحقق من الصحة في النص عندما تحتاج القاعدة إلى قاعدة البيانات أو حقل آخر ("هذا البريد الإلكتروني مستخدم بالفعل"): ارفع `HTTPException(409)` واحتفظ بالرسالة للعميل.

## صفحات الخطأ المخصصة

<!-- router:fbr,custom -->
```nexy filename="src/routes/notfound.nexy"
<h1>Page not found</h1>
<p>The link may be old. <a href="/">Start from the home page</a>.</p>
```

```nexy filename="src/routes/errors.nexy"
<h1>Something went wrong</h1>
<p>Try again in a moment.</p>
```

| ملف | الحالة | النطاق |
|---|---|---|
| `src/routes/notfound.nexy` | `404` | كل مسار للمشروع |
| `src/routes/errors.nexy` | `500` | كل مسار للمشروع |
| `src/routes/forbidden.nexy` | `403` | كل مسار للمشروع |
| `src/routes/unauthorized.nexy` | `401` | كل مسار للمشروع |
| `src/routes/blog/notfound.nexy` | `404` | `/blog` وما دونه |
| `src/routes/blog/errors.nexy` | `500` | `/blog` وما دونه |
| `src/routes/loading.nexy` | - | محفوظة، لا يوجد تأثير وقت التشغيل حتى الآن |

يقوم ملف واحد في مكان ما في المسارات بتثبيت الإجابة حسب حالته: نسخة في الجذر تجيب على المشروع بأكمله، ونسخة في مجلد تجيب على هذا المجلد، ويفوز الملف الأعمق الذي يطابق عنوان URL. يحصل عنوان URL الموجود خارج كل نسخة، والحالة التي لا تحتوي على ملف على الإطلاق، على الصفحات المصممة المضمنة. انظر [خطأ في الصفحات في كل مجلد](../routing/fbr/errors/folder-pages.md).

> [!IMPORTANT]
> تحل صفحة `errors.nexy` محل صفحة `500`؛ لا يلتقط الاستثناء ولا يغير سطر السجل. إذا كان المعالج الذي تم رفعه هو الصفحة نفسها، فلن تتمكن الصفحة من إظهار تفاصيل الخطأ الخاصة بها: احتفظ بـ `errors.nexy` بسيطة ومستقلة.
<!-- /router -->

<!-- router:modular -->
لا يحتوي جهاز التوجيه المعياري على صفحة خطأ في الملف: يحصل `404` أو `500` أو `403` أو `401` على الصفحة المصممة المضمنة. تعد صفحات الخطأ لكل مجلد بمثابة اتفاقية لجهاز التوجيه المستند إلى الملف.
<!-- /router -->

## الاستثناءات غير المعالجة

استثناء هو عدم تسجيل أي شيء تم اكتشافه مرة واحدة، مع مرجعه ومن أين جاء والكود المحيط به. الحالة `500`، والجسم يعتمد على البيئة.

| | `nexy dev` | `nexy build` ثم `nexy start` |
|---|---|---|
| المتصفح | الخطأ وأسطر التعليمات البرمجية الخاصة بك والتتبع | `errors.nexy`، وإلا الصفحة المضمنة، مع مرجع |
| عميل واجهة برمجة التطبيقات | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| المحطة | الاستثناء وأسطر التعليمات البرمجية الخاصة بك | الاستثناء والتتبع الكامل والمرجع |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

المرجع هو ثمانية أحرف جديدة لكل فشل. يمكن للزائر أن يقتبسها، ويمكنك العثور على أثر التتبع من خلال البحث عنها في السجل. لا الاستثناء ولا الكود يصل إلى الزائر في الإنتاج.

> [!CAUTION]
> لا تُرجع التتبع إلى زائر في الإنتاج، ولا تضع أسرارًا في رسالة خطأ: يتم إرسال `detail` من `HTTPException` إلى العميل، مع تخطي HTML. ضع السر في السجل وليس في الإجابة.

## الأفعال والأشكال

الإجراء هو نقطة نهاية `POST` بمسار تم إنشاؤه. إخفاقاتها تتبع نفس القواعد:

| الوضع | الحالة | العميل |
|---|---|---|
| الحقل مفقود أو غير صالح | `422` | `ActionError` مع `fields` |
| `HTTPException(403)` مرفوع في الفعل | `403` | `ActionError` مع `status` و `detail` |
| استثناء غير معالج | `500` | `ActionError`; المرجع موجود في سجل الخادم |
| رأس `Origin` هو موقع آخر | `403` | تم الرفض قبل تشغيل الإجراء |

نموذج بدون JavaScript مشاركات في مسار الإجراء؛ نجاح يجيب `303` على العودة إلى الصفحة، فشل يظهر صفحة الخطأ. انظر [الإجراءات](../guides/actions.md#forms-without-javascript).

## قائمة مرجعية عندما تجيب الصفحة على شيء خاطئ

1. **انظر إلى الحالة**، وليس الصفحة. مخصص `notfound.nexy` لا يزال يجيب `404`.
2. **اقرأ الوحدة الطرفية.** الصفحة التي يفشل استيرادها لا يتم تسجيلها، لذلك يجيب عنوان URL الخاص بها `404` أثناء وجود الملف. خطأ الاستيراد موجود في السجل.
3. **تحقق من الامتداد.** مع `useCSR = True`، تنتمي الصفحات `.nexy` إلى وضع الخادم؛ الصفحة في الوضع الخاطئ ليست طريقا.
4. **تحقق من العمق.** يعمل `notfound.nexy` أو `errors.nexy` فقط عند وجود النسخة الجذرية.
5. **اطلب JSON** مع `Accept: application/json` لمعرفة الشكل الذي يتلقاه عميل API الخاص بك.
6. **اقتبس المرجع** من `500` عندما تفتح مشكلة أو تبحث في السجل.

## الخطوات التالية

- [صفحات الخطأ](../routing/fbr/errors/README.md): سلوك الصفحة بالكامل مع الأمثلة
- [التحقق من الصحة والأخطاء](../routing/fbr/handlers/validation-and-errors.md): معالجات API
- [استكشاف الأخطاء وإصلاحها](../guides/troubleshooting.md): الأخطاء التي وقع فيها الأشخاص بالفعل
- [اختبار](../guides/testing.md): تأكيد الحالة والجسم
