# Use Neon with Nexy

Neon is serverless PostgreSQL: a Nexy project uses it like [PostgreSQL](postgresql.md), with the
`psycopg` driver, Neon's pooled connection string in `DATABASE_URL`, and a pool that survives the
database going to sleep.

## Get the connection strings

In the Neon console, **Connect** shows two strings for each branch:

| String | Host | Use it for |
|---|---|---|
| Pooled | `ep-xxx-pooler.region.aws.neon.tech` | the app: many short connections, through PgBouncer |
| Direct | `ep-xxx.region.aws.neon.tech` | migrations and long sessions |

The only difference is `-pooler` in the host name.

## Install the driver

```bash
uv add "psycopg[binary]"
```

Neon's serverless driver over HTTP is for JavaScript; from Python the connection is ordinary
PostgreSQL over TCP and TLS.

## The two URLs

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3-pooler.eu-central-1.aws.neon.tech/app?sslmode=require
DIRECT_DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3.eu-central-1.aws.neon.tech/app?sslmode=require
```

Neon copies its strings as `postgresql://...`: add `+psycopg` after `postgresql`. Keep
`sslmode=require`, and `channel_binding=require` when the console adds it.

## The engine

A Neon compute suspends when it is idle, which closes the connections of your pool. `pool_pre_ping`
replaces a dead one before it is used, and `pool_recycle` drops connections before Neon would:

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

The first request after a suspend waits while the compute starts, a few hundred milliseconds. Turn
autosuspend off on the production branch if that matters to you.

## A model and a handler

The rest is PostgreSQL. A model:

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

<!-- router:fbr,custom -->
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
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/visits/visits_api_controller.py"
from sqlmodel import Session, func, select

from nexy.decorators import Controller
from nexy.http import Depends
from src.configs.session import get_session
from src.models.visit_model import Visit


@Controller("/api/visits")
class VisitsApiController:
    async def post(self, path: str, session: Session = Depends(get_session)):
        session.add(Visit(path=path))
        session.commit()
        return {"visits": session.exec(select(func.count()).select_from(Visit)).one()}
```

List the controller in the `controllers` of the root module.
<!-- /router -->

## Migrations go through the direct URL

PgBouncer in front of the pooled host shares connections between clients, which suits short
queries, not the long session of a migration. `nx migrate` reads `DATABASE_URL`, so point it at the
direct host for that command:

```bash
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate -m "create visits"
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate --upgrade
```

`alembic/env.py` uses the engine of `src/configs/db.py`, which reads the same variable.

## Prepared statements behind the pooler

psycopg prepares a query it has run five times. If the pooled host answers
`prepared statement "_pg3_0" does not exist`, turn that off:

```python filename="src/configs/db.py"
engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"prepare_threshold": None},
)
```

With `asyncpg`, the setting is `connect_args={"statement_cache_size": 0}`.

## Branches for development and previews

A Neon branch is a copy of a database, made in a second. One per developer, or per pull request,
keeps test data away from production:

```bash
neonctl branches create --name dev-ada
neonctl connection-string dev-ada --pooled
```

Put that string in the `.env` of the developer, or in the preview deployment's environment.

## Tests

Run the tests against a branch made for them, inside a transaction that is rolled back: see
[Tests in a transaction](postgresql.md#tests-in-a-transaction).

## Next steps

- [Use PostgreSQL with Nexy](postgresql.md): types, search, upserts and async
- [Databases](../guides/databases.md)
- [Deploy](../deployment/README.md)
