# Gunakan MySQL atau MariaDB dengan Nexy

Untuk menggunakan MySQL atau MariaDB dengan Nexy, instal driver `pymysql`, setel `DATABASE_URL` ke URL `mysql+pymysql://` atau `mariadb+pymysql://` dengan `charset=utf8mb4`, dan kueri melalui SQLModel.

## Jalankan MySQL atau MariaDB secara lokal

```bash
docker run --name nexy-mysql -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=app -p 3306:3306 -d mysql:8.4
docker run --name nexy-mariadb -e MARIADB_ROOT_PASSWORD=secret -e MARIADB_DATABASE=app -p 3306:3306 -d mariadb:11
```

## Instal drivernya

```bash
uv add pymysql
```

`pymysql` adalah murni Python dan tidak memerlukan apa pun lagi. Untuk kode async, `aiomysql` menggunakannya di bawah:

```bash
uv add aiomysql
```

## String koneksi

```bash filename=".env"
DATABASE_URL=mysql+pymysql://root:secret@localhost:3306/app?charset=utf8mb4
```

| URL | Server dan pengemudi |
|---|---|
| `mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL, sinkronisasi |
| `mariadb+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MariaDB, sinkronkan, dengan SQL MariaDB sendiri |
| `mysql+aiomysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL atau MariaDB, asinkron |

Simpan `charset=utf8mb4`: `utf8` MySQL menyimpan tiga byte per karakter, dan sebuah emoji membutuhkan empat byte.

## Mesinnya

MySQL menutup koneksi yang tidak aktif selama `wait_timeout` detik, delapan jam secara default. `pool_recycle` memutuskan koneksi sebelum itu, dan `pool_pre_ping` menangkap sisanya:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
)
```

Tanpa mereka, permintaan pertama di pagi hari akan terjawab `MySQL server has gone away`.

## Model: beri panjang string

MySQL membutuhkan panjang pada setiap `VARCHAR`. SQLModel menulis `VARCHAR(255)` untuk `str` tanpa siapa pun; atur `max_length` di mana Anda mengetahui ukurannya, dan gunakan `Text` untuk konten panjang:

```python filename="src/model/article_model.py"
from datetime import datetime

from sqlalchemy import Column, DateTime, Text, func
from sqlmodel import Field, SQLModel


class Article(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(max_length=120, unique=True)
    title: str = Field(max_length=200)
    body: str = Field(sa_column=Column(Text))
    created_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime, server_default=func.now())
    )
```

`VARCHAR` yang unik atau terindeks harus sesuai dengan indeks: 3072 byte dengan InnoDB, sehingga hingga 768 karakter dalam `utf8mb4`.

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

<!-- router:fbr,custom -->
```python filename="src/routes/api/articles/index.py"
from pydantic import BaseModel
from sqlmodel import Session, select

from nexy.http import Depends, JSONResponse
from src.configs.session import get_session
from src.models.article_model import Article


class NewArticle(BaseModel):
    slug: str
    title: str
    body: str


async def GET(session: Session = Depends(get_session)):
    return session.exec(select(Article).order_by(Article.id.desc()).limit(20)).all()


async def POST(body: NewArticle, session: Session = Depends(get_session)):
    article = Article(**body.model_dump())
    session.add(article)
    session.commit()
    session.refresh(article)
    return JSONResponse(article.model_dump(mode="json"), status_code=201)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/articles/articles_api_controller.py"
from pydantic import BaseModel
from sqlmodel import Session, select

from nexy.decorators import Controller
from nexy.http import Depends, JSONResponse
from src.configs.session import get_session
from src.models.article_model import Article


class NewArticle(BaseModel):
    slug: str
    title: str
    body: str


@Controller("/api/articles")
class ArticlesApiController:
    async def get(self, session: Session = Depends(get_session)):
        return session.exec(select(Article).order_by(Article.id.desc()).limit(20)).all()

    async def post(self, body: NewArticle, session: Session = Depends(get_session)):
        article = Article(**body.model_dump())
        session.add(article)
        session.commit()
        session.refresh(article)
        return JSONResponse(article.model_dump(mode="json"), status_code=201)
```

Cantumkan pengontrol di `controllers` modul root.
<!-- /router -->

## Kunci duplikat adalah `409`

Artikel kedua dengan siput yang sama merusak indeks unik. Tangkap kesalahannya dan jawab dengan status:

<!-- router:fbr,custom -->
```python filename="src/rute/api/artikel/[siput].py"
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from nexy.http import Depends, HTTPException
from src.configs.session import get_session
from src.models.article_model import Article


class Rename(BaseModel):
    slug: str


async def PATCH(slug: str, body: Rename, session: Session = Depends(get_session)):
    article = session.exec(select(Article).where(Article.slug == slug)).first()
    if article is None:
        raise HTTPException(status_code=404, detail="No such article")
    article.slug = body.slug
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Slug already taken")
    return article
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/articles/articles_by_slug_api_controller.py"
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from nexy.decorators import Controller
from nexy.http import Depends, HTTPException
from src.configs.session import get_session
from src.models.article_model import Article


class Rename(BaseModel):
    slug: str


@Controller("/api/articles/{slug}")
class ArticlesBySlugApiController:
    async def patch(self, slug: str, body: Rename, session: Session = Depends(get_session)):
        article = session.exec(select(Article).where(Article.slug == slug)).first()
        if article is None:
            raise HTTPException(status_code=404, detail="No such article")
        article.slug = body.slug
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=409, detail="Slug already taken")
        return article
```

