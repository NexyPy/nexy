# 教程：10 分钟构建笔记页面

您将创建一个项目、添加一个页面、添加一个 Python 端点、在它们之间共享数据并进行生产构建。最后，您将获得一个作为页面和 JSON 形式的笔记列表。

新来内克西？首先执行[快速启动](quick-start.md)：需要三分钟。

```diagram filename="整个教程在一行"
uvx nexy new notes ──► edit layout ──► add page ──► add endpoint ──► share data ──► nx build ──► nx start
```

## 1.创建项目

```bash
uvx nexy new notes
cd notes
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

`uvx` 随 [uv](https://docs.astral.sh/uv/) 一起提供，并且仅创建项目。之后的每个命令都在项目的虚拟环境中运行（或作为 `uv run nexy dev`）。

选择基于文件的路由器、Web 项目和任何客户端框架（或无）。打开
<http://localhost:3000>。长步骤每行打印一行及其持续时间，如 `uv` 所做的那样。

<!-- router:modular -->
对基于文件的路由器提示回答 `No`：`nx new` 在 `src/apps/` 而不是 `src/routes/` 中搭建模块化路由器。
<!-- /router -->

<!-- router:custom -->
对页面的基于文件的路由器提示回答 `Yes`，然后将现有的 `APIRouter` 安装在 `nexyconfig.py` 中：两个路由器共存。
<!-- /router -->

## 2. 编辑布局

<!-- router:fbr,custom -->
`src/routes/layout.nexy` 拥有 HTML 文档（使用 React 客户端路由它是 `layout.tsx`）。更改 `<title>`：

```nexy
<title>Notes</title>
```

保存：浏览器重新加载。请参阅[布局](../routing/fbr/layouts/README.md)。
<!-- /router -->

<!-- router:modular -->
控制器在视图周围渲染 `src/apps/layout.nexy`，并且该文件拥有 HTML 文档。更改 `<title>`：

```nexy
<title>Notes</title>
```

保存：浏览器重新加载。请参阅[来自控制器的视图](../routing/modular/README.md#views-from-a-controller)。
<!-- /router -->

## 3.添加页面

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

打开 <http://localhost:3000/notes>：您应该看到两颗子弹。供应地点为 `/notes`。 `---` 之间的部分是 Python，其余部分是 Jinja2。
<!-- /router -->

<!-- router:modular -->
控制器返回一个视图。创建 `src/apps/notes_view.nexy`：

```nexy filename="src/apps/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

在 `src/apps/app_controller.py` 中声明路由并将控制器添加到模块中：

```python filename="src/apps/app_controller.py"
@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/notes_view.nexy"),
        })
```

```python filename="src/apps/app_module.py"
from .app_controller import AppController, NotesController

controllers = [AppController, NotesController]
```

打开 <http://localhost:3000/notes>：您应该看到两颗子弹。 `---` 之间的部分是 Python，其余部分是 Jinja2。
<!-- /router -->

## 4. 添加端点

<!-- router:fbr,custom -->
```python filename="src/routes/api/notes.py"
async def GET():
    return [{"id": 1, "text": "Buy milk"}]
```

```bash
curl http://localhost:3000/api/notes
```

你应该得到 `[{"id":1,"text":"Buy milk"}]`。函数名称是 HTTP 方法。交互式 API 文档位于 `/docs`。
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/app_controller.py"
@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": 1, "text": "Buy milk"}]
```

将 `NotesApiController` 添加到 `src/apps/app_module.py`中的 `controllers`，然后运行：

```bash
curl http://localhost:3000/api/notes
```

你应该得到 `[{"id":1,"text":"Buy milk"}]`。方法名称是 HTTP 方法。交互式 API 文档位于 `/docs`。
<!-- /router -->

## 5. 共享数据

将列表移至 Python 模块并在两个文件中使用它：

```python filename="src/notes.py"
NOTES = ["Buy milk", "Ship Nexy"]
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes_view.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/apps/app_controller.py"
from src.notes import NOTES


@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

## 6. 构建和服务

```bash
nx build
nx start
```

`nx build` 打印每个阶段及其持续时间。 `nx start` 使用 Uvicorn 提供编译输出：运行时没有 Node 进程。

## 下一步去哪里

- [路由](../routing/README.md)：动态段和组
- [操作](../guides/actions.md)：从表单或客户端调用 Python
- [测试](../guides/testing.md)：测试页面和端点
- [部署](../deployment/README.md)：容器和反向代理
