# Конфигурация

Конфигурация — это класс в `nexyconfig.py` в корне проекта. Nexy загружает его из каталога, в котором он работает; проект без файла использует значения по умолчанию.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    usePort = 3000
    useTitle = "My App"
    useAliases = {"@": "src"}
```

## Сервер

| Поле | По умолчанию | Значение |
|---|---|---|
| `usePort` | `3000` | порт для `dev` и `start` |
| `useHost` | `"0.0.0.0"` | привязать адрес |
| `useSslKeyfile`, `useSslCertfile` | `None` | обслуживать HTTPS напрямую |
| `useDevTools` | `True` | панель инструментов `nexy dev` добавляет на каждую страницу (информацию о странице, маршруты, ошибки, конфиг); `False` удаляет его. Никогда не присутствует в производстве |
| `useHealth` | `False` | обслуживать `GET /health/live` и `GET /health/ready` для балансировщиков нагрузки и зондов Kubernetes; см. [Развертывание](../deployment/README.md#built-in-endpoints) |
| `useMaxBodySize` | `1048576` | самый большой текст запроса, который читает работник, в байтах (1 МБ); больший — `413`, а `0` отключает ограничение. Поднимите его для маршрута, требующего загрузки файлов. |
| `useSiteUrl` | `None` | общедоступное происхождение сайта, например `"https://example.com"`; после установки Nexy обслуживает `/sitemap.xml` и `/robots.txt`. См. [Карта сайта и robots.txt](../guides/sitemap.md) |
| `useWorkers` | `0` | процессы `nx start` выполняются; `0` — по одному на каждый процессор в Linux и macOS, по одному в Windows |
| `useCSR` | `False` | режим маршрутизации на стороне клиента; `.nexy` маршруты отключены |
| `useBasePath` | `None` | общедоступный префикс для всего приложения, например `"/app"`; запросы за его пределами отвечают 404, а сгенерированные ссылки, клиентские маршруты, вызовы действий и активы содержат префикс. См. [Развертывание](../deployment/README.md#serve-under-a-sub-path) |
| `useImageWidths` | `[320, 640, 960, 1280]` | ширина пикселей `nx build` генерируется для локальных изображений; для преобразования требуется `Pillow`, и без него изображения сохранят свой исходный URL-адрес. См. [Изображение](../routing/fbr/navigation/linking-and-navigating.md#image) |
| `useISRCache` | `None` | Хранилище ISR: `None` или `"memory"` для одного процесса, `"file"` для одного хоста, `"redis"` для нескольких воркеров, сопоставление с `type` и опциями или объект с `get`, `set` и `invalidate`. См. [ISR](../rendering/isr.md#choose-a-store) |

## База данных

| Поле | По умолчанию | Значение |
|---|---|---|
| `useORM` | `None` | ORM проекта: `"SQLModel"`, `"SQLAlchemy"` или `"Tortoise-ORM"`. `nx new` записывает его, а `nx migrate` выбирает из него Alembic или Aerich; без него `nx migrate` принимает первый установленный ORM. См. [Базы данных](../guides/databases.md#migrations) |

## Маршруты

| Поле | По умолчанию | Значение |
|---|---|---|
| `useRouter` | `None` | экземпляр или класс `APIRouter`, смонтированный рядом с файловыми маршрутами; `None` означает только файловый |
| `excludeDirs` | `["templates", "extension", "docs"]` | каталоги пропускаются при сканировании маршрутов |
| `useAliases` | `None` | импортировать псевдонимы, например. `{"@": "src"}` (`@/components/Counter.tsx` означает `src/components/Counter.tsx`); `nx new` записывает тот, который вы выбрали, а Vite и `tsconfig.json` следуют за ним |

## Фронтенд

| Поле | По умолчанию | Значение |
|---|---|---|
| `useFF` | `None` | фабрика клиентских фреймворков: `react()`, `vue()`, `svelte()`, `solid()`, `preact()` |
| `useVite` | `True` | создавать и обслуживать клиентские пакеты с помощью Vite |
| `useMarkdownExtensions` | `[]` | дополнительные расширения для рендеринга `.md`/`.mdx` |
| `useWatchExtensions` | `None` | дополнительные расширения, которые наблюдает сервер разработчиков |
| `useWatchExcludePatterns` | `None` | шаблоны glob, которые сервер разработки игнорирует |

> **Полезно знать**: `NexyConfigModel` объявляет `useVite = False`; значение по умолчанию во время выполнения `Config` — `True`.

## Зарезервированные имена файлов

Каждое поле добавляет расширения к зарезервированной роли. `useLayoutExtensions = ["md"]` делает `layout.md` зарезервированным, точно так же, как `layout.nexy`.

| Поле | Добавляет расширения в |
|---|---|
| `useLayoutExtensions` | `layout.*` |
| `useNotFoundExtensions` | `notfound.*` |
| `useErrorsExtensions` | `errors.*` |
| `useForbiddenExtensions` | `forbidden.*` |
| `useUnauthorizedExtensions` | `unauthorized.*` |
| `useLoadingExtensions` | `loading.*` |

## Документация по API

| Поле | По умолчанию | Значение |
|---|---|---|
| `useDocs` | `"dev"` | где обслуживаются справочная страница Scalar и `/openapi.json`: `"dev"` только на `nx dev`, `True` также в рабочей среде (в схеме перечислены все маршруты и действия сервера), `False` нигде |
| `useDocsUrl` | `"/docs"` | путь к справочной странице API |
| `useRedocsUrl` | `"/redocs"` | объявлено, но маршрут не установлен |
| `useTitle` | `"Nexy App"` | OpenAPI заголовок и заголовок страницы (`"Nexy"` в `NexyConfigModel`) |

### Бесплатно `/docs` на страницу проекта

Ссылка API отвечает на `/docs` перед любым маршрутом, поэтому `src/routes/docs.nexy` или `src/routes/docs/[[...slug]].nexy` там никогда не обслуживаются. `nx dev` и `nx start` называют такую ​​страницу при запуске. Переместите ссылку с помощью `useDocsUrl`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useDocsUrl = "/api-reference"
```

