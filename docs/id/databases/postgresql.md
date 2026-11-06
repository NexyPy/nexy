# Gunakan PostgreSQL dengan Nexy

Untuk menggunakan PostgreSQL dengan Nexy, instal driver `psycopg`, setel `DATABASE_URL` ke URL `postgresql+psycopg://`, dan kueri dari handler dan halaman melalui SQLModel atau SQLAlchemy.

## Jalankan PostgreSQL secara lokal

```bash
docker run --name nexy-db -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=app -p 5432:5432 -d postgres:17
```

## Instal drivernya

```bash
uv add "psycopg[binary]"
```

`psycopg` adalah driver versi 3, untuk kode sinkronisasi dan asinkron. Untuk kode async saja, `asyncpg` adalah pilihan lainnya:

```bash
uv add asyncpg
```

## String koneksi

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://postgres:secret@localhost:5432/app
```

| URL | Sopir |
|---|---|
| `postgresql+psycopg://user:pass@host:5432/db` | psycopg 3, sinkronisasi dan asinkron |
| `postgresql+asyncpg://user:pass@host:5432/db` | asyncpg, hanya async |
| `postgresql://user:pass@host:5432/db` | psycopg2, jika sudah diinstal |
| `postgres://...` | ditolak oleh SQLAlchemy: ganti nama skema menjadi `postgresql+psycopg://` |

Kata sandi dengan `@`, `:` atau `/` di dalamnya dikodekan dalam persen di URL: `p@ss` adalah `p%40ss`.

## Mesinnya

Platform hosting sering kali membagikan URL `postgres://`. Konversikan di tempat mesin dibuat:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()


def database_url() -> str:
    url = os.environ["DATABASE_URL"]
    return url.replace("postgres://", "postgresql+psycopg://", 1)


