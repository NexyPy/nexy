# Use MySQL ou MariaDB com Nexy

Para usar MySQL ou MariaDB com Nexy, instale o driver `pymysql`, defina `DATABASE_URL` como uma URL `mysql+pymysql://` ou `mariadb+pymysql://` com `charset=utf8mb4` e consulte-o através de SQLModel.

## Execute MySQL ou MariaDB localmente

```bash
docker run --name nexy-mysql -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=app -p 3306:3306 -d mysql:8.4
docker run --name nexy-mariadb -e MARIADB_ROOT_PASSWORD=secret -e MARIADB_DATABASE=app -p 3306:3306 -d mariadb:11
```

## Instale o driver

```bash
uv add pymysql
```

`pymysql` é puro Python e não precisa de mais nada. Para código assíncrono, `aiomysql` usa-o abaixo:

```bash
uv add aiomysql
```

## A cadeia de conexão

```bash filename=".env"
DATABASE_URL=mysql+pymysql://root:secret@localhost:3306/app?charset=utf8mb4
```

| URL | Servidor e driver |
|---|---|
| `mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL, sincronizar |
| `mariadb+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MariaDB, sincronizado, com o próprio SQL do MariaDB |
| `mysql+aiomysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL ou MariaDB, assíncrono |

Keep `charset=utf8mb4`: O `utf8` do MySQL armazena três bytes por caractere, e um emoji precisa de quatro.

## O motor

O MySQL fecha uma conexão que ficou inativa por `wait_timeout` segundos, oito horas por padrão. `pool_recycle` elimina conexões antes disso e `pool_pre_ping` captura o resto:

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

Sem eles, o primeiro pedido da manhã responde `MySQL server has gone away`.

## Um modelo: dê um comprimento às cordas

MySQL precisa de um comprimento em cada `VARCHAR`. SQLModel escreve `VARCHAR(255)` para um `str` sem nenhum; defina `max_length` onde você sabe o tamanho e use `Text` para conteúdo longo:

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

Um `VARCHAR` exclusivo ou indexado deve caber no índice: 3072 bytes com InnoDB, portanto, até 768 caracteres em `utf8mb4`.

## Uma sessão por solicitação

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## Ler e escrever de um manipulador

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

## Uma chave duplicada é um `409`

Um segundo artigo com o mesmo slug quebra o índice exclusivo. Capture o erro e responda com um status:

```python filename="src/rotas/api/artigos/[slug].py"
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

## Ler de uma página

```python filename="src/services/articles.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.article_model import Article


def latest_articles() -> list[Article]:
    with Session(engine) as session:
        return list(session.exec(select(Article).order_by(Article.id.desc()).limit(5)))
```

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

Somente os nomes atribuídos no nível superior do frontmatter alcançam o modelo, portanto a consulta reside em uma função.

## Upserts

MySQL e MariaDB escrevem um upsert como `INSERT ... ON DUPLICATE KEY UPDATE`:

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

## Pesquisa de texto completo

Adicione um índice `FULLTEXT` em uma migração e consulte-o com `MATCH ... AGAINST`:

```python filename="alambique/versions/xxxx_article_search.py"
def upgrade() -> None:
    op.execute("CREATE FULLTEXT INDEX article_search ON article (title, body)")
```

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

## Migrações

```bash
nx migrate --init
nx migrate -m "create articles"
nx migrate --upgrade
```

O MySQL confirma cada `CREATE` e `ALTER` por conta própria, então uma migração que falha no meio permanece metade aplicada: mantenha as migrações pequenas, uma alteração cada.

## Assíncrono com `aiomysql`

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

## MySQL ou MariaDB: o que difere

| | MySQL 8 | MariaDB 11 |
|---|---|---|
| Esquema de URL | `mysql+pymysql://` | `mariadb+pymysql://` |
| Coluna `JSON` | tipo nativo | um alias de `LONGTEXT` com um cheque |
| `RETURNING` | não | sim, em `INSERT` e `DELETE` |
| Sequências | não | `CREATE SEQUENCE` |

O código desta página é executado em ambos.

## MySQL gerenciado

| Serviço | O que muda |
|---|---|
| Escala Planetária | adicione `?ssl_ca=/etc/ssl/certs/ca-certificates.crt`; sem chaves estrangeiras por padrão |
| Amazon RDS, Aurora, Cloud SQL, Azure | permitir a rede do aplicativo e usar TLS |

## Próximas etapas

- [Bancos de dados](../guides/databases.md)
- [Use PostgreSQL com Nexy](postgresql.md)
- [Use SQLite com Nexy](sqlite.md)
