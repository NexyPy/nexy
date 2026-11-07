# От Astro до Некси

Страница Nexy `.nexy` - это страница Astro с Python во фронтальной части `---` вместо TypeScript: тот же HTML-код, ориентированный на сервер, те же острова и `client:*` директивы, отображаемые при каждом запросе.

В каждом разделе ниже показана привычка Astro, затем то же самое в Nexy.

## Страница

```astro filename="src/pages/about.astro"
---
const title = "About";
---
<h1>{title}</h1>
```

Вступление - Python и шаблон - Jinja2:

```nexy filename="источник/маршруты/about.nexy"
---
title = "About"
---
<h1>{{ title }}</h1>
```

`src/pages/` - это `src/routes/`, а `index.astro` - это `index.nexy`.

## Циклы и условия

```astro filename="src/pages/users.astro"
---
const users = [{ name: "Ada", admin: true }, { name: "Alan", admin: false }];
---
<ul>
  {users.map((user) => <li>{user.name}{user.admin && <strong> admin</strong>}</li>)}
</ul>
```

```nexy filename="src/маршруты/users.nexy"
---
users = [{"name": "Ada", "admin": True}, {"name": "Alan", "admin": False}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}{% if user.admin %}<strong> admin</strong>{% endif %}</li>
  {% endfor %}
</ul>
```

> [!WARNING]
> Astro экранируется каждые `{value}`. Шаблоны `.nexy` не позволяют: экранировать то, что посетитель набрал с помощью `{{ value | e }}`.

## Компоненты и `Astro.props`

```astro filename="src/компоненты/Card.astro"
---
const { title, tone = "neutral" } = Astro.props;
---
<article class={`card card-${tone}`}>
  <h2>{title}</h2>
  <slot />
</article>
```

Свойства объявляются с помощью `prop[...]`, значением по умолчанию является Python по умолчанию, а `<slot />` - это `<Slot />`:

```nexy filename="источник/компоненты/Card.nexy"
---
title: prop[str]
tone: prop[str] = "neutral"
---
<article class="card card-{{ tone }}">
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="источник/маршруты/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest" tone="warm">
  <p>This week</p>
</Card>
```

`@` - это `src/`: `nx new` записывает `useAliases = {"@": "src"}` в `nexyconfig.py`.

## Макеты

```astro filename="src/layouts/Base.astro"
---
const { title } = Astro.props;
---
<html>
  <head><title>{title}</title></head>
  <body><slot /></body>
</html>
```

```astro filename="src/pages/about.astro"
---
import Base from "../layouts/Base.astro";
---
<Base title="About"><h1>About</h1></Base>
```

Страница не импортирует свой макет: ближайший `layout.nexy` над ней оборачивает его, а корневой владеет документом.

```nexy filename="src/маршруты/layout.nexy"
---
from nexy import useMetadata

children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <head>{{ useMetadata().html() }}</head>
  <body>{{ children | safe }}</body>
</html>
```

## Заголовок и мета-теги

Опция `title` макета становится `metadata` на странице, которую `useMetadata().html()` записывает в `<head>` макета выше:

```nexy filename="src/маршруты/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## Динамические маршруты и `getStaticPaths`

```astro filename="src/pages/posts/[slug].astro"
---
export function getStaticPaths() {
  return [
    { params: { slug: "hello" }, props: { title: "Hello" } },
    { params: { slug: "world" }, props: { title: "World" } },
  ];
}
const { title } = Astro.props;
---
<h1>{title}</h1>
```

Динамическая страница `.nexy` отображается по запросу, поэтому список путей отсутствует: сегмент является реквизитом, а неизвестный - `404`.

```nexy filename="src/маршруты/сообщения/[слизень].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello", "world": "World"}

slug: prop[str]
if slug not in POSTS:
    notFound()
title = POSTS[slug]
---
<h1>{{ title }}</h1>
```

`[...path].astro` - это `[...path].nexy`.

## Острова и `client:*`

```astro filename="src/pages/index.astro"
---
import Counter from "../components/Counter.tsx";
---
<h1>Static heading</h1>
<Counter start={3} client:visible />
```

Директива становится атрибутом `directive` с теми же значениями:

```nexy filename="src/маршруты/home.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

| Astro | Некси |
|---|---|
| `client:load` | `directive="client:load"` или отсутствие директивы |
| `client:idle` | `directive="client:idle"` |
| `client:visible` | `directive="client:visible"` |
| `client:media="(min-width: 768px)"` | `directive="client:media" media="(min-width: 768px)"` |
| `client:only="react"` | принимается, но никогда не увлажняется: используйте `client:load` |

