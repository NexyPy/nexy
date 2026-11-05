# 命令行界面

二进制文件是 `nx`（也安装为 `nexy`）。 `uvx nexy new` 创建一个项目（`uvx` 附带 uv）。在项目的虚拟环境中运行所有其他命令，或通过 `uv run`，例如 `uv run nexy dev`：这是您自己的包所在的位置。

## 命令

| 命令 | 别名 | 它的作用 |
|---|---|---|
| `nx dev` | `nx d` | 开发服务器：更改时编译，Vite，HMR |
| `nx start` | `nx s` | 生产服务器上的编译输出 |
| `nx build` | `nx b` | 生产构建 |
| `nx new` | `nx n` | 搭建一个项目 |
| `nx init` | `nx i` | 将 Nexy 添加到现有项目 |
| `nx add` | - | 从注册表或 URL 添加 UI 组件到 `src/components/ui` |
| `nx migrate` | `nx m` | 使用 Alembic 或 Aerich 创建或应用数据库迁移 |
| `nx check` | `nx c` | 类型检查：mypy on Python, `tsc` on TypeScript |
| `nx format` | `nx f` | 格式 Python（ruff）、JS/TS（更漂亮）、`.nexy` 文件 |
| `nx test` | - | 运行 pytest； `--client` 添加 vitest |
| `nx skills` | - | 添加或刷新编码代理的技能 `AGENTS.md` 和 `CLAUDE.md` |

## 旗帜

| 命令 | 旗帜 | 默认 |
|---|---|---|
| `dev`，`start` | `--port` | `usePort`，`3000` |
| `dev`，`start` | `--host` | `useHost`，`0.0.0.0` |
| `build` | `--check` | off - 构建后运行 ruff 和 mypy |
| `format` | `--check` | off - 报告而不是重写 |
| `test` | `--client` | off - 还运行 vitest 而不是单独运行 pytest |
| `test` | `--no-server` | on - 当您只想进行客户端测试时跳过 pytest |
| `new` | `--template`，`-t` | none - 克隆注册模板而不提示 |
| `new` | `--no-agents` | 特工 - 跳过 `AGENTS.md` 和特工技能 |
| `add` | `--ui`，`--url` | off - 当注册表名称或 URL 不明确时强制使用该名称或 URL |
| `add` | `--all`，`-a` | off - 添加注册表的每个组件 |
| `add` | `--sha256` | none - 远程组件的预期摘要；不匹配中止 |
| `migrate` | `--init` | off - 写入 Alembic 或 Aerich 设置 |
| `migrate` | `--upgrade`，`-u` | off - 应用迁移而不是编写新迁移 |
| `migrate` | `--message`，`-m` | 空 - 新修订的名称 |

## 输出

长步骤（安装包、编译、捆绑）会显示一个带有经过时间的旋转器，然后留下一行：`✔ uv sync .venv  1.4s`。一组步骤（`nx new` 的安装）显示一个进度条，其中包含已完成的步骤数 `━━━━────  2/5`；单个步骤 (`nx add`) 显示运行时脉冲的条形。开发日志对于请求读取 `GET » /about 200 in 12ms`，对于 Vite 读取 `vite » ...`。失败的步骤会打印命令输出的最后几行，而不是隐藏它。无法呈现 Unicode 的终端获取 `+` 和 `x`。

## `nx dev` 运行时出错

保存损坏的文件永远不会停止服务器。报告带有语法错误的 `.py` 文件及其文件和行，并且服务器将继续提供最后一个工作版本，直到您修复它：

```text
  nexy » error  src/routes/users.py:3
  SyntaxError: invalid syntax

    1 | import json
    2 |
  > 3 | def GET(:
                ^
    4 |     x = 1
    5 |     return {"v": 2}

  Fix it and save: the server keeps its last working version.
```

