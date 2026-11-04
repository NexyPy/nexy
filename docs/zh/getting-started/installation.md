# 安装

## 要求

| 要求 | 为什么 |
|---|---|
| Python 3.12+ | `requires-python` 在 `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | 创建项目，安装其软件包并运行 Nexy |
| Node.js 18+ | 仅适用于客户端框架（React、Vue、Svelte、Solid、Preact）|

没有客户端框架的项目根本不需要 Node.js。

## 先安装uv

`uvx` 不是一个单独的工具：它附带 uv，因此请先安装 uv。

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

用`uv --version`和`uvx --version`检查它。

## 创建项目

```bash
uvx nexy new my-app
```

`uvx` 在临时环境中运行 Nexy，并且不会留下任何内容。这足以**创建**一个
项目（`new`，`init`）仅此而已：临时环境包含 Nexy 而没有其他
包。 `nexy new` 创建项目自己的虚拟环境 `.venv`，并安装其软件包
那里。

`nexy new my-app` 提出四个问题：路由器（基于文件或模块化）、项目类型（Web 或 API）、
客户端框架，ORM。然后，Python 和 Node 依赖项的安装每行一行运行
步骤及其持续时间。请参阅 [CLI](../reference/cli.md)。

使用已注册的模板跳过提示：

```bash
uvx nexy new my-app --template <name>
```

## 在项目的虚拟环境中工作

每个其他命令（`nexy dev`、`nexy build`、`nexy migrate`...）必须在项目的内部运行 **
虚拟环境**。这就是您自己的包所在的地方：您的 ORM、您的库和 Nexy
该项目是用.在它之外，需要 `sqlmodel` 的项目失败并显示
`ModuleNotFoundError: No module named 'sqlmodel'`。

从项目文件夹中为每个终端激活一次：

| 外壳程序 | 命令 |
|---|---|
| PowerShell、cmd (Windows) | `.venv\Scripts\activate` |
|macOS、Linux | `source .venv/bin/activate` |

然后提示符以 `(.venv)` 开头。从那里：

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

打开<http://localhost:3000>。

要跳过激活，请让 uv 通过一个命令执行此操作：`uv run nexy dev`。

> [！注意]
> `nexy` 和 `nx` 是相同的二进制文件。使用“uv tool install”安装的副本
> nexy` lives in its own environment, like `uvx`，因此使用它来创建项目并运行所有内容
> 来自项目环境的其他内容。

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