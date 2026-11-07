# ডাটাবেস

`nx new` SQLModel, SQLAlchemy বা কচ্ছপ-ORM সহ একটি মডেল স্তর ভারাক্রান্ত করতে পারে। Nexy ORM র‌্যাপ করে না: আপনি সরাসরি হ্যান্ডলার এবং পেজ থেকে এটি ব্যবহার করেন।

## ভারা কি যোগ করে

| ফাইল | উদ্দেশ্য |
|---|---|
| `src/configs/db.py` | ইঞ্জিন (SQLModel, SQLAlchemy) বা `TORTOISE_ORM` সেটিংস |
| `src/models/` | মডেল ক্লাস |
| `src/services/` | ফাংশন যে মডেল জিজ্ঞাসা |
| `.env` | `DATABASE_URL`, যখন আপনি `nx new` সময় একটি ডাটাবেস URL দেন তখন লেখা হয় |

সংযোগ স্ট্রিং `DATABASE_URL` এনভায়রনমেন্ট ভেরিয়েবল থেকে আসে। যখন এটি সেট করা না থাকে, স্ক্যাফোল্ড ইঞ্জিনটি একটি স্থানীয় SQLite ফাইলে ফিরে আসে, `dev.db`।

## একটি পৃষ্ঠায় একটি পরিষেবা ব্যবহার করুন

<!-- router:fbr,custom -->
```nexy filename="src/routes/users/index.nexy"
---
from src.services.user_service import UserService
users = UserService.get_all()
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## একটি API হ্যান্ডলারে একটি পরিষেবা ব্যবহার করুন

```python filename="src/routes/api/users.py"
from src.services.user_service import UserService


async def GET():
    return UserService.get_all()
```
<!-- /router -->

<!-- router:modular -->
একটি কন্ট্রোলার পরিষেবাটিকে কল করে এবং সারিগুলিকে তার দৃশ্যে পাস করে বা তাদের JSON হিসাবে ফেরত দেয়:

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

from src.services.user_service import UserService


@Controller("/users")
class UserController:
    async def get(self):
        users = UserService.get_all()
        return useViews("src/apps/users/user_view.nexy", context={"users": users})


@Controller("/api/users")
class UserApiController:
    async def get(self):
        return UserService.get_all()
```

```nexy filename="src/apps/users/user_view.nexy"
---
users: prop[list] = []
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```
<!-- /router -->

## কচ্ছপ-ORM async হয়

একটি পৃষ্ঠা সার্ভারের ইভেন্ট লুপে চলে এবং এটিতে অপেক্ষা করতে পারে না, তাই `asyncio.run(...)` সেখানে "চলমান ইভেন্ট লুপ থেকে কল করা যায় না" এর সাথে ব্যর্থ হয়। ভারাটি `src/configs/db.py` দেয় Tortoise নিজস্ব একটি লুপ, একটি থ্রেডে, এবং দুটি সাহায্যকারী যারা এটিতে একটি করুটিন পাঠায়:

| আপনি যেখানে আছেন | কল | করে |
|---|---|---|
| সিঙ্ক কোড, যেমন একটি পৃষ্ঠা | `run(UserService.get_all())` | এটি চালায় এবং ফলাফল প্রদান করে |
| async কোড, যেমন একটি হ্যান্ডলার বা একটি নিয়ামক | `await arun(UserService.get_all())` | একই, সার্ভার ব্লক না করে |

<!-- router:fbr,custom -->
```nexy filename="src/routes/users/index.nexy"
---
from src.configs.db import run
from src.services.user_service import UserService
users = run(UserService.get_all())
---
```
<!-- /router -->

<!-- router:modular -->
একটি কন্ট্রোলার অ্যাসিঙ্ক হয়: এটি `arun` এর মাধ্যমে পরিষেবার জন্য অপেক্ষা করে, এবং দৃশ্যটি শুধুমাত্র সারিগুলি দেখায়:

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

from src.configs.db import arun
from src.services.user_service import UserService


@Controller("/users")
class UserController:
    async def get(self):
        users = await arun(UserService.get_all())
        return useViews("src/apps/users/user_view.nexy", context={"users": users})
