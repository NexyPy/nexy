# Основные понятия

Слова, которые используются в остальных документах — маршрут, страница, представление, компонент, обработчик, конечная точка — каждое в одной строке со ссылкой на более глубокую страницу. Впервые в Некси? Начните с [Что такое Nexy?](what-is-nexy.md).

## Как читать эти документы

| Уровень | Вопрос, на который он отвечает | Начните с |
|---|---|---|
| Архитектура приложения | какой уровень отвечает на запрос и что он отказывается делать | [Как работает Nexy](how-nexy-works.md) |
| Структура приложения | где живет код и каким становится файл | [Структура проекта](project-structure.md) |
| Презентация и рендеринг | что видит читатель и кто создает HTML | [Просмотры](../views/README.md), [Рендеринг](../rendering/README.md) |
| Взаимодействие с приложением | что делает читатель и что происходит в ответ | [Действия](../guides/actions.md) |

Уровни читаются в таком порядке один раз. После этого вам нужна страница — это справочник, а не курс.

## Архитектура приложения

Три способа решить, какой код соответствует URL-адресу. Это альтернативы, а не слои:

- **Маршрутизация на основе файлов (FBR)**: файл в папке `src/routes/` является маршрутом. Значение по умолчанию.
- **Модульный маршрутизатор**: контроллеры и модули из `src/apps/`, объявленные с помощью декораторов, для кодовой базы в стиле NestJS.
- **Пользовательский маршрутизатор**: существующий FastAPI `APIRouter`, включенный в приложение.

Выбор — одна строка класса `NexyConfig` в `nexyconfig.py`.

<!-- router:fbr -->
Маршрутизация на основе файлов не требует строки: без `useRouter` Nexy читает `src/routes/`.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    pass  # file-based: no useRouter, the files of src/routes/ are the routes
```
<!-- /router -->

<!-- router:modular -->
Модульный маршрутизатор является корневым модулем `src/apps/`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule  # modular: the root module of src/apps/
```
<!-- /router -->

<!-- router:custom -->
Пользовательский маршрутизатор — это `APIRouter`, который у вас уже есть:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import api  # an APIRouter you already have


class NexyConfig(NexyConfigModel):
    useRouter = api  # custom: your router, included as it is
```
<!-- /router -->

Выбор одного из трех – это одно решение. Выбор внешнего интерфейса — это еще один отдельный вопрос: см. [Выбор маршрутизатора](../routing/README.md) и [Представления](../views/README.md)].

## Структура приложения

Пять понятий, которые читатель из Next.js обычно сливает в одно. Это не одно и то же, и разница объясняет большинство вопросов «почему моя страница не отображается».

| Понятие | Что это такое | Что это не так |
|---|---|---|
| **Маршрут** | шаблон URL, созданный путем пути к файлу | файл: один файл может отвечать на несколько URL-адресов (`[slug]`) |
| **Страница** | файл маршрута, который отображает представление: `.nexy`, `.md`, `.mdx`, `.tsx`, `.vue`, `.svelte` | конечная точка: она отвечает на документ, а не на данные |
| **Посмотреть** | что создает тело страницы: Jinja2 и Python, Markdown или клиентский компонент | маршрут: одно и то же представление может обслуживать несколько страниц |
| **Компонент** | многоразовый фрагмент, импортируемый страницей | маршрут: в режиме сервера компонент никогда не обслуживается сам по себе |
| **Обработчик маршрута** | функция файла маршрута `.py`, названная в честь метода HTTP (`GET`, `POST`, …) | страница: возвращает JSON, файл или `Response` |
| **Конечная точка** | пара (URL, метод), на которую отвечает обработчик | обработчик: один файл может отвечать нескольким конечным точкам |

В одном предложении: **страница — это файл маршрута, представление — это то, что ее отображает, компонент — это то, что страница повторно использует, обработчик отвечает конечной точке.**

<!-- router:fbr -->
Все пять в одном небольшом проекте:

```text
src/
├─ routes/
│  ├─ blog/[slug].nexy    a route (/blog/{slug}) whose file is a page
│  └─ api/posts.py        a route whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```nexy filename="src/маршруты/блог/[слизняк].nexy"
---
from "@/components/Like.tsx" import Like

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Like post="{{ slug }}" />
```

