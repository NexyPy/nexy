# SSR (серверный рендеринг)

## Определение

SSR используется по умолчанию: сервер отображает страницу в HTML для каждого запроса. Ничто не включает его, и никакой флаг не отключает его — проект в режиме сервера отображается при каждом запросе, если на странице не объявлено `revalidate`.

## Как это работает

<!-- router:fbr,custom -->
| Файл маршрута | Что создает HTML | Когда |
|---|---|---|
| `.nexy` | скомпилированный модуль Python через Jinja2 | каждый запрос |
| `.md` | Markdown, затем ближайший макет | каждый запрос |
| `.mdx`, `.tsx`, `.vue`, `.svelte` | фреймворк, визуализированный в Node | при сборке, когда маршрут не имеет макета, в противном случае в браузере |
| `.py` | ничего: он возвращает JSON или `Response` | - |

Страница Markdown и обработчик в одном проекте:

```md filename="источник/маршруты/changelog.md"
# Changelog

Rendered to HTML on every request, then wrapped in the nearest layout.
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```

Компонентный маршрут — это тот случай, когда требуется второе предложение. В рабочей среде маршрут компонента **без** макета обслуживается с помощью HTML, созданного при сборке, и компонент его гидратирует. В макете или в разработке контейнер пуст, и компонент отображается в браузере — тогда страница представляет собой оболочку, которая заполняется сама собой.

Компонентный маршрут таблицы без макета, поэтому продукция передает HTML из сборки:

```tsx filename="src/маршруты/pricing.tsx"
export default function Pricing() {
  return <h1>Pricing</h1>;
}
```
<!-- /router -->

<!-- router:modular -->
| Контроллер возвращается | Что создает HTML | Когда |
|---|---|---|
| `useViews("....nexy")` | скомпилированный модуль Python через Jinja2 | каждый запрос |
| `dict`, список, модель | ничего: FastAPI отвечает в формате JSON | - |

Представление и конечная точка JSON рядом в одном модуле:

```nexy filename="src/apps/changelog_view.nexy"
<h1>Changelog</h1>
<p>Rendered to HTML on every request.</p>
```

```python filename="src/apps/site_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/changelog")
class ChangelogController:
    async def get(self):
        return useViews("src/apps/changelog_view.nexy")


@Controller("/api/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```
<!-- /router -->

## Жизненный цикл рендеринга

<!-- router:fbr,custom -->
1. Запрос достигает файлового маршрутизатора. Путь сопоставляется, и динамические сегменты приводятся к типам, объявленным компонентом.

   ```nexy filename="src/routes/orders/[id].nexy"
   ---
   идентификатор: prop[int]
   ---
   <h1>Заказ № {{ id + 1000 }}</h1>
   ```

   `/orders/42` отображает `Order #1042`; `/orders/abc` отвечает `404`.
2. Компонент запускается. Тот, который ожидает Node (клиентский документ), работает в пуле потоков, поэтому он не останавливает цикл событий.
3. Тело передается как `text/html`. Компонент, который создает фрагменты, передает их в потоковом режиме по мере их создания.
4. Браузер получает HTML. Острова гидратируются согласно их [директиве](islands.md).

Ошибка, возникшая при рендеринге, преобразуется в страницу с помощью `errors.nexy`, если она есть в проекте: см. [страницы ошибок](../routing/fbr/errors/README.md).
<!-- /router -->

<!-- router:modular -->
1. Запрос достигает контроллера. Его параметры пути приводятся к типам, объявленным методом, и передаются в представление:

   ```python filename="src/apps/order_controller.py"
   из контроллера импорта nexy.decorators
   из nexy.hooks импортировать useViews


   @Controller("/orders/{id}")
   класс OrderController:
       асинхронное определение get(self, id: int):
           return useViews("src/apps/order_view.nexy", context={"id": id})
   ```

   ```nexy filename="src/apps/order_view.nexy"
   ---
   идентификатор: prop[int]
   ---
   <h1>Заказ № {{ id + 1000 }}</h1>
   ```

   `/orders/42/` отображает `Order #1042`; `/orders/abc/` отвечает `404`.
