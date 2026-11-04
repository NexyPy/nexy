# قواعد البيانات

`nx new` يمكنه دعم طبقة النموذج باستخدام SQLModel أو SQLAlchemy أو Tortoise-ORM. لا يلتف Nexy
ORM: يمكنك استخدامه مباشرة من المعالجات والصفحات.

## ما تضيفه السقالة

| الملف | الغرض |
|---|---|
| `src/configs/db.py` | المحرك (SQLModel، SQLAlchemy) أو إعدادات `TORTOISE_ORM` |
| `src/models/` | فئات النموذج |
| `src/services/` | الدوال التي تستعلم عن النماذج |
| `.env` | `DATABASE_URL`، يتم كتابته عند إعطاء عنوان URL لقاعدة البيانات أثناء `nx new` |

تأتي سلسلة الاتصال من متغير البيئة `DATABASE_URL`. عندما يكون غير مضبوط،
يعود المحرك السقالي إلى ملف SQLite محلي، `dev.db`.

## استخدام خدمة في الصفحة

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

## استخدام خدمة في معالج API

```python filename="src/routes/api/users.py"
from src.services.user_service import UserService


async def GET():
    return UserService.get_all()
```

## Tortoise-ORM غير متزامن

يتم تشغيل الصفحة في حلقة حدث الخادم ولا يمكنها الانتظار، لذلك يفشل `asyncio.run(...)` هناك
"لا يمكن استدعاؤه من حلقة حدث قيد التشغيل". السقالة `src/configs/db.py` تعطي السلحفاة أ
حلقة خاصة بها، في خيط واحد، واثنين من المساعدين الذين يرسلون كوروتين إليها:

| أين أنت | اتصل | هل |
|---|---|---|
| كود المزامنة مثل صفحة | `run(UserService.get_all())` | يقوم بتشغيلها وإرجاع النتيجة |
| كود غير متزامن، مثل المعالج أو وحدة التحكم | `await arun(UserService.get_all())` | نفسه، دون حظر الخادم |

```nexy filename="src/routes/users/index.nexy"
---
from src.configs.db import run
from src.services.user_service import UserService
users = run(UserService.get_all())
---
```

تتصل السلحفاة في المرة الأولى التي يتم فيها استدعاء أحدهم. استدعاء النموذج من `async def`
(`await UserModel.all()` داخل الخدمة)، وليس على مستوى الوحدة: يتم تشغيل مكالمة خارج الكوروتين
قبل أن تتصل السلحفاة.

قم بإدراج كل وحدة تحتوي على نماذج في `TORTOISE_ORM` (المدخل `models` من `src/configs/db.py`).
تسرد السقالة نموذج المستخدم و `aerich.models`؛ نموذج في وحدة نمطية غير مدرجة ليست كذلك
وجدت.

## الهجرات

`nx migrate` يختار الأداة الخاصة بـ ORM الخاص بك: Alembic for SQLModel وSQLAlchemy، Aerich for
السلحفاة-ORM.

| الأمر | يفعل |
|---|---|
| `nx migrate --init` | تهيئة أداة الترحيل للمشروع |
| `nx migrate -m "add users"` | إنشاء ترحيل من تغييرات النموذج الخاص بك |
| `nx migrate --upgrade` | تطبيق عمليات الترحيل المعلقة |

مع Aerich، يتم تشغيل `nx migrate` الأول `aerich init-db`، مما يؤدي إلى إنشاء الهجرة الأولى و
الجداول معا؛ التالية تجري `aerich migrate --name "..."`، وتجري `--upgrade`
`aerich upgrade`.

`nx migrate` يتوقف برسالة واضحة عندما يكون `DATABASE_URL` مفقودًا أو لا يمكن أن تكون قاعدة البيانات موجودة
تم الوصول إليه (Alembic فقط: Aerich يبلغ عن أخطائه).

### تم الترحيل الأول لكم

عندما تختار ORM وتعطي عنوان URL لقاعدة البيانات، `nx new` يقوم بإعداد أداة الترحيل وإنشاء ملف
الترحيل الأول وتطبيقه، فتجيب صفحة المستخدمين على الأول `nexy dev`. الهجرة
تم تثبيت الأداة (`alembic` أو `aerich`) في المشروع باستخدام ORM.

إذا لم تستجب قاعدة البيانات (خادم PostgreSQL لا يعمل، برنامج تشغيل مفقود)، `nx new`
يوضح السبب، ويتخطى الترحيل ويسرد الأمرين المطلوب تشغيلهما عندما يكون جاهزًا:

```bash
nexy migrate -m "create tables"
nexy migrate --upgrade
```

وإلى أن توجد الجداول، تفشل الصفحة التي تقرأ قاعدة البيانات مع ظهور عبارة "لا يوجد مثل هذا الجدول".

### إضافة نموذج

يقوم Alembic بمقارنة قاعدة البيانات مع النماذج التي يستوردها `alembic/env.py`. نموذج في جديد
لا تظهر الوحدة حتى يتم استيراد تلك الوحدة هناك، بجوار نموذج المستخدم:

```python filename="الإنبك/env.py"
import src.models.user_model  # noqa: F401
import src.models.post_model  # noqa: F401
```

بالنسبة إلى Tortoise-ORM، قم بإدراج الوحدة في `TORTOISE_ORM` بدلاً من ذلك (انظر أعلاه).

## الخطوات التالية

- [الاختبار](testing.md): اختبار المعالجات مقابل قاعدة بيانات مؤقتة
- [التكوين](../reference/config.md)
-  [نشر ](../deployment/README.md)]: تعيين `DATABASE_URL` في الإنتاج