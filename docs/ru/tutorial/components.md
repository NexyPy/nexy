# Создание приложения для заметок с помощью Nexy, часть 4: компоненты

Часть 4 превращает каждую заметку в компонент многократного использования, файл `.nexy`, который вы импортируете как имя Python и используете как HTML-тег.

**Прежде чем начать:** приложение из [части 3](dynamic-routes.md).

## Напишите компонент

Компонент — это файл `.nexy` вне маршрутов. Его свойства объявлены с помощью `prop[...]`, и вызывающая сторона передает их как атрибуты:

```nexy filename="источник/компоненты/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
---
<article class="note">
  <a href="/notes/{{ id }}">{{ text }}</a>
</article>

<style>
  .note { padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
</style>
```

Блок `<style>` отправляется с каждой страницей, использующей карту. Он не ограничен: `.note` — это один класс для всей страницы, поэтому укажите имена классов компонентов, которые использует только он.

## Используйте его в списке

<!-- router:fbr,custom -->
```nexy filename="источник/маршруты/заметки/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

`@/` — это псевдоним импорта части 1: он указывает на `src/`. Имя файла — это имя компонента в PascalCase: `NoteCard.nexy` экспортирует `NoteCard`.

Откройте <http://localhost:3000/notes>: каждая нота теперь является карточкой.

## Что вы узнали

- Файл `.nexy` вне маршрутов является компонентом; его `prop[...]` — это его атрибуты.
- `from "@/components/x.nexy" import X` импортирует его; `<X />` отображает это.
- Блок `<style>` не ограничен: назовите классы компонента после него.

## Следующие шаги

- [Часть 5: сохраните заметки в SQLite](store-the-notes.md)
- [Компоненты](../views/nexy/components.md): `Image`, `Link` и встроенные помощники.
