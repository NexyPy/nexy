# انحصار انجکشن

Nexy کنٹرولرز اور خدمات کے لیے کنسٹرکٹر انحصار کو حل کرتا ہے۔ ایک کلاس `@Injectable()` کے ساتھ آپٹ ان کرتی ہے۔

## سروس انجیکشن لگائیں۔

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

کنٹرولر کو ماڈیول میں رجسٹر کریں۔ سروس کو `providers` میں درج کرنے سے اس کے آغاز پر بے تابی سے حل ہو جاتا ہے:

```python filename="src/apps/users/users_module.py"
from nexy.decorators import Module
from .user_controller import UserController
from .user_service import UserService


@Module()
class UsersModule:
    controllers = [UserController]
    providers = [UserService]
```

## ریزولوشن کیسے کام کرتا ہے۔

- ہر `__init__` پیرامیٹر کو اس کی **قسم کی تشریح** سے حل کیا جاتا ہے۔ تشریح ایک `@Injectable()` کلاس ہونی چاہیے، یا پیرامیٹر کی ڈیفالٹ قدر ہونی چاہیے۔ بصورت دیگر قرارداد اٹھاتی ہے `ValueError`۔
- شروع ہونے پر کنٹرولرز کو `Container.resolve()` کے ساتھ فوری بنایا جاتا ہے۔
- ایک انحصار کا چکر کلاس کا نام دینے سے `RecursionError` اٹھاتا ہے۔
- خدمات دیگر خدمات کو کسی بھی گہرائی تک انجیکشن کر سکتی ہیں۔

## دائرہ کار

```python
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class CurrentUser: ...
```

| دائرہ کار | تاحیات |
|---|---|
| `Scope.SINGLETON` (پہلے سے طے شدہ) | پورے عمل کے لئے ایک مثال |
| `Scope.REQUEST` | ایک مثال فی درخواست سیاق و سباق |
| `Scope.TRANSIENT` | ہر قرارداد پر ایک نئی مثال |

## کنٹینر

```python
from nexy.decorators import Container

service = Container.resolve(UserService)
```

ایک `@Injectable()` کلاس بنانا خود کو بڑھاتا ہے `TypeError`: کنٹینر اپنے لائف سائیکل کا مالک ہے۔ `Container.resolve(...)` کا استعمال کریں یا کسی دوسرے کنسٹرکٹر کے ذریعے کلاس وصول کریں۔

`Container.clear_request_scope()` موجودہ درخواست کی مثالوں کو چھوڑ دیتا ہے۔

## روٹ کے پیرامیٹرز

FastAPI `Depends` کنسٹرکٹر انجیکشن کے ساتھ ہینڈلر پیرامیٹرز کے لئے معمول کے مطابق کام کرتا ہے:

```python
from fastapi import Depends


def get(self, limit: int = Depends(pagination)) -> list[dict]: ...
```

## حدود

کنٹینر عمل میں وسیع ہے۔ فراہم کنندگان کو فی ماڈیول الگ نہیں کیا جاتا ہے، `exports` صرف یہ فیصلہ کرتا ہے کہ کون سے فراہم کنندگان کو درآمد کرنے والا ماڈیول بے تابی سے حل کرتا ہے، اور ٹیسٹوں میں فراہم کنندہ کو تبدیل کرنے کے لیے کوئی عوامی API نہیں ہے۔ مکمل موازنہ کے لیے [Nexy اور NestJS](vs-nestjs.md) دیکھیں۔

## اگلے اقدامات

- [گارڈز اور میٹا ڈیٹا](guards-and-metadata.md)
- [ٹیسٹنگ](../../guides/testing.md)
