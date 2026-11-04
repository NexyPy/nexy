# Nexy 的工作原理

一页中的思维模型：Nexy 构建的内容、Vite 构建的内容以及文件之间发生的情况
以及浏览器中的一个页面。读一遍； the rest of the documentation is then a set of details.

## Nexy 架构

一个请求跨越五层：Uvicorn接受它，中间件装饰它，路由器选择一个文件，
the renderer turns that file into HTML or JSON, and the client layer takes over if the page has
JavaScript。 Nexy 拥有中间三名； Vite 和你的框架拥有客户端；你的申请
拥有数据、认证和授权。

每一层及其拒绝执行的操作都在[架构](../architecture.md)中。对于以下包
Nexy 本身，请参阅存储库根目录的 `ARCHITECTURE.md` - 它是为贡献者编写的。

## 应用程序生命周期

`nx dev` 在第一个请求之前做了六件事：

1. 验证`nexyconfig.py`，并在无效配置上停止；
2. 确保项目的Python包是可导入的；
3. resolves the ports, and deletes the stale `__nexy__/nexy.prod` marker;
4. generates the client files and compiles the routes, in parallel;
5. 启动Vite并等待其应答；
6. 安装文件观察器，然后让 uvicorn 导入 `nexy.modules.routers.app:_server`。

该导入组装了应用程序 - 中间件、操作、路由器、错误处理程序 - 以及
第一个请求由该大会满足。当你保存时，观察者会重新启动 uvicorn；一个页面
出现、消失或移动也会重新生成客户端路由列表。

## 路由系统

`src/routes/` 下的路径通过四个规则成为 URL：

| 文件 | URL |
|---|---|
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/hello` |
| `blog/[...parts].nexy` | `/blog/a/b` |
| `(marketing)/about.nexy` | `/about` |

扩展名永远不会出现； `index`是其文件夹的路径；括号组中的文件夹
文件而不添加段。

当两个事物可以回答相同的 URL 时，**注册的第一个获胜**，并且 Nexy 始终
按此顺序注册：

1. 操作端点；
2. 静态文件：`/public`、`/assets`、`/favicon.ico`；
3. 模块化`APIRouter`（`useRouter`）；
4. 文件路由，最具体的首先：静态路径，然后是具有最多固定段的动态路径，
   然后包罗万象。

两个具有相同特异性的文件路由按字母路径顺序注册，因此 `[id].nexy`
在`[slug].nexy`之前回答。因此，模块化路由优于具有相同路径的页面。这是一个
您可以依赖的优先顺序，而不是可使用的平局规则：给一个 URL 一个文件。

## 视图系统

文件的扩展名决定它是什么，项目配置决定哪些扩展名
活跃。

| 扩展 | 当 | 由 | 编译并充当 | 时有效
|---|---|---|---|
| `.nexy` | 服务器模式 | Nexy：frontmatter 变为 Python，标记变为 Jinja2 | 页面 |
| `.md` | always | Nexy: GitHub-flavoured Markdown, heading ids, table of contents | a page, inside the nearest layout |
| `.mdx` | 总是 | Vite，使用 React 或 Preact | 组件路由 |
| `.tsx` | `useFF` 是 React、Solid 或 Preact | Vite 和框架 | 组件路由 |
| `.vue` | `useFF` 是 Vue | Vite 和 Vue | 组件路由 |
| `.svelte` | `useFF` 是 Svelte | Vite 和 Svelte | 组件路由 |
| `.py` | 始终 | Python | API 处理程序：`GET`、`POST`、... 是方法 |

扩展名未激活的文件将被跳过并出现警告，且不会提供服务。在客户端模式下，`.nexy`
在服务器启动之前被拒绝。请参阅[文件约定](../reference/file-conventions.md)。

## 渲染生命周期

三个问题决定读者注意到的一切：

|问题|答案|页|
|---|---|---|
| 谁生成 HTML？ | 服务器，或客户端路由的浏览器 | [渲染](../rendering/README.md) |
|什么时候读取数据？ | 在每个请求、每次重新生成或在浏览器中 | [SSR](../rendering/ssr.md)、[ISR](../rendering/isr.md) |
| JavaScript什么时候到来？ | 仅适用于一个岛屿，或适用于整个文档 | [岛屿](../rendering/islands.md)、[CSR](../rendering/csr.md) |

在服务器模式下，服务器呈现每个页面，`revalidate` 为每个 URL 缓存一个页面，并添加岛屿
JavaScript 到一个组件。在客户端模式下，第一个文档在节点和导航中呈现
然后发生在浏览器中。

`__nexy__/` 保存生成的所有内容：编译页面、客户端条目、构建输出。从来没有
编辑它，永远不要提交它；删除它以强制进行干净的构建。

## 前端集成

**Vite 不会取代 Nexy。** Vite 捆绑并提供客户端代码。它不路由请求，
渲染 `.nexy` 页面、运行操作或拥有源。浏览器与一个来源对话 - Nexy 的 -
在开发过程中，Nexy 通过它代理 Vite 的端点，因此无需配置 CORS。

**Nexy 不会取代 React。** Nexy 决定渲染哪个组件、何时渲染以及使用哪些 props；
该框架拥有组件模型、反应性和生态系统。 `.nexy` 页面导入
组件作为一个岛；在客户端模式下，路由*是*一个组件。

对于组件路由，Python 只编写一个指向该文件的薄包装模块。的
编译和服务端渲染是Vite的工作。

## 开发与生产

| | `nx dev` | `nx build` 然后 `nx start` |
|---|---|---|
| 页面 | 在您保存 | 时编译，提前编译一次 |
| 客户端代码 | 具有热重载功能的 Vite 开发服务器，位于 Nexy 自己的起源 | 捆绑在 `__nexy__/client/` 中，预渲染 HTML |
| Node.js | 与 Python | 一起运行，不需要提供服务 |
| 错误 | 覆盖在浏览器中，每个页面上都有工具栏 | 没有详细信息的状态页面 |
| 原点 | 1 个端口，`3000` | 1 个端口 |

不变的是：相同的路由规则，相同的页面文件，相同的`nexyconfig.py`。一页
两者之间的行为不同是一个错误，而不是一种模式。

## 更深入

- [项目结构](project-structure.md)：项目的每个文件夹
- [渲染](../rendering/README.md)：SSR、ISR、CSR和岛屿
- [前端](../guides/frontend.md)：Vite、样式和客户端构建
- [路由](../routing/README.md)：基于文件的、模块化的和自定义的路由器