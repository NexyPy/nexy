# .nexy-файлы

Файл `.nexy` является компонентом: Python сверху, HTML посередине, CSS внизу.

**Прежде чем начать:** проект, созданный с помощью [Быстрый старт](../../getting-started/quick-start.md). Файл `.nexy` не требует настройки сборки: `nx dev` компилирует его при сохранении.

<!-- router:fbr,custom -->
```nexy filename="src/маршруты/блог/[слизняк].nexy"
---
from nexy import usePathname

slug: prop[str] = "untitled"
pathname = usePathname()
---
<article class="post">
  <h1>{{ slug }}</h1>
  <p>You are on {{ pathname }}</p>
</article>

<style>
  .post { max-width: 60ch; }
</style>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/блог/post_view.nexy"
---
from nexy import usePathname

slug: prop[str] = "untitled"
pathname = usePathname()
---
<article class="post">
  <h1>{{ slug }}</h1>
  <p>You are on {{ pathname }}</p>
</article>

<style>
  .post { max-width: 60ch; }
</style>
```

Контроллер передает `slug` со своего пути:

```python filename="src/apps/blog/post_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/blog/post_view.nexy", context={"slug": slug})
```
<!-- /router -->

## Фронтматтер

Все, что находится между двумя строками `---` — это Python. Импорты разрешаются при компиляции компонента; остальное выполняется для каждого запроса и позволяет считывать состояние запроса.

| Что | Пример |
|---|---|
| Импортировать модуль | `import json`, `from datetime import datetime` |
| Импортировать компонент | `from "@/components/card.nexy" import Card` |
| Объявить собственность | `title: prop[str] = "Default"` |
| Вычислить значение | `year = datetime.now().year` |
| Прочитать запрос | `pathname = usePathname()` |
| Кэшировать страницу (ISR) | `revalidate = 60` |

## Свойства

Свойства — это API компонента. `prop[type]` объявляет тип, `= value` дает значение по умолчанию. Свойство без значения по умолчанию должно быть передано родителем.

Импорт, начинающийся с псевдонима, разрешается через `useAliases`. Установка `nx new` записывает карты `@` в `src`, в результате чего `@/components/card.nexy` означает `src/components/card.nexy`.

## Шаблон

Ниже заголовка находится HTML с Jinja2. Переменные из заголовка и свойств находятся в области видимости.

```html
{% for item in items %}
  <li>{{ item.name }}</li>
{% endfor %}

{% if user %}
  <p>Welcome, {{ user.name }}</p>
{% endif %}
```

Автоэкранирование **выключено**: шаблоны представляют собой собственный HTML-код проекта, поэтому `{{ value }}` вставляется так, как написано. Избегайте ненадежных значений самостоятельно с помощью `{{ value | e }}`. `| safe` поэтому ничего не меняет.

> [!NOTE]
> оберните JavaScript, содержащую `{{` или `{%` в `{% raw %}...{% endraw %}`. Такие платформы, как Vue и Svelte используют одни и те же фигурные скобки.

## Компоненты

В качестве тега можно использовать любой импортированный вызываемый объект, имя которого начинается с заглавной буквы. Компилятор переписывает его в вызов Jinja: атрибуты становятся аргументами ключевого слова.

<!-- router:fbr,custom -->
```nexy filename="источник/маршруты/index.nexy"
---
from "@/components/card.nexy" import Card
from nexy import Audio
---
<Card title="Hello">
  <p>Child content</p>
</Card>

<Audio src="/theme.mp3" controls=True />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/card.nexy" import Card
from nexy import Audio
---
<Card title="Hello">
  <p>Child content</p>
</Card>

<Audio src="/theme.mp3" controls=True />
```
<!-- /router -->

Последняя строка — это ровно `{{ Audio("/theme.mp3", controls=True) }}`. Оба синтаксиса действительны для встроенных помощников `Image`, `Link`, `Audio` и `Video` — см. [компоненты](components.md#two-syntaxes-one-function).

Дочерние элементы отображаются через `<Slot />` (заглавная S) внутри дочернего компонента и через `{{ children }}` внутри макета.

Передайте вычисленное значение с помощью Jinja внутри атрибута: `<Icon path="{{ icon }}" size="{{ size }}" />`. Простое имя, такое как `path=icon` — это текст `icon`, а не переменная. Чтобы присвоить компоненту класс CSS, объявите свойство `class_name`: `class` — это ключевое слово Python.

> [!NOTE]
> вспомогательный тег всегда самозакрывающийся. Передача содержимого в `Link` осуществляется через его аргумент `children` (`<Link href="/about" children="About" />`), а не через содержимое элемента.

## Стили

Блоки `<style>` создаются вместе со страницей, которая их объявляет. Они не ограничены областью действия: имя класса, используемое в двух компонентах, представляет собой один класс. Префикс или пространство имен ваших классов.

## Правила, которые экономят время

- Один компонент на файл. Имя файла — это имя компонента в PascalCase (`CopyChip.nexy`). Компонент `.nexy` импортируется как модуль Python: дефис в имени (`copy-chip.nexy`) не компилируется.
- Объявляйте реквизиты перед их использованием: необъявленная переменная отображается как пустая строка, поскольку неопределенное значение Jinja2 здесь не указано.
- Сохраняйте побочные эффекты внутри функций — фронтальная часть запускается снова при каждом запросе.

## Следующие шаги

- [Markdown и MDX](markdown.md): страницы с контентом
- [ISR](../../rendering/isr.md): кэшировать страницу для каждого пути
- [CSR](../../rendering/csr.md): рендеринг на стороне клиента
