# Быстрый старт

Вы создадите проект Nexy, запустите его и увидите изменение страницы по мере его редактирования. Это занимает три минуты. Затем [Руководство](tutorial.md) добавляет конечную точку и производственную сборку.

## Прежде чем начать

| Вам нужно | Почему |
|---|---|
| Python 3.12+ | `requires-python` в `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | предоставляет `uvx`, создает проект и устанавливает его пакеты |
| Node.js 18+ | только если вы используете клиентскую платформу (React, Vue, Svelte, Solid, Preact) |

Еще нет uv? См. [Установка](installation.md).

## 1. Создайте проект

```bash
uvx nexy new my-app
```

`uvx` поставляется с uv, поэтому сначала установите uv. Он запускает Nexy во временной среде, достаточной для **создания** проекта. `nexy new` затем создает собственный проект `.venv` и устанавливает туда его пакеты. Четыре подсказки определяют проводку:

| Подсказка | Эффект |
|---|---|
| Файловый маршрутизатор? | `Yes` сканирует `src/routes/`; `No` формирует модульный маршрутизатор в `src/apps/` |
| Тип проекта | `Web` добавляет макет и клиентские ресурсы, `API` запускается без представлений |
| Клиентский компонент? | добавляет фреймворк и его Vite настройку |
| ORM/база данных | добавляет слой модели или ничего |

Не уверены? Ответ `Yes`, `Web` и никакого клиентского компонента. Вы можете добавить каждый позже.

## 2. Запустите его

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

Откройте <http://localhost:3000>. Вы должны увидеть стартовую страницу. Порт взят из `usePort` (по умолчанию `3000`); `--port` и `--host` переопределяют его при каждом запуске.

> [!NOTE]
> Запустите каждую команду, кроме `new` и `init` внутри виртуальной среды проекта, или добавьте к ней префикс `uv run`, как в `uv run nexy dev`. За его пределами проект, которому требуется `sqlmodel` терпит неудачу с `No module named 'sqlmodel'`.

## 3. Изменить страницу

<!-- router:fbr,custom -->
Файл в папке `src/routes/` является маршрутом. Создайте `src/routes/hello.nexy`:

```nexy filename="src/маршруты/hello.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```
<!-- /router -->

<!-- router:modular -->
Контроллер возвращает представление. Создайте `src/apps/hello_view.nexy`:

```nexy filename="src/apps/hello_view.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

Затем объявите страницу в `src/apps/app_controller.py` и добавьте ее в модуль:

```python filename="src/apps/app_controller.py"
@Controller("/hello")
class HelloController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/hello_view.nexy")})
```

```python filename="src/apps/app_module.py"
from .app_controller import AboutController, AppController, HelloController

controllers = [AppController, AboutController, HelloController]
```
<!-- /router -->

Откройте <http://localhost:3000/hello>. Измените `"Hello"` на `"Bonjour"` и сохраните: страница обновится без перезагрузки вручную. Если код неправильный, браузер вместо пустой страницы отображает ошибку.

`prop[str]` объявляет типизированное свойство. Разметка под заголовком — Jinja2 — см. файлы [.nexy](../views/nexy/README.md).

## Где дальше

| Вы хотите | Прочесть |
|---|---|
| Добавьте конечную точку Python и отправьте сборку | [Руководство](tutorial.md) |
| Знайте, где находится каждый файл | [Структура проекта](project-structure.md) |
| Поймите, кто и что строит | [Как работает Nexy](how-nexy-works.md) |
| Используйте React, Vue, Svelte, Solid или Preact | [Просмотры](../views/README.md) |
