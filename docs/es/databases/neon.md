# Usa neón con Nexy

Neon no tiene servidor PostgreSQL: un proyecto Nexy lo usa como [PostgreSQL](postgresql.md), con el controlador `psycopg`, la cadena de conexión agrupada de Neon en `DATABASE_URL` y un grupo que sobrevive a la base de datos en suspensión.

## Obtener las cadenas de conexión

En la consola Neon, **Connect** muestra dos cadenas para cada rama:

| cuerda | Anfitrión | Úselo para |
|---|---|---|
| agrupado | `ep-xxx-pooler.region.aws.neon.tech` | la aplicación: muchas conexiones cortas, a través de PgBouncer |
| directo | `ep-xxx.region.aws.neon.tech` | migraciones y largas sesiones |

La única diferencia es `-pooler` en el nombre del host.

## Instale el controlador

```bash
uv add "psycopg[binary]"
```

El controlador sin servidor de Neon a través de HTTP es para JavaScript; desde Python la conexión es normal PostgreSQL sobre TCP y TLS.

## Las dos URL

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3-pooler.eu-central-1.aws.neon.tech/app?sslmode=require
DIRECT_DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3.eu-central-1.aws.neon.tech/app?sslmode=require
```

Neon copia sus cadenas como `postgresql://...`: agrega `+psycopg` después de `postgresql`. Mantenga `sslmode=require` y `channel_binding=require` cuando la consola lo agregue.

## el motor

Un cómputo de Neon se suspende cuando está inactivo, lo que cierra las conexiones de su grupo. `pool_pre_ping` reemplaza uno muerto antes de usarlo, y `pool_recycle` desconecta las conexiones antes de que Neon:

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

La primera solicitud después de una suspensión espera mientras se inicia el proceso, unos cientos de milisegundos. Desactive la suspensión automática en la rama de producción si eso le importa.

## Un modelo y un manipulador

El resto es PostgreSQL. Un modelo:

```python filename="src/modelos/visit_model.py"
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

```python filename="src/rutas/api/visits.py"
from sqlmodel import Session, func, select

from nexy.http import Depends
from src.configs.session import get_session
from src.models.visit_model import Visit


async def POST(path: str, session: Session = Depends(get_session)):
    session.add(Visit(path=path))
    session.commit()
    return {"visits": session.exec(select(func.count()).select_from(Visit)).one()}
```

## Las migraciones pasan por la URL directa

PgBouncer frente al host agrupado comparte conexiones entre clientes, lo que se adapta a consultas cortas, no a sesiones largas de una migración. `nx migrate` lee `DATABASE_URL`, así que apúntalo al host directo para ese comando:

```bash
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate -m "create visits"
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate --upgrade
```

`alembic/env.py` usa el motor de `src/configs/db.py`, que lee la misma variable.

## Declaraciones preparadas detrás del pooler

psycopg prepara una consulta que ha ejecutado cinco veces. Si el host agrupado responde `prepared statement "_pg3_0" does not exist`, desactívelo:

```python filename="src/configs/db.py"
engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"prepare_threshold": None},
)
```

Con `asyncpg`, la configuración es `connect_args={"statement_cache_size": 0}`.

## Ramas para desarrollo y vistas previas.

Una rama Neon es una copia de una base de datos, realizada en un segundo. Uno por desarrollador o por solicitud de extracción mantiene los datos de prueba alejados de la producción:

```bash
neonctl branches create --name dev-ada
neonctl connection-string dev-ada --pooled
```

Coloque esa cadena en el `.env` del desarrollador o en el entorno de implementación de vista previa.

## Pruebas

Ejecute las pruebas contra una rama creada para ellos, dentro de una transacción que se revierte: consulte [Pruebas en una transacción](postgresql.md#tests-in-a-transaction).

## Próximos pasos

- [Utilice PostgreSQL con Nexy](postgresql.md): tipos, búsqueda, upserts y asíncrono
- [Bases de datos](../guides/databases.md)
- [Implementar](../deployment/README.md)