当应用程序加载时解析但失败的文件（缺少导入、模块级别的错误）会以相同的方式报告，并且 `nx dev` 等待您的下一次保存；在应用程序再次加载之前不会提供任何服务。当服务器重新加载时，有效的保存读取 `nexy » update <file>`。 `src/routes` 之外的 Markdown 文件（例如 `README.md`）不是页面，不会触发任何内容。 `nx start` 更严格：如果无法加载路由文件，它会以代码 1 退出，并且不启动任何内容。

## `nx new` 的问题

`nx new` 按此顺序询问：基于文件的路由器、项目类型（Web 或 API）、客户端路由、客户端框架、如何设置应用程序样式、导入别名、ORM、数据库和数据库 URL。每个选项都有一个简短的描述，并且当前选项会突出显示。不适用的问题将被跳过（API 项目没有框架或样式；选择 **无数据库**，因为 ORM 会跳过数据库和 URL）。使用箭头键（或 `j`/`k`或数字）移动，使用 `enter`确认，使用 `←` 或 `esc`返回上一个问题，使用 `ctrl+c`退出。

| 问题 | 选择 |
|---|---|
| 导入别名 | `@`（`@/components/...` 指向 `src/`），或其他前缀，例如 `~` 或 `#app` |
| 风格 | Tailwind CSS、UnoCSS、Vanilla CSS、其他（无 CSS 工具，与 Vanilla 相同的普通样式表） |
| ORM | SQLModel，SQLAlchemy，Tortoise-ORM，无数据库 |
| 数据库（带有 ORM） | SQLite、PostgreSQL、Neon、MySQL / MariaDB、其他（您输入 URL） |

所选 ORM 的数据库驱动程序随其一起安装（`psycopg`、`pymysql`、`asyncpg` 或 `aiomysql`），并且 URL 写入 `.env`。

在安装软件包之前，`nx new` 检查连接。如果没有，它会跳过安装并告诉您稍后运行 `uv sync` 和包管理器的安装。使用其中之一时，它会打印延迟和下载速度，并在连接速度较慢（超过 400 毫秒或低于 100 KB/s）时发出警告。每个安装行都会命名该工具及其填充的文件夹，例如 `pnpm install node_modules` 或 `uv sync .venv`。

## `dev`、`build` 和 `start` 创建了什么

在运行之前，这三个命令会在 `src/` 及其下的每个包含 `.py` 或 `.nexy` 文件的文件夹中创建一个空的 `__init__.py`，因此诸如 `src/routes/users.py` 之类的路由在所有这些路径中都会以相同的方式导入。现有文件永远不会被触及，并且当您添加文件夹时 `nx dev` 会再次执行相同的操作。 Python 字节码转到 `__nexy__/__pycache__`，因此源旁边不会出现 `__pycache__` 文件夹。

## 语言

命令行支持英语、中文、印地语、西班牙语、葡萄牙语、法语、德语、日语、俄语、韩语、印度尼西亚语和阿拉伯语。它使用它支持的第一个：

1. `NEXY_LANG` 环境变量（`NEXY_LANG=ja nx dev`）；
2. shell 的语言环境变量（`LC_ALL`、`LC_MESSAGES`、`LANG`，然后是 `LANGUAGE`）；
3. 您的操作系统的语言。

其他任何东西都是英语，任何一种语言还没有的信息也是英语。仅翻译 `nx` 打印的内容：编译器错误、回溯及其运行的工具的输出保持原样。这些翻译尚未经过母语人士的审核：欢迎更正，作为 `nexy/modules/i18n/<language>.json` 的拉取请求。

## 建立行为

`nx build` 编译路由，然后在 `useVite` 开启时捆绑客户端。

> [!NOTE]
> 没有 `--static` 标志。静态托管是一种部署选择，而不是构建模式 - 请参阅[部署](../deployment/README.md)。

## 致力于 Nexy 本身

在这个存储库内，大门是：

```bash
python scripts/verify.py             # lint, format, typecheck, tests
python scripts/audit_dependencies.py # supply-chain audit against the lock
```

## 后续步骤

- [入门](../getting-started/quick-start.md)：第一个项目
- [测试](../guides/testing.md)：`nx test` 运行什么
- [部署](../deployment/README.md)：生产中的 `build` 和 `start`