Фронтальная часть и шаблон под ней представляют собой вид страницы; `Like` — это компонент, который он использует повторно.

```python filename="src/routes/api/posts.py"
async def GET():  # the endpoint GET /api/posts
    return {"posts": []}


async def POST():  # the endpoint POST /api/posts
    return {"created": True}
```

<!-- /router -->

<!-- router:modular -->
В модульном маршрутизаторе маршрут — это путь контроллера, а обработчик — один из его методов, названный в честь глагола HTTP:

```text
src/
├─ apps/
│  ├─ app_module.py       the root module: lists the controllers
│  └─ posts_controller.py a route (/api/posts) whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```python filename="src/apps/posts_controller.py"
from nexy.decorators import Controller


@Controller("/api/posts")
class PostsController:
    async def get(self) -> dict:  # the endpoint GET /api/posts
        return {"posts": []}

    async def post(self) -> dict:  # the endpoint POST /api/posts
        return {"created": True}
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .posts_controller import PostsController


@Module()
class AppModule:
    controllers = [PostsController]
```

Страница по-прежнему является файлом `src/routes/` или представлением, которое контроллер возвращает с помощью `useViews`.
<!-- /router -->

<!-- router:custom -->
В случае пользовательского маршрутизатора маршрут — это путь к вашему `APIRouter`, а обработчик — это функция, которую регистрирует его декоратор:

```python filename="src/legacy.py"
from fastapi import APIRouter

api = APIRouter()


@api.get("/api/posts")  # the endpoint GET /api/posts
async def list_posts():
    return {"posts": []}


@api.post("/api/posts")  # the endpoint POST /api/posts
async def create_post():
    return {"created": True}
```

Страницы по-прежнему представляют собой файлы `src/routes/`: страница `.nexy` отвечает рядом с включенными маршрутами.
<!-- /router -->

Еще два слова, которые повторяются повсюду:

- **Layout**: файл `layout.*`, который оборачивает страницы под своей папкой; корневой владеет HTML-документом. См. [Макеты](../routing/fbr/layouts/README.md).
- **Зависимость**: функция, которая запускается перед обработчиком, применяется для каждого маршрута или для каждой папки. См. [Зависимости](../routing/fbr/dependencies/README.md).

## Презентация и рендеринг

Два независимых решения, которые часто путают:

- **Формат** определяет, какой файл отображает страницу: [Представления](../views/README.md).
- **Режим** решает, кто и когда создает HTML: [Рендеринг](../rendering/README.md).

| Понятие | Одна линия |
|---|---|
| Режим сервера | сервер отображает страницы `.nexy` и `.md`; компоненты являются островами ([режимы](../routing/fbr/modes.md)) |
| Клиентский режим | `useCSR = True`: файлы фреймворка представляют собой маршруты, а навигация происходит в браузере. |
| ССР, ИСР, КСР, острова | четыре режима рендеринга, определяемые для каждой страницы, кроме CSR, который устанавливается для каждого проекта ([рендеринг](../rendering/README.md)) |
| Увлажнение | браузер прикрепляет фреймворк к уже отправленному сервером HTML ([острова](../rendering/islands.md)) |
| Реквизит | значения, которые родитель передает компоненту, объявленному `name: prop[type]` в файле `.nexy` ([файлы .nexy](../views/nexy/README.md)) |

Страница в режиме сервера с одним островом: сервер отображает страницу, браузер увлажняет диаграмму только при ее прокрутке в поле зрения.

<!-- router:fbr,custom -->
```nexy filename="источник/маршруты/sales.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Sales</h1>
<Chart directive="client:visible" />
```
<!-- /router -->

<!-- router:modular -->
Остров попадает в представление, а контроллер возвращает представление:

```nexy filename="src/apps/sales_view.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Sales</h1>
<Chart directive="client:visible" />
```

```python filename="src/apps/sales_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/sales")
class SalesController:
    async def get(self):
        return useViews("src/apps/sales_view.nexy")
