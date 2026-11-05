# Nexy 的工作原理

一页中的心理模型：Nexy 构建什么、Vite 构建什么以及浏览器中的文件和页面之间会发生什么。读一遍；文档的其余部分是一组详细信息。

## Nexy 架构

请求跨越五层：Uvicorn 接受它，中间件装饰它，路由器选择一个文件，渲染器将该文件转换为 HTML 或 JSON，如果页面有 JavaScript，则客户端层接管。 Nexy 拥有中间三名； Vite 并且您的框架拥有客户端；您的应用程序拥有数据、身份验证和授权。

每一层以及它拒绝执行的操作都在[架构](../architecture.md)中。对于 Nexy 本身的软件包，请参阅存储库根目录的 `ARCHITECTURE.md` - 它是为贡献者编写的。

## 应用程序生命周期

`nx dev` 在第一个请求之前做了六件事：

1. 验证 `nexyconfig.py`，并在无效配置上停止；
2. 确保项目的 Python 包是可导入的；
3. 解析端口，并删除过时的 `__nexy__/nexy.prod` 标记；
4. 并行生成客户端文件并编译路由；
5. 启动 Vite 并等待直到它回答；
6. 安装文件观察器，然后让 uvicorn 导入 `nexy.modules.routers.app:_server`。

该导入组装了应用程序 - 中间件、操作、路由器、错误处理程序 - 并且第一个请求由该程序集提供服务。当你保存时，观察者会重新启动 uvicorn；出现、消失或移动的页面也会重新生成客户端路由列表。

## 路由系统

`src/routes/` 下的路径通过四个规则成为 URL：

| 文件 | URL |
|---|---|
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/hello` |
| `blog/[...parts].nexy` | `/blog/a/b` |
| `(marketing)/about.nexy` | `/about` |

扩展名永远不会出现； `index` 是其文件夹的路径；括号中的文件夹将文件分组而不添加段。

当两个事物可以回答相同的 URL 时，**注册的第一个获胜**，并且 Nexy 始终按以下顺序注册：

1. 操作端点；
2. 静态文件：`/public`、`/assets`、`/favicon.ico`；
3. 模块化 `APIRouter` (`useRouter`)；
4. 文件路由，最具体的首先：静态路径，然后是具有最固定段的动态路径，然后是包罗万象的路径。

两个具有相同特异性的文件路由按字母路径顺序注册，因此 `[id].nexy` 在 `[slug].nexy` 之前回答。因此，模块化路由优于具有相同路径的页面。这是您可以信赖的优先顺序，而不是可使用的平局规则：给一个 URL 一个文件。

## 视图系统

文件的扩展名决定它是什么，项目配置决定哪些扩展名处于活动状态。

| 扩展 | 当 | 由 | 编译 充当 | 时有效
|---|---|---|---|
| `.nexy` | 服务器模式 | Nexy：frontmatter 变为 Python，标记变为 Jinja2 | 页面 |
| `.md` | 总是 | Nexy：GitHub 风格的 Markdown，标题 ID，目录 | 页面，在最近的布局 | 内
| `.mdx` | 始终 | Vite，其中 React 或 Preact | 为组件路由 |
| `.tsx` | `useFF` 是 React、Solid 或 Preact | Vite，框架 | 是组件路由 |
| `.vue` | `useFF` 是 Vue | Vite 和 Vue | 组件路由 |
| `.svelte` | `useFF` 是 Svelte | Vite 和 Svelte | 组件路由 |
| `.py` | 始终 | Python | API 处理程序：`GET`、`POST`、... 是方法 |

扩展名未激活的文件将被跳过并出现警告，且不会提供服务。在客户端模式下，`.nexy` 在服务器启动之前被拒绝。请参阅[文件约定](../reference/file-conventions.md)。

## 渲染生命周期

三个问题决定读者注意到的一切：

| 问题 | 答案 | 页 |
|---|---|---|
| 谁生成 HTML？ | 服务器，或客户端路由的浏览器 | [渲染](../rendering/README.md) |
| 什么时候读取数据？ | 在每个请求、每次重新生成或在浏览器中 | [SSR](../rendering/ssr.md)、[ISR](../rendering/isr.md) |
| JavaScript 什么时候到达？ | 仅适用于一个岛屿，或适用于整个文档 | [岛屿](../rendering/islands.md)、[CSR](../rendering/csr.md) |

在服务器模式下，服务器呈现每一页，`revalidate` 为每个 URL 缓存一页，岛将 JavaScript 添加到一个组件。在客户端模式下，第一个文档在 Node 中呈现，然后在浏览器中进行导航。

`__nexy__/` 保存生成的所有内容：编译页面、客户端条目、构建输出。永远不要编辑它，永远不要提交它；删除它以强制进行干净的构建。

## 前端集成

**Vite 不会取代 Nexy。** Vite 捆绑并提供客户端代码。它不路由请求、渲染 `.nexy` 页面、运行操作或拥有源。浏览器与一个源（Nexy 的）进行通信，并且在开发过程中，Nexy 通过它代理 Vite 的端点，因此无需配置 CORS。

**Nexy 不会取代 React。** Nexy 决定渲染哪个组件、何时渲染以及使用哪些 props；该框架拥有组件模型、反应性和生态系统。 `.nexy` 页面将组件作为孤岛导入；在客户端模式下，路由*是*一个组件。

对于组件路由，Python 仅写入指向该文件的瘦包装器模块。编译和服务器端渲染是 Vite的工作。

## 开发生产

| | `nx dev` | `nx build` 然后 `nx start` |
|---|---|---|
| 保存 | 时编译的页面 | 提前编译一次 |
| 客户端代码 | Vite 具有热重载功能的开发服务器，位于 `__nexy__/client/` 中的 Nexy 自己的源 | 捆绑包之后，预渲染 HTML |
| Node.js | 在 Python | 旁边运行，不需要服务 |
| 错误 | 覆盖在浏览器中，每个页面上的工具栏 | 没有详细信息的状态页面 |
| 始发地 | 1 个端口，`3000` | 1 个端口 |

不变的是：相同的路由规则，相同的页面文件，相同的 `nexyconfig.py`。两者之间行为不同的页面是错误，而不是模式。

## 更深入

- [项目结构](project-structure.md)：项目的每个文件夹
- [渲染](../rendering/README.md)：SSR、ISR、CSR和岛屿
- [前端](../guides/frontend.md)：Vite，样式和客户端构建
- [路由](../routing/README.md)：基于文件的、模块化的和自定义的路由器
