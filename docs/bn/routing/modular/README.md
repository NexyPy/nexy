# মডুলার রাউটিং

মডুলার রাউটিং `src/routes/`-এর অধীনে ফাইলগুলির পরিবর্তে ডেকোরেটর সহ ক্লাস ব্যবহার করে: কন্ট্রোলাররা অনুরোধগুলি পরিচালনা করে, মডিউলগুলি তাদের গোষ্ঠীভুক্ত করে এবং প্রদানকারীদের ইনজেকশন করা হয়। `nexyconfig.py`-এ `useRouter` সহ ফলাফল `APIRouter` মাউন্ট করুন।

**আপনি শুরু করার আগে:** একটি Nexy প্রকল্প এবং একটি কাজের পৃষ্ঠা। মডুলার রাউটারটি ফাইল-ভিত্তিক একটিকে প্রতিস্থাপন করে, তাই আপনি যদি এখনও রাউটার বেছে না থাকেন তবে প্রথমে [রাউটিং](../README.md) পড়ুন।

| পৃষ্ঠা | এটি কি কভার করে |
|---|---|
| এই পৃষ্ঠাটি | একটি মডিউল মাউন্ট করুন, একটি কন্ট্রোলার লিখুন, গ্রুপ কন্ট্রোলারগুলি |
| [নির্ভরতা ইনজেকশন](dependency-injection.md) | `@Injectable`, স্কোপ, ধারক |
| [রক্ষী এবং মেটাডেটা](guards-and-metadata.md) | `@UseGuard`, `@Middleware`, `@UseRoute`, `@UseResponse` |
| [নেক্সি এবং NestJS](vs-nestjs.md) | কী মেলে NestJS এবং কী মেলে না |

## রাউটার সেট আপ করুন

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

> [!দ্রষ্টব্য]
> ফাইল-ভিত্তিক রাউটিং কাজ করে। যদি `src/routes/` বিদ্যমান থাকে, তবে `useRouter` সেট থাকা অবস্থায়ও এটি স্ক্যান করা হয়।

## একটি নিয়ামক লিখুন

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
```

পদ্ধতিগুলি নামের সাথে মিলে যায়, অক্ষর-সংবেদনশীলভাবে: `get`, `post`, `put`, `patch`, `delete`, `options`, `head`, `trace`।

একটি কন্ট্রোলার প্রতি HTTP পদ্ধতিতে একটি হ্যান্ডলার ঘোষণা করে; একটি ডুপ্লিকেট স্টার্টআপে উত্থাপিত হয়। `@Controller(prefix="/users")` এর সাথে একটি উপসর্গ যোগ করুন - প্রতিটি হ্যান্ডলার `prefix/` এ মাউন্ট করা হয়। একটি কন্ট্রোলারে `async def SOCKET(...)` একই পথে একটি WebSocket নিবন্ধন করে।

## একটি মডিউলে গ্রুপ কন্ট্রোলার

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

`@Module(prefix="/api")` একটি `APIRouter` প্রদান করে। `controllers` প্রয়োজন; `providers`, `imports` এবং `exports` ঐচ্ছিক। আমদানি করা মডিউলগুলি সাব-রাউটার হিসাবে মাউন্ট করা হয়, এবং তাদের রপ্তানি করা প্রদানকারীরা স্টার্টআপে সমাধান করা হয়।

## একটি কন্ট্রোলার থেকে দেখা

একটি নিয়ামক একটি পৃষ্ঠা ফেরত দিতে পারে। `useViews` একটি `.nexy` ভিউ রেন্ডার করে; একটি লেআউটে এটি মোড়ানোর জন্য একে অপরের ভিতরে নেস্ট করুন:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller()
class AppController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/app_view.nexy"),
        })
```

[লেআউটস](../fbr/layouts/README.md) দেখুন।

## উদাহরণ

দেখুন `examples/Modular/api/minimal/`।

## পরবর্তী পদক্ষেপ

- [নির্ভরতা ইনজেকশন ](dependency-injection.md): পরিষেবা এবং সুযোগ
- [রক্ষী এবং মেটাডেটা](guards-and-metadata.md): সুরক্ষা এবং নথির রুট
- [রাউটিং](../README.md): ফাইল-ভিত্তিক রাউটার
- [কনফিগ](../../reference/config.md): প্রতিটি বিকল্প, সহ `useRouter`
