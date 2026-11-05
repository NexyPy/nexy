# 什么是内克西？

Nexy 是一个用于全栈 Web 应用程序的 Python 框架：您的页面和 API 位于一个项目中，并由一台服务器提供服务。

## 你得到什么

- **Python.** 中的页面 `.nexy` 文件是 HTML，顶部有几行 Python； `.md` 文件也是一个页面。渲染页面不需要 JavaScript。
- **同一项目中的 API。** `src/routes/` 下的 `.py` 文件应答 HTTP 请求：名为 `GET` 的函数应答 `GET`，名为 `POST` 的函数应答 `POST`。
- **免费的 API 文档。** 每个 API 路由都出现在 OpenAPI 模式中，Scalar 将其显示为 `/docs` 中的交互式参考。
- **调用 Python.** 的表单 表单或来自浏览器的键入调用会到达相同的 Python 函数。
- **当您需要一个前端框架时。** React、Vue、Svelte、Solid 或 Preact，用于一个组件或整个站点。
- **一条命令起作用，一条命令发送。** `nx dev` 在您保存时重新加载； `nx build` 准备生产。

## 它是建立在什么之上的

当前版本 2.2 基于您可能已经知道的工具：

| 部分 | 建立在 | 这对你意味着什么 |
|---|---|---|
| 服务器和API | [FastAPI](https://fastapi.tiangolo.com/) | API 路由是 FastAPI 路由：Pydantic 验证和依赖项照常工作 |
| API参考 | OpenAPI 和 [标量 ](https://scalar.com/) | 架构位于 `/openapi.json`，参考位于 `/docs` |
| 页数 | Jinja2 | `.nexy` 页面使用 Jinja2 标签，例如 `{{ title }}` |
| 前端（可选） | [Vite](https://vite.dev/) | 仅具有前端框架，这也需要 Node.js |

## 第一页和第一端点

页面，位于 `/hello`：

```nexy filename="src/routes/hello.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

端点位于 `GET /api/items`，在 `/docs` 中列出，无需任何额外代码：

```python filename="src/routes/api/items.py"
from nexy.http import Request


async def GET(request: Request):
    return {"items": []}
```

## Nexy 留给你什么

数据库、登录名以及有关谁可以执行哪些操作的规则都属于您的应用程序，因此您可以选择库。 [数据库](../guides/databases.md) 和[中间件和安全性](../guides/middleware-and-security.md) 显示了每个数据库的插入位置。

## 后续步骤

- [安装](installation.md)：安装 uv 并创建项目
- [快速启动](quick-start.md)：运行它，更改页面，构建它
- [核心概念](core-concepts.md)：其余文档使用的几个词
