# Python API

Каждое имя Nexy экспортирует в ваш код Python по модулю. Тест проверяет эту страницу на соответствие коду в обоих направлениях: имя, указанное здесь, должно существовать, и имя, экспортируемое кодом, должно быть указано здесь.

## `nexy`

Компоненты для шаблонов `.nexy` и перехватчики запросов.

| Имя | Что это такое |
|---|---|
| `Audio`, `Video` | родные проигрыватели `<audio>` и `<video>`, см. [компоненты](../views/nexy/components.md) |
| `Image` | `<img>`, который по умолчанию загружается лениво |
| `Link` | клиентская сторона `<a>` с дополнительной предварительной выборкой |
| `Import` | импортировать клиентский компонент на страницу `.nexy` |
| `Template` | визуализировать шаблоны Jinja2 и Markdown |
| `Vite` | клиентский тег Vite нужен каждой странице |
| `Form` | заполнитель без поведения: используйте простой `<form>` с [действием](../guides/actions.md) |
| `usePathname` | путь текущего запроса |
| `useSearchParams` | строка запроса как словарь |
| `useParams` | параметры динамического пути в виде dict, например `useParams()` на клиенте |
| `useQuery` | исходное имя `useParams`, сохраненное для существующих страниц (оно не читает строку запроса) |
| `useRequest` | текущий запрос, на который не перекрываются другие хуки |
| `useHeaders` | заголовки запросов в виде слов с именами в нижнем регистре |
| `useUrl` | полный URL: `.scheme`, `.hostname`, `.path`, `.query` |
| `useIsActive` | указывает ли ссылка на текущую страницу или на одного из ее родителей для панели навигации |
| `useRouter` | `path`, `base_url` и `url_for` текущего запроса |
| `useSession` | словарь сеанса, пустой, когда сеансы отключены |
| `useCookies` | файлы cookie запроса как dict |
| `useToc` | оглавление текущей страницы в формате HTML |
| `useViews` | визуализировать файл представления, например `about.tsx` из обработчика |
| `setMetadata`, `useMetadata` | назовите теги заголовка и заголовка страницы и запишите их в макете. |
| `redirect`, `permanentRedirect` | отправить посетителя в другое место (307, 308) и остановить запрос |
| `notFound`, `forbidden`, `unauthorized` | ответьте на 404, 403 или 401 откуда угодно |

Перехватчики работают только внутри запроса: см. [крючки](../routing/fbr/navigation/hooks.md).

```nexy filename="источник/маршруты/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```

## `nexy.http`

HTTP-словарь обработчика. Импортируйте отсюда, а не из FastAPI, поэтому ваши обработчики зависят от контракта Nexy.

| Имя | Что это такое |
|---|---|
| `Request`, `Response` | входящий запрос и исходящий ответ |
| `HTTPException` | остановить обработчик со статусом и `detail` |
| `status` | именованные коды состояния, например `status.HTTP_404_NOT_FOUND` |
| `Depends` | сначала запустите функцию и передайте ее результат в |
| `Header`, `Cookie`, `Query`, `Path`, `Body` | откуда берется параметр |
| `Form`, `File`, `UploadFile` | поля формы и загрузки (нужно `python-multipart`) |
| `BackgroundTasks` | работа, которая выполняется после отправки ответа |
| `JSONResponse`, `HTMLResponse`, `PlainTextResponse` | ответы с фиксированным типом контента |
| `RedirectResponse` | HTTP-перенаправление |
| `redirect`, `permanentRedirect` | вызвать перенаправление (307, 308) со страницы, обработчика, контроллера или охранника |
| `notFound`, `forbidden`, `unauthorized` | поднять 404, 403 или 401 из тех же мест |
| `FileResponse`, `StreamingResponse` | ответьте файлом или потоком |

```python filename="src/маршруты/api/items/[id].py"
from nexy.http import Depends, Header, HTTPException, status


def api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != "secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad key")
    return x_api_key


async def GET(id: int, key: str = Depends(api_key)):
    return {"id": id}
```

## `nexy.decorators`

| Имя | Что это такое |
|---|---|
| `Action` | превратить функцию в конечную точку `POST`, см. [действия](../guides/actions.md) |
| `revalidate` | сообщить браузеру, на каких страницах действие стало устаревшим |
| `Module`, `Controller` | объявить модуль и контроллер в [модульном маршрутизаторе](../routing/modular/README.md) |
| `Injectable`, `Container`, `Scope` | [внедрение зависимостей](../routing/modular/dependency-injection.md) и время его жизни |
| `UseGuard`, `Middleware` | защитить или обернуть один обработчик, см. [гарды](../routing/modular/guards-and-metadata.md) |
| `UseRoute`, `useRoute`, `RouteMeta` | назовите маршрут и опишите его для OpenAPI |
| `UseResponse`, `ResponseMeta` | описать ответ на маршрут |
| `HTTP_METHODS` | методы HTTP, которые может определить файл обработчика |
| `ACTIONS_STORE` | реестр действий, для инструментов и тестов |

```python filename="src/actions/posts.py"
from nexy.decorators import Action, revalidate


@Action
async def publish(post_id: int) -> bool:
    revalidate("/blog")
    return True
```

## `nexy.testing`

| Имя | Что это такое |
|---|---|
| `render` | HTML компонента `.nexy` для заданных реквизитов без сервера, см. [тестирование](../guides/testing.md) |

```python filename="тесты/test_button.py"
from nexy.testing import render


def test_the_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

## Где дальше

- [Конфигурация](config.md): поля `use*` за этими именами.
- [Исключения и ошибки](exceptions.md): на что отвечает каждый сбой
- [Индекс документации](../README.md): страница того, что вы создаете.
