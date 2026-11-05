# Наследование

Некоторые файлы в `src/routes/` применяются ко всему, что находится ниже их каталога. Все они решаются одинаково: Nexy начинается с каталога маршрута и доходит до `src/routes/`.

```text
src/routes/
├─ layout.nexy               1. outermost
├─ dependencies.py           1. runs first
├─ middleware.py             1. wraps first
├─ notfound.nexy             fallback for every URL
├─ (shop)/                   a group is a directory: it takes part, it is not in the URL
│  ├─ layout.nexy            2.
│  ├─ dependencies.py        2.
│  └─ cart/
│     ├─ layout.nexy         3. innermost
│     ├─ dependencies.py     3. runs last
│     └─ index.nexy          the page
```

| Файл | Правило |
|---|---|
| `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` | каждый макет от корня до страницы оборачивает его, **самый внешний** |
| `middleware.py` | каждый файл от корня до маршрута оборачивает запрос, **самый внешний**, перед зависимостями |
| `dependencies.py` | каждый файл от корня до маршрута запускается, **сначала внешний**, затем собственные охранники обработчика |
| `notfound.nexy`, `errors.nexy` | выиграет **ближайший** по коду статуса |

На странице выше макеты вложены как `root layout > (shop) layout > cart layout > page`, а зависимости выполняются как `root > (shop) > cart > handler guards`.

## Почему сначала самое внешнее

Внешний макет рисует фрейм, а внешняя зависимость решает, кто вообще может войти. Размещение их первыми означает, что внутренние каталоги могут полагаться на них: каталог, требующий аутентификации, запускается до обработчика, читающего пользователя.

Зависимость дерева `(shop)` проверяет файл cookie корзины, поэтому зависимость корзины под ней может прочитать корзину без повторной проверки:

```python filename="src/routes/(магазин)/dependents.py"
from nexy.http import HTTPException, Request


def require_cart(request: Request) -> None:
    if "cart" not in request.cookies:
        raise HTTPException(status_code=400, detail="No cart")


dependencies = [require_cart]
```

## Макеты

Все файлы макетов семейства папок: см. [Макеты](layouts/README.md). Разные семейства не смешиваются: `layout.vue` никогда не оборачивает страницу `.tsx`, а проект имеет либо `layout.nexy`, либо клиентский макет, но никогда и то и другое ([режимы](modes.md)).

Самый внутренний макет дерева добавляет только свой собственный фрейм: корневой макет вокруг него по-прежнему рисует документ.

```nexy filename="src/маршруты/(магазин)/cart/layout.nexy"
---
children: prop[NexyElement]
---
<section class="cart">
  <h2>Your cart</h2>
  {{ children | safe }}
</section>
```

## Файлы промежуточного программного обеспечения

См. [Файлы промежуточного программного обеспечения](middleware/README.md): они запускаются до зависимостей и могут отвечать, не достигая маршрута.

Корень `middleware.py` охватывает каждый маршрут дерева, включая тележку:

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## Зависимости

Порядок в файле-обработчике, включая `@UseGuard` и `@Middleware`, см. в разделе [Зависимости](dependencies/README.md).

## Страницы ошибок

`notfound.nexy` и `errors.nexy` устанавливаются один раз в корень маршрута; копия в подкаталоге уточняет страницу для этого префикса. См. [Страницы ошибок](errors/README.md).

Копия в `cart/` отвечает на 404 в `/cart`, а корневая копия сохраняет все остальное:

```nexy filename="src/routes/(магазин)/cart/notfound.nexy"
---
title: Product not found
---
<h1>This product is gone</h1>
<p><a href="/cart">Back to your cart</a></p>
```

## Следующие шаги

- [Макеты](layouts/README.md)
- [Зависимости](dependencies/README.md)
- [Страницы ошибок](errors/README.md)
