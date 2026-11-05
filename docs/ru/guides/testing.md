# Тестирование

`nx test` запускает тесты сервера с помощью pytest, а тесты клиента с помощью vitest, когда вы их запрашиваете.

```bash
nx test                       # pytest
nx test -k create_user        # extra arguments go to pytest
nx test --client              # pytest, then vitest
nx test --no-server --client  # vitest only
```

## Что работает

| Часть | Команда | Условие |
|---|---|---|
| Сервер | `pytest` | работает на `tests/`, если он существует, в противном случае — в корне проекта; пропускается с предупреждением, если pytest не установлено |
| Клиент | `npx vitest run` | только с `--client` и только тогда, когда `vitest.config.ts` существует или `vitest` появляется в `package.json` |

Встроенного сквозного раннера нет. Управляйте сервером с помощью `TestClient` и сами добавьте Playwright или Cypress для поведения браузера.

## Протестируйте сервер

Тестовый клиент взаимодействует с приложением ASGI в процессе: не нужно запускать сервер и не нужно выбирать порт.

```python filename="тесты/test_pages.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_home_renders():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
```

`nexy.app.app` — это собранное приложение, созданное при первом чтении. Он читает `nexyconfig.py` из рабочего каталога, поэтому запустите pytest из корня проекта.

Когда тест меняет конфигурацию или маршруты, создайте новое приложение вместо повторного использования приложения на уровне модуля:

```python
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer


def test_api_hello():
    with TestClient(AppServer().run()) as client:
        response = client.get("/api/hello")
    assert response.json() == {"message": "Hello"}
```

`AppServer().run()` повторно собирает маршруты, промежуточное программное обеспечение, сеансы и трансляции, поэтому каждый вызов начинается с текущего состояния каталога проекта.

## Что утверждать

Страница возвращает HTML. Подтвердите статус, а затем интересующий вас контент:

```python
def test_blog_page_renders_slug(client):
    response = client.get("/blog/post-1")
    assert "post-1" in response.text
```

Обработчик API возвращает JSON. Ошибка проверки — это `422`, а отсутствующий маршрут — это `404`, на который отвечает `notfound.nexy`, если этот файл существует:

```python
def test_create_item_validates_body(client):
    assert client.post("/api/items", json={}).status_code == 422
```

Для действия протестируйте функцию напрямую (это обычная функция) и проверьте конечную точку HTTP, прочитав ее сгенерированный путь со страницы, которая ее предоставляет:

```python
from src.actions.user import create_user


async def test_create_user_returns_name():
    assert await create_user("Ada") == {"name": "Ada"}
```

```python
def test_form_posts_to_action(client):
    html = client.get("/").text
    action = html.split('action="')[1].split('"')[0]
    response = client.post(action, data={"name": "Ada"}, follow_redirects=False)
    assert response.status_code == 303
```

Вызов с JSON отвечает результатом, а `422` — недопустимыми полями.

> [!NOTE]
> Пути действий специфичны для проекта и генерируются. Никогда не кодируйте `/_nx_<hash>` в тесте.

## Проверьте компонент `.nexy`

`nexy.testing.render` компилирует компонент с импортируемыми компонентами и возвращает его HTML. Реквизиты являются аргументами ключевых слов, а `children=` заполняет слот:

```python filename="тесты/test_button.py"
from nexy.testing import render


def test_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

Запустите pytest из корня проекта: скомпилированные файлы попадают в `__nexy__/`, как и в случае с `nx dev`. Компоненту, который читает запрос (`usePathname`, `useSession`), вместо этого требуется проверка страницы с помощью `TestClient`.

## Тестирование клиента

`nx test --client` ожидает вашу собственную настройку vitest. Минимальный тест компонентов:

```tsx filename="src/компоненты/counter.test.tsx"
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Counter from "./counter";

describe("Counter", () => {
  it("starts at zero", () => {
    const { getByText } = render(<Counter start={0} />);
    expect(getByText("0")).toBeTruthy();
  });
});
```

`vitest` и библиотека тестирования являются зависимостями проекта: `nexy new` не устанавливает тестовый стек. Добавьте `vitest.config.ts` с нужным вам окружением (jsdom или Happy-dom для компонентов).

## Непрерывная интеграция

Для конвейера проекта достаточно двух команд:

```bash
nx build
nx test
```

`nx build` завершается сбоем из-за ошибки компиляции; `nx test` терпит неудачу из-за ошибочного утверждения и завершает работу с ненулевым значением. `nx check` добавляет в прогон mypy и `tsc` .

Работа над самим Nexy использует разные команды: см. [ВКЛАД](https://github.com/NexyPy/nexy/blob/main/CONTRIBUTING.md).

## Следующие шаги

- [CLI](../reference/cli.md): каждый флаг `nx test`
- [API](../routing/fbr/handlers/README.md): что возвращает конечная точка
- [Развертывание](../deployment/README.md): сборка перед тестированием в CI
