# Gunakan Neon dengan Nexy

Neon tidak memiliki server PostgreSQL: proyek Nexy menggunakannya seperti [PostgreSQL](postgresql.md), dengan driver `psycopg`, string koneksi gabungan Neon di `DATABASE_URL`, dan kumpulan yang bertahan saat database tertidur.

## Dapatkan string koneksi

Di konsol Neon, **Connect** menampilkan dua string untuk setiap cabang:

| Tali | Tuan rumah | Gunakan untuk |
|---|---|---|
| Dikumpulkan | `ep-xxx-pooler.region.aws.neon.tech` | aplikasi: banyak koneksi pendek, melalui PgBouncer |
| Langsung | `ep-xxx.region.aws.neon.tech` | migrasi dan sesi panjang |

Perbedaannya hanya pada `-pooler` pada nama hostnya.

## Instal drivernya

```bash
uv add "psycopg[binary]"
```

Driver tanpa server Neon melalui HTTP adalah untuk JavaScript; dari Python koneksinya biasa PostgreSQL melalui TCP dan TLS.

## Kedua URL

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3-pooler.eu-central-1.aws.neon.tech/app?sslmode=require
DIRECT_DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3.eu-central-1.aws.neon.tech/app?sslmode=require
```

Neon menyalin stringnya sebagai `postgresql://...`: tambahkan `+psycopg` setelah `postgresql`. Pertahankan `sslmode=require`, dan `channel_binding=require` saat konsol menambahkannya.

## Mesinnya

Komputasi Neon ditangguhkan saat tidak aktif, sehingga menutup koneksi kumpulan Anda. `pool_pre_ping` menggantikan yang mati sebelum digunakan, dan `pool_recycle` memutuskan koneksi sebelum Neon melakukan:

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

Permintaan pertama setelah penangguhan menunggu saat komputasi dimulai, beberapa ratus milidetik. Matikan penangguhan otomatis di cabang produksi jika itu penting bagi Anda.

## Seorang model dan seorang pawang

Sisanya adalah PostgreSQL. Sebuah model:

```python filename="src/model/visit_model.py"
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

```python filename="src/routes/api/visit.py"
from sqlmodel import Session, func, select

from nexy.http import Depends
from src.configs.session import get_session
from src.models.visit_model import Visit


async def POST(path: str, session: Session = Depends(get_session)):
    session.add(Visit(path=path))
    session.commit()
    return {"visits": session.exec(select(func.count()).select_from(Visit)).one()}
```

## Migrasi melalui URL langsung

PgBouncer di depan kumpulan host berbagi koneksi antar klien, yang sesuai dengan kueri singkat, bukan sesi migrasi yang panjang. `nx migrate` berbunyi `DATABASE_URL`, jadi arahkan ke host langsung untuk perintah itu:

```bash
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate -m "create visits"
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate --upgrade
```

`alembic/env.py` menggunakan mesin `src/configs/db.py`, yang membaca variabel yang sama.

## Pernyataan yang disiapkan di belakang pooler

psycopg menyiapkan kueri yang telah dijalankan lima kali. Jika host yang dikumpulkan menjawab `prepared statement "_pg3_0" does not exist`, matikan:

```python filename="src/configs/db.py"
engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"prepare_threshold": None},
)
```

Dengan `asyncpg`, pengaturannya adalah `connect_args={"statement_cache_size": 0}`.

## Cabang untuk pengembangan dan pratinjau

Cabang Neon adalah salinan database, dibuat dalam hitungan detik. Satu per pengembang, atau per permintaan penarikan, menjauhkan data pengujian dari produksi:

```bash
neonctl branches create --name dev-ada
neonctl connection-string dev-ada --pooled
```

Letakkan string tersebut di `.env` pengembang, atau di lingkungan penerapan pratinjau.

## Tes

Jalankan pengujian terhadap cabang yang dibuat untuk mereka, di dalam transaksi yang dibatalkan: lihat [Pengujian dalam suatu transaksi](postgresql.md#tests-in-a-transaction).

## Langkah selanjutnya

- [Gunakan PostgreSQL dengan Nexy](postgresql.md): tipe, pencarian, upsert, dan async
- [Basis Data](../guides/databases.md)
- [Menyebarkan](../deployment/README.md)
