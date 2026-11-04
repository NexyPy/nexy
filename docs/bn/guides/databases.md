# ডাটাবেস

`nx new` SQLModel, SQLAlchemy বা Tortoise-ORM সহ একটি মডেল স্তর ভারাক্রান্ত করতে পারে। Nexy মোড়ানো হয় না
ORM: আপনি এটি সরাসরি ব্যবহার করেন, হ্যান্ডলার এবং পেজ থেকে।

## ভারা কি যোগ করে

| ফাইল | উদ্দেশ্য |
|---|---|
| `src/configs/db.py` | ইঞ্জিন (SQLModel, SQLAlchemy) বা `TORTOISE_ORM` সেটিংস |
| `src/models/` | মডেল ক্লাস |
| `src/services/` | ফাংশন যা মডেলগুলিকে জিজ্ঞাসা করে |
| `.env` | `DATABASE_URL`, যখন আপনি `nx new` | সময় একটি ডাটাবেস URL দেন তখন লেখা হয়।

সংযোগ স্ট্রিং `DATABASE_URL` এনভায়রনমেন্ট ভেরিয়েবল থেকে আসে। এটি আনসেট করা হলে,
স্ক্যাফোল্ডেড ইঞ্জিন একটি স্থানীয় SQLite ফাইলে ফিরে আসে, `dev.db`।

## একটি পৃষ্ঠায় একটি পরিষেবা ব্যবহার করুন৷

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

## কচ্ছপ-ORM অ্যাসিঙ্ক

একটি পৃষ্ঠা সার্ভারের ইভেন্ট লুপে চলে এবং এটিতে অপেক্ষা করতে পারে না, তাই `asyncio.run(...)` সেখানে ব্যর্থ হয়
"একটি চলমান ইভেন্ট লুপ থেকে কল করা যাবে না"। ভারা `src/configs/db.py` কচ্ছপ দেয়
তার নিজস্ব লুপ, একটি থ্রেডে, এবং দুটি সাহায্যকারী যারা এটিতে একটি করুটিন পাঠায়:

| আপনি যেখানে | কল করেন | করেন |
|---|---|---|
| সিঙ্ক কোড, যেমন একটি পৃষ্ঠা | `run(UserService.get_all())` | এটি চালায় এবং ফলাফল প্রদান করে |
| অ্যাসিঙ্ক কোড, যেমন একটি হ্যান্ডলার বা কন্ট্রোলার | `await arun(UserService.get_all())` | সার্ভার ব্লক না করেই |

```nexy filename="src/routes/users/index.nexy"
---
from src.configs.db import run
from src.services.user_service import UserService
users = run(UserService.get_all())
---
```

কচ্ছপ প্রথমবার সংযোগ করে তাদের মধ্যে একজনকে ডাকা হয়। একটি `async def` থেকে মডেলটিকে কল করুন
(`await UserModel.all()` একটি পরিষেবার ভিতরে), মডিউল স্তরে নয়: একটি কোরোটিনের বাইরে একটি কল চলে
কচ্ছপ সংযুক্ত হওয়ার আগে।

`TORTOISE_ORM` (`src/configs/db.py`-এর `models` এন্ট্রিতে মডেল ধারণ করে এমন প্রতিটি মডিউলের তালিকা করুন।
ভারা ব্যবহারকারী মডেল এবং `aerich.models` তালিকাভুক্ত; একটি মডিউলের একটি মডেল যা তালিকাভুক্ত নয়
পাওয়া গেছে

## দেশান্তর

`nx migrate` আপনার ORM-এর জন্য টুল বাছাই করে: SQLModel এর জন্য Alembic এবং SQLAlchemy, এরিচ এর জন্য
কচ্ছপ-ORM.

| আদেশ | করে |
|---|---|
| `nx migrate --init` | প্রকল্পের জন্য মাইগ্রেশন টুল শুরু করুন |
| `nx migrate -m "add users"` | আপনার মডেল পরিবর্তনগুলি থেকে একটি মাইগ্রেশন তৈরি করুন |
| `nx migrate --upgrade` | মুলতুবি মাইগ্রেশন প্রয়োগ করুন |

Aerich এর সাথে, প্রথম `nx migrate` রান `aerich init-db`, যা প্রথম মাইগ্রেশন এবং
একসাথে টেবিল; পরেরগুলো রান করে `aerich migrate --name "..."`, এবং `--upgrade` রান করে
`aerich upgrade`।

`nx migrate` একটি পরিষ্কার বার্তা দিয়ে থামে যখন `DATABASE_URL` অনুপস্থিত থাকে বা ডাটাবেস হতে পারে না
পৌঁছেছে (শুধুমাত্র অ্যালেম্বিক: এরিচ তার নিজস্ব ত্রুটিগুলি রিপোর্ট করে)।

### প্রথম স্থানান্তর আপনার জন্য করা হয়েছে

আপনি যখন একটি ORM চয়ন করেন এবং একটি ডাটাবেস URL দেন, `nx new` মাইগ্রেশন টুল সেট আপ করে, তৈরি করে
প্রথম স্থানান্তর এবং এটি প্রয়োগ করে, তাই ব্যবহারকারীর পৃষ্ঠাটি প্রথম `nexy dev`-এ উত্তর দেয়। অভিবাসন
টুল (`alembic` বা `aerich`) ওআরএম-এর সাথে প্রকল্পে ইনস্টল করা হয়।

যদি ডাটাবেস উত্তর না দেয় (একটি PostgreSQL সার্ভার যেটি চলছে না, একটি অনুপস্থিত ড্রাইভার), `nx new`
কেন বলে, মাইগ্রেশন এড়িয়ে যায় এবং যখন এটি প্রস্তুত হয় তখন চালানোর জন্য দুটি কমান্ড তালিকাভুক্ত করে:

```bash
nexy migrate -m "create tables"
nexy migrate --upgrade
```

টেবিলের অস্তিত্ব না থাকা পর্যন্ত, ডাটাবেস পড়ার একটি পৃষ্ঠা "এমন কোনো টেবিল" দিয়ে ব্যর্থ হয়।

### একটি মডেল যোগ করুন

অ্যালেম্বিক ডাটাবেসকে মডেলের সাথে তুলনা করে যা `alembic/env.py` আমদানি করে। একটি নতুন মডেল
ব্যবহারকারী মডেলের পাশে সেই মডিউলটি সেখানে আমদানি না হওয়া পর্যন্ত মডিউলটি দেখা যায় না:

```python filename="alembic/env.py"
import src.models.user_model  # noqa: F401
import src.models.post_model  # noqa: F401
```

Tortoise-ORM-এর জন্য, পরিবর্তে `TORTOISE_ORM`-এ মডিউলটি তালিকাভুক্ত করুন (উপরে দেখুন)।

## পরবর্তী ধাপ

- [টেস্টিং](testing.md): একটি অস্থায়ী ডাটাবেসের বিরুদ্ধে পরীক্ষা পরিচালনাকারী
- [কনফিগ](../reference/config.md)
- [মোতায়েন](../deployment/README.md): উৎপাদনে `DATABASE_URL` সেট করুন