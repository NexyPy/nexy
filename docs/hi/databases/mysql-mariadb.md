# नेक्सी के साथ MySQL या MariaDB का उपयोग करें

नेक्सी के साथ MySQL या MariaDB का उपयोग करने के लिए, `pymysql` ड्राइवर स्थापित करें, `DATABASE_URL` को `mysql+pymysql://` या `mariadb+pymysql://` URL के साथ `charset=utf8mb4` पर सेट करें, और इसे SQLModel के माध्यम से क्वेरी करें।

## स्थानीय रूप से MySQL या MariaDB चलाएँ

```bash
docker run --name nexy-mysql -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=app -p 3306:3306 -d mysql:8.4
docker run --name nexy-mariadb -e MARIADB_ROOT_PASSWORD=secret -e MARIADB_DATABASE=app -p 3306:3306 -d mariadb:11
```

## ड्राइवर स्थापित करें

```bash
uv add pymysql
```

`pymysql` शुद्ध है Python और किसी और चीज़ की आवश्यकता नहीं है। एसिंक कोड के लिए, `aiomysql` इसे नीचे उपयोग करता है:

```bash
uv add aiomysql
```

## कनेक्शन स्ट्रिंग

```bash filename=".env"
DATABASE_URL=mysql+pymysql://root:secret@localhost:3306/app?charset=utf8mb4
```

| यूआरएल | सर्वर और ड्राइवर |
|---|---|
| `mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL, सिंक |
| `mariadb+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MariaDB, सिंक, MariaDB के अपने SQL के साथ |
| `mysql+aiomysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL या MariaDB, async |

`charset=utf8mb4` रखें: MySQL का `utf8` प्रति वर्ण तीन बाइट्स संग्रहीत करता है, और एक इमोजी के लिए चार की आवश्यकता होती है।

## इंजन

MySQL उस कनेक्शन को बंद कर देता है जो डिफ़ॉल्ट रूप से आठ घंटे, `wait_timeout` सेकंड के लिए निष्क्रिय रहता है। `pool_recycle` उससे पहले कनेक्शन छोड़ देता है, और `pool_pre_ping` बाकी को पकड़ लेता है:

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

उनके बिना, सुबह का पहला अनुरोध उत्तर देता है `MySQL server has gone away`।

## एक मॉडल: तारों को एक लंबाई दें

MySQL को प्रत्येक `VARCHAR` पर एक लंबाई की आवश्यकता होती है। SQLModel बिना किसी के `str` के लिए `VARCHAR(255)` लिखता है; `max_length` को वहां सेट करें जहां आप आकार जानते हैं, और लंबी सामग्री के लिए `Text` का उपयोग करें:

```python filename="src/models/article_model.py"
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

एक अद्वितीय या अनुक्रमित `VARCHAR` को सूचकांक में फिट होना चाहिए: InnoDB के साथ 3072 बाइट्स, इसलिए `utf8mb4` में 768 वर्ण तक।

## प्रति अनुरोध एक सत्र

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## हैंडलर से पढ़ें और लिखें

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

नियंत्रक को रूट मॉड्यूल के `controllers` में सूचीबद्ध करें।
<!-- /router -->

## डुप्लिकेट कुंजी एक `409` है

उसी स्लग वाला दूसरा लेख अद्वितीय सूचकांक को तोड़ता है। त्रुटि पकड़ें और स्थिति के साथ उत्तर दें:

<!-- router:fbr,custom -->
```python filename="src/routes/api/articles/[slug].py"
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

नियंत्रक को रूट मॉड्यूल के `controllers` में सूचीबद्ध करें।
<!-- /router -->

## एक पेज से पढ़ें

```python filename="src/services/articles.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.article_model import Article


def latest_articles() -> list[Article]:
    with Session(engine) as session:
        return list(session.exec(select(Article).order_by(Article.id.desc()).limit(5)))
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/articles.nexy"
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

केवल फ्रंटमैटर के शीर्ष स्तर पर निर्दिष्ट नाम ही टेम्पलेट तक पहुंचते हैं, इसलिए क्वेरी एक फ़ंक्शन में रहती है।

## अप्सर्ट्स

MySQL और MariaDB इस प्रकार एक उत्तर लिखते हैं `INSERT ... ON DUPLICATE KEY UPDATE`:

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

## पूर्ण-पाठ खोज

माइग्रेशन में एक `FULLTEXT` इंडेक्स जोड़ें, फिर इसे `MATCH ... AGAINST` के साथ क्वेरी करें:

```python filename="एलेम्बिक/संस्करण/xxxx_article_search.py"
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

नियंत्रक को रूट मॉड्यूल के `controllers` में सूचीबद्ध करें।
<!-- /router -->

## पलायन

```bash
nx migrate --init
nx migrate -m "create articles"
nx migrate --upgrade
```

MySQL प्रत्येक `CREATE` और `ALTER` को स्वयं ही प्रतिबद्ध करता है, इसलिए जो माइग्रेशन आधे रास्ते में विफल हो जाता है वह आधा लागू रहता है: माइग्रेशन को छोटा रखें, प्रत्येक में एक बदलाव करें।

## `aiomysql` के साथ एसिंक

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

## MySQL या MariaDB: क्या भिन्न है

| | MySQL 8 | मारियाडीबी 11 |
|---|---|---|
| यूआरएल योजना | `mysql+pymysql://` | `mariadb+pymysql://` |
| `JSON` कॉलम | देशी प्रकार | चेक के साथ `LONGTEXT` का एक उपनाम |
| `RETURNING` | नहीं | हाँ, `INSERT` और `DELETE` पर |
| अनुक्रम | नहीं | `CREATE SEQUENCE` |

इस पेज का कोड दोनों पर चलता है.

## प्रबंधित MySQL

| सेवा | क्या बदलता है |
|---|---|
| प्लैनेटस्केल | जोड़ें `?ssl_ca=/etc/ssl/certs/ca-certificates.crt`; डिफ़ॉल्ट रूप से कोई विदेशी कुंजी नहीं |
| अमेज़ॅन आरडीएस, ऑरोरा, क्लाउड एसक्यूएल, एज़्योर | ऐप के नेटवर्क को अनुमति दें और टीएलएस का उपयोग करें |

## अगले चरण

- [डेटाबेस](../guides/databases.md)
- [उपयोग करें PostgreSQL नेक्सी के साथ](postgresql.md)
- [उपयोग करें SQLite नेक्सी के साथ](sqlite.md)
