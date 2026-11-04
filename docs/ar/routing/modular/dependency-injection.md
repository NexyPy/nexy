# حقن التبعية

يقوم Nexy بحل تبعيات المنشئ لوحدات التحكم والخدمات. فئة تختار مع
`@Injectable()`.

## ادخل خدمة

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

قم بتسجيل وحدة التحكم في الوحدة النمطية. إدراج الخدمة في `providers` يحل المشكلة أيضًا
بفارغ الصبر عند بدء التشغيل:

```python filename="src/apps/users/users_module.py"
from nexy.decorators import Module
from .user_controller import UserController
from .user_service import UserService


@Module()
class UsersModule:
    controllers = [UserController]
    providers = [UserService]
```

## كيفية عمل القرار

- يتم حل كل `__init__` من المعلمة من **التعليق التوضيحي للنوع**. يجب أن يكون التعليق التوضيحي
  `@Injectable()` فئة، أو يجب أن يكون للمعلمة قيمة افتراضية؛ خلاف ذلك يثير القرار
  `ValueError`.
- يتم إنشاء مثيل لوحدات التحكم باستخدام `Container.resolve()` عند بدء التشغيل.
- تؤدي دورة التبعية إلى رفع `RecursionError` تسمية الفئة.
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
| `Scope.TRANSIENT` | مثيل جديد على كل قرار |

##  الحاوية

```python
from nexy.decorators import Container

service = Container.resolve(UserService)
```

يؤدي إنشاء فئة `@Injectable()` بنفسك إلى رفع `TypeError`: الحاوية تمتلك دورة حياتها.
استخدم `Container.resolve(...)` أو احصل على الفصل من خلال مُنشئ آخر.

`Container.clear_request_scope()` يسقط مثيلات الطلب الحالي.

## معلمات المسار

يعمل FastAPI `Depends` كالمعتاد لمعلمات المعالج، بجوار حقن المُنشئ:

```python
from fastapi import Depends


def get(self, limit: int = Depends(pagination)) -> list[dict]: ...
```

## الحدود

الحاوية على مستوى العملية. لا يتم عزل موفري الخدمة لكل وحدة، `exports` هم فقط من يقرر أي منهم
يتم حل وحدة الاستيراد بفارغ الصبر، ولا توجد واجهة برمجة تطبيقات عامة لتبديل الموفر بها
الاختبارات. راجع [Nexy وNestJS](vs-nestjs.md) للمقارنة الكاملة.

## الخطوات التالية

- [الحراسات والبيانات الوصفية](guards-and-metadata.md)
-  [الاختبار](../../guides/testing.md)