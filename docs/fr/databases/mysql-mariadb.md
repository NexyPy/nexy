# Utilisez MySQL ou MariaDB avec Nexy

Pour utiliser MySQL ou MariaDB avec Nexy, installez le pilote `pymysql`, définissez `DATABASE_URL` sur une URL `mysql+pymysql://` ou `mariadb+pymysql://` avec `charset=utf8mb4` et interrogez-le via SQLModel.

## Exécutez MySQL ou MariaDB localement

```bash
docker run --name nexy-mysql -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=app -p 3306:3306 -d mysql:8.4
docker run --name nexy-mariadb -e MARIADB_ROOT_PASSWORD=secret -e MARIADB_DATABASE=app -p 3306:3306 -d mariadb:11
```

## Installer le pilote

```bash
uv add pymysql
```

`pymysql` est pur Python et n'a besoin de rien d'autre. Pour le code asynchrone, `aiomysql` l'utilise en dessous :

```bash
uv add aiomysql
```

## La chaîne de connexion

```bash filename=".env"
DATABASE_URL=mysql+pymysql://root:secret@localhost:3306/app?charset=utf8mb4
```

| URL | Serveur et pilote |
|---|---|
| `mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL, synchronisation |
| `mariadb+pymysql://user:pass@host:3306/db?charset=utf8mb4` | MariaDB, synchronisation, avec le propre SQL de MariaDB |
| `mysql+aiomysql://user:pass@host:3306/db?charset=utf8mb4` | MySQL ou MariaDB, asynchrone |

Conserver `charset=utf8mb4` : le `utf8` de MySQL stocke trois octets par caractère, et un emoji en a besoin de quatre.

## Le moteur

MySQL ferme une connexion restée inactive pendant `wait_timeout` secondes, soit huit heures par défaut. `pool_recycle` abandonne les connexions avant cela, et `pool_pre_ping` rattrape le reste :

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

Sans eux, la première demande du matin répond `MySQL server has gone away`.

## Un modèle : donner une longueur aux cordes

MySQL a besoin d'une longueur pour chaque `VARCHAR`. SQLModel écrit `VARCHAR(255)` pour un `str` sans aucun ; définissez `max_length` là où vous connaissez la taille et utilisez `Text` pour le contenu long :

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

Un `VARCHAR` unique ou indexé doit tenir dans l'index : 3072 octets avec InnoDB, donc jusqu'à 768 caractères dans `utf8mb4`.

## Une séance par demande

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## Lire et écrire à partir d'un gestionnaire

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

Répertoriez le contrôleur dans le `controllers` du module racine.
<!-- /router -->

## Une clé en double est un `409`

Un deuxième article avec le même slug casse l'index unique. Détectez l'erreur et répondez avec un statut :

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

Répertoriez le contrôleur dans le `controllers` du module racine.
<!-- /router -->

## Lire à partir d'une page

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

Seuls les noms attribués au niveau supérieur du frontmatter atteignent le modèle, la requête réside donc dans une fonction.

## Insertions

MySQL et MariaDB écrivent un upsert sous la forme `INSERT ... ON DUPLICATE KEY UPDATE` :

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

## Recherche en texte intégral

Ajoutez un index `FULLTEXT` dans une migration, puis interrogez-le avec `MATCH ... AGAINST` :

```python filename="alambic/versions/xxxx_article_search.py"
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

Répertoriez le contrôleur dans le `controllers` du module racine.
<!-- /router -->

## Migrations

```bash
nx migrate --init
nx migrate -m "create articles"
nx migrate --upgrade
```

MySQL valide chacun `CREATE` et `ALTER` individuellement, donc une migration qui échoue à moitié reste appliquée à moitié : gardez les migrations petites, une modification chacune.

## Asynchrone avec `aiomysql`

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

## MySQL ou MariaDB : ce qui diffère

| | MySQL 8 | MariaDB 11 |
|---|---|---|
| Schéma d'URL | `mysql+pymysql://` | `mariadb+pymysql://` |
| colonne `JSON` | type natif | un alias de `LONGTEXT` avec un chèque |
| `RETURNING` | non | oui, le `INSERT` et `DELETE` |
| Séquences | non | `CREATE SEQUENCE` |

Le code de cette page fonctionne sur les deux.

## MySQL géré

| Service | Quels changements |
|---|---|
| Échelle Planétaire | ajouter `?ssl_ca=/etc/ssl/certs/ca-certificates.crt` ; pas de clés étrangères par défaut |
| Amazon RDS, Aurora, Cloud SQL, Azure | autoriser le réseau de l'application et utiliser TLS |

## Prochaines étapes

- [Bases de données](../guides/databases.md)
- [Utiliser PostgreSQL avec Nexy](postgresql.md)
- [Utiliser SQLite avec Nexy](sqlite.md)
