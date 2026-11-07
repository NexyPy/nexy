# প্রকল্প কাঠামো

একটি Nexy প্রজেক্টের প্রতিটি ফাইলের একটি কাজ থাকে এবং এটি কোথায় যায় তা রাউটারের উপর নির্ভর করে: ফাইল-ভিত্তিক রাউটিংয়ের জন্য `src/routes/`, মডুলার রাউটারের জন্য `src/apps/`।

## শীর্ষ স্তর

<!-- router:fbr -->
```text
my-app/
├─ src/
│  ├─ routes/            every file is a route
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

একটি ফোল্ডার চয়ন করতে, ফাইলটি কী তা জিজ্ঞাসা করুন:

- **ব্রাউজার খুলতে পারে এমন কিছু** - একটি রুট: `src/routes/`।
- **বিভিন্ন রুট দ্বারা ব্যবহৃত একটি অংশ** - একটি উপাদান বা একটি মডিউল: `src/components/`, `src/`।
- **একটি ফাইল যেভাবে পরিবেশিত হয়** - `public/`।
- **উৎপন্ন** - `__nexy__/`; এটি সম্পাদনা করবেন না

> [!WARNING]
> `src/routes/` স্ক্যান করা হয়: সেখানে রাখা একজন সাহায্যকারী একটি রুট হয়ে যায়। একটি সাহায্যকারী রাখুন যেটি `src/routes/` এর বাইরে কোনো রুট নয়, অথবা `_` দিয়ে এর নাম শুরু করুন।
<!-- /router -->

<!-- router:modular -->
```text
my-app/
├─ src/
│  ├─ apps/              controllers, modules and their views
│  │  ├─ app_module.py   the root module, given to useRouter
│  │  ├─ app_controller.py
│  │  ├─ app_view.nexy   a view a controller returns
│  │  ├─ layout.nexy     the frame the controllers pass their view to
│  │  └─ users/          one folder per feature: controller, module, service, model
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = AppModule
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

একটি ফোল্ডার চয়ন করতে, ফাইলটি কী তা জিজ্ঞাসা করুন:

- **একটি URL** - `src/apps/`-এ একটি নিয়ামকের একটি পদ্ধতি, এটির মডিউল দ্বারা নিবন্ধিত।
- **একটি পৃষ্ঠা** - এর কন্ট্রোলারের পাশে একটি `.nexy` ভিউ, `useViews` দিয়ে ফিরে এসেছে।
- **একটি অংশ যা বেশ কয়েকটি দর্শন দ্বারা ব্যবহৃত হয়** - `src/components/`।
- **একটি ফাইল যেভাবে পরিবেশিত হয়** - `public/`।
- **উৎপন্ন** - `__nexy__/`; এটি সম্পাদনা করবেন না
<!-- /router -->