engine = create_engine(database_url(), pool_size=5, max_overflow=10, pool_pre_ping=True)
```

| Opsi kolam renang | Apa fungsinya |
|---|---|
| `pool_size=5` | koneksi tetap terbuka per proses |
| `max_overflow=10` | koneksi tambahan diperbolehkan di bawah beban, ditutup setelahnya |
| `pool_pre_ping=True` | memeriksa koneksi sebelum digunakan, sehingga database yang direstart tidak ada kesalahan |

Setiap pekerja `nx start` memiliki kumpulannya sendiri: `workers × (pool_size + max_overflow)` harus tetap berada di bawah `max_connections` server.

## Model dengan tipe PostgreSQL

Kunci `uuid`, `JSONB`, array, dan `timestamptz` adalah tipe kolom asli:

```python filename="src/model/post_model.py"
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=200, index=True)
    tags: list[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    extra: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    published_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
```

## Sesi per permintaan

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## Membaca dan menulis dari seorang pawang

```python filename="src/routes/api/posts/index.py"
from pydantic import BaseModel
from sqlmodel import Session, select

from nexy.http import Depends, JSONResponse
from src.configs.session import get_session
from src.models.post_model import Post


class NewPost(BaseModel):
    title: str
    tags: list[str] = []


async def GET(tag: str | None = None, session: Session = Depends(get_session)):
    query = select(Post).order_by(Post.published_at.desc())
    if tag:
        query = query.where(Post.tags.contains([tag]))
    return session.exec(query).all()


async def POST(body: NewPost, session: Session = Depends(get_session)):
    post = Post(title=body.title, tags=body.tags)
    session.add(post)
    session.commit()
    session.refresh(post)
    return JSONResponse(post.model_dump(mode="json"), status_code=201)
```

`Post.tags.contains([tag])` adalah `@>` milik PostgreSQL: kiriman yang tagnya berisi `tag`.

## A `uuid` di URL

```python filename="src/routes/api/posts/[id].py"
import uuid

from sqlmodel import Session

from nexy.http import Depends, HTTPException
from src.configs.session import get_session
from src.models.post_model import Post


async def GET(id: uuid.UUID, session: Session = Depends(get_session)):
    post = session.get(Post, id)
    if post is None:
        raise HTTPException(status_code=404, detail="No such post")
    return post
```

Segmen yang bukan UUID menjawab `404` sebelum kueri dijalankan.

## Kueri `JSONB`

```python filename="src/layanan/posts.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.post_model import Post


def featured_posts() -> list[Post]:
    with Session(engine) as session:
        query = select(Post).where(Post.extra["featured"].as_boolean())
        return list(session.exec(query))
```

```nexy filename="src/routes/featured.nexy"
---
from src.services.posts import featured_posts

posts = featured_posts()
---
<ul>
  {% for post in posts %}
  <li>{{ post.title | e }}</li>
  {% endfor %}
</ul>
```

Pertahankan kueri dalam suatu fungsi: hanya nama yang ditetapkan di tingkat atas materi depan yang mencapai templat.

## Pencarian teks lengkap

```python filename="src/routes/api/search.py"
from sqlalchemy import func
from sqlmodel import Session, select

from nexy.http import Depends
from src.configs.session import get_session
from src.models.post_model import Post


async def GET(q: str, session: Session = Depends(get_session)):
    document = func.to_tsvector("english", Post.title)
    query = func.websearch_to_tsquery("english", q)
    rank = func.ts_rank(document, query)
    rows = session.exec(select(Post).where(document.op("@@")(query)).order_by(rank.desc()))
    return rows.all()
```

Indeks membuatnya tetap cepat di tabel besar. Tambahkan dalam migrasi:

```python filename="alembic/versions/xxxx_search_index.py"
def upgrade() -> None:
    op.execute(
        "CREATE INDEX post_title_search ON post USING GIN (to_tsvector('english', title))"
    )
```

## bagian atas

```python filename="src/layanan/tags.py"
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Field, Session, SQLModel

from src.configs.db import engine


class TagCount(SQLModel, table=True):
    tag: str = Field(primary_key=True)
    count: int = 0


def count_tag(tag: str) -> None:
    statement = insert(TagCount).values(tag=tag, count=1)
    statement = statement.on_conflict_do_update(
        index_elements=[TagCount.tag], set_={"count": TagCount.count + 1}
    )
    with Session(engine) as session:
        session.exec(statement)
        session.commit()
```

## Migrasi

```bash
nx migrate --init
nx migrate -m "create posts"
nx migrate --upgrade
```

`nx migrate` membaca `DATABASE_URL`, memeriksa apakah driver telah diinstal dan server menjawab, kemudian menjalankan Alembic. Impor setiap modul model di `alembic/env.py` sehingga autogenerate melihatnya.

## Asinkron dengan `asyncpg`

```python filename="src/configs/async_db.py"
import os

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

async_engine = create_async_engine(
    os.environ["DATABASE_URL"].replace("+psycopg", "+asyncpg", 1), pool_pre_ping=True
)


async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session
```

```python filename="src/routes/api/posts/count.py"
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from nexy.http import Depends
from src.configs.async_db import get_async_session
from src.models.post_model import Post


async def GET(session: AsyncSession = Depends(get_async_session)):
    count = (await session.exec(select(func.count()).select_from(Post))).one()
    return {"count": count}
```

psycopg 3 juga menjalankan async: `postgresql+psycopg://` berfungsi dengan `create_async_engine` juga.

## Tes dalam suatu transaksi

Setiap pengujian dijalankan di dalam transaksi yang dibatalkan, sehingga database pengujian tetap kosong:

```python filename="tes/conftest.py"
import pytest
from sqlmodel import Session, SQLModel, create_engine

from nexy.app import app
from src.configs.session import get_session

test_engine = create_engine("postgresql+psycopg://postgres:secret@localhost:5432/app_test")
SQLModel.metadata.create_all(test_engine)


@pytest.fixture(autouse=True)
def session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    app.dependency_overrides[get_session] = lambda: session
    yield session
    session.close()
    transaction.rollback()
    connection.close()
```

## Dikelola PostgreSQL

| Layanan | Perubahan apa |
|---|---|
| [Neon](neon.md) | tambahkan `?sslmode=require`; gunakan host yang dikumpulkan untuk banyak koneksi pendek |
| Supabase | formulir URL yang sama; gunakan port pooler `6543` untuk banyak pekerja |
| Amazon RDS, Cloud SQL, Azure | tambahkan `?sslmode=require`, dan izinkan jaringan aplikasi |

## Langkah selanjutnya

- [Basis Data](../guides/databases.md)
- [Gunakan Neon dengan Nexy](neon.md)
- [Gunakan SQLite dengan Nexy](sqlite.md)
