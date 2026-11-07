# Utiliser PostgreSQL avec Nexy

Pour utiliser PostgreSQL avec Nexy, installez le pilote `psycopg`, définissez `DATABASE_URL` sur une URL `postgresql+psycopg://` et interrogez-le à partir des gestionnaires et des pages via SQLModel ou SQLAlchemy.

## Exécuter PostgreSQL localement

```bash
docker run --name nexy-db -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=app -p 5432:5432 -d postgres:17
```

## Installer le pilote

```bash
uv add "psycopg[binary]"
```

`psycopg` est la version 3 du pilote, pour le code de synchronisation et asynchrone. Pour le code asynchrone uniquement, `asyncpg` est l'autre choix :

```bash
uv add asyncpg
```

## La chaîne de connexion

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://postgres:secret@localhost:5432/app
```

| URL | Chauffeur |
|---|---|
| `postgresql+psycopg://user:pass@host:5432/db` | psycopg 3, synchronisation et asynchrone |
| `postgresql+asyncpg://user:pass@host:5432/db` | asyncpg, asynchrone uniquement |
| `postgresql://user:pass@host:5432/db` | psycopg2, s'il est installé |
| `postgres://...` | rejeté par SQLAlchemy : renommez le schéma en `postgresql+psycopg://` |

Un mot de passe contenant `@`, `:` ou `/` est codé en pourcentage dans l'URL : `p@ss` est `p%40ss`.

## Le moteur

Les plateformes d'hébergement distribuent souvent une URL `postgres://`. Convertissez-le là où le moteur est fabriqué :

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

| Option piscine | Ce que ça fait |
|---|---|
| `pool_size=5` | connexions maintenues ouvertes par processus |
| `max_overflow=10` | connexions supplémentaires autorisées sous charge, fermées après |
| `pool_pre_ping=True` | vérifie une connexion avant utilisation, donc une base de données redémarrée n'est pas une erreur |

Chaque travailleur `nx start` possède son propre pool : `workers × (pool_size + max_overflow)` doit rester sous le `max_connections` du serveur.

## Un modèle avec PostgreSQL types

Les clés `uuid`, `JSONB`, les tableaux et `timestamptz` sont des types de colonnes natifs :

```python filename="src/models/post_model.py"
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
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/posts/posts_api_controller.py"
from pydantic import BaseModel
from sqlmodel import Session, select

from nexy.decorators import Controller
from nexy.http import Depends, JSONResponse
from src.configs.session import get_session
from src.models.post_model import Post


class NewPost(BaseModel):
    title: str
    tags: list[str] = []


@Controller("/api/posts")
class PostsApiController:
    async def get(self, tag: str | None = None, session: Session = Depends(get_session)):
        query = select(Post).order_by(Post.published_at.desc())
        if tag:
            query = query.where(Post.tags.contains([tag]))
        return session.exec(query).all()

    async def post(self, body: NewPost, session: Session = Depends(get_session)):
        post = Post(title=body.title, tags=body.tags)
        session.add(post)
        session.commit()
        session.refresh(post)
        return JSONResponse(post.model_dump(mode="json"), status_code=201)
```

Répertoriez le contrôleur dans le `controllers` du module racine.
<!-- /router -->

`Post.tags.contains([tag])` est le `@>` de PostgreSQL : les publications dont les balises contiennent `tag`.

## Un `uuid` dans l'URL

<!-- router:fbr,custom -->
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
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/posts/posts_by_id_api_controller.py"
import uuid

from sqlmodel import Session

from nexy.decorators import Controller
from nexy.http import Depends, HTTPException
from src.configs.session import get_session
from src.models.post_model import Post


@Controller("/api/posts/{id}")
class PostsByIdApiController:
    async def get(self, id: uuid.UUID, session: Session = Depends(get_session)):
        post = session.get(Post, id)
        if post is None:
            raise HTTPException(status_code=404, detail="No such post")
        return post
