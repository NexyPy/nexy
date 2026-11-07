# Включите существующий маршрутизатор FastAPI в Nexy.

Чтобы включить существующий маршрутизатор FastAPI в Nexy, установите для `useRouter` значение `APIRouter` в классе `NexyConfig` маршрутизатора `nexyconfig.py`: его маршруты обслуживаются как есть, рядом с файлами `src/routes/`.

## Когда использовать собственный маршрутизатор

- **Постепенная миграция**: приложение FastAPI перемещается в Nexy маршрут за маршрутом, а его старые маршруты тем временем продолжают отвечать.
- **Повторное использование кода**: пакет уже предоставляет `APIRouter` для аутентификации или выставления счетов.
- **Серверная часть, которую вы сохраняете**: API остается простым FastAPI, а Nexy добавляет страницы.

## Установите `useRouter` в `nexyconfig.py`

Маршрутизатор - это любой FastAPI `APIRouter`, написанный так, как вы его уже пишете:

```python filename="src/legacy/api.py"
from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/status")
async def status():
    return {"status": "ok"}


@router.get("/users/{id}")
async def user(id: int):
    return {"id": id}
```

`useRouter` - поле класса `NexyConfig`, как и все настройки проекта:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

Затем `nx dev` отвечает на `GET /api/status` и `GET /api/users/{id}`, а `/docs` перечисляет их.

> [!NOTE]
> `useRouter` в `nexyconfig.py` - это настройка. `from nexy import useRouter` - это еще одна вещь: перехватчик, который страница `.nexy` использует для чтения текущего маршрута. Не импортируйте его для настройки маршрутизатора.

## Несколько роутеров

`useRouter` занимает один маршрутизатор. Соберите несколько под одним родителем с помощью `include_router`:

```python filename="src/legacy/__init__.py"
from fastapi import APIRouter

from .api import router as api
from .auth import router as auth

router = APIRouter()
router.include_router(api)
router.include_router(auth, prefix="/auth")
```

```python filename="src/legacy/auth.py"
from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login():
    return {"token": "demo"}
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

## Страницы и файлы маршрутов рядом с ними

`src/routes/` все еще читается, пока `useRouter` установлен: страница `.nexy` или файл маршрута `.py` отвечают рядом с включенными маршрутами.

```nexy filename="источник/маршруты/index.nexy"
---
title = "Home"
---
<h1>{{ title }}</h1>
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"ok": True}
```

Два ограничения, пока установлено `useRouter`:

- страницы не переносятся `layout.nexy`;
- `useCSR = True` отказывают: `nx dev` и `nx build` отвечают `useCSR requires file-based routing`.

На URL-адрес отвечают один раз. Дайте включенному маршрутизатору префикс, здесь `/api`, и не допускайте, чтобы файлы `src/routes/` использовались по путям, которые он использует.

## Целое FastAPI приложение

`useRouter` требует приложения `APIRouter`, а не `FastAPI`. Маршруты приложения основаны на его атрибуте `router`:

```python filename="src/legacy/service.py"
from fastapi import FastAPI

service = FastAPI(title="Billing")


@service.get("/billing/invoices")
async def invoices():
    return []
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.service import service


class NexyConfig(NexyConfigModel):
    useRouter = service.router
```

Собственное промежуточное программное обеспечение приложения, обработчики исключений и события запуска остаются позади: переместите их в `useMiddlewares` и другие поля `nexyconfig.py`.

## Зависимости, аутентификация и база данных

Маршрутизатор работает в процессе Nexy, поэтому `Depends` схемы безопасности и сеансы базы данных работают как в оригинальном приложении:

```python filename="src/legacy/secure.py"
from fastapi import APIRouter, Depends, Header, HTTPException


def require_token(x_token: str = Header("")) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=401, detail="Bad token")


router = APIRouter(prefix="/secure", dependencies=[Depends(require_token)])


@router.get("/data")
async def data():
    return {"data": 42}
```

## Проверьте это

```python filename="тесты/test_legacy.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_the_included_route_answers():
    assert TestClient(app).get("/api/status").json() == {"status": "ok"}
```

## Следующие шаги

- [От FastAPI до Nexy](../../coming-from/fastapi.md): переместите маршруты в файлы один за другим.
- [Маршрутизация на основе файлов](../fbr/README.md)
- [Модульная маршрутизация](../modular/README.md): `useRouter = AppModule`