```
<!-- /router -->

Tortoise প্রথমবার তাদের মধ্যে একজনকে ডাকা হলে সংযোগ করে। একটি `async def` (`await UserModel.all()`) পরিষেবার ভিতরে থেকে মডেলটিকে কল করুন, মডিউল স্তরে নয়: একটি করটিনের বাইরে একটি কল Tortoise সংযুক্ত হওয়ার আগে চলে।

`TORTOISE_ORM` (`src/configs/db.py`-এর `models` এন্ট্রিতে মডেল ধারণ করে এমন প্রতিটি মডিউলের তালিকা করুন। ভারা ব্যবহারকারী মডেল এবং `aerich.models` তালিকাভুক্ত করে; তালিকাভুক্ত নয় এমন একটি মডিউলের একটি মডেল পাওয়া যায় না।

## মাইগ্রেশন

`nx migrate` আপনার ORM-এর জন্য টুলটি বেছে নেয়: Alembic SQLModel এবং SQLAlchemy, Aerich কচ্ছপ-ORM-এর জন্য।

| আদেশ | করে |
|---|---|
| `nx migrate --init` | প্রকল্পের জন্য মাইগ্রেশন টুল শুরু করুন |
| `nx migrate -m "add users"` | আপনার মডেল পরিবর্তন থেকে একটি মাইগ্রেশন তৈরি করুন |
| `nx migrate --upgrade` | মুলতুবি মাইগ্রেশন প্রয়োগ করুন |

Aerich এর সাথে, প্রথম `nx migrate` রান করে `aerich init-db`, যা প্রথম স্থানান্তর এবং টেবিল একসাথে তৈরি করে; পরেরগুলো রান করে `aerich migrate --name "..."`, এবং `--upgrade` রান করে `aerich upgrade`।

`nx migrate` একটি স্পষ্ট বার্তা দিয়ে থামে যখন `DATABASE_URL` অনুপস্থিত থাকে বা ডাটাবেসে পৌঁছানো যায় না (Alembic শুধুমাত্র: Aerich তার নিজস্ব ত্রুটির প্রতিবেদন করে)।

### প্রথম মাইগ্রেশন আপনার জন্য করা হয়

আপনি যখন একটি ORM চয়ন করেন এবং একটি ডাটাবেস URL দেন, `nx new` মাইগ্রেশন টুল সেট আপ করে, প্রথম মাইগ্রেশন তৈরি করে এবং এটি প্রয়োগ করে, তাই ব্যবহারকারী পৃষ্ঠা প্রথম `nexy dev`-এ উত্তর দেয়। মাইগ্রেশন টুল (`alembic` বা `aerich`) ORM-এর সাথে প্রজেক্টে ইনস্টল করা আছে।

যদি ডাটাবেস উত্তর না দেয় (একটি PostgreSQL সার্ভার যেটি চলছে না, একটি অনুপস্থিত ড্রাইভার), `nx new` কেন বলে, মাইগ্রেশন এড়িয়ে যায় এবং এটি প্রস্তুত হলে চালানোর জন্য দুটি কমান্ড তালিকাভুক্ত করে:

```bash
nexy migrate -m "create tables"
nexy migrate --upgrade
```

টেবিলের অস্তিত্ব না থাকা পর্যন্ত, ডাটাবেস পড়ার একটি পৃষ্ঠা "এমন কোনো টেবিল" দিয়ে ব্যর্থ হয়।

### একটি মডেল যোগ করুন

Alembic মডেলের সাথে ডাটাবেসের তুলনা করে যা `alembic/env.py` আমদানি করে। একটি নতুন মডিউলের একটি মডেল দেখা যায় না যতক্ষণ না সেই মডিউলটি সেখানে আমদানি করা হয়, ব্যবহারকারী মডেলের পাশে:

```python filename="alembic/env.py"
import src.models.user_model  # noqa: F401
import src.models.post_model  # noqa: F401
```

Tortoise-ORM-এর জন্য, পরিবর্তে `TORTOISE_ORM`-এ মডিউলটি তালিকাভুক্ত করুন (উপরে দেখুন)।

## পরবর্তী পদক্ষেপ

- [টেস্টিং](testing.md): একটি অস্থায়ী ডাটাবেসের বিরুদ্ধে পরীক্ষা হ্যান্ডলার
- [কনফিগারেশন](../reference/config.md)
- [স্থাপন ](../deployment/README.md): উৎপাদনে `DATABASE_URL` সেট করুন
