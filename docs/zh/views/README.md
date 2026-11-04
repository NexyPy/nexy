# 观看次数

在选择文件格式之前，区分 Nexy 如何处理资源以及如何呈现资源非常重要。

| 术语 | 定义 |
|---|---|
| **页面** | 应用程序的 URL 可寻址资源。它由 `src/routes/` 下的文件定义。 |
| **View** | 生成页面响应正文的过程。视图将逻辑和数据转换为 HTML 或 JSON。 |
| **组件** | 用于组成视图的可重用 UI 构建块。组件可以是本机 Nexy 帮助程序或特定于框架的组件（React、Vue 等）。 |
| **路由处理程序** | 处理特定方法（例如，`GET`、`POST`）的 HTTP 请求的 Python 函数。 |
| **Endpoint** | 路由处理程序应答的 URL 和 HTTP 方法的唯一组合。 |

**不确定？编写一个`.nexy`文件。**它不需要客户端框架，你可以稍后在其中添加React、Vue、Svelte、Solid或Preact组件，作为一个岛。

```diagram filename="哪个文件对应哪个页面"
server logic + HTML          →  .nexy      (Python frontmatter + Jinja2)
prose that changes rarely    →  .md        (GitHub-flavoured Markdown)
prose + components           →  .mdx       (React or Preact)
app-like page, client router →  .tsx .vue .svelte (framework files)
API handler                  →  .py        (GET, POST, …)
```

## 格式

| 格式 | 文件 | 服务器渲染 | 客户端框架 | 注释 |
|---|---|---|---|---|
| `.nexy` | [.nexy 文件](nexy/README.md) | Jinja2 + Python 逻辑，流式传输 | 可选 | 本机 Nexy 页面格式 |
| `.md` | [Markdown 和 MDX](nexy/markdown.md) | cmarkgfm 在请求时 | 通过布局可选 | 纯 Markdown、GFM、布局包装 |
| `.mdx` | [Markdown 和 MDX](nexy/markdown.md) | 框架 SSR | React 或 Preact | 带组件的 Markdown |
| `.tsx` | [React](react/differences.md)、[Solid](solid/differences.md) 或 [Preact](preact/differences.md) | 客户端模式：框架，在 Node | React、Solid 或 Preact | 组件路由 | 中呈现
| `.vue` | [Vue](vue/differences.md) | 客户端模式：框架，在 Node | Vue | SFC 路由 | 中渲染
| `.svelte` | [Svelte](svelte/differences.md) | 客户端模式：框架，在 Node 中渲染 | Svelte | SFC 路由 |

内置 `Image`、`Link`、`Audio`、`Video` 和 `Import` 帮助器：[Components](nexy/components.md)。

## 混合格式

您可以在同一项目中混合使用不同的技术：
- **Islands**：您可以在 `.nexy` 页面内导入 React 或 Vue 组件。服务器渲染外壳，框架在客户端上填充组件。
- **共享逻辑**：`.py`文件中的路由处理程序可以通过共享应用程序状态或API调用向任何格式的页面提供数据。

## 启用框架

在 `nexyconfig.py` 中设置 `useFF` 并运行 `nexy new` 添加依赖项：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

启用框架后，Vite 可以处理其客户端捆绑包。在客户端模式下，它的扩展变成
路线；在服务器模式下，相同的文件是您作为岛屿导入的组件 - 下的框架文件
`src/routes/` 在那里被拒绝。请参阅[服务器模式和客户端模式](../routing/fbr/modes.md)。

> [！注意]
> 在[CSR](../rendering/csr.md)模式下，只有框架路由文件是可导航的
> 客户端。

## 布局

目录中的 `layout.*` 包含其下面的页面。请参阅[布局](../routing/fbr/layouts/README.md)。

## 后续步骤

- [.nexy 文件](nexy/README.md)：Python + Jinja2 + 道具
- [Markdown 和 MDX](nexy/markdown.md)：内容页面
- [组件](nexy/components.md)：内置 HTML 帮助器