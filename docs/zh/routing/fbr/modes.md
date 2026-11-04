# 服务器模式和客户端模式

Nexy 项目是 ** 服务器渲染 ** 或 ** 客户端路由 **，就像 Next.js 项目是
在服务器或客户端应用程序上呈现的页面。 `nexyconfig.py`中的`useCSR`选择。

## 服务器模式（`useCSR = False`）

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

- 页面是`src/routes/`下的`.nexy`、`.md`或`.mdx`文件。
- 根`layout.nexy`拥有`<!DOCTYPE html>`、`<html>`、`<head>`和`<body>`。
- 客户端组件（React、Vue、Svelte、Solid 或 Preact）可以作为**岛屿**：您导入一个
  来自 `.nexy` 页面并在浏览器中水合。参见[岛屿](../../rendering/islands.md)。
- 客户端组件从来都不是路由。将它们保留在`src/components/`中。
- 一次一个客户端框架。

```text
src/
├─ routes/
│  ├─ layout.nexy         document
│  ├─ index.nexy          page
│  └─ api/users.py        API handler
└─ components/Counter.tsx island
```

## 客户端模式（`useCSR = True`）

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

- Pages 是客户端框架的文件：React 的 `.tsx`、`.vue`、`.svelte`。
- `.md` 和 `.mdx` 文件保持有效路由：Nexy 将它们呈现在客户端内的服务器上
  布局，客户端路由器从那里接管导航。
- 任何框架（`layout.tsx`、`layout.vue`、`layout.svelte`）的根布局都拥有 `<!DOCTYPE html>`、`<html>`、`<head>` 和 `<body>`，就像
  Next.js App Router 的根布局。 Nexy 将其呈现在 Node 中作为第一个响应，并且
  框架使整个文档水合起来。请参阅 [layout.tsx](../../views/react/differences.md)。
- `.py` 文件是 FastAPI 提供的 API 处理程序，位于客户端路由旁边。
- 根本没有`.nexy`文件，也没有`layout.nexy`。
- 页面之间的导航发生在浏览器中。

```text
src/routes/
├─ layout.tsx             document
├─ index.tsx              page
├─ users.tsx              page
└─ api/users.py           API handler
```

## 什么被拒绝

Nexy 在 `nx dev`、`nx start` 和 `nx build` 之前检查项目并停止并显示文件列表：

| 模式 | 已拒绝 | 消息 |
|---|---|---|
|服务器|`.tsx`、`.jsx`、`.vue`或`.svelte`下的`src/routes/`|将组件移动到`src/components/`，或设置`useCSR = True`|
| 客户端 | `src/routes/` | 下的任何 `.nexy` 文件将它们写入框架组件，或设置 `useCSR = False` |
| | `useFF` | `useFF must configure exactly one frontend framework` | 中都有多个前端框架
| 客户端 | `useRouter`（模块化路由器）| `useCSR requires file-based routing` |
| 客户端 | 没有 `useFF` | `useCSR requires a client framework` |

此检查将忽略以 `_` 或 `.` 开头的文件和文件夹。

## 哪一个

- **内容、营销、文档、SEO优先网站**：带有岛屿的服务器模式。
- **具有丰富客户端导航的仪表板和应用程序**：客户端模式。
- **顶部有客户端应用程序的 Python API**：客户端模式，页面旁边有 `.py` 处理程序。

## 后续步骤

- [布局](layouts/README.md)
- [渲染](../../rendering/README.md)
- [配置](../../reference/config.md)