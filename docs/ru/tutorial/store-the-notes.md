# Создайте приложение для заметок с помощью Nexy, часть 5: сохраните заметки в SQLite

Часть 5 перемещает заметки из словаря Python в базу данных SQLite с моделью, миграцией и двумя заметками для начала, и страницы считывают их оттуда.

**Прежде чем начать:** приложение из [части 4](components.md).

## Установите ORM и инструмент миграции.

```bash
uv add sqlmodel alembic
```

[SQLModel](https://sqlmodel.tiangolo.com/) описывает таблицу как класс Python, а Alembic превращает изменения в этих классах в миграции. Nexy тоже не наворачивает: пользуешься ими как есть.

## Открыть базу данных

Адрес базы данных находится в `.env` в корне проекта. `nx migrate` и приложение прочитали его оттуда:

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

`sqlite:///dev.db` — это файл, `dev.db`, следующий за `nexyconfig.py`: SQLite не нуждается в сервере. Не допускайте использования `.env` в Git: он хранит секреты реальной базы данных.

Движок — это соединение с базой данных. Он читает `DATABASE_URL` с тем же файлом, что и по умолчанию, когда переменная не установлена:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///dev.db"))
```

## Описать заметку

<!-- router:fbr,custom -->
```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

<!-- router:modular -->
Модель живет вместе с функцией, которой она принадлежит, рядом с ее контроллером:

```python filename="src/apps/notes/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

`table=True` превращает класс в таблицу, `note`. `id` предоставляется базой данных при сохранении заметки.

## Создайте таблицу с миграцией

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` записывает папку `alembic/` и указывает на вашу модель. `-m` сравнивает модель с базой данных и записывает миграцию, создающую таблицу; `--upgrade` запускает его. Измените модель позже, снова запустите последние две команды, и таблица будет следовать.

## Прочитать заметки из базы данных

Функции `src/notes.py` сохраняют свои имена, поэтому страницы меняются мало: теперь они открывают сеанс, запрашивают таблицу и возвращают объекты `Note` вместо строк.

<!-- router:fbr,custom -->
```python filename="src/notes.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def all_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).order_by(Note.id)))


def find(note_id: int) -> Note | None:
    with Session(engine) as session:
        return session.get(Note, note_id)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/notes.py"
from sqlmodel import Session, select

from src.apps.notes.note_model import Note
from src.configs.db import engine


def all_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).order_by(Note.id)))


def find(note_id: int) -> Note | None:
    with Session(engine) as session:
        return session.get(Note, note_id)
```
<!-- /router -->

## Добавьте две заметки для начала

Начальный скрипт заполняет пустую базу данных, поэтому каждая новая копия проекта начинается с чего-то, что можно показать:

<!-- router:fbr,custom -->
```python filename="источник/seed.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def seed() -> None:
    with Session(engine) as session:
        if session.exec(select(Note)).first() is None:
            session.add_all([Note(text="Buy milk"), Note(text="Ship Nexy")])
            session.commit()


if __name__ == "__main__":
    seed()
```
<!-- /router -->

<!-- router:modular -->
```python filename="источник/seed.py"
from sqlmodel import Session, select

from src.apps.notes.note_model import Note
from src.configs.db import engine


def seed() -> None:
    with Session(engine) as session:
        if session.exec(select(Note)).first() is None:
            session.add_all([Note(text="Buy milk"), Note(text="Ship Nexy")])
            session.commit()


if __name__ == "__main__":
    seed()
```
<!-- /router -->

```bash
python -m src.seed
```

При запуске Nexy импортирует каждый модуль из `src/`, чтобы найти действия из [части 6](create-a-note.md). `if __name__ == "__main__":` сохраняет начальное значение для приведенной выше команды: импортированный приложением файл определяет только `seed` и ничего не затрагивает.

## Показать заметки из базы данных

<!-- router:fbr,custom -->
```nexy filename="источник/маршруты/заметки/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```

```nexy filename="src/маршруты/заметки/[id].nexy"
---
from nexy import notFound
from src.notes import find

id: prop[int]
note = find(id)
if note is None:
    notFound()
---
<section class="app-page">
  <h1>{{ note.text }}</h1>
  <a href="/notes">All notes</a>
</section>
```

```python filename="src/routes/api/notes.py"
from src.notes import all_notes


async def GET():
    return [note.model_dump() for note in all_notes()]
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```

```python filename="src/apps/notes/notes_controller.py"
from nexy import notFound
from nexy.decorators import Controller
from nexy.hooks import useViews
from src.notes import all_notes, find

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
        note = find(id)
        if note is None:
            notFound()
        return page("src/apps/notes/note_view.nexy", text=note.text)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        return [note.model_dump() for note in all_notes()]
```
<!-- /router -->

Открыть <http://localhost:3000/notes>: те же две карты, теперь прочитанные из `dev.db`. Перезапустите `nexy dev`, и они все еще там.

## Что вы узнали

- SQLModel описывает таблицу как класс; движок в `src/configs/db.py` открывает базу данных.
- `nx migrate` записывает и запускает миграции: `--init` один раз, затем `-m` и `--upgrade` для каждого изменения.
- Страницы и контроллеры вызывают простые Python функции, которые запрашивают базу данных: Nexy не добавляет никаких слоев.

## Следующие шаги

- [Часть 6: создайте заметку из формы](create-a-note.md)
- [SQLite](../databases/sqlite.md): прагмы, асинхронный доступ и тесты в базе данных в памяти.
