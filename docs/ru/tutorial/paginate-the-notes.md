# Создайте приложение для заметок с помощью Nexy, часть 9: разбивка заметок на страницы

В части 9 показаны примечания по пять одновременно со ссылками на следующую и предыдущую страницы, читаемые из `page` URL-адреса: `/notes?page=2`.

**Прежде чем начать:** приложение из [части 8](edit-and-delete.md).

## Запросить в базе данных одну страницу

`OFFSET` пропускает примечания на предыдущих страницах, `LIMIT` оставляет пять. Запрос на одну больше пяти бесплатно сообщает, существует ли следующая страница:

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


def add_note(text: str) -> Note:
    note = Note(text=text)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note


def change_note(note_id: int, text: str) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        note.text = text
        session.commit()
    return True


def remove_note(note_id: int) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        session.delete(note)
        session.commit()
    return True


PAGE_SIZE = 5


def notes_page(number: int) -> tuple[list[Note], bool]:
    """One page of notes, oldest first, and whether a page comes after it."""
    with Session(engine) as session:
        query = select(Note).order_by(Note.id).offset((number - 1) * PAGE_SIZE).limit(PAGE_SIZE + 1)
        found = list(session.exec(query))
    return found[:PAGE_SIZE], len(found) > PAGE_SIZE
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


def add_note(text: str) -> Note:
    note = Note(text=text)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note


def change_note(note_id: int, text: str) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        note.text = text
        session.commit()
    return True


def remove_note(note_id: int) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        session.delete(note)
        session.commit()
    return True


PAGE_SIZE = 5


def notes_page(number: int) -> tuple[list[Note], bool]:
    """One page of notes, oldest first, and whether a page comes after it."""
    with Session(engine) as session:
        query = select(Note).order_by(Note.id).offset((number - 1) * PAGE_SIZE).limit(PAGE_SIZE + 1)
        found = list(session.exec(query))
    return found[:PAGE_SIZE], len(found) > PAGE_SIZE
```
<!-- /router -->

## Прочтите номер страницы по URL-адресу.

`page` строки запроса — это текст, отправленный посетителем: все, что не является положительным числом, возвращается на первую страницу, поэтому `/notes?page=abc` по-прежнему отвечает.

<!-- router:fbr,custom -->
```nexy filename="источник/маршруты/заметки/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import notes_page

params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(number)
notes = found[0]
more = found[1]
---
<section class="app-page">
  <h1>Notes</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import notes_page

params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(number)
notes = found[0]
more = found[1]
---
<section class="app-page">
  <h1>Notes</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

`rel="prev"` и `rel="next"` сообщают браузерам и поисковым системам, как страницы следуют друг за другом, а `aria-label` называет ссылки для программы чтения с экрана.

Добавляйте примечания, пока их не станет больше пяти: список заканчивается на пяти со ссылкой **Старее**. Он ведет на `/notes?page=2`, на который есть обратная ссылка **Новая**.

## Что вы узнали

- `offset` и `limit` читают одну страницу; запрос на еще одну строку говорит о том, следует ли за ней еще одна страница.
- `useSearchParams()` читается `?page=`; значение посетителя проверяется перед его использованием.
- `rel="prev"` и `rel="next"` связывают страницы для браузеров, сканеров и программ чтения с экрана.

## Следующие шаги

- [Модуль 3, часть 10: создайте учетную запись и войдите в нее](accounts.md)
- [SQLite](../databases/sqlite.md): индексы, прагмы и тесты для базы данных в памяти.
