# 快速启动

您将创建一个 Nexy 项目，运行它，并在编辑时看到页面更改。需要三分钟。 [教程](tutorial.md) 然后添加一个端点和一个生产版本。

## 开始之前

| 你需要 | 为什么 |
|---|---|
| Python 3.12+ | `requires-python` 在 `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | 提供 `uvx`，创建项目并安装其包 |
| Node.js 18+ | 仅当您使用客户端框架时（React、Vue、Svelte、Solid、Preact） |

还没有 uv 吗？请参阅[安装](installation.md)。

## 1.创建项目

```bash
uvx nexy new my-app
```

`uvx` 附带 uv，因此请先安装 uv。它在临时环境中运行 Nexy，足以 **创建** 项目。 `nexy new` 然后创建项目自己的 `.venv` 并在那里安装它的包。四个提示决定接线：

| 提示 | 效果 |
|---|---|
| 基于文件的路由器？ | `Yes` 扫描 `src/routes/`； `No` 在 `src/apps/` 中搭建模块化路由器 |
| 项目类型 | `Web` 添加布局和客户端资源，`API` 开始时没有视图 |
| 客户端组件？ | 添加一个框架及其 Vite 设置 |
| ORM/数据库 | 添加模型层，或者什么都不添加 |

不确定？回答 `Yes`、`Web`，并且没有客户端组件。您可以稍后添加。

## 2.运行它

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

打开 <http://localhost:3000>。您应该看到起始页。端口来自 `usePort`（默认 `3000`）； `--port` 和 `--host` 每次运行都会覆盖它。

> [!NOTE]
> 在项目的虚拟环境中运行除 `new` 和 `init` 之外的所有命令，或在其前面加上 `uv run` 前缀，如 `uv run nexy dev` 中所示。在它之外，需要 `sqlmodel` 的项目会失败并显示 `No module named 'sqlmodel'`。

## 3. 更改页面

<!-- router:fbr,custom -->
`src/routes/` 下的文件是一个路由。创建 `src/routes/hello.nexy`：

```nexy filename="src/routes/hello.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```
<!-- /router -->

<!-- router:modular -->
控制器返回一个视图。创建 `src/apps/hello_view.nexy`：

```nexy filename="src/apps/hello_view.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

然后在 `src/apps/app_controller.py` 中声明页面并将其添加到模块中：

```python filename="src/apps/app_controller.py"
@Controller("/hello")
class HelloController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/hello_view.nexy")})
```

```python filename="src/apps/app_module.py"
from .app_controller import AboutController, AppController, HelloController

controllers = [AppController, AboutController, HelloController]
```
<!-- /router -->

打开 <http://localhost:3000/hello>。将 `"Hello"` 更改为 `"Bonjour"` 并保存：页面更新，无需手动重新加载。如果代码错误，浏览器会显示错误而不是空白页面。

`prop[str]` 声明一个类型化属性。 frontmatter 下的标记是 Jinja2 - 请参阅 [.nexy 文件 ](../views/nexy/README.md)。

## 下一步去哪里

| 你想要 | 阅读 |
|---|---|
| 添加 Python 端点并发布构建 | [教程](tutorial.md) |
| 知道每个文件所属的位置 | [项目结构](project-structure.md) |
| 了解谁建造了什么 | [Nexy 的工作原理](how-nexy-works.md) |
| 使用 React、Vue、Svelte、Solid 或 Preact | [浏览次数](../views/README.md) |
