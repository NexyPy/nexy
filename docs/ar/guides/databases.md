# قواعد البيانات

`nx new` يمكن أن يدعم طبقة نموذجية باستخدام SQLModel، SQLAlchemy أو Tortoise-ORM. لا يقوم Nexy بتغليف ORM: يمكنك استخدامه مباشرةً من المعالجات والصفحات.

## ما تضيفه السقالة

| ملف | الغرض |
|---|---|
| `src/configs/db.py` | المحرك (SQLModel، SQLAlchemy) أو إعدادات `TORTOISE_ORM` |
| `src/models/` | فئات نموذجية |
| `src/services/` | الوظائف التي تستعلم عن النماذج |
| `.env` | `DATABASE_URL`، يتم كتابته عند إعطاء عنوان URL لقاعدة البيانات أثناء `nx new` |

تأتي سلسلة الاتصال من متغير البيئة `DATABASE_URL`. عندما يتم عدم ضبطه، يعود محرك السقالات إلى ملف SQLite محلي، `dev.db`.

## استخدام الخدمة في الصفحة

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

## استخدم خدمة في معالج API

```python filename="src/routes/api/users.py"
from src.services.user_service import UserService


async def GET():
    return UserService.get_all()
```
<!-- /router -->

<!-- router:modular -->
تستدعي وحدة التحكم الخدمة، وتمرر الصفوف إلى طريقة العرض الخاصة بها أو ترجعها بتنسيق JSON:

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

## Tortoise-ORM غير متزامن

يتم تشغيل الصفحة في حلقة حدث الخادم ولا يمكنها الانتظار، لذلك يفشل `asyncio.run(...)` هناك مع "لا يمكن استدعاؤها من حلقة حدث قيد التشغيل". السقالة `src/configs/db.py` تعطي Tortoise حلقة خاصة بها، في خيط واحد، ومساعدين يرسلان لها كوروتين:

| أين أنت | اتصل | هل |
|---|---|---|
| رمز المزامنة، مثل صفحة | `run(UserService.get_all())` | تشغيله وإرجاع النتيجة |
| رمز غير متزامن، مثل معالج أو وحدة تحكم | `await arun(UserService.get_all())` | نفس الشيء، دون حظر الخادم |

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
وحدة التحكم غير متزامنة: تنتظر الخدمة من خلال `arun`، ويظهر العرض الصفوف فقط:

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

Tortoise يتصل أول مرة يتم استدعاء أحدهما. استدعاء النموذج من `async def` (`await UserModel.all()` داخل الخدمة)، وليس على مستوى الوحدة: يتم تشغيل مكالمة خارج coroutine قبل اتصال Tortoise.

قم بإدراج كل وحدة تحتوي على نماذج في `TORTOISE_ORM` (المدخل `models` في `src/configs/db.py`). تسرد السقالة نموذج المستخدم و `aerich.models`؛ لم يتم العثور على نموذج في الوحدة النمطية غير المدرجة.

## الهجرات

`nx migrate` يختار الأداة لـ ORM الخاص بك: Alembic لـ SQLModel و SQLAlchemy، Aerich لـ Tortoise-ORM.

| القيادة | هل |
|---|---|
| `nx migrate --init` | تهيئة أداة الترحيل للمشروع |
| `nx migrate -m "add users"` | إنشاء ترحيل من تغييرات النموذج الخاص بك |
| `nx migrate --upgrade` | تطبيق عمليات الترحيل المعلقة |

مع Aerich، يتم تشغيل `nx migrate` الأول `aerich init-db`، مما يؤدي إلى إنشاء الترحيل الأول والجداول معًا؛ التالية تجري `aerich migrate --name "..."`، و `--upgrade` تجري `aerich upgrade`.

`nx migrate` يتوقف برسالة واضحة عندما يكون `DATABASE_URL` مفقودًا أو لا يمكن الوصول إلى قاعدة البيانات (Alembic فقط: يبلغ Aerich عن الأخطاء الخاصة به).

### الهجرة الأولى مصنوعة لك

عندما تختار ORM وتعطي عنوان URL لقاعدة البيانات، يقوم `nx new` بإعداد أداة الترحيل، وإنشاء أول ترحيل وتطبيقه، بحيث تجيب صفحة المستخدمين على `nexy dev` الأول. تم تثبيت أداة الترحيل (`alembic` أو `aerich`) في المشروع باستخدام ORM.

إذا لم تستجب قاعدة البيانات (خادم PostgreSQL لا يعمل، برنامج تشغيل مفقود)، `nx new` يوضح السبب، ويتخطى الترحيل ويسرد الأمرين المطلوب تشغيلهما عندما يكون جاهزًا:

```bash
nexy migrate -m "create tables"
nexy migrate --upgrade
```

وإلى أن توجد الجداول، تفشل الصفحة التي تقرأ قاعدة البيانات مع ظهور عبارة "لا يوجد مثل هذا الجدول".

### إضافة نموذج

Alembic يقارن قاعدة البيانات مع النماذج التي يستوردها `alembic/env.py`. لا يتم رؤية النموذج الموجود في وحدة نمطية جديدة حتى يتم استيراد تلك الوحدة هناك، بجوار نموذج المستخدم:

```python filename="الإنبك/env.py"
import src.models.user_model  # noqa: F401
import src.models.post_model  # noqa: F401
```

بالنسبة إلى Tortoise-ORM، قم بإدراج الوحدة في `TORTOISE_ORM` بدلاً من ذلك (انظر أعلاه).

## الخطوات التالية

- [الاختبار ](testing.md): اختبار المعالجات مقابل قاعدة بيانات مؤقتة
- [التكوين](../reference/config.md)
- [نشر ](../deployment/README.md): تعيين `DATABASE_URL` في الإنتاج
