# Структура проекта

Каждый файл в проекте Nexy выполняет одно задание. На этой странице написано, какой.

## Верхний уровень

```text
my-app/
├─ src/
│  ├─ routes/            file-based routes (FBR)
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ apps/              modular router, decorators (optional, next to routes/)
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
- **Контроллер модульного маршрутизатора** - `src/apps/`.
- **Сгенерировано** - `__nexy__/`; никогда не редактируйте его.

> [!WARNING]
> `src/routes/` сканируется: помещенный туда помощник становится маршрутом. Поместите помощник, который не является маршрутом за пределами `src/routes/` или начните его имя с `_`.

## `src/routes/`

Каждый файл становится маршрутом, за исключением зарезервированных имен, указанных ниже. Путь к файлу без расширения представляет собой URL-адрес — см. [маршрутизация](../routing/README.md).

| Файл | Роль |
|---|---|
| `layout.nexy` | переносит дочерние и дочерние страницы |
| `errors.nexy` | 500 страниц для каталога |
| `notfound.nexy` | 404 страница для каталога |
| `dependencies.py` | общие FastAPI зависимости для каталога |
| `__init__.py` | Python маркер пакета |
| `loading.nexy` | зарезервировано — исключено из маршрутов, но пока не имеет эффекта во время выполнения |

Каждое имя страницы также существует для каждой платформы. При настройке `react()` `layout.jsx` и `layout.tsx` зарезервированы точно так же, как `layout.nexy`. Списки строятся в `nexy/core/config.py` (`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`).

> [!NOTE]
> `notfound.nexy` и `errors.nexy` устанавливаются только в том случае, если копия существует в корне маршрута. Копия в подкаталоге затем уточняет страницу для этого префикса.

## `src/apps/`

Каталог `nexy new` используется для модульного маршрутизатора: контроллеры, модули и провайдеры регистрируют свои маршруты через декораторы из `nexy.decorators`, затем агрегат `APIRouter` монтируется с `useRouter` в `nexyconfig.py`.

В проекте могут быть оба маршрутизатора: `useRouter` монтирует модульный маршрутизатор, а `src/routes/` сканируется всякий раз, когда этот каталог существует. См. [модульная маршрутизация](../routing/modular/README.md).

## `public/`

Файлы сюда подаются из корня сайта: `/favicon.ico`, `/robots.txt`, изображения, шрифты.

## `__nexy__/`

Генерируется `nx build` (и `nx dev` для необходимых частей). Он содержит:

- скомпилированные модули маршрутов в виде пакета Python (`__nexy__/src/routes/...`);
- сгенерированные точки входа клиента (`main.ts`, `vite.ts`, `*.auto.ts`);
- `client/` после сборки Vite — ресурсы, манифест, предварительно обработанный HTML;
- `build-cache.json`.

Относитесь ко всему каталогу как к одноразовому: удалите его, создайте заново. Редактирование вручную приведет к потере изменений в следующей сборке. Добавьте его в `.gitignore`.

## Следующие шаги

- [Маршрутизация](../routing/README.md): как путь становится URL-адресом
- [Config](../reference/config.md): каждый вариант проекта.
- [Frontend](../guides/frontend.md): Vite, стиль и сборка клиента
