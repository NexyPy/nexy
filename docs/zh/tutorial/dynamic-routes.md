# 使用 Nexy 构建笔记应用程序，第 3 部分：动态路由和 API

第 3 部分为每个注释提供了自己的 URL `/notes/1`，并在 `/api/notes` 处提供与 JSON 相同的注释，两者都从一个 Python 模块读取。

**开始之前：**[第 2 部分](pages-and-layouts.md) 的应用程序。

## 将笔记保留在一个模块中

页面和 API 将读取相同的列表。将其移至其自己的模块中，并使用查找一个音符的函数：

```python filename="src/notes.py"
NOTES = {1: "Buy milk", 2: "Ship Nexy"}


def find(note_id: int) -> str | None:
    return NOTES.get(note_id)
```

## 将每个注释链接到其页面

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for id, text in notes %}
    <li><a href="/notes/{{ id }}">{{ text }}</a></li>
    {% endfor %}
  </ul>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for id, text in notes %}
    <li><a href="/notes/{{ id }}">{{ text }}</a></li>
    {% endfor %}
  </ul>
</section>
```
<!-- /router -->

## 每个注释添加一页

<!-- router:fbr,custom -->
括号中的文件夹或文件名是 URL 的一段：`[id].nexy` 回答 `/notes/1`、`/notes/2`，并将该段作为 prop 传递到页面。 `id: prop[int]` 将其转换为数字，因此 `/notes/abc` 在页面运行之前回答 `404`。

```nexy filename="src/routes/notes/[id].nexy"
---
from nexy import notFound
from src.notes import find

id: prop[int]
text = find(id)
if text is None:
    notFound()
---
<section class="app-page">
  <h1>{{ text }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

<!-- router:modular -->
控制器路径中的 `{id}` 是 URL 的一部分，传递给该名称下的方法。 `id: int` 将其转换为数字，因此 `/notes/abc` 在该方法运行之前回答 `404`。

```nexy filename="src/apps/notes/note_view.nexy"
---
text: prop[str]
---
<section class="app-page">
  <h1>{{ text }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

`notFound()` 使用 `404` 停止请求：不存在的注释就像不存在的 URL 一样。

## 以 JSON 形式提供注释

<!-- router:fbr,custom -->
`src/routes/` 下的 `.py` 文件是 API 路由。每个以 HTTP 方法命名的函数都会响应该方法：

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": id, "text": text} for id, text in NOTES.items()]
```
<!-- /router -->

<!-- router:modular -->
笔记的三个控制器，在一个文件中。每个以 HTTP 方法命名的方法都会响应该方法：

```python filename="src/apps/notes/notes_controller.py"
from nexy import notFound
from nexy.decorators import Controller
from nexy.hooks import useViews
from src.notes import NOTES, find

LAYOUT = "src/apps/layout.nexy"


def page(view: str, **context: object):
    return useViews(LAYOUT, context={"children": useViews(view, context=context)})


@Controller("/notes")
class NotesController:
    async def get(self):
        return page("src/apps/notes/notes_view.nexy")


@Controller("/notes/{id}")
class NoteController:
    async def get(self, id: int):
        text = find(id)
        if text is None:
            notFound()
        return page("src/apps/notes/note_view.nexy", text=text)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        return [{"id": id, "text": text} for id, text in NOTES.items()]
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NoteController, NotesApiController, NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController, NoteController, NotesApiController]
```
<!-- /router -->

检查三个 URL：

- <http://localhost:3000/notes/1> 显示*购买牛奶*；
- <http://localhost:3000/notes/9> 答案 *找不到页面*；
- `curl http://localhost:3000/api/notes` 打印 `[{"id":1,"text":"Buy milk"},{"id":2,"text":"Ship Nexy"}]`。

该 API 及其架构列于 <http://localhost:3000/docs>。

## 你学到了什么

<!-- router:fbr,custom -->
- `[id].nexy` 是动态段； `id: prop[int]` 读取并转换它。
- `src/routes/` 下的 `.py` 文件响应 JSON，每个 HTTP 方法一个函数。
<!-- /router -->
<!-- router:modular -->
- 控制器路径中的 `{id}` 是动态段； `id: int` 对其进行转换。
- 返回数据应答 JSON 的控制器方法；返回 `useViews` 的则应答一页。
<!-- /router -->
- `notFound()` 从任何地方回答 `404`；共享模块使页面和 API 保持同步。

## 后续步骤

- [第 4 部分：组件](components.md)
- [异常和错误](../reference/exceptions.md)：`notFound`、`redirect` 和其他退出
