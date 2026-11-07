# Создание приложения для заметок с помощью Nexy, часть 3: динамические маршруты и API

Часть 3 дает каждой заметке свой собственный URL-адрес `/notes/1` и обслуживает те же заметки, что и JSON в `/api/notes`, оба считываются из одного модуля Python.

**Прежде чем начать:** приложение из [части 2](pages-and-layouts.md).

## Храните заметки в одном модуле

Страница и API будут читать один и тот же список. Переместите его в отдельный модуль с помощью функции, которая находит одну заметку:

```python filename="src/notes.py"
NOTES = {1: "Buy milk", 2: "Ship Nexy"}


def find(note_id: int) -> str | None:
    return NOTES.get(note_id)
```

## Свяжите каждую заметку с соответствующей страницей.

<!-- router:fbr,custom -->
```nexy filename="источник/маршруты/заметки/index.nexy"
---
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for id, text in notes %}
    <li><a href="/notes/{{ id }}">{{ text }}</a></li>
    {% endfor %}
  </ul>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for id, text in notes %}
    <li><a href="/notes/{{ id }}">{{ text }}</a></li>
    {% endfor %}
  </ul>
</section>
```
<!-- /router -->

## Добавить страницу в заметку

<!-- router:fbr,custom -->
Имя папки или файла в скобках является сегментом URL-адреса: `[id].nexy` отвечает на `/notes/1`, `/notes/2` и передает сегмент на страницу в качестве реквизита. `id: prop[int]` преобразует его в число, поэтому `/notes/abc` отвечает на `404` до запуска страницы.

```nexy filename="src/маршруты/заметки/[id].nexy"
---
from nexy import notFound
from src.notes import find

id: prop[int]
text = find(id)
if text is None:
    notFound()
---
<section class="app-page">
  <h1>{{ text }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

<!-- router:modular -->
`{id}` в пути контроллера — это сегмент URL-адреса, передаваемый методу под этим именем. `id: int` преобразует его в число, поэтому `/notes/abc` отвечает на `404` до запуска метода.

```nexy filename="src/apps/notes/note_view.nexy"
---
text: prop[str]
---
<section class="app-page">
  <h1>{{ text }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

`notFound()` останавливает запрос с помощью `404`: примечание, которое не существует, отвечает как URL-адрес, который не существует.

## Подавать заметки в формате JSON

<!-- router:fbr,custom -->
Файл `.py` в папке `src/routes/` представляет собой маршрут API. Каждая функция, названная в честь метода HTTP, отвечает этому методу:

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": id, "text": text} for id, text in NOTES.items()]
```
<!-- /router -->

<!-- router:modular -->
Три контроллера заметок в одном файле. Каждый метод, названный в честь метода HTTP, отвечает этому методу:

```python filename="src/apps/notes/notes_controller.py"
from nexy import notFound
from nexy.decorators import Controller
from nexy.hooks import useViews
from src.notes import NOTES, find

LAYOUT = "src/apps/layout.nexy"


def page(view: str, **context: object):
    return useViews(LAYOUT, context={"children": useViews(view, context=context)})


@Controller("/notes")
class NotesController:
    async def get(self):
        return page("src/apps/notes/notes_view.nexy")


@Controller("/notes/{id}")
class NoteController:
    async def get(self, id: int):
        text = find(id)
        if text is None:
            notFound()
        return page("src/apps/notes/note_view.nexy", text=text)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        return [{"id": id, "text": text} for id, text in NOTES.items()]
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NoteController, NotesApiController, NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController, NoteController, NotesApiController]
```
<!-- /router -->

Проверьте три URL-адреса:

- <http://localhost:3000/notes/1> показывает *Купить молоко*;
- <http://localhost:3000/notes/9> отвечает *Страница не найдена*;
- `curl http://localhost:3000/api/notes` печатает `[{"id":1,"text":"Buy milk"},{"id":2,"text":"Ship Nexy"}]`.

API вместе со схемой указан в <http://localhost:3000/docs>.

## Что вы узнали

<!-- router:fbr,custom -->
- `[id].nexy` — динамический сегмент; `id: prop[int]` читает и преобразует его.
- Файл `.py` под `src/routes/` отвечает в формате JSON, по одной функции на каждый HTTP-метод.
<!-- /router -->
<!-- router:modular -->
- `{id}` в пути контроллера — динамический сегмент; `id: int` преобразует его.
- Метод контроллера, возвращающий данные, отвечает в формате JSON; тот, который возвращает `useViews` отвечает на страницу.
<!-- /router -->
- `notFound()` отвечает `404` откуда угодно; общий модуль поддерживает синхронизацию страниц и API.

## Следующие шаги

- [Часть 4: компоненты](components.md)
- [Исключения и ошибки](../reference/exceptions.md): `notFound`, `redirect` и другие выходы
