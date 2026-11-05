# 布局

布局将每个页面包裹在其目录下。布局嵌套：页面在其目录的布局内呈现，该目录的布局在父目录的布局内呈现，直到根布局。

每种布局文件类型都有一页：

| 文件 | 模式 | 拥有 HTML 文档 | 页面 |
|---|---|---|---|
| `layout.nexy` | 服务器 (`useCSR = False`) | 是，在根 | [layout.nexy](../../../views/nexy/layouts.md) |
| `layout.tsx` | 客户端 (`useCSR = True`) | 是，在根 (React、Solid、Preact) | [React](../../../views/react/differences.md)、[Solid](../../../views/solid/differences.md)、[Preact](../../../views/preact/differences.md) |
| `layout.vue` | 客户端 | 是的，在根 | [layout.vue](../../../views/vue/differences.md) |
| `layout.svelte` | 客户端 | 是的，在根 | [layout.svelte](../../../views/svelte/differences.md) |

一个项目使用一个家庭。 `layout.nexy` 和 `layout.tsx` 不能存在于同一个项目中：服务器模式具有 `.nexy` 布局，客户端模式具有框架布局。请参阅[服务器模式和客户端模式](../modes.md)。

## 浏览器如何接管文档

在客户端模式下，Nexy 在 Node 中渲染根布局，因此第一个响应是一个完整的文档。然后浏览器通过以下两种方式之一接管它：

| 框架 | 接管 | 含义 |
|---|---|---|
| 整个文档的 React、Solid | **水合** | 服务器 HTML 按原样重用 |
| Preact、Vue、Svelte | **主体接管** | 框架构建页面主体并将其替换为服务器发送的页面主体 |

Preact、Vue 和 Svelte 无法水合整个文档：Preact 的 `hydrate` 构建第二个 `<html>` 元素，Vue 的编译器从客户端模板中删除 `<script>`，并且 Svelte 无法在浏览器中创建 `<html>`、`<head>` 或 `<body>`。因此，对于它们来说，`<html>`、`<head>` 和 `<body>` 属性是服务器发送的属性，只有主体是由浏览器构建的。在实践中：

- 将标题、元标记、字体和主题脚本放在根布局中：它们由服务器呈现并保持原样。
- `<html>`、`<head>` 或 `<body>`（例如反应类）上的绑定由服务器应用，但不会在浏览器中更新。从脚本中更改它们，就像主题脚本一样。
- 浏览器从头开始渲染主体，而不是重用服务器标记，因此主体在与第一次渲染相同的任务中被替换一次。

## 根布局

根布局是 `src/routes/layout.<ext>`。它由 `nx new` 创建，并且是唯一写入 `<!DOCTYPE html>`、`<html>`、`<head>` 和 `<body>`（每个框架和 `.nexy`）的地方。页面和嵌套布局永远不会重复。

```text
src/routes/
├─ layout.*              root: the document
├─ index.*
└─ dashboard/
   ├─ layout.*           nested: UI only
   ├─ index.*
   └─ settings.*
```

`dashboard/index` 呈现为 `root layout > dashboard layout > page`。

## 路由组

括号中的目录可以有自己的布局，而无需更改 URL：

```text
src/routes/
├─ layout.nexy
├─ (marketing)/
│  ├─ layout.nexy        wraps /pricing and /about only
│  ├─ pricing.nexy
│  └─ about.nexy
└─ (app)/
   └─ dashboard.nexy     only the root layout
```

## 坚持

在客户端模式下，当用户在共享布局的页面之间导航时，布局保持安装状态：保留其 DOM、状态和滚动位置。在服务器模式下，每个导航都是一个新文档。

## 后续步骤

- [布局.nexy](../../../views/nexy/layouts.md)
- [布局.tsx](../../../views/react/differences.md)
- [继承](../inheritance.md)
