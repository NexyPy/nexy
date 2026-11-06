# Nexy এর সাথে নিয়ন ব্যবহার করুন

নিয়ন সার্ভারবিহীন PostgreSQL: একটি Nexy প্রকল্প এটি ব্যবহার করে যেমন [PostgreSQL](postgresql.md), `psycopg` ড্রাইভার সহ, `DATABASE_URL`-এ নিয়নের পুল করা সংযোগ স্ট্রিং, এবং একটি পুল যা ডাটাবেসকে ঘুমাতে গিয়ে বেঁচে থাকে।

## সংযোগ স্ট্রিং পান

নিয়ন কনসোলে, **কানেক্ট** প্রতিটি শাখার জন্য দুটি স্ট্রিং দেখায়:

| স্ট্রিং | হোস্ট | জন্য এটি ব্যবহার করুন |
|---|---|---|
| পুল করা | `ep-xxx-pooler.region.aws.neon.tech` | অ্যাপ: অনেক ছোট সংযোগ, PgBouncer এর মাধ্যমে |
| সরাসরি | `ep-xxx.region.aws.neon.tech` | মাইগ্রেশন এবং দীর্ঘ সেশন |

একমাত্র পার্থক্য হল হোস্ট নামের `-pooler`।

## ড্রাইভার ইনস্টল করুন

```bash
uv add "psycopg[binary]"
```

HTTP এর উপর নিয়নের সার্ভারহীন ড্রাইভার JavaScript; Python থেকে সংযোগটি TCP এবং TLS-এর উপর সাধারণ PostgreSQL।

## দুটি URL

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3-pooler.eu-central-1.aws.neon.tech/app?sslmode=require
DIRECT_DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3.eu-central-1.aws.neon.tech/app?sslmode=require
```

নিয়ন তার স্ট্রিংগুলিকে `postgresql://...` হিসাবে কপি করে: `postgresql` এর পরে `+psycopg` যোগ করুন। কনসোল এটি যোগ করার সময় `sslmode=require`, এবং `channel_binding=require` রাখুন।

## ইঞ্জিন

একটি নিয়ন কম্পিউট নিষ্ক্রিয় থাকলে তা স্থগিত করে, যা আপনার পুলের সংযোগ বন্ধ করে দেয়। `pool_pre_ping` এটি ব্যবহার করার আগে একটি মৃতকে প্রতিস্থাপন করে, এবং `pool_recycle` নিয়নের আগে সংযোগ ড্রপ করে:

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

সাসপেন্ডের পর প্রথম অনুরোধটি অপেক্ষা করে যখন গণনা শুরু হয়, কয়েকশ মিলিসেকেন্ড। প্রোডাকশন শাখায় অটোসাসপেন্ড বন্ধ করুন যদি এটি আপনার কাছে গুরুত্বপূর্ণ হয়।

## একজন মডেল এবং একজন হ্যান্ডলার

বাকিটা PostgreSQL। একটি মডেল:

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

## মাইগ্রেশন সরাসরি URL এর মাধ্যমে যায়

পুল করা হোস্টের সামনে PgBouncer ক্লায়েন্টদের মধ্যে সংযোগ শেয়ার করে, যা সংক্ষিপ্ত প্রশ্নগুলির জন্য উপযুক্ত, একটি মাইগ্রেশনের দীর্ঘ সেশন নয়। `nx migrate` পড়ে `DATABASE_URL`, তাই সেই কমান্ডের জন্য সরাসরি হোস্টের দিকে নির্দেশ করুন:

```bash
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate -m "create visits"
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate --upgrade
```

`alembic/env.py` `src/configs/db.py` এর ইঞ্জিন ব্যবহার করে, যা একই পরিবর্তনশীলকে পড়ে।

## পুলার পিছনে বিবৃতি প্রস্তুত

psycopg একটি প্রশ্ন প্রস্তুত করে যা এটি পাঁচবার চালানো হয়েছে। যদি পুল করা হোস্ট উত্তর দেয় `prepared statement "_pg3_0" does not exist`, তাহলে সেটি বন্ধ করুন:

```python filename="src/configs/db.py"
engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"prepare_threshold": None},
)
```

`asyncpg` এর সাথে, সেটিং হল `connect_args={"statement_cache_size": 0}`।

## উন্নয়ন এবং পূর্বরূপ জন্য শাখা

একটি নিয়ন শাখা একটি ডাটাবেসের একটি অনুলিপি, যা এক সেকেন্ডে তৈরি করা হয়। ডেভেলপার প্রতি একজন, বা প্রতি টান অনুরোধ, পরীক্ষার ডেটা উৎপাদন থেকে দূরে রাখে:

```bash
neonctl branches create --name dev-ada
neonctl connection-string dev-ada --pooled
```

সেই স্ট্রিংটিকে ডেভেলপারের `.env` বা পূর্বরূপ স্থাপনার পরিবেশে রাখুন।

## টেস্ট

তাদের জন্য তৈরি একটি শাখার বিরুদ্ধে পরীক্ষাগুলি চালান, একটি লেনদেনের ভিতরে যা রোল ব্যাক করা হয়েছে: দেখুন [একটি লেনদেনের পরীক্ষাগুলি](postgresql.md#tests-in-a-transaction)।

## পরবর্তী পদক্ষেপ

- [ব্যবহার করুন PostgreSQL Nexy সহ ](postgresql.md): প্রকার, অনুসন্ধান, আপসার্ট এবং অ্যাসিঙ্ক
- [ডাটাবেস](../guides/databases.md)
- [স্থাপন ](../deployment/README.md)
