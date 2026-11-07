# ڈیٹا بیس

`nx new` ماڈل کی پرت کو SQLModel، SQLAlchemy یا ٹورٹوائز-ORM کے ساتھ سہار سکتا ہے۔ Nexy ORM کو لپیٹ نہیں کرتا: آپ اسے براہ راست ہینڈلرز اور صفحات سے استعمال کرتے ہیں۔

## پاڑ کیا جوڑتا ہے

| فائل | مقصد |
|---|---|
| `src/configs/db.py` | انجن (SQLModel، SQLAlchemy) یا `TORTOISE_ORM` ترتیبات |
| `src/models/` | ماڈل کلاسز |
| `src/services/` | فنکشنز جو ماڈلز سے استفسار کرتے ہیں۔ |
| `.env` | `DATABASE_URL`، جب آپ `nx new` کے دوران ڈیٹا بیس کا یو آر ایل دیتے ہیں تو لکھا جاتا ہے۔ |

کنکشن کی تار `DATABASE_URL` ماحولیاتی متغیر سے آتی ہے۔ جب یہ سیٹ نہیں ہوتا ہے تو، سہاروں والا انجن ایک مقامی SQLite فائل، `dev.db` میں واپس آتا ہے۔

## کسی صفحہ میں سروس استعمال کریں۔

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

## API ہینڈلر میں سروس استعمال کریں۔

```python filename="src/routes/api/users.py"
from src.services.user_service import UserService


async def GET():
    return UserService.get_all()
```
<!-- /router -->

<!-- router:modular -->
ایک کنٹرولر سروس کو کال کرتا ہے، اور قطاروں کو اس کے نظارے میں منتقل کرتا ہے یا انہیں JSON کے طور پر واپس کرتا ہے:

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

## کچھوا-ORM async ہے۔

ایک صفحہ سرور کے ایونٹ لوپ میں چلتا ہے اور اس پر انتظار نہیں کر سکتا، اس لیے وہاں `asyncio.run(...)` ناکام ہو جاتا ہے "رننگ ایونٹ لوپ سے کال نہیں کیا جا سکتا"۔ اسکافولڈ `src/configs/db.py` ایک دھاگے میں اپنا ایک لوپ Tortoise دیتا ہے، اور دو مددگار جو اس کو ایک کورٹین بھیجتے ہیں:

| جہاں آپ ہیں | کال کریں۔ | کرتا ہے۔ |
|---|---|---|
| مطابقت پذیری کوڈ، جیسے صفحہ | `run(UserService.get_all())` | اسے چلاتا ہے اور نتیجہ واپس کرتا ہے۔ |
| async کوڈ، جیسے ہینڈلر یا کنٹرولر | `await arun(UserService.get_all())` | اسی طرح، سرور کو بلاک کیے بغیر |

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
ایک کنٹرولر async ہے: یہ `arun` کے ذریعے سروس کا انتظار کر رہا ہے، اور منظر صرف قطاریں دکھاتا ہے:

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

Tortoise پہلی بار جوڑتا ہے ان میں سے کسی کو بلایا جاتا ہے۔ ماڈل کو کسی سروس کے اندر `async def` (`await UserModel.all()` سے کال کریں، ماڈیول کی سطح پر نہیں: کورٹین کے باہر کال Tortoise کے منسلک ہونے سے پہلے چلتی ہے۔

ہر اس ماڈیول کی فہرست بنائیں جو `TORTOISE_ORM` میں ماڈل رکھتا ہے (`src/configs/db.py` کی `models` اندراج)۔ سہاروں میں صارف کے ماڈل اور `aerich.models` کی فہرست دی گئی ہے۔ ماڈیول میں ایسا ماڈل نہیں ملا جو درج نہیں ہے۔

## ہجرتیں

`nx migrate` آپ کے ORM کے لیے ٹول چنتا ہے: Alembic کے لیے SQLModel اور SQLAlchemy، Aerich Tortoise-ORM کے لیے۔

| حکم | کرتا ہے۔ |
|---|---|
| `nx migrate --init` | پروجیکٹ کے لیے منتقلی کے آلے کو شروع کریں۔ |
| `nx migrate -m "add users"` | اپنے ماڈل کی تبدیلیوں سے ایک ہجرت بنائیں |
| `nx migrate --upgrade` | زیر التواء ہجرتیں لاگو کریں۔ |

Aerich کے ساتھ، پہلا `nx migrate` چلتا ہے `aerich init-db`، جو پہلی منتقلی اور میزیں ایک ساتھ بناتا ہے؛ اگلے والے دوڑتے ہیں `aerich migrate --name "..."`، اور `--upgrade` رنز `aerich upgrade`۔

`nx migrate` ایک واضح پیغام کے ساتھ رک جاتا ہے جب `DATABASE_URL` غائب ہو یا ڈیٹا بیس تک نہیں پہنچا جا سکتا (Alembic صرف: Aerich اپنی غلطیوں کی اطلاع دیتا ہے)۔

### پہلی ہجرت آپ کے لیے کی گئی ہے۔

جب آپ ایک ORM کا انتخاب کرتے ہیں اور ڈیٹا بیس یو آر ایل دیتے ہیں تو، `nx new` منتقلی کے آلے کو ترتیب دیتا ہے، پہلی منتقلی بناتا ہے اور اسے لاگو کرتا ہے، لہذا صارف صفحہ پہلے `nexy dev` پر جواب دیتا ہے۔ ORM کے ساتھ پروجیکٹ میں منتقلی کا آلہ (`alembic` یا `aerich`) نصب ہے۔

اگر ڈیٹا بیس جواب نہیں دیتا ہے (ایک PostgreSQL سرور جو نہیں چل رہا ہے، ایک گمشدہ ڈرائیور)، `nx new` کیوں کہتا ہے، منتقلی کو چھوڑ دیتا ہے اور جب یہ تیار ہوتا ہے تو چلانے کے لیے دو کمانڈز کی فہرست دیتا ہے:

```bash
nexy migrate -m "create tables"
nexy migrate --upgrade
```

جدولوں کے موجود ہونے تک، ڈیٹا بیس کو پڑھنے والا صفحہ "ایسی کوئی میز نہیں" کے ساتھ ناکام ہو جاتا ہے۔

### ایک ماڈل شامل کریں۔

Alembic ڈیٹا بیس کا ان ماڈلز سے موازنہ کرتا ہے جو `alembic/env.py` درآمد کرتے ہیں۔ نئے ماڈیول میں ایک ماڈل اس وقت تک نہیں دیکھا جاتا جب تک کہ وہ ماڈیول وہاں درآمد نہ کیا جائے، صارف کے ماڈل کے آگے:

```python filename="alembic/env.py"
import src.models.user_model  # noqa: F401
import src.models.post_model  # noqa: F401
```

Tortoise-ORM کے لیے، ماڈیول کو `TORTOISE_ORM` میں درج کریں (اوپر دیکھیں)۔

## اگلے اقدامات

- [ٹیسٹنگ](testing.md): عارضی ڈیٹا بیس کے خلاف ٹیسٹ ہینڈلرز
- [ترتیب ](../reference/config.md)
- [تعینات کریں ](../deployment/README.md): پیداوار میں `DATABASE_URL` سیٹ کریں۔
