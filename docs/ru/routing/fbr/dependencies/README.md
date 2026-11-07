# Зависимости и охранники

Совместное использование аутентификации, сеансов базы данных и других настроек по маршрутам с зависимостями FastAPI. Они работают на двух уровнях, причем уровень каталога наследуется как макеты.

| Уровень | Где | Применяется к |
|---|---|---|
| Каталог | `dependencies.py` | каждый маршрут в каталоге и ниже, включая страницы |
| Обработчик | `Depends`, `@UseGuard`, `@Middleware` | один обработчик |

## По каталогу: `dependencies.py`

`dependencies.py` объявляет `dependencies` список простых функций. Nexy оборачивает каждый из них в `Depends`.

```python filename="src/routes/admin/dependents.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

> [!NOTE]
> перечислите сами функции. Объект `Depends(...)` в списке игнорируется.

Для каждого маршрута под `src/routes/admin/` теперь требуется заголовок, обработчики `.py` и страницы `.nexy`.

## Наследование

Зависимости собираются от корня маршрутов до каталога маршрута, **самый внешний**, точно так же, как и макеты, а собственная защита обработчика запускается последней:

```text
src/routes/
├─ dependencies.py              1. root
└─ admin/
   ├─ dependencies.py           2. admin
   └─ users/
      ├─ dependencies.py        3. users
      └─ index.py               4. handler guards, then the handler
```

Для `GET /admin/users` порядок следующий: `root`, `admin`, `users`, функции обработчика `@UseGuard`, его функции `@Middleware`, затем обработчик. Группа маршрутов (`(group)/`) - это каталог, как и любой другой, поэтому его `dependencies.py` принимает участие.

## За обработчик

Используйте `Depends` в подписи, как и в любом приложении FastAPI:

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header, HTTPException


def current_user(authorization: str = Header(...)) -> str:
    if authorization != "Bearer secret":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return "ada"


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## Охранники и промежуточное ПО в обработчике

`@UseGuard` и `@Middleware` присоединяют зависимости FastAPI к обработчику без изменения его сигнатуры. Оба являются зависимостями, а не промежуточным программным обеспечением ASGI:

```python filename="src/routes/admin/users/index.py"
from nexy.decorators import Middleware, UseGuard


def audit() -> None: ...


def must_be_staff(x_staff: str = Header(...)) -> None: ...


@UseGuard(must_be_staff)
@Middleware(audit)
async def GET():
    return {"ok": True}
```

Для настоящего промежуточного программного обеспечения ASGI (CORS, GZip, сеансы, ваши собственные) используйте параметры `useMiddlewares` и `use*` в разделе [Промежуточное программное обеспечение и безопасность](../../../guides/middleware-and-security.md).

## Ошибка зависимости

Зависимость отклоняет запрос путем поднятия. `HTTPException` отвечает с поднятым вами статусом в виде JSON для клиентов API (`Accept: application/json`) и в виде страницы ошибки для браузеров. См. [Проверка и ошибки](../handlers/validation-and-errors.md).

## Следующие шаги

- [Наследование](../inheritance.md)
- [Обработчики](../handlers/README.md)
- [Промежуточное ПО и безопасность](../../../guides/middleware-and-security.md)
