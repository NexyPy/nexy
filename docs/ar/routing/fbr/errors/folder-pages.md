# خطأ في الصفحات في كل مجلد

يمكن للمجلد أن يجيب على أخطائه: مدونة تحتوي على 404 بكلماتها الخاصة، وهي منطقة خاصة توفر ذلك
نموذج تسجيل الدخول بدلاً من `401`. يحتفظ باقي الموقع بالصفحة الموجودة به بالفعل.

تضيف هذه الصفحة أحد هذه الملفات وتظهر الإجابة عليها.

##  القاعدة

**أعمق ملف يطابق إجابات URL.** كل شيء آخر يبقى كما هو: نفس الحالة
الرموز، وJSON لعميل API، والصفحة المضمنة بمجرد عدم وجود ملف في مجلد السلسلة.

![نطاقات صفحة الخطأ](../../../assets/error-page-scopes.svg)

ل`/blog/2024/hello` نكسي يمشي فوق الشجرة: `/blog/2024`، ثم `/blog`، ثم `/`. الأول
مجلد يحمل إجابات الملف. المجلد مطابق بالكامل: `/blogger/hello` ليس ضمن `/blog`، لذا
نسخة في `blog/` لا تجيب عليه أبداً.

## الملفات الأربعة

| الملف | الإجابات | ما يصل إليه |
|---|---|---|
| `notfound.nexy` | `404` | عنوان URL لا يتطابق مع المسار، `notFound()` |
| `errors.nexy` | `500` | استثناء لم يتم التعامل معه |
| `forbidden.nexy` | `403` | `forbidden()`، `raise HTTPException(403)` |
| `unauthorized.nexy` | `401` | `unauthorized()`، `raise HTTPException(401)` |

`loading.nexy` يبقى محجوزًا: ليس له تأثير وقت التشغيل بعد.

ملف واحد في مكان ما في `src/routes/` يكفي لكي يجيب Nexy على هذه الحالة: نسخة في الجذر
يجيب على المشروع بأكمله، ونسخة في مجلد تجيب على هذا المجلد، وعنوان URL خارج كل نسخة
يحصل على الصفحة المضمنة. حجز ملحق آخر لهذه الأسماء في `nexyconfig.py` مع
`useNotFoundExtensions`، `useErrorsExtensions`، `useForbiddenExtensions` و
`useUnauthorizedExtensions`.

## صفحة مجلدك الأول

```nexy filename="src/routes/blog/notfound.nexy"
---
title: Nothing here yet
---
<h1>That post is gone</h1>
<p>The <a href="/blog">blog</a> still has the others.</p>
```

قم بتشغيل المشروع واطلب مشاركة غير موجودة:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/blog/old
# HTTP/1.1 404 Not Found
```

يحتفظ عنوان URL الموجود خارج المجلد بالصفحة التي لديك بالفعل:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/about
# HTTP/1.1 404 Not Found    (the root page, or the built-in one)
```

##  401 يؤدي إلى مكان ما

يجيب مجلد المنطقة المحمية `401` بالصفحة التي تعرض الطريق في:

```nexy filename="src/routes/private/unauthorized.nexy"
---
title: Sign in to continue
---
<h1>Sign in to see your notes</h1>
<a href="/sign-in" class="button">Sign in</a>
```

```python filename="src/routes/private/dependeency.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

كل مكالمة وكل حالة تحتفظ بإجابتين:

| من يسأل | `401` بملف | `401` بغير واحد |
|---|---|---|
| المتصفح (`Accept: text/html`) | صفحة المجلد | الصفحة المضمنة |
| العميل (`Accept: application/json`) | `{"detail": "..."}` | `{"detail": "..."}` |

`unauthorized(scheme="Bearer")` يضيف `WWW-Authenticate: Bearer` إلى كلا الإجابتين. التفاصيل بنيت
من إدخال المستخدم يتم تخطي HTML في الصفحة.

> [!نصيحة]
>  `Accept: */*`، الإعداد الافتراضي لـ `curl` والعديد من مكتبات HTTP، لا يطلب أيًا منهما ويتلقى
> صفحة HTML. أضف `-H "Accept: application/json"` عندما تريد إجابة JSON.

## التحقق منه

```python filename="الاختبارات/test_private.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_a_private_url_asks_for_sign_in():
    answer = TestClient(app).get("/private/notes")
    assert answer.status_code == 401
    assert "Sign in" in answer.text


def test_an_api_client_gets_json():
    answer = TestClient(app).get(
        "/private/notes", headers={"accept": "application/json"}
    )
    assert answer.json() == {"detail": "Unauthorized"}
```

## الخطوات التالية

- [صفحات الخطأ](README.md): ما الذي يؤدي إلى ظهور كل حالة، HTML أو JSON
- [التبعيات والحراس](../dependencies/README.md): حماية مجلد كامل
- [الاختبار](../../../guides/testing.md): `TestClient` من الاختبار الأول