```

Répertoriez le contrôleur dans le `controllers` du module racine.
<!-- /router -->

Un segment qui n'est pas un UUID répond `404` avant l'exécution de la requête.

## Requête `JSONB`

```python filename="src/services/posts.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.post_model import Post


def featured_posts() -> list[Post]:
    with Session(engine) as session:
        query = select(Post).where(Post.extra["featured"].as_boolean())
        return list(session.exec(query))
```

<!-- router:fbr,custom -->
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
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/featured/featured_view.nexy"
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

```python filename="src/apps/featured/featured_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/featured")
class FeaturedController:
    async def get(self):
        return useViews("src/apps/featured/featured_view.nexy")
```
<!-- /router -->

Conservez la requête dans une fonction : seuls les noms attribués au niveau supérieur du frontmatter atteignent le modèle.

## Recherche en texte intégral

<!-- router:fbr,custom -->
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
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/search/search_api_controller.py"
from sqlalchemy import func
from sqlmodel import Session, select

from nexy.decorators import Controller
from nexy.http import Depends
from src.configs.session import get_session
from src.models.post_model import Post


@Controller("/api/search")
class SearchApiController:
    async def get(self, q: str, session: Session = Depends(get_session)):
        document = func.to_tsvector("english", Post.title)
        query = func.websearch_to_tsquery("english", q)
        rank = func.ts_rank(document, query)
        rows = session.exec(select(Post).where(document.op("@@")(query)).order_by(rank.desc()))
        return rows.all()
```

Répertoriez le contrôleur dans le `controllers` du module racine.
<!-- /router -->

Un index le maintient rapide sur une grande table. Ajoutez-le dans une migration :

```python filename="alambic/versions/xxxx_search_index.py"
def upgrade() -> None:
    op.execute(
        "CREATE INDEX post_title_search ON post USING GIN (to_tsvector('english', title))"
    )
```

## Insertions

```python filename="src/services/tags.py"
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

## Migrations

```bash
nx migrate --init
nx migrate -m "create posts"
nx migrate --upgrade
```

`nx migrate` lit `DATABASE_URL`, vérifie que le pilote est installé et que le serveur répond, puis exécute Alembic. Importez chaque module de modèle dans `alembic/env.py` pour que la génération automatique le voie.

## Asynchrone avec `asyncpg`

```python filename="src/configs/async_db.py"
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.configs.db import database_url

async_engine = create_async_engine(
    database_url().replace("+psycopg", "+asyncpg", 1), pool_pre_ping=True
)


async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session
```

<!-- router:fbr,custom -->
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
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/posts/posts_count_api_controller.py"
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from nexy.decorators import Controller
from nexy.http import Depends
from src.configs.async_db import get_async_session
from src.models.post_model import Post


@Controller("/api/posts/count")
class PostsCountApiController:
    async def get(self, session: AsyncSession = Depends(get_async_session)):
        count = (await session.exec(select(func.count()).select_from(Post))).one()
        return {"count": count}
```

Répertoriez le contrôleur dans le `controllers` du module racine, avant `PostsByIdApiController` : le premier contrôleur dont le chemin correspond aux réponses, et répertorié après lui, `/api/posts/count/` répond `404`.
<!-- /router -->

psycopg 3 fonctionne également de manière asynchrone : `postgresql+psycopg://` fonctionne également avec `create_async_engine`.

## Tests dans une transaction

Chaque test s'exécute dans une transaction qui est annulée, de sorte que la base de données de test reste vide :

```python filename="tests/contest.py"
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

## Géré PostgreSQL

| Service | Quels changements |
|---|---|
| [Néon](neon.md) | ajouter `?sslmode=require` ; utiliser l'hôte mis en pool pour de nombreuses connexions courtes |
| Supabase | le même formulaire URL ; utiliser le port pooler `6543` pour de nombreux travailleurs |
| Amazon RDS, Cloud SQL, Azure | ajoutez `?sslmode=require` et autorisez le réseau de l'application |

## Prochaines étapes

- [Bases de données](../guides/databases.md)
- [Utiliser Neon avec Nexy](neon.md)
- [Utiliser SQLite avec Nexy](sqlite.md)
