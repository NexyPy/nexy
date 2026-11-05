# الحراس والبيانات الوصفية

أدوات تزيين تحمي المسار وتصفه في مخطط OpenAPI.

## حراس

`@UseGuard(*guards)` يعمل على وحدة تحكم (كل طريقة) أو على طريقة واحدة. تتم إضافة كل حارس كـ FastAPI `Depends`، لذلك يعلن عن المعلمات التي يحتاجها ويرفع لرفض الاستدعاء:

```python filename="src/apps/admin/admin_controller.py"
from fastapi import Header, HTTPException
from nexy.decorators import Controller, UseGuard


def require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller(prefix="/admin")
@UseGuard(require_token)
class AdminController:
    async def get(self) -> dict:
        return {"ok": True}
```

## مصمم ديكورات وسطية

`@Middleware(*middlewares)` يتصرف بنفس الطريقة: هذه هي FastAPI تبعيات، وليست برامج ASGI الوسيطة. بالنسبة للبرامج الوسيطة الحقيقية لـ ASGI، استخدم `useMiddlewares` في [التكوين](../../reference/config.md) أو [البرامج الوسيطة والأمان](../../guides/middleware-and-security.md).

## البيانات الوصفية للطريق

`@UseRoute(...)` يقوم بتعيين OpenAPI البيانات الوصفية. لا يغير المسار.

| الحجة | المعنى |
|---|---|
| `name` | اسم الطريق |
| `tags` | OpenAPI العلامات |
| `summary`، `description` | نص في مرجع واجهة برمجة التطبيقات |
| `deprecated` | وضع علامة على العملية المهملة |
| `include_in_schema` | إخفاء المسار من المخطط |
| `operation_id` | معرف العملية الصريحة |
| `openapi_extra` | حقول إضافية OpenAPI |

## الردود

`@UseResponse(...)` يحدد `status_code`، `response_class`، `response_model`، `responses` وخيارات التسلسل.

```python
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller(prefix="/users")
class UserController:
    @UseRoute(summary="List users", tags=["users"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

يتم تقديم مرجع API الذي تم إنشاؤه في `/docs` ما لم `useDocs = False`.

## الخطوات التالية

- [حقن التبعية](dependency-injection.md)
- [مسارات واجهة برمجة التطبيقات](../fbr/handlers/README.md): نفس الخيارات للمعالجات القائمة على الملفات
