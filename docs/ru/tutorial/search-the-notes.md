# Создание приложения для заметок с помощью Nexy, часть 13: поиск по заметкам по мере ввода

В части 13 над заметками добавляется поле поиска: остров React фильтрует каждую заметку пользователя при каждом нажатии клавиши в браузере без запроса к серверу.

**Прежде чем начать:** приложение из [части 12](password-reset.md). Проект был создан с помощью React в [части 1](create-the-project.md), поэтому React уже установлен.

## Остров, и почему именно здесь

Остальная часть страницы остается HTML, отображаемым сервером: список, формы, страницы заметок. Браузер нужен только окну поиска, поэтому только окно поиска — React. Это *остров*: один клиентский компонент внутри серверной страницы, который сам по себе становится интерактивным.

## Компонент поиска

```tsx filename="источник/компоненты/NoteSearch.tsx"
import { useState } from "react"

type Note = { id: number; text: string }

export default function NoteSearch({ notes }: { notes: Note[] }) {
  const [query, setQuery] = useState("")
  const words = query.trim().toLowerCase()
  const found = words ? notes.filter((note) => note.text.toLowerCase().includes(words)) : []
  return (
    <section className="note-search" aria-label="Search the notes">
      <label>
        Search
        <input type="search" value={query} onChange={(event) => setQuery(event.target.value)} />
      </label>
      <div aria-live="polite">
        {words && found.length === 0 && <p>No note matches “{query}”.</p>}
        {found.length > 0 && (
          <ul>
            {found.map((note) => (
              <li key={note.id}>
                <a href={`/notes/${note.id}`}>{note.text}</a>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
```

React записывает `{note.text}` как текст: примечание `<b>x</b>` показывает скобки, без `| e` для добавления.

`found` вычисляется только после того, как что-то напечатано, и это имеет значение для сборки: `nx build` отображает каждый остров один раз в HTML, с заполнителями вместо его свойств. Компонент, который считывает свойство списка во время первого рендеринга, получает заполнитель вместо списка и не отправляет HTML. Этот читает `notes` только после нажатия клавиши, поэтому сборка отображает окно поиска, и страница показывает его до запуска любого JavaScript.

`aria-live="polite"` заставляет программу чтения с экрана читать результаты при их изменении, не прерывая их.

## Поместите остров на страницу

Страница передает заметки как реквизит: список словарей, который Nexy превращает в JSON для браузера. Входят все заметки, а не только пять на текущей странице, поэтому поиск охватывает их все:

<!-- router:fbr,custom -->
```nexy filename="источник/маршруты/заметки/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from "@/components/NoteSearch.tsx" import NoteSearch
from nexy import useSearchParams
from src.guard import signed_in_user
from src.notes import all_notes, notes_page

user_id = signed_in_user()
params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(user_id, number)
notes = found[0]
more = found[1]
searchable = [{"id": note.id, "text": note.text} for note in all_notes(user_id)]
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['sign_out'] }}">
    <button type="submit">Sign out</button>
  </form>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <NoteSearch notes="{{ searchable }}" directive="client:idle" />

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
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
from "@/components/NoteSearch.tsx" import NoteSearch
from nexy import useSearchParams
from src.guard import signed_in_user
from src.notes import all_notes, notes_page

user_id = signed_in_user()
params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(user_id, number)
notes = found[0]
more = found[1]
searchable = [{"id": note.id, "text": note.text} for note in all_notes(user_id)]
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['sign_out'] }}">
    <button type="submit">Sign out</button>
  </form>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <NoteSearch notes="{{ searchable }}" directive="client:idle" />

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

`from "@/components/NoteSearch.tsx" import NoteSearch` импортирует компонент React на страницу `.nexy`; тег передает свои атрибуты в качестве реквизита. `notes="{{ searchable }}"` передает сам список Python, а не строку. `directive="client:idle"` делает остров интерактивным, когда браузеру больше нечего делать.

Откройте <http://localhost:3000/notes> и введите несколько букв заметки: соответствующие заметки отображаются под полем при каждом нажатии клавиши. Очистите поле, и результаты исчезнут.

> [!NOTE]
> Реквизит острова перемещается по странице в формате JSON. Отправка каждой записки подходит нескольким сотням из них; для тысяч вместо этого выполните поиск на сервере с помощью запроса и фильтра `LIKE`.

## Что вы узнали

- Остров — это клиентский компонент внутри страницы сервера: здесь React только для поля поиска.
- Страница `.nexy` импортирует ее по пути и передает значения Python как реквизиты, сериализованные в JSON.
- При сборке остров визуализируется один раз с заполнителями для его реквизитов: прочитайте реквизиты списка после первого рендеринга, и остров отправит HTML.

## Следующие шаги

- [Часть 14: отметьте заметку без перезагрузки страницы](tick-a-note.md)
- [Острова и гидратация](../rendering/islands.md): директивы, реквизиты и ограничения
