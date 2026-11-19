# Как отладить серверный код в Nexy?

Отладьте код сервера `nx dev` с помощью `breakpoint()` в терминале или с помощью VS Code и `debugpy`: сервер разработки запускает ваш Python в своем собственном процессе, поэтому прикрепленный к нему отладчик останавливается на ваших страницах, обработчиках API и действиях.

## Как `nx dev` запускает ваш код

`nx dev` запускает uvicorn в своем собственном процессе, без отдельного исполнителя. При изменении файла Python или страницы `.nexy` модули вашего проекта забываются и импортируются снова в том же процессе. Таким образом, отладчик, подключенный к `nx dev`, остается подключенным после перезагрузки, а точка останова, установленная в файле, сохраняет свое место в новом коде.

Файл `.nexy` компилируется в модуль Python под `__nexy__/` по тому же пути, что и выполняется:

<!-- router:fbr,custom -->
| Ты пишешь | Некси бежит |
|---|---|
| `src/routes/about.nexy` | `__nexy__/src/routes/about.py`, функция `About()` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/routes/api/users.py` | сам файл |
<!-- /router -->

<!-- router:modular -->
| Ты пишешь | Некси бежит |
|---|---|
| `src/apps/users/user_view.nexy` | `__nexy__/src/apps/users/user_view.py` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/apps/users/user_controller.py` | сам файл |
<!-- /router -->

Начальная часть файла `.nexy` (Python между двумя строками `---`) становится телом функции этого модуля. `__nexy__/` записывается заново при каждом изменении: никогда не редактируйте его.

## Остановитесь в терминале с помощью `breakpoint()`

Поместите `breakpoint()` в том месте, где вы хотите остановиться, в файле `.py` или в начале файла `.nexy`:

<!-- router:fbr,custom -->
```nexy filename="источник/маршруты/about.nexy"
---
from nexy import useSearchParams

page = useSearchParams().get("page", "1")
breakpoint()
---
<p>Page {{ page }}</p>
```

Откройте страницу. Запрос ожидает, и терминал `nx dev` показывает pdb в скомпилированном модуле:

```text
> /path/to/app/__nexy__/src/routes/about.py(21)About()
-> breakpoint()
(Pdb)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users")
class UserController:
    async def get(self):
        page = "1"
        breakpoint()
        return {"page": page}
```

Откройте `/users`. Запрос ожидает, и терминал `nx dev` показывает pdb в этой строке. В начале представления pdb показывает скомпилированный модуль под `__nexy__/src/apps/`.
<!-- /router -->

Введите `p page` для вывода значения, `n` для следующей строки, `c` для продолжения запроса. Когда закончите, удалите строку: следующий запрос снова остановится на ней.

## Отладка с помощью VS Code

Установите `debugpy` в среду проекта:

```bash
uv add --dev debugpy
```

Затем добавьте конфигурацию запуска. `nexy.modules.cli` — это модуль, стоящий за командой `nx`, поэтому он работает одинаково в Linux, macOS и Windows:

```json filename=".vscode/launch.json"
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "nx dev",
      "type": "debugpy",
      "request": "launch",
      "module": "nexy.modules.cli",
      "args": ["dev"],
      "console": "integratedTerminal"
    }
  ]
}
```

Нажмите F5. Установите точки останова в ваших файлах `.py` и в скомпилированном модуле в `__nexy__/` для файла `.nexy`: VS Code не может остановиться в файле `.nexy`, потому что он не является Python до тех пор, пока он не будет скомпилирован. Номера строк скомпилированного модуля следуют за вступительной частью, поэтому точка останова может переместиться после редактирования страницы; `breakpoint()` во вступительной части нет.

## Подключиться с другого терминала

Чтобы запустить сервер разработки самостоятельно и подключить отладчик позже:

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m nexy.modules.cli dev
```

`--wait-for-client` удерживает начало до тех пор, пока не подключится отладчик; оставьте это, чтобы начать сразу. В VS Code прикрепите конфигурацию `"request": "attach"` и `"connect": { "host": "127.0.0.1", "port": 5678 }`.

debugpy может предупредить, что «используются замороженные модули». Начните Python с `-Xfrozen_modules=off` (`python -Xfrozen_modules=off -m debugpy ...`), если точка останова в стандартной библиотеке пропущена; точки останова в вашем собственном коде не затрагиваются.

## Следующие шаги

- [Устранение неполадок](troubleshooting.md): первые проблемы, с которыми столкнулись люди
- [Тестирование](testing.md): воспроизведите ошибку в тесте, как только вы ее обнаружите.
- [Файлы .nexy](../views/nexy/README.md): оформление, реквизит и шаблоны.
