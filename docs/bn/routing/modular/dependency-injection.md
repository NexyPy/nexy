# নির্ভরতা ইনজেকশন

Nexy কন্ট্রোলার এবং পরিষেবাগুলির জন্য কনস্ট্রাক্টর নির্ভরতা সমাধান করে। একটি ক্লাস `@Injectable()` এর সাথে নির্বাচন করে।

## একটি পরিষেবা ইনজেক্ট করুন

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

একটি মডিউলে নিয়ামক নিবন্ধন করুন। পরিষেবাটিকে `providers`-এ তালিকাভুক্ত করা অতিরিক্তভাবে স্টার্টআপে এটিকে সাগ্রহে সমাধান করে:

```python filename="src/apps/users/users_module.py"
from nexy.decorators import Module
from .user_controller import UserController
from .user_service import UserService


@Module()
class UsersModule:
    controllers = [UserController]
    providers = [UserService]
```

## কিভাবে রেজোলিউশন কাজ করে

- প্রতিটি `__init__` প্যারামিটার তার **টাইপ টীকা** থেকে সমাধান করা হয়। টীকাটি অবশ্যই একটি `@Injectable()` শ্রেণী হতে হবে, অথবা প্যারামিটারের একটি ডিফল্ট মান থাকতে হবে; অন্যথায় রেজোলিউশন উত্থাপন `ValueError`.
- স্টার্টআপে কন্ট্রোলারগুলিকে `Container.resolve()` দিয়ে ইনস্ট্যান্ট করা হয়।
- একটি নির্ভরতা চক্র ক্লাসের নামকরণ `RecursionError` উত্থাপন করে।
- পরিষেবাগুলি অন্য পরিষেবাগুলিকে যে কোনও গভীরতায় ইনজেকশন করতে পারে৷

## স্কোপ

```python
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class CurrentUser: ...
```

| সুযোগ | আজীবন |
|---|---|
| `Scope.SINGLETON` (ডিফল্ট) | পুরো প্রক্রিয়ার জন্য একটি উদাহরণ |
| `Scope.REQUEST` | অনুরোধের প্রসঙ্গে একটি উদাহরণ |
| `Scope.TRANSIENT` | প্রতিটি রেজোলিউশনে একটি নতুন উদাহরণ |

## ধারক

```python
from nexy.decorators import Container

service = Container.resolve(UserService)
```

একটি `@Injectable()` শ্রেণী তৈরি করা নিজেকে উত্থাপন করে `TypeError`: ধারক তার জীবনচক্রের মালিক। `Container.resolve(...)` ব্যবহার করুন বা অন্য কনস্ট্রাক্টরের মাধ্যমে ক্লাস গ্রহণ করুন।

`Container.clear_request_scope()` বর্তমান অনুরোধের দৃষ্টান্তগুলি ড্রপ করে।

## রুট পরামিতি

FastAPI `Depends` কনস্ট্রাক্টর ইনজেকশনের পাশে, হ্যান্ডলার প্যারামিটারের জন্য স্বাভাবিক হিসাবে কাজ করে:

```python
from fastapi import Depends


def get(self, limit: int = Depends(pagination)) -> list[dict]: ...
```

## সীমা

ধারকটি প্রক্রিয়া-প্রশস্ত। সরবরাহকারীরা প্রতি মডিউলে বিচ্ছিন্ন নয়, `exports` শুধুমাত্র কোন সরবরাহকারীকে একটি আমদানি মডিউল সাগ্রহে সমাধান করে তা নির্ধারণ করে, এবং পরীক্ষায় একটি প্রদানকারীকে অদলবদল করার জন্য কোন পাবলিক API নেই। সম্পূর্ণ তুলনার জন্য [Nexy এবং NestJS](vs-nestjs.md) দেখুন।

## পরবর্তী পদক্ষেপ

- [রক্ষী এবং মেটাডেটা](guards-and-metadata.md)
- [পরীক্ষা](../../guides/testing.md)