Cantumkan pengontrol di `controllers` modul root.
<!-- /router -->

## Membaca dari satu halaman

```python filename="src/layanan/artikel.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.article_model import Article


def latest_articles() -> list[Article]:
    with Session(engine) as session:
        return list(session.exec(select(Article).order_by(Article.id.desc()).limit(5)))
```

<!-- router:fbr,custom -->
```nexy filename="src/rute/artikel.nexy"
---
from src.services.articles import latest_articles

articles = latest_articles()
---
<ul>
  {% for article in articles %}
  <li><a href="/articles/{{ article.slug | e }}">{{ article.title | e }}</a></li>
  {% endfor %}
</ul>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/articles/articles_view.nexy"
---
from src.services.articles import latest_articles

articles = latest_articles()
---
<ul>
  {% for article in articles %}
  <li><a href="/articles/{{ article.slug | e }}">{{ article.title | e }}</a></li>
  {% endfor %}
</ul>
```

```python filename="src/apps/articles/articles_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/articles")
class ArticlesController:
    async def get(self):
        return useViews("src/apps/articles/articles_view.nexy")
```
<!-- /router -->

Hanya nama yang ditetapkan di tingkat atas frontmatter yang mencapai templat, sehingga kueri berada dalam suatu fungsi.

## bagian atas

MySQL dan MariaDB menulis upsert sebagai `INSERT ... ON DUPLICATE KEY UPDATE`:

```python filename="src/services/counters.py"
from sqlalchemy.dialects.mysql import insert
from sqlmodel import Field, Session, SQLModel

from src.configs.db import engine


class PageView(SQLModel, table=True):
    path: str = Field(primary_key=True, max_length=255)
    views: int = 0


def count_view(path: str) -> None:
    statement = insert(PageView).values(path=path, views=1)
    statement = statement.on_duplicate_key_update(views=PageView.views + 1)
    with Session(engine) as session:
        session.exec(statement)
        session.commit()
```

## Pencarian teks lengkap

Tambahkan indeks `FULLTEXT` dalam migrasi, lalu kueri dengan `MATCH ... AGAINST`:

```python filename="alembic/versions/xxxx_article_search.py"
def upgrade() -> None:
    op.execute("CREATE FULLTEXT INDEX article_search ON article (title, body)")
```

<!-- router:fbr,custom -->
```python filename="src/routes/api/search.py"
from sqlalchemy import text
from sqlmodel import Session, select

from nexy.http import Depends
from src.configs.session import get_session
from src.models.article_model import Article


async def GET(q: str, session: Session = Depends(get_session)):
    match = text("MATCH (title, body) AGAINST (:q IN NATURAL LANGUAGE MODE)")
    return session.exec(select(Article).where(match.bindparams(q=q))).all()
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/search/search_api_controller.py"
from sqlalchemy import text
from sqlmodel import Session, select

from nexy.decorators import Controller
from nexy.http import Depends
from src.configs.session import get_session
from src.models.article_model import Article


@Controller("/api/search")
class SearchApiController:
    async def get(self, q: str, session: Session = Depends(get_session)):
        match = text("MATCH (title, body) AGAINST (:q IN NATURAL LANGUAGE MODE)")
        return session.exec(select(Article).where(match.bindparams(q=q))).all()
```

Cantumkan pengontrol di `controllers` modul root.
<!-- /router -->

## Migrasi

```bash
nx migrate --init
nx migrate -m "create articles"
nx migrate --upgrade
```

MySQL mengkomit masing-masing `CREATE` dan `ALTER` sendiri-sendiri, sehingga migrasi yang gagal di tengah jalan akan tetap setengah diterapkan: jaga agar migrasi tetap kecil, masing-masing satu perubahan.

## Asinkron dengan `aiomysql`

```python filename="src/configs/async_db.py"
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

load_dotenv()

async_engine = create_async_engine(
    os.environ["DATABASE_URL"].replace("+pymysql", "+aiomysql", 1), pool_recycle=3600
)


async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session
```

## MySQL atau MariaDB: apa bedanya

| | MySQL8 | MariaDB 11 |
|---|---|---|
| Skema URL | `mysql+pymysql://` | `mariadb+pymysql://` |
| `JSON` kolom | tipe asli | alias `LONGTEXT` dengan tanda centang |
| `RETURNING` | tidak | ya, pada `INSERT` dan `DELETE` |
| Urutan | tidak | `CREATE SEQUENCE` |

Kode halaman ini berjalan pada keduanya.

## MySQL yang dikelola

| Layanan | Perubahan apa |
|---|---|
| Skala Planet | tambahkan `?ssl_ca=/etc/ssl/certs/ca-certificates.crt`; tidak ada kunci asing secara default |
| Amazon RDS, Aurora, Cloud SQL, Azure | izinkan jaringan aplikasi, dan gunakan TLS |

## Langkah selanjutnya

- [Basis Data](../guides/databases.md)
- [Gunakan PostgreSQL dengan Nexy](postgresql.md)
- [Gunakan SQLite dengan Nexy](sqlite.md)
