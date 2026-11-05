# 渲染

渲染回答了一个问题：**谁生成 HTML，以及何时生成**。 Nexy 有四个答案和一个默认答案。

**没有把握？保留 SSR。** 仅当您能说出原因时才更改页面：很少更改的内容 (ISR)、需要浏览器的一个小部件（孤岛）或类似应用程序的导航 (CSR)。

## 它是如何运作的

```diagram filename="谁生成 HTML 以及何时生成"
SSR       request ──► server renders ────────────────► HTML ──► browser
ISR       request ──► cached HTML? ──► browser, regenerated in the background
CSR       request ──► document rendered by the server ──► browser takes over navigation
Islands   request ──► server renders the page ──► one widget hydrates on demand
```

## 四种模式

| | 潜艇监视监视 | 情报监视监视 | 企业监视监视 | 岛屿 |
|---|---|---|---|---|
| 每次请求 | 时，浏览器中的每次重新生成 | 时 | 都会读取数据 |，每次请求 |
| HTML 来自 | 服务器 | 服务器，然后是第一个文档的缓存 | 服务器，然后是浏览器 | 服务器 |
| JavaScript | 仅适用于岛屿 | 仅适用于岛屿 | 框架捆绑 | 仅适用于岛屿 |
| 水合作用 | 无 | 无 | 整个文档 | 岛屿 |
| 每个 URL 缓存 | 无 |，在内存中 | 无 | 无 |
| 由组件 | 上项目 | `directive` 页面 | `useCSR = True` 中的 | 默认 | `revalidate = N` 决定
| 谷物 | 页 | 页 | **项目** | 组件 |

## 渲染生命周期

有两个事实可以解释最令人惊讶的事情。

1. **项目处于一种模式。** `useCSR` 在服务器模式（SSR、ISR、岛屿、`.nexy`、`.md`、`.mdx` 路由）和客户端模式（框架路由和客户端路由器）之间进行选择。两者不能混合：参见[服务器模式和客户端模式](../routing/fbr/modes.md)。
2. **在服务器模式中，该模式是每页。** 一个页面可以使用 `revalidate`进行缓存，另一个可以容纳一个岛，第三个则两者都不能。

客户端模式仍然发送真实的文档：Nexy 在 Node 中呈现它作为第一个响应，然后浏览器接管导航。 CSR 页面不是等待捆绑的空白页面。

## 何时使用

- **内容、营销、文档**：SSR，当内容很少更改时加上 ISR。
- **带有一个交互式小部件的大部分静态页面**：带有岛屿的 SSR。
- **仪表板、编辑器、类似应用程序的导航**：CSR。
- **不断读取且很少更改的页面**：ISR。

## 配置

| 模式 | 其中 |
|---|---|
| SSR | 无处：它是默认的 |
| ISR | `revalidate = 60` 位于 `.nexy` 页 | 的 frontmatter
| CSR | `useCSR = True` 在 `nexyconfig.py` 中，`useFF` 设置为 |
| 组件标签 | 上的岛屿 | `directive="client:visible"`

## 示例

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

没有 frontmatter 行的同一页面是 SSR。

## 局限性

- **没有 SSG 模式。** Nexy 在构建时预渲染 HTML（组件 HTML、客户端文档），但始终通过服务器读回：没有导出命令，没有静态托管的独立文件夹。对于冻结的内容，请使用具有长窗口的 ISR。
- **ISR 不是 CDN。** 缓存存在于呈现页面的进程中；几个工作人员保留多个缓存。参见[ISR](isr.md)。
- **CSR 是一项项目决策。** 您不能制作一页 CSR 并保留其余的 SSR。
- **岛屿为岛屿提供水分，而不是页面。** 岛屿相互依赖的页面是变相的 CSR 页面。

## 后续步骤

- [SSR](ssr.md)：默认
- [ISR](isr.md)：为每个 URL 缓存一个页面
- [CSR](csr.md)：手动导航到浏览器
- [岛屿](islands.md)：水合一个小部件
- [性能](../deployment/performance.md)
