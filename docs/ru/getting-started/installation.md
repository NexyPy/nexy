# Установка

## Требования

| Требование | Почему |
|---|---|
| Python 3.12+ | `requires-python` в `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | создает проект, устанавливает его пакеты и запускает Nexy |
| Node.js 18+ | только для клиентской платформы (React, Vue, Svelte, Solid, Preact) |

Проект без клиентской среды вообще не нуждается в Node.js.

## Сначала установите uv

`uvx` не является отдельным инструментом: он поставляется вместе с uv, поэтому установите uv прежде всего.

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Проверьте это с помощью `uv --version` и `uvx --version`.

## Создать проект

```bash
uvx nexy new my-app
```

`uvx` запускает Nexy во временной среде и ничего не оставляет после себя. Этого достаточно, чтобы **создать** проект (`new`, `init`) и не более того: временная среда содержит Nexy и никакой другой пакет. `nexy new` создает собственную виртуальную среду проекта, `.venv` и устанавливает туда свои пакеты.

`nexy new my-app` задает четыре вопроса: маршрутизатор (файловый или модульный), тип проекта (веб или API), клиентская среда, ORM. Затем установка зависимостей Python и Node выполняется с одной строкой на шаг и ее продолжительностью. См. [CLI](../reference/cli.md).

Пропускаем запросы при зарегистрированном шаблоне:

```bash
uvx nexy new my-app --template <name>
```

## Работа внутри виртуальной среды проекта

Любая другая команда (`nexy dev`, `nexy build`, `nexy migrate`...) должна выполняться **внутри виртуальной среды проекта**. Здесь живут ваши собственные пакеты: ваш ORM, ваши библиотеки и Nexy, на котором был создан проект. За его пределами проект, которому требуется `sqlmodel` терпит неудачу с `ModuleNotFoundError: No module named 'sqlmodel'`.

Активируйте его один раз для каждого терминала из папки проекта:

| Оболочка | Команда |
|---|---|
| PowerShell, cmd (Windows) | `.venv\Scripts\activate` |
| macOS, Linux | `source .venv/bin/activate` |

Затем приглашение начинается с `(.venv)`. Отсюда:

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

Откройте <http://localhost:3000>.

Чтобы пропустить активацию, позвольте uv сделать это одной командой: `uv run nexy dev`.

> [!ПРИМЕЧАНИЕ]
> `nexy` и `nx` — один и тот же двоичный файл. Копия, установленная с `uv tool install nexy`, живет в своей собственной среде, например `uvx`, поэтому используйте ее для создания проектов и запуска всего остального из среды проекта.

## Добавьте Nexy в существующий проект

Запустите его из виртуальной среды проекта, включив в него Nexy (`uv add nexy`):

```bash
nexy init
```

## Следующие шаги

- [Быстрый старт](quick-start.md)
- [Учебник](tutorial.md)
- [Структура проекта](project-structure.md)
- [Устранение неполадок](../guides/troubleshooting.md)