```
<!-- /router -->

## Взаимодействие с приложением

| Понятие | Одна линия |
|---|---|
| Действие | функция Python с пометкой `@Action`, служащая как `POST`, вызываемая из формы или как типизированная функция ([действия](../guides/actions.md)) |
| Форма | HTML-форма, которая отправляет сообщение в действие, с ошибками проверки, возвращающимися на страницу ([действия](../guides/actions.md)) |
| Навигация | ссылки, выполняющие предварительную выборку, и перехватчики, считывающие путь, запрос, файлы cookie и сеанс ([хуки](../routing/fbr/navigation/hooks.md)) |
| Получение данных | выполняется страницей или обработчиком, которому это необходимо; Nexy не поставляет уровень клиентских данных ([обработчики](../routing/fbr/handlers/README.md)) |

Действие и форма, которая его отправляет, которая работает до загрузки любого скрипта:

```python filename="src/actions/newsletter.py"
from nexy.decorators import Action


@Action
async def subscribe(email: str) -> bool:
    return True
```

<!-- router:fbr,custom -->
```html filename="источник/маршруты/index.nexy"
<form method="post" action="{{ __actions_path['subscribe'] }}">
  <input name="email" type="email">
  <button type="submit">Subscribe</button>
</form>
```
<!-- /router -->

<!-- router:modular -->
```html filename="src/apps/home_view.nexy"
<form method="post" action="{{ __actions_path['subscribe'] }}">
  <input name="email" type="email">
  <button type="submit">Subscribe</button>
</form>
```
<!-- /router -->

## Чего Nexy не делает

Аутентификация, авторизация, база данных, интернационализация, фоновые задания, электронная почта, платежи и поиск — это **ответственность вашего приложения**, а не фреймворка. Nexy дает точки расширения и говорит, куда подключить каждую: см. [Что Nexy оставляет вам](how-nexy-works.md#what-nexy-leaves-to-you).

<!-- router:fbr -->
Например, аутентификация подключается к зависимости от папки, которую она защищает. Nexy запускает его перед каждым маршрутом ниже; кто пользователь, остается за вами:

```python filename="src/routes/account/dependents.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```
<!-- /router -->

<!-- router:modular -->
Например, аутентификация подключается к устройству защиты на контроллере, который она защищает. Nexy запускает его перед каждым обработчиком класса; кто пользователь, остается за вами:

```python filename="src/apps/account_controller.py"
from nexy import unauthorized
from nexy.decorators import Controller, UseGuard
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


@Controller("/account")
@UseGuard(require_login)
class AccountController:
    async def get(self) -> dict:
        return {"ok": True}
```
<!-- /router -->

<!-- router:custom -->
Аутентификация, например, подключается к зависимости маршрутизатора, который она защищает, как в FastAPI; кто пользователь, остается за вами:

```python filename="src/account.py"
from fastapi import APIRouter, Depends

from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


api = APIRouter(prefix="/account", dependencies=[Depends(require_login)])
```
<!-- /router -->

Причина не в минимализме как таковом: фреймворк, который выбирает ваш ORM или вашу библиотеку аутентификации, решил что-то, что может решить только ваше приложение.

## Следующие шаги

- [Структура проекта](project-structure.md): каждая папка и файл проекта.
- [Глоссарий](../reference/glossary.md): одни и те же слова, в одном алфавитном указателе.
- [Как работает Nexy](how-nexy-works.md): слои, кто что строит и что Nexy оставляет вам