2. Представление запускается, и `useViews` возвращает свой HTML в качестве ответа.
3. Браузер получает HTML. Острова гидратируются в соответствии с их [директивой](islands.md).

На ошибку, возникшую во время рендеринга, отвечает страница ошибки по умолчанию.
<!-- /router -->

## Когда использовать

- На странице показано то, что принадлежит читателю: сеанс, учетная запись, корзина.
- Данные должны быть свежими при каждой загрузке.
- Содержимое должно быть в формате HTML для сканеров, которые не запускают JavaScript.
- Рендеринг страницы не требует больших затрат: один запрос, один шаблон.

Первый случай — страница, приветствующая читателя из сеанса. `useSession` читает сеанс `useSession` в `nexyconfig.py`, без чего происходит сбой:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me"}
```

<!-- router:fbr,custom -->
```nexy filename="src/маршруты/account.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/account_view.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

## Конфигурация

<!-- router:fbr,custom -->
Нет. Выхода два, и они не имеют одинакового зерна:

| Уйти из ССР в | сделай это | Зерно |
|---|---|---|
| одна страница, с кэшем | `revalidate = 60` во вступительной части → [ISR](isr.md) | страница |
| весь проект, маршрутизируемый клиентом | `useCSR = True` в `nexyconfig.py` → [CSR](csr.md) | проект |

Переключатель всего проекта, в `nexyconfig.py`. Клиентский режим требует клиентской инфраструктуры:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```
<!-- /router -->

<!-- router:modular -->
Нет. Каждое представление, возвращаемое контроллером, отображается при каждом запросе: [ISR](isr.md) и [CSR](csr.md) — это режимы файлового маршрутизатора.
<!-- /router -->

## Пример

<!-- router:fbr,custom -->
```nexy filename="src/маршруты/блог/[слизняк].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` запускает этот шаблон один раз, при этом для `slug` установлено значение `hello`. Второй запрос запускает его снова: между ними ничего не сохраняется. Строка запроса не является реквизитом — прочитайте ее с помощью перехватчиков в [навигация](../routing/fbr/navigation/hooks.md).
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/blog_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/post_view.nexy", context={"slug": slug})
```

```nexy filename="src/apps/post_view.nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello/` запускает это представление один раз, при этом для `slug` установлено значение `hello`. Второй запрос запускает его снова: между ними ничего не сохраняется. Строка запроса не является реквизитом — прочитайте ее с помощью `useSearchParams`.
<!-- /router -->

## Ограничения

- **Один рендер на запрос.** Два посетителя в одну и ту же секунду платят за рендеринг и за запросы, стоящие за ним.
- **Нет кеша.** Не существует общего кеша ответов для разогрева: при использовании файловых маршрутов [ISR](isr.md) добавляет по одному для каждого URL-адреса.
- **Потоковая передача помогает только компоненту, который передает данные.** Медленный запрос в верхней части страницы по-прежнему задерживает первый байт.
- **Нет статического вывода.** В режиме сервера при сборке ничего не зависает: нет режима SSG и нет команды экспорта. См. [Рендеринг](README.md).
- **Автоэкранирование отключено** в шаблонах `.nexy`. Экранируйте ненадежные значения с помощью `| e`.

<!-- router:fbr,custom -->
```nexy filename="src/маршруты/search.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/search_view.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

## Следующие шаги

<!-- router:fbr,custom -->
- [ISR](isr.md): кэшировать эту страницу для каждого URL-адреса.
<!-- /router -->
- [Острова](islands.md): сохраните SSR и сделайте один виджет интерактивным
<!-- router:fbr,custom -->
- [CSR](csr.md): ручная навигация в браузере.
<!-- /router -->
- [Производительность](../deployment/performance.md)
