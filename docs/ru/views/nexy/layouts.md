# макет.nexy

Файл макета режима сервера (`useCSR = False`). Корневой владеет HTML-документом.

## Корневая раскладка

```nexy filename="src/маршруты/layout.nexy"
---
from nexy import Vite

children: prop[NexyElement]
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My app</title>
  <Vite />
</head>
<body>
  <main>{{ children | safe }}</main>
</body>
</html>
```

- `<!DOCTYPE html>`, `<html>`, `<head>` и `<body>` живут здесь и больше нигде.
- `<Vite />` внедряет клиентские сценарии и стили один раз в `<head>`.
- `{{ children | safe }}` — это место, где отображается страница или следующий вложенный макет.

## Вложенные макеты

`layout.nexy` в подкаталоге оборачивает это поддерево и визуализируется внутри его родителя. Он не повторяет теги документа:

```nexy filename="src/маршруты/блог/layout.nexy"
---
children: prop[NexyElement]
---
<nav>...</nav>
<article>{{ children | safe }}</article>
```

`blog/[slug].nexy` отображается как `layout.nexy > blog/layout.nexy > page`.

## Компоненты и острова

Макет может импортировать `.nexy` компоненты (верхний и нижний колонтитулы) и клиентские компоненты. Клиентский компонент в макете — это [остров](../../rendering/islands.md), как и любой другой:

```nexy
---
from "@/components/Header.nexy" import Header
from "@/components/theme/theme.tsx" import Theme
---
<Header />
<Theme directive="client:idle" />
```

## Без макета

Проект без `layout.nexy` по-прежнему отвечает действительным документом: Nexy возвращается к минимальной оболочке с `<!DOCTYPE html>`, мета-окном просмотра и тегами Vite. Добавьте макет, как только вам понадобится заголовок, шрифты или навигация.

## В модульном маршрутизаторе

Контроллеры выбирают свои представления, поэтому сами составляют макет:

```python
return useViews("src/apps/layout.nexy", context={"children": useViews("src/apps/app_view.nexy")})
```

## Чего он не может сделать

- Он не может сосуществовать с `layout.tsx`, `layout.vue` или `layout.svelte`: проект в режиме сервера не имеет клиентских маршрутов ([режимы](../../routing/fbr/modes.md)).
- Он не запускается на клиенте: используйте остров для интерактивности.

## Следующие шаги

- [Макеты](../../routing/fbr/layouts/README.md)
- [Наследование](../../routing/fbr/inheritance.md)
- [файлы .nexy](README.md)
