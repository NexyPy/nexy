# Структура проекта

Каждый файл в проекте Nexy выполняет одно задание, и его расположение зависит от маршрутизатора: `src/routes/` для файловой маршрутизации, `src/apps/` для модульного маршрутизатора.

## Верхний уровень

<!-- router:fbr -->
```text
my-app/
├─ src/
│  ├─ routes/            every file is a route
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Чтобы выбрать папку, спросите, что это за файл:

- **Что-то, что браузер может открыть** — маршрут: `src/routes/`.
- **Кусок, используемый несколькими маршрутами** — компонент или модуль: `src/components/`, `src/`.
- **Файл использовался как есть** - `public/`.
- **Сгенерировано** - `__nexy__/`; никогда не редактируйте его.

> [!WARNING]
> `src/routes/` сканируется: помещенный туда помощник становится маршрутом. Поместите помощник, который не является маршрутом за пределами `src/routes/` или начните его имя с `_`.
<!-- /router -->

<!-- router:modular -->
```text
my-app/
├─ src/
│  ├─ apps/              controllers, modules and their views
│  │  ├─ app_module.py   the root module, given to useRouter
│  │  ├─ app_controller.py
│  │  ├─ app_view.nexy   a view a controller returns
│  │  ├─ layout.nexy     the frame the controllers pass their view to
│  │  └─ users/          one folder per feature: controller, module, service, model
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = AppModule
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Чтобы выбрать папку, спросите, что это за файл:

- **URL** — метод контроллера в `src/apps/`, зарегистрированный его модулем.
- **Страница** — представление `.nexy` рядом с его контроллером, возвращаемое с помощью `useViews`.
- **Фрагмент, использованный в нескольких представлениях** - `src/components/`.
- **Файл использовался как есть** - `public/`.
- **Сгенерировано** - `__nexy__/`; никогда не редактируйте его.
<!-- /router -->

<!-- router:custom -->
```text
my-app/
├─ src/
│  ├─ legacy/            the FastAPI router you include
│  │  └─ api.py          router = APIRouter(prefix="/api")
│  ├─ routes/            pages and route files, served next to it
│  │  └─ index.nexy      → /
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = router
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Чтобы выбрать папку, спросите, что это за файл:

- **Маршрут включенного приложения** - там, где оно уже есть, здесь `src/legacy/`.
- **Новая страница или маршрут** - `src/routes/`, рядом с включенным роутером.
- **Файл использовался как есть** - `public/`.
- **Сгенерировано** - `__nexy__/`; никогда не редактируйте его.
<!-- /router -->

<!-- router:fbr,custom -->
## `src/routes/`

Каждый файл становится маршрутом, за исключением зарезервированных имен, указанных ниже. Путь к файлу без расширения представляет собой URL-адрес — см. [маршрутизация на основе файлов](../routing/fbr/README.md).

| Файл | Роль |
|---|---|
| `layout.nexy` | оборачивает родственные и дочерние страницы |
| `errors.nexy` | 500 страниц для каталога |
| `notfound.nexy` | Страница 404 для каталога |
| `dependencies.py` | общие FastAPI зависимости для каталога |
| `__init__.py` | Python маркер пакета |
| `loading.nexy` | зарезервировано — исключено из маршрутов, но пока не имеет эффекта во время выполнения |

Каждое имя страницы также существует для каждой платформы. При настройке `react()` `layout.jsx` и `layout.tsx` зарезервированы точно так же, как `layout.nexy`. Списки строятся в `nexy/core/config.py` (`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`).

> [!NOTE]
> `notfound.nexy` и `errors.nexy` устанавливаются только в том случае, если копия существует в корне маршрута. Копия в подкаталоге затем уточняет страницу для этого префикса.
<!-- /router -->

<!-- router:modular -->
## `src/apps/`

Контроллер отвечает на URL-адреса, модуль группирует контроллеры и провайдеры, а корневой модуль монтируется с помощью `useRouter` в `nexyconfig.py`:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller()
class AppController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/app_view.nexy")})
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    useAliases = {"@": "src"}  # the views import @/components/...
```

Ни один файл в `src/apps/` не является маршрутом по своему имени: отвечают только контроллеры, перечисленные в модуле. См. [модульная маршрутизация](../routing/modular/README.md).
<!-- /router -->

## `public/`

Здесь подаются файлы из корня сайта: `/favicon.ico`, `/robots.txt`, изображения, шрифты.

## `__nexy__/`

Генерируется `nx build` (и `nx dev` для необходимых частей). Он содержит:

- скомпилированные файлы `.nexy` в виде пакета Python (`__nexy__/src/...`);
- сгенерированные точки входа клиента (`main.ts`, `vite.ts`, `*.auto.ts`);
- `client/` после сборки Vite — ресурсы, манифест, предварительно обработанный HTML;
- `build-cache.json`.

Относитесь ко всему каталогу как к одноразовому: удалите его, создайте заново. Редактирование вручную приведет к потере изменений в следующей сборке. Добавьте его в `.gitignore`.

## Следующие шаги

<!-- router:fbr -->
- [Маршрутизация на основе файлов](../routing/fbr/README.md): как путь становится URL-адресом
<!-- /router -->
<!-- router:modular -->
- [Модульная маршрутизация](../routing/modular/README.md): контроллеры, модули и провайдеры
<!-- /router -->
<!-- router:custom -->
- [Пользовательская маршрутизация](../routing/custom/README.md): включите существующий маршрутизатор FastAPI
<!-- /router -->
- [Конфигурация](../reference/config.md): каждый вариант проекта.
- [Интерфейс](../guides/frontend.md): Vite, стиль и сборка клиента
