# Маршрутизация

У Nexy два родных роутера. Вы можете выбрать по одному для каждой функции; они могут сосуществовать в одном приложении.

**Не уверен? Используйте маршрутизацию на основе файлов.** Она охватывает страницы и конечные точки API без какой-либо настройки. Добавьте модульный маршрутизатор, если серверной части нужны контроллеры, внедренные службы или средства защиты.

| Вы строите | Использование |
|---|---|
| Страницы, контент, сайт с несколькими конечными точками | Файловый |
| Большой API с сервисами, общими для всех маршрутов. | Модульный |
| И то, и другое: страницы для людей, структурированный API для машин. | Файловое и модульное вместе |

<!-- router:fbr,custom -->
```diagram filename="Файловый маршрутизатор, краткий обзор"
src/routes/index.nexy           →  /
src/routes/about.nexy           →  /about
src/routes/blog/index.nexy      →  /blog
src/routes/blog/[slug].nexy     →  /blog/:slug
src/routes/(app)/dashboard.nexy →  /dashboard
src/routes/api/users.py         →  /api/users  (GET, POST, …)
```
<!-- /router -->

<!-- router:modular -->
```diagram filename="Модульный маршрутизатор, краткий обзор"
@Controller()             class AppController   →  /
@Controller("/about")     class AboutController →  /about/
@Controller("/api/users") class UserController  →  /api/users/  (get, post, …)
@Module()                 class AppModule       →  lists the controllers
useRouter = AppModule     nexyconfig.py         →  mounts the module
```
<!-- /router -->

| Маршрутизатор | Источник | Включено |
|---|---|---|
| [На основе файлов (FBR)](fbr/README.md) | каждый файл под `src/routes/` | каталог существует |
| [Модульный](modular/README.md) | контроллеры и модули | `useRouter = AppModule` в `nexyconfig.py` |

FBR сканируется всякий раз, когда существует `src/routes/`, даже если установлен модульный маршрутизатор.

## Сосуществование и приоритеты

Вы можете комбинировать FBR, модульную и пользовательскую интеграцию. Nexy регистрирует эти маршруты в порядке их обнаружения. Если два маршрутизатора определяют один и тот же путь URL-адреса, побеждает первый зарегистрированный. 

*Примечание. Nexy в настоящее время не обеспечивает диагностику конфликтов URL-адресов; первый маршрут, претендующий на путь, просто затеняет остальные.*

<!-- router:fbr,custom -->
## Маршрутизация на основе файлов

Маршрут — это файл. URL-адрес — это его путь в `src/routes/` без расширения. Как и Next.js, проект находится в одном из двух режимов, выбранных с помощью `useCSR`:

| | `useCSR = False` (по умолчанию) | `useCSR = True` |
|---|---|---|
| Страницы | `.nexy`, `.md`, `.mdx` | файлы вашего клиентского фреймворка |
| Корневая раскладка | `layout.nexy` | `layout.tsx` (React) |
| Клиентские компоненты | разрешено, так как острова внутри страниц | сами страницы |
| API-маршруты | `.py` | `.py` |

См. [Режим сервера и режим клиента](fbr/modes.md).

| Раздел | Что он охватывает |
|---|---|
| [fbr/страницы](fbr/pages/README.md) | страницы, [динамические маршруты](fbr/pages/dynamic-routes.md) и группы маршрутов |
| [fbr/макеты](fbr/layouts/README.md) | `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` |
| [fbr/обработчики](fbr/handlers/README.md) | `.py` обработчики маршрутов, [проверка и ошибки](fbr/handlers/validation-and-errors.md) |
| [fbr/зависимости](fbr/dependencies/README.md) | `dependencies.py` и охранники, наследуемые каталогом |
| [fbr/промежуточное ПО](fbr/middleware/README.md) | `middleware.py`, наследуется каталогом |
| [fbr/ошибки](fbr/errors/README.md) | `notfound.nexy`, `errors.nexy`, ошибки JSON |
| [fbr/навигация](fbr/navigation/linking-and-navigating.md) | связывание, навигация по клиенту, [крючки](fbr/navigation/hooks.md) |
| [fbr/в реальном времени](fbr/realtime/websocket.md) | WebSocket обработчики |
| [fbr/наследование](fbr/inheritance.md) | как наследуются макеты, зависимости и страницы ошибок |
<!-- /router -->

## Модульная маршрутизация

Контроллеры, модули и внедрение зависимостей в стиле NestJS. См. [Модульная маршрутизация](modular/README.md) и [Nexy и NestJS](modular/vs-nestjs.md).

<!-- router:modular -->
| Раздел | Что он охватывает |
|---|---|
| [модульный](modular/README.md) | `@Controller`, `@Module`, импорт и экспорт |
| [модульность/внедрение зависимостей](modular/dependency-injection.md) | `@Injectable`, области видимости и контейнер |
| [модульные/защитные и метаданные](modular/guards-and-metadata.md) | `@UseGuard`, `@UseResponse` и метаданные OpenAPI |

Контроллер возвращает представление `.nexy` с помощью `useViews` и вручную передает его в свой макет: `layout.nexy` не применяется к папке.
<!-- /router -->

## Пользовательская интеграция

Вы также можете интегрировать существующий маршрутизатор FastAPI в свой проект Nexy. См. [Интеграция пользовательской маршрутизации](custom/README.md).

## Следующие шаги

<!-- router:fbr,custom -->
- [Маршрутизация на основе файлов](fbr/README.md)
<!-- /router -->
<!-- router:modular -->
- [Модульная маршрутизация](modular/README.md)
<!-- /router -->
- [Рендеринг](../rendering/README.md)
- [Просмотры](../views/README.md): что находится внутри файлов
