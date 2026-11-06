# Verwenden Sie Neon mit Nexy

Neon ist serverlos PostgreSQL: Ein Nexy-Projekt verwendet es wie [PostgreSQL](postgresql.md), mit dem `psycopg`-Treiber, der gepoolten Verbindungszeichenfolge von Neon in `DATABASE_URL` und einem Pool, der den Ruhezustand der Datenbank übersteht.

## Rufen Sie die Verbindungszeichenfolgen ab

In der Neon-Konsole zeigt **Connect** zwei Zeichenfolgen für jeden Zweig:

| Zeichenfolge | Gastgeber | Benutze es für |
|---|---|---|
| Gebündelt | `ep-xxx-pooler.region.aws.neon.tech` | die App: viele kurze Verbindungen, durch PgBouncer |
| Direkt | `ep-xxx.region.aws.neon.tech` | Migrationen und lange Sitzungen |

Der einzige Unterschied besteht in `-pooler` im Hostnamen.

## Installieren Sie den Treiber

```bash
uv add "psycopg[binary]"
```

Der serverlose Treiber von Neon über HTTP ist für JavaScript; Ab Python ist die Verbindung normal PostgreSQL über TCP und TLS.

## Die beiden URLs

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3-pooler.eu-central-1.aws.neon.tech/app?sslmode=require
DIRECT_DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3.eu-central-1.aws.neon.tech/app?sslmode=require
```

Neon kopiert seine Zeichenfolgen als `postgresql://...`: Fügen Sie `+psycopg` nach `postgresql` hinzu. Behalten Sie `sslmode=require` und `channel_binding=require` bei, wenn die Konsole es hinzufügt.

## Der Motor

Ein Neon-Rechner wird angehalten, wenn er inaktiv ist, wodurch die Verbindungen Ihres Pools geschlossen werden. `pool_pre_ping` ersetzt eine tote Verbindung, bevor sie verwendet wird, und `pool_recycle` trennt Verbindungen, bevor Neon Folgendes tun würde:

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

Die erste Anfrage nach einem Suspend wartet, während die Berechnung beginnt, einige hundert Millisekunden. Deaktivieren Sie die automatische Suspendierung im Produktionszweig, wenn Ihnen das wichtig ist.

## Ein Model und ein Handler

Der Rest ist PostgreSQL. Ein Modell:

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

## Migrationen erfolgen über die direkte URL

PgBouncer vor dem gepoolten Host teilt Verbindungen zwischen Clients, was für kurze Abfragen geeignet ist, nicht für lange Sitzungen einer Migration. `nx migrate` liest `DATABASE_URL`, also richten Sie es auf den direkten Host für diesen Befehl:

```bash
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate -m "create visits"
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate --upgrade
```

`alembic/env.py` verwendet die Engine von `src/configs/db.py`, die dieselbe Variable liest.

## Vorbereitete Aussagen hinter dem Pooler

psycopg bereitet eine Abfrage vor, die fünfmal ausgeführt wurde. Wenn der gepoolte Host antwortet `prepared statement "_pg3_0" does not exist`, schalten Sie das aus:

```python filename="src/configs/db.py"
engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"prepare_threshold": None},
)
```

Bei `asyncpg` ist die Einstellung `connect_args={"statement_cache_size": 0}`.

## Zweige für Entwicklung und Vorschau

Ein Neon-Zweig ist eine Kopie einer Datenbank, die in einer Sekunde erstellt wird. Einer pro Entwickler oder pro Pull-Anfrage hält Testdaten von der Produktion fern:

```bash
neonctl branches create --name dev-ada
neonctl connection-string dev-ada --pooled
```

Fügen Sie diese Zeichenfolge in das `.env` des Entwicklers oder in die Umgebung der Vorschaubereitstellung ein.

## Tests

Führen Sie die Tests für einen für sie erstellten Zweig innerhalb einer zurückgesetzten Transaktion aus: siehe [Tests in einer Transaktion](postgresql.md#tests-in-a-transaction).

## Nächste Schritte

- [Verwenden Sie PostgreSQL mit Nexy](postgresql.md): Typen, Suche, Upserts und Async
- [Datenbanken](../guides/databases.md)
- [Bereitstellen](../deployment/README.md)
