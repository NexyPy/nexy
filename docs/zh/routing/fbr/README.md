# 基于文件的路由

路线是一个文件。 URL 是相对于 `src/routes/` 的文件路径，减去扩展名。

## 文件到 URL

| 文件 | 网址 |
|---|---|
| `index.nexy` | `/` |
| `about.nexy` | `/about` |
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/{slug}` |
| `docs/[...path].nexy` | `/docs/{path:path}` |
| `(marketing)/pricing.nexy` | `/pricing` |
| `api/users.py` | `/api/users` |

`index` 映射到其目录，而不是 `/index`。括号中的目录是一个 **group**：它组织文件，但不会出现在 URL 中。

在客户端模式下，页面文件为 `.tsx`、`.vue` 或 `.svelte`，而不是 `.nexy`； URL 规则是相同的。

该表的两个文件：一个读取其段的页面，以及一个应答 JSON 的处理程序。

```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str]
---
<h1>{{ slug }}</h1>
```

```python filename="src/routes/api/users.py"
async def GET():
    return {"users": []}
```

## 两种模式

`useCSR` 决定页面是什么。两者不能混合在一个项目中：当服务器页面位于客户端路由旁边时，Nexy 拒绝启动。

| 模式 | 页数 | 根布局 | 参见 |
|---|---|---|---|
| 服务器（`useCSR = False`） | `.nexy`，`.md`，`.mdx` | `layout.nexy` | [服务器模式和客户端模式](modes.md) |
| 客户端（`useCSR = True`） | 框架文件 | `layout.tsx` | [布局.tsx](../../views/react/differences.md) |

`.py` 文件是两种模式下的 API 处理程序。

开关是 `nexyconfig.py` 中的一行：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True  # client mode: src/routes/*.tsx are the pages
```

## 什么不是路线

- 保留文件名：`layout.*`、`loading.nexy`、`errors.nexy`、`notfound.nexy`、`dependencies.py`、`middleware.py`、`__init__.py`。
- 以 `_` 或 `.` 开头的文件和文件夹：将它们用于部分和草稿。
- 对于您的项目不活跃的扩展。扩展名无效的文件将被跳过并带有警告。

```text
src/routes/
├─ layout.nexy          wraps the pages, not a route
├─ middleware.py        wraps the requests, not a route
├─ index.nexy           /
├─ _card.nexy           a partial: no URL
└─ .draft.nexy          a draft: no URL
```

## 每个 URL 一个文件

解析为同一 URL 的两个文件都会注册。不要在 `blog/index.nexy` 旁边创建 `blog.nexy`，并且不要在同一路径中混合 `index.nexy` 和 `index.py`。选择一个。

```text
src/routes/
├─ blog.nexy            /blog
└─ blog/
   └─ index.nexy        /blog as well: delete one of the two
```

## 在本节中

| 文件夹 | 它涵盖什么 |
|---|---|
| [页数/](pages/README.md) | 页面、[动态路由](pages/dynamic-routes.md)、路由组 |
| [布局/](layouts/README.md) | 每种布局文件类型一页 |
| [处理程序/](handlers/README.md) | `.py` 处理程序、验证和错误 |
| [依赖项/](dependencies/README.md) | `dependencies.py`，守卫 |
| [中间件/](middleware/README.md) | `middleware.py` |
| [错误/](errors/README.md) | 未找到和错误页面 |
| [导航/](navigation/linking-and-navigating.md) | 链接、挂钩 |
| [实时/](realtime/websocket.md) | WebSocket |
| [继承](inheritance.md) | 继承规则在一张表中 |

## 后续步骤

- [服务器模式和客户端模式](modes.md)
- [布局](layouts/README.md)
- [模块化路由](../modular/README.md)