<!-- router:custom -->
```text
my-app/
├─ src/
│  ├─ legacy/            the FastAPI router you include
│  │  └─ api.py          router = APIRouter(prefix="/api")
│  ├─ routes/            pages and route files, served next to it
│  │  └─ index.nexy      → /
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = router
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

একটি ফোল্ডার চয়ন করতে, ফাইলটি কী তা জিজ্ঞাসা করুন:

- **অন্তর্ভুক্ত অ্যাপের একটি রুট** - যেখানে এটি ইতিমধ্যেই আছে, এখানে `src/legacy/`।
- **একটি নতুন পৃষ্ঠা বা রুট** - `src/routes/`, অন্তর্ভুক্ত রাউটারের পাশে।
- **একটি ফাইল যেভাবে পরিবেশিত হয়** - `public/`।
- **উৎপন্ন** - `__nexy__/`; এটি সম্পাদনা করবেন না
<!-- /router -->

<!-- router:fbr,custom -->
## `src/routes/`

নীচের সংরক্ষিত নামগুলি ছাড়া প্রতিটি ফাইল একটি রুট হয়ে যায়। ফাইল পাথ বিয়োগ এক্সটেনশন হল URL - দেখুন [ফাইল-ভিত্তিক রাউটিং](../routing/fbr/README.md)।

| ফাইল | ভূমিকা |
|---|---|
| `layout.nexy` | ভাইবোন এবং শিশু পাতা মোড়ানো |
| `errors.nexy` | ডিরেক্টরির জন্য 500 পৃষ্ঠা |
| `notfound.nexy` | ডিরেক্টরির জন্য 404 পৃষ্ঠা |
| `dependencies.py` | ডিরেক্টরীর জন্য শেয়ার করা FastAPI নির্ভরতা |
| `__init__.py` | Python প্যাকেজ চিহ্নিতকারী |
| `loading.nexy` | সংরক্ষিত - রুটগুলি থেকে বাদ দেওয়া হয়েছে, তবে এটির এখনও কোন রানটাইম প্রভাব নেই৷ |

প্রতিটি পৃষ্ঠার নামও ফ্রেমওয়ার্ক প্রতি বিদ্যমান। `react()` কনফিগার করা সহ, `layout.jsx` এবং `layout.tsx` ঠিক `layout.nexy` এর মতো সংরক্ষিত। তালিকাগুলি `nexy/core/config.py` (`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`) এ তৈরি করা হয়েছে।

> [!NOTE]
> `notfound.nexy` এবং `errors.nexy` শুধুমাত্র তখনই ইনস্টল করা হয় যখন রুট রুটে একটি কপি বিদ্যমান থাকে। একটি সাবডিরেক্টরিতে একটি অনুলিপি তারপর সেই উপসর্গের জন্য পৃষ্ঠাটিকে পরিমার্জন করে।
<!-- /router -->

<!-- router:modular -->
## `src/apps/`

একটি কন্ট্রোলার URL-এর উত্তর দেয়, একটি মডিউল কন্ট্রোলার এবং প্রদানকারীদের গ্রুপ করে এবং রুট মডিউলটি `useRouter` এর সাথে `nexyconfig.py`:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller()
class AppController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/app_view.nexy")})
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    useAliases = {"@": "src"}  # the views import @/components/...
```

`src/apps/`-এ কোনো ফাইলই এর নামের একটি রুট নয়: শুধুমাত্র কন্ট্রোলার একটি মডিউল উত্তর দেয়। [মডুলার রাউটিং](../routing/modular/README.md) দেখুন।
<!-- /router -->

## `public/`

এখানে ফাইলগুলি সাইট রুট থেকে পরিবেশন করা হয়: `/favicon.ico`, `/robots.txt`, ছবি, ফন্ট।

## `__nexy__/`

`nx build` দ্বারা উত্পন্ন (এবং `nx dev` দ্বারা এটির প্রয়োজনীয় অংশগুলির জন্য)। এতে রয়েছে:

- সংকলিত `.nexy` ফাইলগুলি, একটি Python প্যাকেজ হিসাবে (`__nexy__/src/...`);
- উৎপন্ন ক্লায়েন্ট এন্ট্রি পয়েন্ট (`main.ts`, `vite.ts`, `*.auto.ts`);
- `client/` একটি Vite বিল্ডের পরে - সম্পদ, ম্যানিফেস্ট, প্রি-রেন্ডার করা HTML;
- `build-cache.json`।

সম্পূর্ণ ডিরেক্টরিটিকে নিষ্পত্তিযোগ্য হিসাবে বিবেচনা করুন: এটি মুছুন, এটি পুনর্নির্মাণ করুন। এটি হাতে সম্পাদনা করা পরবর্তী বিল্ডে পরিবর্তন হারায়। এটি `.gitignore` এ যোগ করুন।

## পরবর্তী পদক্ষেপ

<!-- router:fbr -->
- [ফাইল-ভিত্তিক রাউটিং](../routing/fbr/README.md): কিভাবে একটি পাথ একটি URL হয়ে যায়
<!-- /router -->
<!-- router:modular -->
- [মডুলার রাউটিং ](../routing/modular/README.md): কন্ট্রোলার, মডিউল এবং প্রদানকারী
<!-- /router -->
<!-- router:custom -->
- [কাস্টম রাউটিং](../routing/custom/README.md): একটি বিদ্যমান FastAPI রাউটার অন্তর্ভুক্ত করুন
<!-- /router -->
- [কনফিগ](../reference/config.md): প্রতিটি প্রকল্পের বিকল্প
- [ফ্রন্টএন্ড](../guides/frontend.md): Vite, স্টাইলিং এবং ক্লায়েন্ট বিল্ড
