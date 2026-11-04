# CSR（客户端渲染）

## 定义

CSR 将导航交给浏览器：第一个文档之后，页面之间的移动不再需要
HTML 服务器。在 Nexy 中，这是一个 ** 项目 ** 的决定，而不是一页 - `useCSR = True` 变成了
整个应用程序由客户端路由。

## 它是如何工作的

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

然后该项目改变形状：

| | 服务器模式 (`False`) | 客户端模式 (`True`) |
|---|---|---|
| 路线 | `.nexy`、`.md`、`.mdx` | `.tsx`、`.jsx`、`.vue`、`.svelte` |
| 文档 | `layout.nexy` | 根 `layout.tsx` / `.vue` / `.svelte` 拥有 `<html>`、`<head>`、`<body>` |
| 客户端组件 | 页面内的岛屿 | 页面本身 |
| `.nexy` 在 `src/routes/` | 下，页面格式 | 在 `nx dev`、`nx start` 和 `nx build` | 之前被拒绝
| 导航 | 每个链接的完整请求 | 客户端路由器 |

`.md` 和 `.mdx` 保持有效：Nexy 将它们呈现在客户端布局内的服务器上，并且
客户端路由器从那里接管。 `.py` 处理程序位于路由旁边并由 FastAPI 提供服务。

## 渲染生命周期

1. 请求到达基于文件的路由器，该路由器找到匹配的路由及其布局。
2. 根布局在 Node 中渲染 **整个文档 ** - 第一个响应已经携带
   真正的`<html>`，而不是一个空壳。
3. Nexy 在 `</body>` 之前注入客户端资产和页面的 JSON 描述。
4. 浏览器会对该文档进行水合。嵌套布局从那时起就保持其状态。
5. 到另一个路由的链接由客户端路由器处理：没有文档请求，页面是
   在浏览器中呈现。

在开发过程中，文档由 Vite 开发服务器按需渲染。在生产中是
在构建时渲染一次：静态路由获取其文档，动态路由每个声明获取一个文档
静态参数，或外壳 - 空页面周围的布局 - 当它声明无时。

## 何时使用

- 仪表板、编辑器、任何行为类似于应用程序的东西。
- 一个Python API，顶部有一个客户端应用程序。
- 在这个页面中，每次交互都是本地的，并且会感觉到往返。

## 配置

| 设置 | 值 |
|---|---|
| `useFF` | 必需：`useCSR` 没有客户端框架会被拒绝 |
| `useCSR` | `True` |
| `useRouter` | 必须保持关闭状态：模块化路由器在客户端模式下被拒绝 |

这些检查将忽略以 `_` 或 `.` 开头的文件和文件夹。

## 示例

```tsx filename="src/routes/layout.tsx"
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head><title>My app</title></head>
      <body>{children}</body>
    </html>
  )
}
```

```tsx filename="src/routes/index.tsx"
export default function Home() {
  return <h1>Home</h1>
}
```

## 局限性

- **整个项目。** 您不能将一个 CSR 页面混合到服务器模式项目中：选择以下模式：
  应用程序，然后使用 [islands](islands.md) 作为服务器模式页面的交互部分。
- **没有`.nexy`路由。**你在`.nexy`中编写的任何内容都必须成为框架组件。
- **服务器数据通过端点。**客户端路由无法在渲染时读取数据库；它
  调用 `.py` 处理程序或 [Action](../guides/actions.md)。
- **动态路由需要声明的静态参数，或者从 shell 启动。** 导出
  页面中的 `getStaticParams()` - Next.js 名称 `getStaticPaths` 和 `generateStaticParams`
  也被接受 - 每个值有一个文档。没有它，外壳会承载布局和
  不是页面：浏览器运行后就会出现页面。
- **CSR不是空白页，也不是SPA。**第一个文档由服务器呈现；它
  是在浏览器中发生的导航。

## 后续步骤

- [服务器模式和客户端模式](../routing/fbr/modes.md)：检查和拒绝的文件
- [布局](../routing/fbr/layouts/README.md)：哪个文件拥有该文档
- [SSR](ssr.md)：默认，逐页
- [Frontend](../guides/frontend.md)：开发服务器和客户端构建