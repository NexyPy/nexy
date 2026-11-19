# Как добавить файлы sitemap.xml и robots.txt на сайт Nexy?

Установите `useSiteUrl` в `nexyconfig.py`: Nexy затем обслуживает `/sitemap.xml`, в котором перечислены все статические страницы проекта, и `/robots.txt`, указывающий на нее поисковым системам.

## Включите его с помощью `useSiteUrl`

`useSiteUrl` — общедоступное происхождение сайта, которое видят поисковые системы:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSiteUrl = "https://example.com"
```

`nx dev` и `nx start` затем ответят на оба файла. Без `useSiteUrl` ни один из них не существует, поэтому проект никогда не публикует URL-адрес своего сервера разработки по ошибке.

## Что указано в карте сайта

В карте сайта каждая страница указана как абсолютный URL-адрес на `useSiteUrl`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/</loc></url><url><loc>https://example.com/about</loc></url></urlset>
```

Маршрут отображается в списке, если он отвечает HTML на `GET` по фиксированному пути:

<!-- router:fbr,custom -->
- указана страница (`.nexy`, `.md`, `.mdx`, `.tsx`, `.jsx`, `.vue`, `.svelte`);
- динамическая страница, такая как `src/routes/users/[id].nexy`, не учитывается: Nexy не может знать ее значения;
- обработчик маршрута Python отвечает в формате JSON, поэтому он не учитывается.
<!-- /router -->

<!-- router:modular -->
- указан маршрут контроллера, который отвечает HTML, с `@UseResponse(response_class=HTMLResponse)`;
- маршрут с параметром пути, например `/users/{id}`, не учитывается: Nexy не может знать его значения;
- маршрут, отвечающий JSON, не учитывается.
<!-- /router -->

Маршрут, скрытый из схемы API (`include_in_schema=False`), также не учитывается.

## `robots.txt` он служит

```text
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

## Вместо этого напишите свой собственный

Ваш собственный файл всегда выигрывает, и Nexy никогда его не перезапишет:

- `public/robots.txt` или `public/sitemap.xml` обрабатываются как есть, как и каждый файл `public/`;
- маршрут проекта в `/robots.txt` или `/sitemap.xml` сохраняет свой путь.

Напишите свою собственную карту сайта, чтобы перечислить динамические страницы, например один URL-адрес для каждой публикации в блоге.

## Следующие шаги

- [Метаданные страницы](../routing/fbr/pages/metadata.md): поисковые системы показывают заголовок и описание
- [Конфигурация](../reference/config.md): все настройки `nexyconfig.py`
- [Развертывание](../deployment/README.md): обслуживание проекта в производстве.
