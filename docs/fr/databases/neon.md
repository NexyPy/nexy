# Utiliser Néon avec Nexy

Neon est sans serveur PostgreSQL : un projet Nexy l'utilise comme [PostgreSQL](postgresql.md), avec le pilote `psycopg`, la chaîne de connexion poolée de Neon dans `DATABASE_URL` et un pool qui survit à la mise en veille de la base de données.

## Récupérer les chaînes de connexion

Dans la console Neon, **Connect** affiche deux chaînes pour chaque branche :

| Chaîne | Hôte | Utilisez-le pour |
|---|---|---|
| Regroupé | `ep-xxx-pooler.region.aws.neon.tech` | l'application : de nombreuses connexions courtes, via PgBouncer |
| Direct | `ep-xxx.region.aws.neon.tech` | migrations et longues sessions |

La seule différence est `-pooler` dans le nom d'hôte.

## Installer le pilote

```bash
uv add "psycopg[binary]"
```

Le pilote sans serveur de Neon sur HTTP est destiné à JavaScript ; à partir de Python, la connexion est ordinaire PostgreSQL via TCP et TLS.

## Les deux URL

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3-pooler.eu-central-1.aws.neon.tech/app?sslmode=require
DIRECT_DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3.eu-central-1.aws.neon.tech/app?sslmode=require
```

Neon copie ses chaînes sous la forme `postgresql://...` : ajoutez `+psycopg` après `postgresql`. Conservez `sslmode=require` et `channel_binding=require` lorsque la console l'ajoute.

## Le moteur

Un calcul Neon se suspend lorsqu'il est inactif, ce qui ferme les connexions de votre pool. `pool_pre_ping` remplace un réseau mort avant qu'il ne soit utilisé, et `pool_recycle` supprime les connexions avant que Neon :

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

La première requête après une suspension attend pendant que le calcul démarre, quelques centaines de millisecondes. Désactivez la suspension automatique sur la branche de production si cela vous intéresse.

## Un modèle et un gestionnaire

Le reste est PostgreSQL. Un modèle :

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

## Les migrations passent par l'URL directe

PgBouncer devant l'hôte mutualisé partage les connexions entre les clients, ce qui convient aux requêtes courtes, et non à la longue session d'une migration. `nx migrate` lit `DATABASE_URL`, alors pointez-le vers l'hôte direct pour cette commande :

```bash
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate -m "create visits"
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate --upgrade
```

`alembic/env.py` utilise le moteur de `src/configs/db.py`, qui lit la même variable.

## Déclarations préparées derrière le pooler

psycopg prépare une requête qu'il a exécutée cinq fois. Si l'hôte du pool répond `prepared statement "_pg3_0" does not exist`, désactivez-le :

```python filename="src/configs/db.py"
engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"prepare_threshold": None},
)
```

Avec `asyncpg`, le réglage est `connect_args={"statement_cache_size": 0}`.

## Branches pour le développement et les aperçus

Une branche Neon est une copie d'une base de données, réalisée en une seconde. Un par développeur, ou par pull request, maintient les données de test à l'écart de la production :

```bash
neonctl branches create --name dev-ada
neonctl connection-string dev-ada --pooled
```

Placez cette chaîne dans le `.env` du développeur ou dans l'environnement du déploiement préliminaire.

## Essais

Exécutez les tests sur une branche créée pour eux, à l'intérieur d'une transaction annulée : voir [Tests dans une transaction](postgresql.md#tests-in-a-transaction).

## Prochaines étapes

- [Utilisez PostgreSQL avec Nexy](postgresql.md) : types, recherche, upserts et async
- [Bases de données](../guides/databases.md)
- [Déployer](../deployment/README.md)