Фреймворк устанавливается один раз в `nexyconfig.py`, и проект использует его:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

## Markdown страниц

```md filename="src/pages/changelog.md"
---
layout: ../layouts/Base.astro
---
# Changelog
```

Файл `.md` в папке `src/routes/` - это страница, завернутая в ближайший макет без ключа `layout:`:

```md filename="источник/маршруты/changelog.md"
# Changelog

Version 2.2 is out.
```

Страницы `.mdx` также работают с React или Preact в качестве основы. См. [Markdown и MDX](../views/nexy/markdown.md).

## Конечные точки API

```ts filename="src/pages/api/items/[id].ts"
export function GET({ params }) {
  return Response.json({ id: Number(params.id) });
}
```

```python filename="src/маршруты/api/items/[id].py"
async def GET(id: int):
    return {"id": id}
```

Тело - это модель Pydantic, проверенная перед запуском функции:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## `Astro.redirect`, `Astro.cookies` и `Astro.url`

```astro filename="src/pages/account.astro"
---
const theme = Astro.cookies.get("theme")?.value ?? "light";
if (!Astro.cookies.has("session")) return Astro.redirect("/login");
const page = Astro.url.searchParams.get("page") ?? "1";
---
<p>{theme} theme, page {page}</p>
```

Те же чтения - это хуки, а редирект - функция:

```nexy filename="src/маршруты/account.nexy"
---
from nexy import redirect, useCookies, useSearchParams

cookies = useCookies()
if "session" not in cookies:
    redirect("/login")
theme = cookies.get("theme", "light")
page = useSearchParams().get("page", "1")
---
<p>{{ theme }} theme, page {{ page }}</p>
```

## Промежуточное ПО

```ts filename="src/middleware.ts"
export function onRequest(context, next) {
  return next().then((response) => {
    response.headers.set("x-app", "demo");
    return response;
  });
}
```

```python filename="src/routes/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

`middleware.py` в подпапке оборачивает только маршруты ниже него, что заменяет проверки пути внутри `onRequest`.

## Astro Действия

```ts filename="источник/действия/index.ts"
import { defineAction } from "astro:actions";
import { z } from "astro:schema";

export const server = {
  addNote: defineAction({
    accept: "form",
    input: z.object({ title: z.string() }),
    handler: async ({ title }) => ({ title }),
  }),
};
```

```astro filename="src/pages/notes.astro"
---
import { actions } from "astro:actions";
---
<form method="POST" action={actions.addNote}>
  <input name="title" />
  <button>Add</button>
</form>
```

Действие - это функция Python в `src/actions/`; форма отправляет сообщения по своему пути:

```python filename="src/actions/notes.py"
from nexy.decorators import Action

NOTES: list[str] = []


@Action
async def add_note(title: str) -> None:
    NOTES.append(title)
```

```nexy filename="src/маршруты/notes.nexy"
---
from src.actions.notes import NOTES
---
<form method="post" action="{{ __actions_path['add_note'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
<ul>
  {% for note in NOTES %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

На острове `useAction(add_note)` в `@nexy/client` вызывает ту же функцию с типизированным вводом.

## `<Image />`

```astro
---
import { Image } from "astro:assets";
import logo from "../assets/logo.png";
---
<Image src={logo} alt="Logo" width={128} height={32} />
```

```nexy filename="src/маршруты/brand.nexy"
---
from nexy import Image
---
<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

## `404.astro`

```astro filename="src/pages/404.astro"
<h1>Not found</h1>
```

```nexy filename="источник/маршруты/notfound.nexy"
<h1>Not found</h1>
```

Клиенты API по-прежнему получают `{"detail": "Not Found"}`.

## Статический вывод и рендеринг по требованию

Astro по умолчанию создает статический HTML и отображает по требованию с помощью `output: "server"` или `export const prerender = false`. Nexy отображает каждую страницу по запросу и кэширует те, которые вы выбираете для каждого URL-адреса:

```nexy filename="src/маршруты/news.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

Статического экспорта нет: `nx start` обслуживает сайт. См. [Рендеринг](../rendering/README.md).

## Бег

| Astro | Некси |
|---|---|
| `npm create astro@latest` | `nx new` |
| `astro dev` | `nx dev` |
| `astro build` и `astro preview` | `nx build`, затем `nx start` |
| `public/` | `public/`, служил в `/` |
| `astro add react` | `nx new` с фреймворком или `useFF = react()` |

## Следующие шаги

- [файлы .nexy](../views/nexy/README.md)
- [Острова](../rendering/islands.md)
- [Markdown и MDX](../views/nexy/markdown.md)
- [От Next.js до Некси](nextjs.md)
