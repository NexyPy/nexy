# Создание приложения для заметок с помощью Nexy, часть 2: страницы и макеты

Во второй части добавляется страница со списком заметок и показано, как макет помещает ее в HTML-документ.

**Прежде чем начать:** проект из [части 1](create-the-project.md) с запущенным `nexy dev`.

## Добавить страницу заметок

<!-- router:fbr,custom -->
Страница — это файл в папке `src/routes/`, а ее путь — это URL-адрес. Создайте страницу заметок:

```nexy filename="источник/маршруты/заметки/index.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

`notes/index.nexy` отвечает `/notes`.
<!-- /router -->

<!-- router:modular -->
Контроллер отвечает на URL-адрес и возвращает представление. Дайте заметкам отдельную папку с видом:

```nexy filename="src/apps/notes/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

и контроллер, который отображает его в `/notes`:

```python filename="src/apps/notes/notes_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/notes/notes_view.nexy")})
```

Контроллер отвечает только после того, как модуль зарегистрирует его. Добавьте его в корневой модуль:

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController]
```
<!-- /router -->

Откройте <http://localhost:3000/notes>: вы должны увидеть две пули. Часть между двумя строками `---` — Python, выполняется на сервере; остальное — HTML с тегами Jinja2, такими как `{% for %}` и `{{ note }}`.

## Изменить макет

<!-- router:fbr,custom -->
`src/routes/layout.nexy` владеет HTML-документом: `<html>`, `<head>` и `<body>`. Nexy оборачивает в него каждую страницу, где пишет `{{children | safe}}`.
<!-- /router -->
<!-- router:modular -->
`src/apps/layout.nexy` является владельцем HTML-документа: `<html>`, `<head>` и `<body>`. Контроллер оборачивает в него свое представление, передавая представление как `children`.
<!-- /router -->

Откройте макет и измените строку `<title>Nexy App</title>` на:

```html
<title>Notes</title>
```

Сохранение: на вкладке браузера теперь написано *Заметки* на каждой странице.

## Оставьте страницам место под заголовком

Заголовок макета фиксирован: он остается в верхней части окна, над страницей. Страницы стартера занимают под ним собственное пространство; страницы приложения заметок имеют для этого один класс, `app-page`, который каждая страница руководства помещает в свое содержимое. Добавьте его в конец `src/globale.css`, таблица стилей уже загружается на каждой странице:

```css
/* The pages of the notes app: one readable column below the fixed header. */
.app-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 42rem;
  margin: 0 auto;
  padding: 8rem 1.5rem 5rem;
}

.app-page h1 {
  font-size: 2rem;
}

.app-page form {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  gap: 0.5rem;
}

.app-page label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.app-page input:not([type="hidden"]) {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-second);
  border-radius: 0.375rem;
  background: var(--background);
}

.app-page button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  background: var(--foreground);
  color: var(--background);
  cursor: pointer;
}

.app-page a {
  text-decoration: underline;
}
```

Tailwind, который использует стартер, убирает границы полей формы: эти правила возвращают их, поэтому можно увидеть формы следующих частей.

## Что вы узнали

<!-- router:fbr,custom -->
- Файл `.nexy` под `src/routes/` является страницей; его папка и имя являются его URL-адресом.
- Корень `layout.nexy` оборачивает каждую страницу HTML-документа.
<!-- /router -->
<!-- router:modular -->
- Контроллер отвечает на URL-адрес и отображает представление `.nexy` с помощью `useViews`; модуль перечисляет это.
- Макет тоже является представлением: контроллер передает ему представление страницы как `children`.
<!-- /router -->
- Файл `.nexy` — это Python между `---`, затем HTML с Jinja2.
- `src/globale.css` содержит стили, общие для каждой страницы, например `app-page`.

## Следующие шаги

- [Часть 3: динамические маршруты и API](dynamic-routes.md)
- [Файлы .nexy](../views/nexy/README.md): реквизиты, компоненты и стили.
