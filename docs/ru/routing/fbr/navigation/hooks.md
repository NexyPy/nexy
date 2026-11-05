# Крючки

Хуки считывают текущий HTTP-запрос изнутри страницы `.nexy`, обработчика API или модульного контроллера. Их имена соответствуют перехватчикам клиентского маршрутизатора (`@nexy/client`), где они делают то же самое.

> [!NOTE]
> перехватчики работают только во время обработки запроса. Вызов одного из других мест повышает значение `RuntimeError`.

## Крючки

| Крючок | Возвращает |
|---|---|
| `usePathname()` | путь запроса, например. `"/blog/post-1"` |
| `useSearchParams()` | строка запроса как `dict[str, str]`, первое значение для каждого ключа |
| `useParams()` | параметры динамического пути, например. `{"slug": "post-1"}` |
| `useQuery()` | исходное имя `useParams()`, сохраненное для существующих страниц |
| `useRequest()` | запрос Starlette, для чего другие хуки не покрывают |
| `useHeaders()` | заголовки запросов в виде `dict[str, str]`, имена в нижнем регистре |
| `useUrl()` | полный URL: `.scheme`, `.hostname`, `.port`, `.path`, `.query` |
| `useIsActive(href, exact=False)` | является ли `href` текущей страницей или одной из ее родительских страниц |
| `useRouter()` | `{"path", "base_url", "url_for"}` |
| `useCookies()` | все файлы cookie как `dict[str, str]` |
| `useSession()` | запись сеанса, `{}` когда сеансы не включены |
| `useToc(depth_range="2-6")` | оглавление HTML для текущей страницы, `""` если нет |
| `useViews(path, context=None)` | отображает другое представление и возвращает `HTMLResponse` |

## Прочитать запрос

```nexy filename="источник/маршруты/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```

## Активная ссылка на панели навигации.

`useIsActive` следует тому же правилу, что и на клиенте: строка запроса, фрагмент и завершающая косая черта игнорируются, ссылка на родительский объект активна для его дочерних элементов, если не установлено `exact`, а `/` активен только для `/`.

```nexy filename="источник/компоненты/NavLink.nexy"
---
from nexy import useIsActive

href: prop[str]
label: prop[str]
---
<a href="{{ href }}"{% if useIsActive(href) %} aria-current="page"{% endif %}>{{ label }}</a>
```

## Примечания

- `useQuery()` возвращает параметры **path**, а не строку запроса, поэтому `useParams()` существует. Строка запроса: `useSearchParams()`.
- `useRouter()` вот хук запроса. Это не поле конфигурации `useRouter`, которое монтирует `APIRouter`.
- `useSession()` нуждается в `useSession = {...}` в `nexyconfig.py`; без него дикт пуст.
- `useViews("about.tsx", {"title": "About"})` возвращает HTML: представление `.nexy` отображается его скомпилированным модулем, представление `.tsx`/`.jsx`/`.vue`/`.svelte`/`.mdx` становится контейнером монтирования клиента.

## Следующие шаги

- [Страницы](../pages/README.md): динамические сегменты и макеты.
- [Рецепты](../../../guides/recipes.md): проверенный процесс входа в систему, построенный на `useSession()`
- [Конфигурация](../../../reference/config.md): включить сеансы и локали
- [.nexy файлы](../../../views/nexy/README.md): где обычно вызываются хуки
