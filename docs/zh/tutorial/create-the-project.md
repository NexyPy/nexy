# 使用 Nexy 构建笔记应用程序，第 1 部分：创建项目

本教程的第 1 部分创建您将发展为笔记应用程序的项目，并在大约五分钟内在浏览器中运行它。

**开始之前：** [uv](https://docs.astral.sh/uv/) 和 Node.js 20 或更高版本。本教程遵循在菜单顶部选择的路由器：将其切换到那里，每个部分都会显示该路由器的文件。

## 你将构建什么

在教程结束时，该应用程序具有用于笔记、数据库、帐户、通过电子邮件共享的笔记、实时更新、测试和生产构建的页面和 JSON API。每个部分都以一个运行的应用程序结束，因此您可以在完成任何一个部分后停止。

## 创建项目

```bash
uvx nexy new notes
```

这样回答问题：

| 问题 | 回答 |
|---|---|
| 基于文件的路由器？ | `Yes` 用于基于文件和自定义路由器，`No` 用于模块化路由器 |
| 项目类型 | `Web` |
| 客户端路由 | `No`：服务器渲染页面 |
| 客户端框架 | `React`：它在第 4 单元中返回，用于岛屿 |
| 风格 | `Tailwind CSS` |
| 导入别名 | `@` |
| ORM | `No database`：第 5 部分添加 1 |

<!-- router:custom -->
自定义路由器是基于文件的路由器加上您已有的 `APIRouter`。本教程使用文件构建应用程序； [包括现有的 FastAPI 路由器](../routing/custom/README.md) 展示了如何将您的路由器安装在它们旁边。
<!-- /router -->

## 运行它

```bash
cd notes
source .venv/bin/activate    # Windows: .venv\Scripts\activate
nexy dev
```

打开 <http://localhost:3000>。您应该看到欢迎页面。保持 `nexy dev` 运行：从现在开始，您保存的每个文件都会重新加载浏览器。

## 你学到了什么

- `uvx nexy new` 创建一个项目并安装其 Python 和 JavaScript 包。
- `nexy dev` 提供服务并在保存时重新加载。
<!-- router:fbr,custom -->
- 这些页面位于 `src/routes/` 中：下一部分添加一个。
<!-- /router -->
<!-- router:modular -->
- 控制器及其视图位于 `src/apps/` 中：下一部分添加一个。
<!-- /router -->

## 后续步骤

- [第 2 部分：页面和布局](pages-and-layouts.md)
- [项目结构](../getting-started/project-structure.md)：项目的每个文件的用途
