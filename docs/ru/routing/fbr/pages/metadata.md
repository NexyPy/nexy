# Метаданные страницы

Страница называет свой заголовок и теги заголовка, а корневой макет записывает их один раз.

## Скажи это на странице

Для страницы, которая никогда не меняется, напишите литерал вверху заголовка:

```nexy filename="src/маршруты/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

Если заголовок зависит от данных, вместо этого вызовите `setMetadata`:

```nexy filename="src/маршруты/сообщения/[слизень].nexy"
---
from nexy import notFound, setMetadata

from src.posts import find

slug: prop[str]
post = find(slug) or notFound()
setMetadata(title=post.title, description=post.summary, og={"image": post.cover})
---
<h1>{{ post.title }}</h1>
```

Модульный контроллер вызывает `setMetadata(...)` перед возвратом `useViews(...)`.

## Напишите это в макете

Корневой макет владеет `<head>`. Одна строка записывает то, что написано на странице, экранировано:

```nexy filename="src/маршруты/layout.nexy"
---
from nexy import setMetadata, useMetadata

children: prop[NexyElement]
setMetadata(title_template="%s | My site")
---
<!DOCTYPE html>
<html>
  <head>
    {{ useMetadata().html() }}
  </head>
  <body>{{ children }}</body>
</html>
```

Страница запускается раньше своих макетов, поэтому макет находит то, что запрашивает страница. Страница, на которой ничего не сказано, получает `useTitle` вашего `nexyconfig.py` и никакой другой тег.

## Поля

| Поле | Записывается как |
|---|---|
| `title` | `<title>`; с `title_template="%s \| My site"` заголовок помещается в `%s` |
| `description` | `<meta name="description">` |
| `canonical` | `<link rel="canonical">` |
| `robots` | `<meta name="robots">`, например `"noindex"` |
| `icon` | `<link rel="icon">` |
| `og` | по одному `<meta property="og:...">` на клавишу: `{"image": "/cover.png"}` дает `og:image` |
| `twitter` | по одному `<meta name="twitter:...">` на каждую клавишу |
| `extra` | список атрибутов, по одному `<meta>` каждый: `[{"name": "theme-color", "content": "#fff"}]` |

Более поздний вызов заменяет значение; `og`, `twitter` и `extra` дополняют то, что есть. Поле, которое не существует, вызывает `TypeError`, поэтому опечатка не приводит к молчанию.

## Безопасно по умолчанию

Каждое значение экранируется HTML, поэтому заголовок, созданный на основе URL-адреса или базы данных, не может закрыть тег и внедрить скрипт. Значение экранируется один раз, когда макет вызывает `html()`: не экранируйте его самостоятельно.

## Следующие шаги

- [Страницы](README.md)
- [Макеты](../layouts/README.md)
- [Страницы ошибок](../errors/README.md)
