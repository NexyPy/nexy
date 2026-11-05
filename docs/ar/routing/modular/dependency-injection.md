# حقن التبعية

يقوم Nexy بحل تبعيات المنشئ لوحدات التحكم والخدمات. يختار الفصل الدراسي الاشتراك بـ `@Injectable()`.

## حقن الخدمة

```python filename="src/apps/users/user_service.py"
from nexy.decorators import Injectable


@Injectable()
class UserService:
    def get_all(self) -> list[dict]:
        return [{"id": 1, "name": "Ada"}]
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller
from .user_service import UserService


@Controller(prefix="/users")
class UserController:
    def __init__(self, svc: UserService) -> None:
        self.svc = svc

    def get(self) -> list[dict]:
        return self.svc.get_all()
```

قم بتسجيل وحدة التحكم في الوحدة النمطية. يؤدي إدراج الخدمة في `providers` أيضًا إلى حلها بفارغ الصبر عند بدء التشغيل:

```python filename="src/apps/users/users_module.py"
from nexy.decorators import Module
from .user_controller import UserController
from .user_service import UserService


@Module()
class UsersModule:
    controllers = [UserController]
    providers = [UserService]
```

## كيف يعمل القرار

- يتم حل كل معلمة `__init__` من **التعليق التوضيحي للنوع**. يجب أن يكون التعليق التوضيحي فئة `@Injectable()`، أو يجب أن يكون للمعلمة قيمة افتراضية؛ وإلا فإن القرار يرفع `ValueError`.
- يتم إنشاء مثيل لوحدات التحكم باستخدام `Container.resolve()` عند بدء التشغيل.
- تثير دورة التبعية `RecursionError` تسمية الفصل.
- يمكن للخدمات أن تضخ خدمات أخرى، إلى أي عمق.

## النطاقات

```python
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class CurrentUser: ...
```

| النطاق | مدى الحياة |
|---|---|
| `Scope.SINGLETON` (افتراضي) | مثيل واحد للعملية بأكملها |
| `Scope.REQUEST` | مثيل واحد لكل سياق طلب |
| `Scope.TRANSIENT` | مثيل جديد في كل قرار |

## الحاوية

```python
from nexy.decorators import Container

service = Container.resolve(UserService)
```

يؤدي إنشاء فئة `@Injectable()` بنفسك إلى رفع `TypeError`: الحاوية تمتلك دورة حياتها. استخدم `Container.resolve(...)` أو احصل على الفصل من خلال مُنشئ آخر.

`Container.clear_request_scope()` يسقط مثيلات الطلب الحالي.

## معلمات الطريق

FastAPI `Depends` يعمل كالمعتاد لمعلمات المعالج، بجانب حقن المنشئ:

```python
from fastapi import Depends


def get(self, limit: int = Depends(pagination)) -> list[dict]: ...
```

## حدود

الحاوية على مستوى العملية. لا يتم عزل الموفرين لكل وحدة، `exports` يقرر فقط الموفرين الذين تحلهم وحدة الاستيراد بفارغ الصبر، ولا توجد واجهة برمجة تطبيقات عامة لتبديل الموفر في الاختبارات. راجع [[Nexy و NestJS](vs-nestjs.md) للمقارنة الكاملة.

## الخطوات التالية

- [الحراس والبيانات الوصفية](guards-and-metadata.md)
- [الاختبار](../../guides/testing.md)
