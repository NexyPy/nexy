# Используйте Неон с Nexy

Neon является бессерверным PostgreSQL: проект Nexy использует его как [PostgreSQL](postgresql.md) с драйвером `psycopg`, строкой подключения к пулу Neon в `DATABASE_URL` и пулом, который выдерживает переход базы данных в спящий режим.

## Получить строки подключения

В консоли Neon **Connect** показывает две строки для каждой ветки:

| Строка | Хост | Используйте его для |
|---|---|---|
| Объединенный | `ep-xxx-pooler.region.aws.neon.tech` | приложение: много коротких соединений через PgBouncer |
| Прямой | `ep-xxx.region.aws.neon.tech` | миграции и длинные сессии |

Единственная разница — `-pooler` в имени хоста.

## Установите драйвер

```bash
uv add "psycopg[binary]"
```

Бессерверный драйвер Neon через HTTP предназначен для JavaScript; из Python соединение обычное PostgreSQL по TCP и TLS.

## Два URL-адреса

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3-pooler.eu-central-1.aws.neon.tech/app?sslmode=require
DIRECT_DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3.eu-central-1.aws.neon.tech/app?sslmode=require
```

Neon копирует свои строки как `postgresql://...`: добавьте `+psycopg` после `postgresql`. Сохраните `sslmode=require` и `channel_binding=require`, когда консоль добавит их.

## Двигатель

Вычисления Neon приостанавливаются, когда они простаивают, что приводит к закрытию соединений вашего пула. `pool_pre_ping` заменяет нерабочее соединение до его использования, а `pool_recycle` разрывает соединения до того, как Neon:

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

Первый запрос после приостановки ожидает начала вычислений в течение нескольких сотен миллисекунд. Отключите автоприостановку в производственной ветке, если это для вас важно.

## Модель и обработчик

Остальное — PostgreSQL. Модель:

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

Перечислите контроллер в `controllers` корневого модуля.
<!-- /router -->

## Миграции выполняются через прямой URL-адрес.

PgBouncer перед объединенным хостом разделяет соединения между клиентами, что подходит для коротких запросов, а не для длительного сеанса миграции. `nx migrate` читается как `DATABASE_URL`, поэтому укажите прямой хост для этой команды:

```bash
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate -m "create visits"
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate --upgrade
```

`alembic/env.py` использует механизм `src/configs/db.py`, который считывает ту же переменную.

## Подготовленные заявления за пулером

psycopg готовит запрос, который он запускал пять раз. Если хост в пуле отвечает `prepared statement "_pg3_0" does not exist`, отключите это:

```python filename="src/configs/db.py"
engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"prepare_threshold": None},
)
```

При использовании `asyncpg` устанавливается значение `connect_args={"statement_cache_size": 0}`.

## Ветки для разработки и превью

Ветка Neon — это копия базы данных, созданная за секунду. По одному на каждого разработчика или на каждый запрос на включение тестовые данные не попадают в рабочую среду:

```bash
neonctl branches create --name dev-ada
neonctl connection-string dev-ada --pooled
```

Поместите эту строку в `.env` разработчика или в среду развертывания предварительной версии.

## Тесты

Запустите тесты для созданной для них ветки внутри транзакции, откат которой выполнен: см. [Тесты в транзакции](postgresql.md#tests-in-a-transaction).

## Следующие шаги

- [Используйте PostgreSQL с Nexy](postgresql.md): типы, поиск, обновления и асинхронность.
- [Базы данных](../guides/databases.md)
- [Развернуть](../deployment/README.md)
