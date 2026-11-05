# Учебник: создайте страницу заметок за 10 минут

Вы создадите проект, добавите страницу, добавите конечную точку Python, поделитесь данными между ними и выполните сборку для производства. В конце вы получите один список заметок, обслуживаемый в виде страницы и в формате JSON.

Впервые в Некси? Сначала выполните [Быстрый старт](quick-start.md): это займет три минуты.

```diagram filename="Весь урок в одной строке"
uvx nexy new notes ──► edit layout ──► add page ──► add endpoint ──► share data ──► nx build ──► nx start
```

## 1. Создайте проект

```bash
uvx nexy new notes
cd notes
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

`uvx` поставляется с [uv](https://docs.astral.sh/uv/) и только создает проект. Каждая команда после нее запускается внутри виртуальной среды проекта (или как `uv run nexy dev`).

Выберите файловый маршрутизатор, веб-проект и любую клиентскую платформу (или ничего). Открыть
<http://localhost:3000>. Длинные шаги печатают по одной строке со своей длительностью, как это делает `uv`.

<!-- router:modular -->
Ответьте `No` на запрос файлового маршрутизатора: `nx new` формирует модульный маршрутизатор в `src/apps/` вместо `src/routes/`.
<!-- /router -->

<!-- router:custom -->
Ответьте `Yes` на запрос файлового маршрутизатора для страниц, затем смонтируйте существующий `APIRouter` в `nexyconfig.py`: два маршрутизатора сосуществуют.
<!-- /router -->

## 2. Отредактируйте макет

<!-- router:fbr,custom -->
`src/routes/layout.nexy` владеет HTML-документом (при маршрутизации клиента React это `layout.tsx`). Измените `<title>`:

```nexy
<title>Notes</title>
```

Сохранить: браузер перезагружается. См. [Макеты](../routing/fbr/layouts/README.md).
<!-- /router -->

<!-- router:modular -->
Контроллер визуализирует `src/apps/layout.nexy` вокруг представления, и этот файл владеет HTML-документом. Измените `<title>`:

```nexy
<title>Notes</title>
```

Сохранить: браузер перезагружается. См. [Вид с контроллера](../routing/modular/README.md#views-from-a-controller).
<!-- /router -->

## 3. Добавить страницу

<!-- router:fbr,custom -->
```nexy filename="src/маршруты/notes.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

Откройте <http://localhost:3000/notes>: вы должны увидеть две пули. Он подается в `/notes`. Часть между `---` — Python, остальная часть — Jinja2.
<!-- /router -->

<!-- router:modular -->
Контроллер возвращает представление. Создайте `src/apps/notes_view.nexy`:

```nexy filename="src/apps/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

Объявите маршрут в `src/apps/app_controller.py` и добавьте контроллер в модуль:

```python filename="src/apps/app_controller.py"
@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/notes_view.nexy"),
        })
```

```python filename="src/apps/app_module.py"
from .app_controller import AppController, NotesController

controllers = [AppController, NotesController]
```

Откройте <http://localhost:3000/notes>: вы должны увидеть две пули. Часть между `---` — Python, остальная часть — Jinja2.
<!-- /router -->

## 4. Добавьте конечную точку

<!-- router:fbr,custom -->
```python filename="src/routes/api/notes.py"
async def GET():
    return [{"id": 1, "text": "Buy milk"}]
```

```bash
curl http://localhost:3000/api/notes
```

Вы должны получить `[{"id":1,"text":"Buy milk"}]`. Имя функции — метод HTTP. Интерактивная документация по API находится по адресу `/docs`.
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/app_controller.py"
@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": 1, "text": "Buy milk"}]
```

Добавьте `NotesApiController` к `controllers` в `src/apps/app_module.py`, затем запустите:

```bash
curl http://localhost:3000/api/notes
```

Вы должны получить `[{"id":1,"text":"Buy milk"}]`. Имя метода — метод HTTP. Документация по интерактивному API находится по адресу `/docs`.
<!-- /router -->

## 5. Поделитесь данными

Переместите список в модуль Python и используйте его в обоих файлах:

```python filename="src/notes.py"
NOTES = ["Buy milk", "Ship Nexy"]
```

<!-- router:fbr,custom -->
```nexy filename="src/маршруты/notes.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes_view.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/apps/app_controller.py"
from src.notes import NOTES


@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

## 6. Стройте и обслуживайте

```bash
nx build
nx start
```

`nx build` печатает каждую фазу с указанием ее продолжительности. `nx start` обслуживает скомпилированный вывод с Uvicorn: нет процесса Node во время выполнения.

## Где дальше

- [Маршрутизация](../routing/README.md): динамические сегменты и группы
- [Действия](../guides/actions.md): вызов Python из формы или из клиента
- [Тестирование](../guides/testing.md): тестовые страницы и конечные точки
- [Deploy](../deployment/README.md): контейнеры и обратные прокси
