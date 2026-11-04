# 渲染

渲染回答了一个问题：**谁生成 HTML，以及何时生成**。 Nexy 有四个答案和一个
默认。

**不确定？保留 SSR。** 仅当您能说出原因时才更改页面：很少更改的内容
（ISR），一种需要浏览器（岛）或类似应用程序的导航（CSR）的小部件。

## 它是如何工作的

```diagram filename="谁生成 HTML 以及何时生成"
SSR       request ──► server renders ────────────────► HTML ──► browser
ISR       request ──► cached HTML? ──► browser, regenerated in the background
CSR       request ──► document rendered by the server ──► browser takes over navigation
Islands   request ──► server renders the page ──► one widget hydrates on demand
```

## 四种模式

| | 苏维埃侦察 | 情监侦 | 企业社会责任 | 岛屿 |
|---|---|---|---|---|
| 每次请求时 | 读取数据 | 每次重新生成 | 时在浏览器中 | 每次请求 |
| HTML 来自 | 服务器 | 服务器，然后是第一个文档的缓存 | 服务器，然后是浏览器 | 服务器 |
| JavaScript | 仅适用于岛屿 | 仅适用于岛屿 | 框架包 | 仅适用于岛屿 |
| 水合 | 无 | 无 | 整个文档 | 岛屿 |
| 每个 URL 缓存 | 无 |，在内存中 | 无 | 无 |
| 由组件 | 上项目 | `directive` 页面 | `useCSR = True` 中的 | 默认值 | `revalidate = N` 决定
| 谷物 | 页 | 页 | ** 项目 ** | 组件 |

## 渲染生命周期

有两个事实可以解释最令人惊讶的事情。

1. **项目处于一种模式。**`useCSR`在服务器模式之间进行选择（SSR、ISR、岛屿、`.nexy`、
   `.md`、`.mdx` 路由）和客户端模式（框架路由和客户端路由器）。两者不可兼得
   混合：参见[服务器模式和客户端模式](../routing/fbr/modes.md)。
2. **在服务器模式下，该模式是每页。**一个页面可以用`revalidate`缓存，另一个页面可以缓存
   可以守住一座岛，但第三个岛却两样都做不到。

客户端模式仍然发送一个真实的文档：Nexy 在 Node 中渲染它作为第一个响应，然后
浏览器接管导航。 CSR 页面不是等待捆绑的空白页面。

## 何时使用

- **内容、营销、文档**：SSR，当内容很少更改时加上 ISR。
- **一个主要是静态的页面，带有一个交互式小部件**：带有一个岛的 SSR。
- **仪表板、编辑器、类似应用程序的导航**：CSR。
- **不断读取且很少更改的页面**：ISR。

## 配置

| 模式 | 其中 |
|---|---|
| SSR | 无处：它是默认的 |
| ISR | `revalidate = 60` 在 `.nexy` 页 | 的前面
| CSR | `useCSR = True` 在 `nexyconfig.py` 中，`useFF` 设置为 |
组件标签 | 上的 | 岛屿 | `directive="client:visible"`

## 示例

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

没有 frontmatter 行的同一页面是 SSR。

## 限制

- **没有 SSG 模式。** Nexy 在构建时预渲染 HTML（组件 HTML、客户端文档），
  但总是通过服务器读回它：没有导出命令，没有独立的文件夹来托管
  静态地。对于冻结的内容，请使用具有长窗口的 ISR。
- **ISR 不是 CDN。** 缓存存在于呈现页面的进程中；几名工人保留
  几个缓存。参见[ISR](isr.md)。
- **CSR 是一项项目决策。** 您不能制作一页 CSR 并保留其余的 SSR。
- **岛屿为岛屿提供水合物，而不是页面。** 岛屿全部相互依赖的页面是一个
  伪装的 CSR 页面。

## 后续步骤

- [SSR](ssr.md)：默认值
- [ISR](isr.md)：为每个 URL 缓存一个页面
- [CSR](csr.md)：手动导航到浏览器
- [岛屿](islands.md)：为一个小部件提供水合物
- [性能](../deployment/performance.md)