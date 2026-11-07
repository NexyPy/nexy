# Создание приложения для заметок с помощью Nexy, часть 7: отображение ошибок проверки

Часть 7 отклоняет пустое или слишком длинное примечание и показывает, почему над формой на той же странице все еще нет JavaScript.

**Прежде чем начать:** приложение из [части 6](create-a-note.md).

## Два вида ошибок

Подсказки типа действия уже отказываются от неправильной формы: форма без поля `text` отвечает на `422` до запуска `create_note`. Правило, касающееся самого значения, например «не пусто», вы можете указать в действии.

## Проверьте примечание в действии

В случае сбоя посетитель отправляется обратно в список с указанием причины в URL-адресе; успех возвращается в список без него:

```python filename="src/actions/notes.py"
from urllib.parse import urlencode

from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.notes import add_note

MAX_LENGTH = 200


def back(error: str = "") -> RedirectResponse:
    query = f"?{urlencode({'error': error})}" if error else ""
    return RedirectResponse(f"/notes{query}", status_code=303)


@Action
async def create_note(text: str) -> RedirectResponse:
    text = text.strip()
    if not text:
        return back("A note cannot be blank.")
    if len(text) > MAX_LENGTH:
        return back(f"A note is at most {MAX_LENGTH} characters.")
    add_note(text)
    return back()
```

`303` сообщает браузеру загрузить следующую страницу с `GET`, поэтому при обновлении форма не публикуется во второй раз.

## Покажите причину над формой

`useSearchParams()` считывает строку запроса текущего запроса:

<!-- router:fbr,custom -->
```nexy filename="источник/маршруты/заметки/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
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
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
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
</section>
```
<!-- /router -->

`| e` экранирует сообщение: строка запроса исходит от посетителя, поэтому она никогда не записывается на страницу в виде HTML. `role="alert"` заставляет программу чтения с экрана объявить об этом.

`required` и `maxlength` позволяют браузеру остановить большинство ошибок, прежде чем они покинут его. Действие проверяет еще раз: запрос не обязательно должен поступать из вашей формы.

Добавьте примечание из трех пробелов: список вернется с надписью *Примечание не может быть пустым.* над формой.

## Что вы узнали

- Подсказки типа исключают неправильную форму с помощью `422`; правила о значении идут в действии.
- Действие может ответить `RedirectResponse`; `303` после формы избегает второго сообщения.
- `useSearchParams()` считывает строку запроса, а `| e` экранирует то, что отправил посетитель.

## Следующие шаги

- [Часть 8: редактирование и удаление заметки](edit-and-delete.md)
- [Исключения и ошибки](../reference/exceptions.md): на каждый статус может ответить Действие и страница.
