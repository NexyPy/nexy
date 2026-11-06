# 前端布局

**布局** 是一个包装器，它定义一个或多个页面的共享结构。布局通过保留状态并避免在导航期间重新加载整页来实现“类似应用程序”的体验。

## 嵌套逻辑

布局遵循基于 `src/routes/` 下目录树的分层结构。

1.  **根布局**：每个项目都有一个根布局（例如 `src/routes/layout.nexy`）。这是负责定义文档外壳的唯一布局：`<html>`、`<head>` 和 `<body>`。
2.  **嵌套布局**：任何文件夹都可以包含自己的 `layout.*` 文件。此布局包含该文件夹内的所有页面和子布局。
3.  **继承**：页面由从根目录到其自己的文件夹的所有布局包裹。

```text
src/routes/
├─ layout.tsx            root: <html>, <head>, <body>
├─ index.tsx             root > page
└─ dashboard/
   ├─ layout.tsx         nested: the dashboard menu
   └─ settings.tsx       root > dashboard > page
```

嵌套布局仅绘制 UI 的一部分，并将页面放置在 `children` 所在的位置：

```tsx filename="src/routes/dashboard/layout.tsx"
import type { ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="dashboard">
      <nav>Dashboard</nav>
      <main>{children}</main>
    </div>
  );
}
```

## 共享状态和组合

布局设计得稳定。在客户端模式下，当在共享相同布局的两个页面之间导航时，布局 **不会** 重新渲染；只有子内容发生变化。在服务器模式下，每个导航都是一个新文档。

- **Slots**：布局提供了一个插入嵌套页面的槽：JSX 中的 `children`，以及 `.nexy` 布局中的 `children` 属性。
- **状态保留**：由于布局保持安装状态，因此在导航期间保留其中的任何状态（例如，标题中的搜索查询）。

`.nexy` 布局中的相同插槽：

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children }}</body>
</html>
```

下面的搜索字段保留用户在仪表板页面之间移动时输入的内容，因为保存它的布局永远不会卸载：

```tsx filename="src/routes/dashboard/layout.tsx"
import { useState, type ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const [query, setQuery] = useState("");
  return (
    <>
      <input value={query} onChange={(event) => setQuery(event.target.value)} />
      {children}
    </>
  );
}
```

## 静态约束

对于预渲染 (SSG) 的路由，根布局不能依赖于请求时数据，例如 cookie 或标头。它必须表示为客户端随后水合的静态外壳。

相反，在静态 shell 的脚本中从浏览器读取主题：

```tsx filename="src/routes/layout.tsx"
import type { ReactNode } from "react";

const theme = `document.documentElement.dataset.theme =
  localStorage.getItem("theme") ?? "light";`;

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <head>
        <script dangerouslySetInnerHTML={{ __html: theme }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

## 框架实施

槽和嵌套的实现因框架而略有不同。请参阅您选择的技术的 **差异** 指南：

- [React 差异](../react/differences.md)
- [Vue 差异](../vue/differences.md)
- [Svelte 差异](../svelte/differences.md)
- [Solid 差异](../solid/differences.md)
- [Preact 差异](../preact/differences.md)
