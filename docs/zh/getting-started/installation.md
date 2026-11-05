# 安装

## 要求

| 要求 | 为什么 |
|---|---|
| Python 3.12+ | `pyproject.toml`中的 `requires-python`；无需 C 编译器，包括 Windows |
| [uv](https://docs.astral.sh/uv/) | 创建项目、安装其软件包并运行 Nexy |
| Node.js 18+ | 仅适用于客户端框架（React、Vue、Svelte、Solid、Preact） |

没有客户端框架的项目根本不需要 Node.js。

## 首先安装 uv

`uvx` 不是一个单独的工具：它随 uv 一起提供，因此请先安装 uv。

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

用 `uv --version` 和 `uvx --version`检查它。

## 创建一个项目

```bash
uvx nexy new my-app
```

`uvx` 在临时环境中运行 Nexy，并且不会留下任何内容。这足以 **创建** 一个项目（`new`，`init`），仅此而已：临时环境包含 Nexy 而没有其他包。 `nexy new` 创建项目自己的虚拟环境 `.venv`，并在那里安装其软件包。

`nexy new my-app` 提出四个问题：路由器（基于文件或模块化）、项目类型（Web 或 API）、客户端框架、ORM。然后，Python 和节点依赖项的安装以每步骤一行及其持续时间运行。请参阅 [CLI](../reference/cli.md)。

使用已注册的模板跳过提示：

```bash
uvx nexy new my-app --template <name>
```

## 在项目的虚拟环境中工作

每个其他命令（`nexy dev`、`nexy build`、`nexy migrate`...）必须在项目的虚拟环境**内运行**。这就是您自己的包所在的位置：您的 ORM、您的库以及构建项目所使用的 Nexy。在它之外，需要 `sqlmodel` 的项目会失败并显示 `ModuleNotFoundError: No module named 'sqlmodel'`。

从项目文件夹中为每个终端激活一次：

| 壳牌 | 命令 |
|---|---|
| PowerShell、cmd (Windows) | `.venv\Scripts\activate` |
| macOS、Linux | `source .venv/bin/activate` |

然后提示符以 `(.venv)` 开头。从那里：

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

打开 <http://localhost:3000>。

要跳过激活，请让 uv 对一个命令执行此操作：`uv run nexy dev`。

> [!NOTE]
> `nexy` 和 `nx` 是相同的二进制文件。使用 `uv tool install nexy` 安装的副本存在于其自己的环境中，例如 `uvx`，因此使用它来创建项目并运行项目环境中的其他所有内容。

## 将 Nexy 添加到现有项目

从项目的虚拟环境运行它，并在其包中包含 Nexy (`uv add nexy`)：

```bash
nexy init
```

## 后续步骤

- [快速启动](quick-start.md)
- [教程](tutorial.md)
- [项目结构](project-structure.md)
- [故障排除](../guides/troubleshooting.md)
