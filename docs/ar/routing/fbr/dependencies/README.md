# التبعيات والحراس

مشاركة المصادقة وجلسات قاعدة البيانات والإعدادات الأخرى عبر المسارات باستخدام تبعيات FastAPI.
وهي تعمل على مستويين، ويتم توريث مستوى الدليل مثل التخطيطات.

| المستوى | حيث ينطبق | على |
|---|---|---|
| الدليل | `dependencies.py` | كل طريق في الدليل وما دونه، الصفحات المتضمنة |
| معالج | `Depends`، `@UseGuard`، `@Middleware` | معالج واحد |

## لكل دليل: `dependencies.py`

يعلن `dependencies.py` عن قائمة `dependencies` من الوظائف البسيطة. Nexy يلف كل واحد في
`Depends`.

```python filename="src/routes/admin/dependeency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

> [!ملاحظة]
> سرد الوظائف نفسها. يتم تجاهل كائن `Depends(...)` في القائمة.

يتطلب كل مسار ضمن `src/routes/admin/` الآن الرأس و`.py` المعالجات و`.nexy` الصفحات
على حد سواء.

## الميراث

يتم جمع التبعيات من جذر المسارات وصولاً إلى دليل المسار، **الأبعد أولاً**،
تمامًا مثل التخطيطات، ويتم تشغيل حراس المعالج أخيرًا:

```text
src/routes/
├─ dependencies.py              1. root
└─ admin/
   ├─ dependencies.py           2. admin
   └─ users/
      ├─ dependencies.py        3. users
      └─ index.py               4. handler guards, then the handler
```

بالنسبة لـ `GET /admin/users` الترتيب هو `root`، `admin`، `users`، وظائف المعالج `@UseGuard`،
وظائفه `@Middleware`، ثم المعالج. مجموعة المسار (`(group)/`) هي دليل مثل أي دليل
أخرى، فيشارك `dependencies.py` فيها.

## لكل معالج

استخدم `Depends` في التوقيع، كما هو الحال في أي تطبيق FastAPI:

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header, HTTPException


def current_user(authorization: str = Header(...)) -> str:
    if authorization != "Bearer secret":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return "ada"


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

##  الحراس والبرمجيات الوسيطة على المعالج

`@UseGuard` و `@Middleware` يربطان تبعيات FastAPI بالمعالج دون تغييره
التوقيع. كلاهما تبعيات، وليست برمجيات ASGI الوسيطة:

```python filename="src/routes/admin/users/index.py"
from nexy.decorators import Middleware, UseGuard


def audit() -> None: ...


def must_be_staff(x_staff: str = Header(...)) -> None: ...


@UseGuard(must_be_staff)
@Middleware(audit)
async def GET():
    return {"ok": True}
```

بالنسبة للبرامج الوسيطة الحقيقية لـ ASGI (CORS، GZip، الجلسات، الخاصة بك) استخدم `useMiddlewares` و`use*`
الخيارات في [البرامج الوسيطة والأمان](../../../guides/middleware-and-security.md).

## فشل التبعية

التبعية ترفض الطلب عن طريق الرفع. `HTTPException` يجيب بالحالة التي رفعتها، كما
JSON لعملاء API (`Accept: application/json`) وكصفحة خطأ للمتصفحات. انظر
[التصديق والأخطاء](../handlers/validation-and-errors.md).

## الخطوات التالية

- [الميراث](../inheritance.md)
- [المتعاملون](../handlers/README.md)
-  [البرامج الوسيطة والأمن](../../../guides/middleware-and-security.md)