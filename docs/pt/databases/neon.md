# Use Neon com Nexy

Neon não tem servidor PostgreSQL: um projeto Nexy o usa como [PostgreSQL](postgresql.md), com o driver `psycopg`, a string de conexão agrupada do Neon em `DATABASE_URL`, e um pool que sobrevive ao banco de dados indo dormir.

## Obtenha as cadeias de conexão

No console Neon, **Connect** mostra duas strings para cada branch:

| Corda | Anfitrião | Use-o para |
|---|---|---|
| Agrupados | `ep-xxx-pooler.region.aws.neon.tech` | o aplicativo: muitas conexões curtas, através do PgBouncer |
| Direto | `ep-xxx.region.aws.neon.tech` | migrações e sessões longas |

A única diferença está `-pooler` no nome do host.

## Instale o driver

```bash
uv add "psycopg[binary]"
```

O driver sem servidor do Neon sobre HTTP é para JavaScript; de Python a conexão é comum PostgreSQL sobre TCP e TLS.

## Os dois URLs

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3-pooler.eu-central-1.aws.neon.tech/app?sslmode=require
DIRECT_DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3.eu-central-1.aws.neon.tech/app?sslmode=require
```

Neon copia suas strings como `postgresql://...`: adicione `+psycopg` após `postgresql`. Mantenha `sslmode=require` e `channel_binding=require` quando o console o adicionar.

## O motor

Um cálculo Neon é suspenso quando está ocioso, o que fecha as conexões do seu pool. `pool_pre_ping` substitui um morto antes de ser usado, e `pool_recycle` descarta conexões antes que o Neon:

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

A primeira solicitação após uma suspensão aguarda enquanto a computação é iniciada, algumas centenas de milissegundos. Desative a suspensão automática no ramo de produção, se isso for importante para você.

## Um modelo e um manipulador

O resto é PostgreSQL. Um modelo:

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

## As migrações passam pela URL direta

O PgBouncer na frente do host em pool compartilha conexões entre clientes, o que atende a consultas curtas, não à longa sessão de uma migração. `nx migrate` lê `DATABASE_URL`, então aponte para o host direto desse comando:

```bash
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate -m "create visits"
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate --upgrade
```

`alembic/env.py` usa o mecanismo de `src/configs/db.py`, que lê a mesma variável.

## Declarações preparadas por trás do pooler

psycopg prepara uma consulta que foi executada cinco vezes. Se o host em pool responder `prepared statement "_pg3_0" does not exist`, desligue isso:

```python filename="src/configs/db.py"
engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"prepare_threshold": None},
)
```

Com `asyncpg`, a configuração é `connect_args={"statement_cache_size": 0}`.

## Ramos para desenvolvimento e visualizações

Uma ramificação Neon é uma cópia de um banco de dados, feita em um segundo. Um por desenvolvedor ou por solicitação pull mantém os dados de teste longe da produção:

```bash
neonctl branches create --name dev-ada
neonctl connection-string dev-ada --pooled
```

Coloque essa string no `.env` do desenvolvedor ou no ambiente de implantação de visualização.

## Testes

Execute os testes em uma ramificação feita para eles, dentro de uma transação que é revertida: veja [Testes em uma transação](postgresql.md#tests-in-a-transaction).

## Próximas etapas

- [Use PostgreSQL com Nexy](postgresql.md): tipos, pesquisa, upserts e assíncronos
- [Bancos de dados](../guides/databases.md)
- [Implantar](../deployment/README.md)
