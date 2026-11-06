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
| `useWorkers` | `0` | процессы `nx start` выполняются; `0` — по одному на каждый процессор в Linux и macOS, по одному в Windows. |
| `useCSR` | `False` | режим маршрутизации на стороне клиента; `.nexy` маршруты отключены |

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
| `useDocs` | `True` | обслуживать справочную страницу Scalar; `/openapi.json` обслуживается в любом случае |
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

Или выключите его с помощью `useDocs = False`. `/openapi.json` остается обслуживаемым в обоих случаях: держите маршруты проекта подальше от этого пути.

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