Или отключите его с помощью `useDocs = False`, что также перестанет обслуживать `/openapi.json`. Пока ссылка включена, держите маршруты проекта подальше от этого пути.

## Промежуточное ПО

| Поле | По умолчанию | Значение |
|---|---|---|
| `useMiddlewares` | `[]` | Классы промежуточного программного обеспечения ASGI |
| `useCORS` | `None` | кварги для `CORSMiddleware` |
| `useGZip` | `None` | кварги для `GZipMiddleware` |
| `useTrustedHost` | `None` | кварги для `TrustedHostMiddleware` |
| `useSession` | `None` | кварги для `SessionMiddleware` |
| `useAuth` | `None` | конфигурация промежуточного программного обеспечения аутентификации |
| `useHTTPSRedirect` | `False` | перенаправить HTTP на HTTPS |

## Markdown

| Поле | По умолчанию | Значение |
|---|---|---|
| `useTocDepth` | `"2-6"` | уровни заголовков, включенные в оглавление |
| `useTocTitle` | `"Table of Contents"` | заголовок оглавления |
| `useTocAuto` | `True` | создать оглавление для Markdown страниц |

## Маршруты вне файлового дерева

Создайте FastAPI `APIRouter` и смонтируйте его с помощью `useRouter`. Он обслуживается рядом с файловыми маршрутами:

```python filename="nexyconfig.py"
from fastapi import APIRouter
from nexy.core.models import NexyConfigModel

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


class NexyConfig(NexyConfigModel):
    useRouter = router
```

Значения по умолчанию, указанные выше, считываются из `nexy/core/config.py`.

## Заявлено, еще не прочитано

Эти поля существуют в `NexyConfigModel`, но ни один код их не использует. Их установка не имеет никакого эффекта:

`useViteDevUrl`, `useRTL`.

## Следующие шаги

- [i18n](../guides/i18n.md): интернационализация
- [Фронтенд](../guides/frontend.md): `useFF` и клиентская сборка
- [Развертывание](../deployment/README.md): варианты производства
