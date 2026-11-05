# Компоненты

Nexy экспортирует небольшой набор помощников, которые возвращают строки HTML. Каждый из них используется в шаблоне `.nexy` двумя способами: как вызов Jinja или как тег в стиле HTML.

## Два синтаксиса, одна функция

```nexy filename="источник/маршруты/index.nexy"
---
from nexy import Audio
---
{{ Audio("/theme.mp3", controls=True) }}

<Audio src="/theme.mp3" controls=True />
```

Обе строки создают одинаковую разметку:

```html
<audio preload="metadata" controls><source src="/theme.mp3" type="audio/mp3" /></audio>
```

Компилятор переписывает `<Audio ... />` на `{{ Audio(...) }}`, поэтому форма тега не является вторым API: атрибуты — это аргументы ключевого слова функции.

## Правила оформления тега

| В теге | становится |
|---|---|
| `<Audio src="/a.mp3" />` | `Audio(src="/a.mp3")` |
| `controls=True` | `controls=True`, реальное логическое значение |
| `width=640` | `width=640`, число |
| `src="{{ url }}"` | `src=(url)`, оценено в Jinja |
| любой другой `value` | `"value"`, строка |

- Тег должен начинаться с заглавной буквы и быть импортирован во вступительной части; в противном случае компилятор вызывает `Missing Import: <Name> used but not declared.`
- Форма тега **самозакрывающаяся**. `<Audio src="/a.mp3" />` и `{{ Audio("/a.mp3") }}` эквивалентны; запись дочерних элементов внутри вспомогательного тега не поддерживается.
- Простой HTML-атрибут здесь не является логическим значением: `controls` становится `controls=""`, что неверно. Напишите `controls=True`.

> [!NOTE]
> `class_name` — документированное ключевое слово для классов CSS. Дополнительные аргументы ключевого слова становятся атрибутами HTML, поэтому `class="nav"` также достигает вывода.

## Изображение

```nexy
---
from nexy import Image
---
{{ Image("/logo.png", alt="Logo", width=128, height=32) }}

<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

`Image(src, alt="", width=None, height=None, loading="lazy", class_name=None, **attrs)` отображает `<img>` с отложенной загрузкой по умолчанию.

## Ссылка

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` отображает `<a data-nexy-link>`, обрабатываемый клиентским маршрутизатором. При использовании `prefetch=True` наведение курсора мыши или прикосновение к ссылке нагревает цель через `window.__nexy_prefetch`.

> [!NOTE]
> форма тега принимает метку как `children`, а не как содержимое элемента: `<Link href="/about" children="About" />`. Чтобы поместить разметку внутри ссылки, используйте форму вызова с компонентом `children=` или `.nexy`, который отображает `<Slot />`.

## Аудио и видео

```nexy
---
from nexy import Audio, Video
---
{{ Audio("/theme.mp3", controls=True) }}
{{ Video("/demo.mp4", width=640, height=360, muted=True, sources=["/demo.webm", "/demo.mp4"]) }}

<Audio src="/theme.mp3" controls=True />
<Video src="/demo.mp4" width=640 height=360 muted=True />
```

`Audio(src, controls=True, autoplay=False, loop=False, muted=False, preload="metadata", class_name=None, sources=None, **attrs)` и `Video(src, width=None, height=None, ...)` отображают родные проигрыватели. `sources` добавляет теги `<source>` с типом MIME, полученным из каждого расширения.

## Компонент, который вы пишете сами

Многоразовый компонент `.nexy` — это файл в папке `src/components/`: реквизиты Python вверху, HTML внизу. Он импортируется как любой другой модуль Python.

```nexy filename="источник/компоненты/Card.nexy"
---
title: prop[str]
tone: prop[str] = "neutral"
---
<article class="card card-{{ tone }}">
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="источник/маршруты/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest notes" tone="warm">
  <p>Everything published this week.</p>
</Card>
```

`title` не имеет значения по умолчанию, поэтому страница должна передать его; `tone` возвращается к `"neutral"`. Разметка между тегами находится внутри `<Slot />` (заглавная S). См. файлы [.nexy](README.md#components) для реквизитов, слотов и правил формы тегов.

## Импорт клиентского компонента

Из файла `.nexy` импортируйте компонент платформы по пути; компилятор монтирует его на клиенте и передает атрибуты в качестве реквизита:

```nexy
---
from "@/components/Counter.tsx" import Counter
---
<Counter start="0" />
```

`Import(path, framework, symbol)` делает то же самое в Python:

```python
from nexy import Import

counter = Import("@/components/Counter.tsx", "react", "Counter")
html = counter(start=0)
```

Тот же синтаксис импорта преобразует `.json`, `.css` и файлы изображений в их URL-адреса.

## Шаблон и Vite

`Template().render(path, context)` отображает файл шаблона (Jinja2 или Markdown визуализируется в HTML для маршрутов `.md`. `Template().invalidate(path)` удаляет его из кеша.

`Vite()` возвращает теги клиента для текущего режима: сценарий HMR в разработке, встроенный пакет клиента в производстве. Nexy вызывает его для каждой страницы; вам это редко нужно напрямую.

## Еще не реализовано

`Form` и `Script` — экспортированные заполнители без поведения. Не полагайтесь на них.

## Следующие шаги

- [.nexy файлы](README.md): где используются эти помощники
- [React](../react/differences.md): импорт компонентов `.tsx`
- [Frontend](../../guides/frontend.md): как связаны клиентские компоненты
