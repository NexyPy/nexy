# Соглашения о файлах

Зарезервированные имена и правила в `src/routes/`.

## Файлы маршрутов

| Файл | становится |
|---|---|
| `index.nexy`, `index.md`, `index.mdx`, `index.py` | маршрут своего каталога |
| `about.nexy` | `/about` |
| `[slug].nexy` | динамический сегмент `{slug}` |
| `[...path].nexy` | всеобъемлющий `{path:path}` |
| `(group)/page.nexy` | `/page`: группа не отображается в URL-адресе |
| `name.py` | обработчик API; имена функций `GET`, `POST`, ... это методы |
| `name.tsx`, `.jsx`, `.vue`, `.svelte` | маршрут клиента, когда платформа включена с помощью `useFF` |

## Зарезервированные файлы

| Файл | Роль | Подробности |
|---|---|---|
| `layout.nexy` | режим сервера: переносит каждую страницу под ним; корневому принадлежит HTML-документ | [layout.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | клиентский режим (React): корневой владеет HTML-документом, вложенные — обертывают страницы | [layout.tsx](../views/react/differences.md) |
| `layout.vue`, `layout.svelte` | клиентский режим: вложенные макеты | [layout.vue](../views/vue/differences.md), [layout.svelte](../views/svelte/differences.md) |
| `notfound.nexy` | Страница 404 для своего каталога | [Страницы ошибок](../routing/fbr/errors/README.md) |
| `errors.nexy` | 500 страниц для своего каталога | [Страницы ошибок](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | Страница 403 для своего каталога | [Страниц ошибок в каждой папке](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | 401 страница для своего каталога | [Страниц ошибок в каждой папке](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | зарезервировано; пока нет эффекта времени выполнения | [Страницы ошибок](../routing/fbr/errors/README.md) |
| `middleware.py` | `async def middleware(request, call_next)` обертка запросов каталога и ниже | [Файлы промежуточного программного обеспечения](../routing/fbr/middleware/README.md) |
| `dependencies.py` | список `dependencies = [fn, ...]` применяется к каталогу и его дочерним элементам | [Зависимости](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Python маркер пакета | |
| `favicon.ico` | служил в `/favicon.ico` | |

`useLayoutExtensions`, `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions`, `useUnauthorizedExtensions` и `useLoadingExtensions` резервируют дополнительные расширения для этих имен. См. [Конфигурация](config.md).

## Игнорируемые файлы

- Файл или папка, начинающаяся с `_` или `.`: используйте их для партиалов, черновиков и вспомогательных файлов.
- Файл, расширение которого неактивно для проекта: пропускается с предупреждением.

## Один файл на каждый URL

Регистрируются два файла, которые разрешаются по одному и тому же URL-адресу. Не ставьте `blog.nexy` рядом с `blog/index.nexy`.

## Снаружи `src/routes/`

| Папка | Назначение |
|---|---|
| `src/components/` | компоненты, импортированные по страницам; никогда не маршрутизирует |
| `src/apps/` | контроллеры и модули [модульного маршрутизатора](../routing/modular/README.md) |
| `public/` | статические файлы, обслуживаемые в корне: `public/logo.svg` — это `/logo.svg` (также в `/public/`) |
| `__nexy__/` | сгенерированы выходные данные; не совершайте |

## Следующие шаги

- [Маршрутизация](../routing/README.md)
- [Структура проекта](../getting-started/project-structure.md)
