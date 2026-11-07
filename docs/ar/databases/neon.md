# استخدم النيون مع Nexy

نيون بدون خادم PostgreSQL: يستخدمه مشروع Nexy مثل [PostgreSQL ](postgresql.md)، مع برنامج التشغيل `psycopg`، وسلسلة اتصال نيون المجمعة في `DATABASE_URL`، وتجمع ينجو من قاعدة البيانات التي ستدخل في وضع السكون.

## الحصول على سلاسل الاتصال

في وحدة تحكم النيون، يعرض **Connect** سلسلتين لكل فرع:

| سلسلة | المضيف | استخدامه ل |
|---|---|---|
| مجمعة | `ep-xxx-pooler.region.aws.neon.tech` | التطبيق: العديد من الاتصالات القصيرة، من خلال PgBouncer |
| مباشر | `ep-xxx.region.aws.neon.tech` | الهجرات والدورات الطويلة |

والفرق الوحيد هو `-pooler` في اسم المضيف.

## تثبيت برنامج التشغيل

```bash
uv add "psycopg[binary]"
```

برنامج تشغيل Neon بدون خادم عبر HTTP مخصص لـ JavaScript؛ من Python الاتصال عادي PostgreSQL عبر TCP وTLS.

## عنواني URL اثنين

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3-pooler.eu-central-1.aws.neon.tech/app?sslmode=require
DIRECT_DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3.eu-central-1.aws.neon.tech/app?sslmode=require
```

النيون ينسخ سلاسله كـ `postgresql://...`: أضف `+psycopg` بعد `postgresql`. احتفظ بـ `sslmode=require`، و `channel_binding=require` عندما تضيفها وحدة التحكم.

## المحرك

يتم تعليق حساب النيون عندما يكون خاملاً، مما يؤدي إلى إغلاق اتصالات مجموعتك. `pool_pre_ping` يستبدل واحدًا ميتًا قبل استخدامه، ويسقط `pool_recycle` الاتصالات قبل أن يقوم النيون بما يلي:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_size=5,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=300,
)
```

ينتظر الطلب الأول بعد التوقف المرحلي بينما يبدأ الحساب، بضع مئات من المللي ثانية. قم بإيقاف تشغيل التعليق التلقائي في فرع الإنتاج إذا كان ذلك يهمك.

## نموذج ومعالج

والباقي PostgreSQL. نموذج:

```python filename="src/models/visit_model.py"
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class Visit(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    path: str
    at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
```

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

<!-- router:fbr,custom -->
```python filename="src/routes/api/visits.py"
from sqlmodel import Session, func, select

from nexy.http import Depends
from src.configs.session import get_session
from src.models.visit_model import Visit


async def POST(path: str, session: Session = Depends(get_session)):
    session.add(Visit(path=path))
    session.commit()
    return {"visits": session.exec(select(func.count()).select_from(Visit)).one()}
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/visits/visits_api_controller.py"
from sqlmodel import Session, func, select

from nexy.decorators import Controller
from nexy.http import Depends
from src.configs.session import get_session
from src.models.visit_model import Visit


@Controller("/api/visits")
class VisitsApiController:
    async def post(self, path: str, session: Session = Depends(get_session)):
        session.add(Visit(path=path))
        session.commit()
        return {"visits": session.exec(select(func.count()).select_from(Visit)).one()}
```

قم بإدراج وحدة التحكم في `controllers` من الوحدة الجذرية.
<!-- /router -->

## تتم عمليات الترحيل عبر عنوان URL المباشر

يقوم PgBouncer الموجود أمام المضيف المجمع بمشاركة الاتصالات بين العملاء، وهو ما يناسب الاستعلامات القصيرة، وليس الجلسة الطويلة للترحيل. `nx migrate` يقرأ `DATABASE_URL`، لذا قم بتوجيهه إلى المضيف المباشر لهذا الأمر:

```bash
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate -m "create visits"
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate --upgrade
```

`alembic/env.py` يستخدم محرك `src/configs/db.py` الذي يقرأ نفس المتغير.

## البيانات المعدة وراء المجمع

يقوم psycopg بإعداد استعلام تم تشغيله خمس مرات. إذا أجاب المضيف المجمع `prepared statement "_pg3_0" does not exist`، قم بإيقاف تشغيل ذلك:

```python filename="src/configs/db.py"
engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"prepare_threshold": None},
)
```

مع `asyncpg`، يكون الإعداد `connect_args={"statement_cache_size": 0}`.

## فروع للتطوير والمعاينات

فرع النيون هو نسخة من قاعدة البيانات، يتم إنشاؤها في ثانية واحدة. واحد لكل مطور، أو لكل طلب سحب، يبقي بيانات الاختبار بعيدًا عن الإنتاج:

```bash
neonctl branches create --name dev-ada
neonctl connection-string dev-ada --pooled
```

ضع هذه السلسلة في `.env` للمطور، أو في بيئة نشر المعاينة.

## الاختبارات

قم بإجراء الاختبارات على فرع تم إنشاؤه لهم، داخل معاملة تم إرجاعها: راجع [الاختبارات في معاملة](postgresql.md#tests-in-a-transaction).

## الخطوات التالية

- [استخدم PostgreSQL مع Nexy](postgresql.md): الأنواع والبحث والإدراج والمزامنة
- [قواعد البيانات](../guides/databases.md)
- [نشر](../deployment/README.md)
