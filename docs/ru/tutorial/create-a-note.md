# Создание приложения заметок с помощью Nexy, часть 6: создание заметки из формы

В части 6 над списком добавляется форма: она отправляет сообщение в функцию Python с пометкой `@Action`, которая сохраняет заметку, и посетитель возвращается в список с новой заметкой в нем.

**Прежде чем начать:** приложение из [части 5](store-the-notes.md) с его базой данных.

## Сохранить заметку

Добавьте функцию, которая сохраняет одну заметку и возвращает ее рядом с двумя, которые их прочитали:

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
```
<!-- /router -->

## Превратите это в действие

Действие — это Python функция, которую может вызвать браузер. `@Action` служит ему как `POST`, проверяет ввод на соответствие подсказкам типов и запускает его:

```python filename="src/actions/notes.py"
from nexy.decorators import Action
from src.notes import add_note


@Action
async def create_note(text: str) -> int:
    return add_note(text).id
```

При запуске Nexy импортирует каждый модуль `src/` и выполняет найденные действия: для любого маршрутизатора нет маршрута, который можно было бы объявить. `src/actions/` — это то место, где они хранятся в этом руководстве.

## Отправьте туда форму

Шаблон `.nexy` знает путь каждого действия как `__actions_path["name"]`. Там публикуется простая HTML-форма, поэтому страница работает до загрузки любого скрипта:

<!-- router:fbr,custom -->
```nexy filename="источник/маршруты/заметки/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
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

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

Вход имеет имя `text`, как и параметр `create_note`: именно так поле достигает его.

## Показывать заметку как текст, а не как HTML

Отныне заметка — это то, что напечатал посетитель. Шаблон `.nexy` записывает значение как есть, поэтому примечание `<script>…</script>` будет отображаться в браузере каждого, кто откроет список. `| e` экранирует его: `<` становится `&lt;`, и примечание отображается как текст.

```nexy filename="источник/компоненты/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
---
<article class="note">
  <a href="/notes/{{ id }}">{{ text | e }}</a>
</article>

<style>
  .note { padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
</style>
```

<!-- router:fbr,custom -->
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
  <h1>{{ note.text | e }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/note_view.nexy"
---
text: prop[str]
---
<section class="app-page">
  <h1>{{ text | e }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

Экранируйте каждое значение, поступающее от посетителя или из базы данных. `| safe` делает обратное: сохраняет его для HTML, который вы написали сами.

## Попробуйте это

Введите *Читать документацию* и нажмите **Добавить**. Действие сохраняет заметку, затем отвечает на `303` обратно на `/notes`, и браузер снова отображает список с третьей заметкой внизу.

## Что вы узнали

- `@Action` превращает функцию Python в конечную точку `POST` с подсказками ее типа в качестве входных данных.
- Форма отправляет сообщение через `__actions_path["name"]` без JavaScript и возвращает `303`.
- Имена полей формы — это имена параметров Действия.
- `| e` показывает, что посетитель напечатал в виде текста: экранируйте все значения, которые не были получены от вас.

## Следующие шаги

- [Часть 7: показать ошибки проверки](validation-errors.md)
- [Действия](../guides/actions.md): вводимые вызовы из браузера, ошибки и безопасность
