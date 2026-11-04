# 基于文件的路由

路线是一个文件。 URL 是相对于 `src/routes/` 的文件路径，减去扩展名。

## 文件到 URL

| 文件 | URL |
|---|---|
| `index.nexy` | `/` |
| `about.nexy` | `/about` |
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/{slug}` |
| `docs/[...path].nexy` | `/docs/{path:path}` |
| `(marketing)/pricing.nexy` | `/pricing` |
| `api/users.py` | `/api/users` |

`index` 映射到其目录，而不是 `/index`。括号中的目录是一个**组**：它
组织文件而不出现在 URL 中。

在客户端模式下，页面文件为 `.tsx`、`.vue` 或 `.svelte`，而不是 `.nexy`； URL 规则是
一样的。

## 两种模式

`useCSR` 决定页面是什么。两者不能混合在一个项目中：Nexy 拒绝启动
当服务器页面位于客户端路由旁边时。

| 模式 | 页 | 根布局 | 请参阅 |
|---|---|---|---|
| 服务器 (`useCSR = False`) | `.nexy`、`.md`、`.mdx` | `layout.nexy` | [服务器模式和客户端模式](modes.md) |
| 客户端 (`useCSR = True`) | 框架文件 | `layout.tsx` | [layout.tsx](../../views/react/differences.md) |

`.py` 文件是两种模式下的 API 处理程序。

## 什么不是路线

- 保留文件名：`layout.*`、`loading.nexy`、`errors.nexy`、`notfound.nexy`、
  `dependencies.py`、`middleware.py`、`__init__.py`。
- 以 `_` 或 `.` 开头的文件和文件夹：将它们用于部分和草稿。
- 对您的项目不活跃的扩展。扩展名无效的文件将被跳过
  一个警告。

## 每个 URL 一个文件

解析为同一 URL 的两个文件都会注册。不要在旁边创建 `blog.nexy`
`blog/index.nexy`，并且不要将 `index.nexy` 和 `index.py` 混合用于同一路径。选择一个。

## 在本节中

| 文件夹 | 它涵盖的内容 |
|---|---|
| [页面/](pages/README.md) |页面，[动态路由](pages/dynamic-routes.md)，路由组|
| [布局/](layouts/README.md) | 每种布局文件类型一页 |
| [处理程序/](handlers/README.md) | `.py` 处理程序、验证和错误 |
| [依赖项/](dependencies/README.md) | `dependencies.py`，警卫|
| [中间件/](middleware/README.md) | `middleware.py` |
| [错误/](errors/README.md) | 未找到和错误页面 |
| [导航/](navigation/linking-and-navigating.md) | 链接、挂钩 |
| [实时/](realtime/websocket.md) | WebSocket |
| [继承](inheritance.md) |一张表中的继承规则|

## 后续步骤

- [服务器模式和客户端模式](modes.md)
- [布局](layouts/README.md)
- [模块化路由](../modular/README.md)