# Nexy کے ساتھ نیین کا استعمال کریں۔

نیون سرور لیس ہے PostgreSQL: ایک Nexy پروجیکٹ اسے [PostgreSQL](postgresql.md) کی طرح استعمال کرتا ہے، `psycopg` ڈرائیور کے ساتھ، `DATABASE_URL` میں نیون کا پولڈ کنکشن سٹرنگ، اور ایک ایسا پول جو ڈیٹابیس کو سونے سے بچاتا ہے۔

## کنکشن کی تاریں حاصل کریں۔

نیون کنسول میں، **Connect** ہر شاخ کے لیے دو تار دکھاتا ہے:

| تار | میزبان | کے لیے استعمال کریں۔ |
|---|---|---|
| پولڈ | `ep-xxx-pooler.region.aws.neon.tech` | ایپ: بہت سے مختصر رابطے، پی جی باؤنسر کے ذریعے |
| براہ راست | `ep-xxx.region.aws.neon.tech` | ہجرت اور طویل سیشن |

فرق صرف میزبان کے نام میں `-pooler` ہے۔

## ڈرائیور انسٹال کریں۔

```bash
uv add "psycopg[binary]"
```

HTTP پر نیون کا سرور لیس ڈرائیور JavaScript کے لیے ہے۔ Python سے کنکشن TCP اور TLS پر عام PostgreSQL ہے۔

## دو URLs

```bash filename="env"
DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3-pooler.eu-central-1.aws.neon.tech/app?sslmode=require
DIRECT_DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3.eu-central-1.aws.neon.tech/app?sslmode=require
```

نیون اپنے تاروں کو `postgresql://...` کے طور پر نقل کرتا ہے: `postgresql` کے بعد `+psycopg` شامل کریں۔ رکھیں `sslmode=require`، اور `channel_binding=require` جب کنسول اسے شامل کرتا ہے۔

## انجن

نیون کمپیوٹ اس وقت معطل ہو جاتا ہے جب یہ بیکار ہوتا ہے، جو آپ کے پول کے کنکشن کو بند کر دیتا ہے۔ `pool_pre_ping` ایک مردہ کو استعمال کرنے سے پہلے اس کی جگہ لے لیتا ہے، اور `pool_recycle` نیون سے پہلے کنکشن گرا دیتا ہے:

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

معطلی کے بعد پہلی درخواست انتظار کرتی ہے جب کہ کمپیوٹ شروع ہوتا ہے، چند سو ملی سیکنڈ۔ اگر آپ کے لیے اہم ہے تو پروڈکشن برانچ پر آٹو سسپینڈ کو بند کر دیں۔

## ایک ماڈل اور ایک ہینڈلر

باقی ہے PostgreSQL۔ ایک ماڈل:

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

## منتقلی براہ راست یو آر ایل سے ہوتی ہے۔

پولڈ ہوسٹ کے سامنے پی جی باؤنسر کلائنٹس کے درمیان رابطوں کا اشتراک کرتا ہے، جو مختصر سوالات کے مطابق ہوتا ہے، نہ کہ منتقلی کے طویل سیشن کے۔ `nx migrate` پڑھتا ہے `DATABASE_URL`، تو اس کمانڈ کے لیے براہ راست میزبان کی طرف اشارہ کریں:

```bash
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate -m "create visits"
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate --upgrade
```

`alembic/env.py` `src/configs/db.py` کا انجن استعمال کرتا ہے، جو ایک ہی متغیر کو پڑھتا ہے۔

## پولر کے پیچھے بیانات تیار

psycopg ایک استفسار تیار کرتا ہے جو اس نے پانچ بار چلایا ہے۔ اگر پولڈ میزبان جواب دیتا ہے `prepared statement "_pg3_0" does not exist`، تو اسے بند کر دیں:

```python filename="src/configs/db.py"
engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"prepare_threshold": None},
)
```

`asyncpg` کے ساتھ، ترتیب `connect_args={"statement_cache_size": 0}` ہے۔

## ترقی اور پیش نظارہ کے لیے شاخیں

نیون برانچ ڈیٹا بیس کی ایک کاپی ہے، جو ایک سیکنڈ میں بنتی ہے۔ ایک فی ڈویلپر، یا فی پل کی درخواست، ٹیسٹ ڈیٹا کو پیداوار سے دور رکھتا ہے:

```bash
neonctl branches create --name dev-ada
neonctl connection-string dev-ada --pooled
```

اس سٹرنگ کو ڈویلپر کے `.env` میں، یا پیش نظارہ تعیناتی کے ماحول میں رکھیں۔

## ٹیسٹ

ان کے لیے بنائی گئی برانچ کے خلاف ٹیسٹ چلائیں، ایک ٹرانزیکشن کے اندر جو رول بیک کیا گیا ہے: دیکھیں [ٹرانزیکشن میں ٹیسٹ](postgresql.md#tests-in-a-transaction)۔

## اگلے اقدامات

- [استعمال کریں۔ PostgreSQL Nexy کے ساتھ ](postgresql.md): اقسام، تلاش، اپسرٹس اور async
- [ڈیٹا بیس](../guides/databases.md)
- [تعیناتی ](../deployment/README.md)
