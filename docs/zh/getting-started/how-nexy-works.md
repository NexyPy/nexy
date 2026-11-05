# Nexy 的工作原理

您编写的文件和浏览器中的页面之间会发生什么：请求跨越的层、谁构建什么以及 Nexy 留给您的应用程序什么。您不需要此页面即可启动；它稍后回答了“为什么它会那样工作”的问题。

## 各层

```diagram filename="一个请求，五层"
Browser
   │
   ▼
Uvicorn ───── ASGI transport
   │
   ▼
Middleware ── sessions, CORS, gzip, trusted hosts, your own
   │
   ▼
Router ────── FBR | Modular | Custom ── picks the file that answers
   │
   ▼
Renderer ──── HTML (Jinja2, Markdown, Node) or JSON
   │
   ▼
Response
```

| 图层 | 责任 | 不 |
|---|---|---|
| Uvicorn | 接受连接，说出 ASGI | 知道什么是页面 |
| 中间件 | 修饰请求：会话、CORS、gzip、受信任的主机、HTTPS 重定向、您的 | 选择路线 |
| 路由器 | 将 URL 与文件及其布局、依赖项和错误页面相匹配 | 产生内容 |
| 渲染器 | 运行页面并将其结果转换为 HTML 或 JSON | 获取你的数据 |
| 客户 | Vite 和你的框架：捆绑、水合作用、客户端导航 | 应答服务器请求 |

## 谁建造什么

| 演员 | 拥有 | 不拥有 |
|---|---|---|
| 内克西 | 路由、服务器渲染、操作、`.nexy` 编译、同源 | 成分、反应性、数据 |
| Vite | 客户端捆绑包、开发服务器、热重载 | 路由、服务器渲染、动作 |
| 你的框架 | 成分、反应性、生态系统 | 路由、文档（Nexy 询问其布局） |
| 您的申请 | 数据、认证、授权、业务规则 | 运输、渲染 |

表背后的规则：**Nexy 构建它拥有的内容，并且从不编译 Vite 编译的内容。**

## 路由系统

`src/routes/` 下的路径通过四个规则成为 URL：

| 文件 | 网址 |
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

| 扩展 | 活跃时 | 编译者 | 担任 |
|---|---|---|---|
| `.nexy` | 服务器模式 | Nexy：frontmatter 变为 Python，标记变为 Jinja2 | 一页 |
| `.md` | 总是 | Nexy：GitHub 风格的 Markdown、标题 ID、目录 | 一个页面，位于最近的布局内 |
| `.mdx` | 总是 | Vite，与 React 或 Preact | 组件路径 |
| `.tsx` | `useFF` 是 React、Solid 或 Preact | Vite 和框架 | 组件路径 |
| `.vue` | `useFF` 是 Vue | Vite 和 Vue | 组件路径 |
| `.svelte` | `useFF` 是 Svelte | Vite 和 Svelte | 组件路径 |
| `.py` | 总是 | Python | API 处理程序：`GET`、`POST`、... 是方法 |

扩展名未激活的文件将被跳过并出现警告，且不会提供服务。在客户端模式下，`.nexy` 在服务器启动之前被拒绝。请参阅[文件约定](../reference/file-conventions.md)。

## 渲染生命周期

三个问题决定读者注意到的一切：

| 问题 | 回答 | 页面 |
|---|---|---|
| 谁生成 HTML？ | 服务器或客户端路由的浏览器 | [渲染](../rendering/README.md) |
| 什么时候读取数据？ | 在每个请求、每次重新生成或在浏览器中 | [SSR](../rendering/ssr.md)，[ISR](../rendering/isr.md) |
| JavaScript 什么时候到达？ | 仅针对一个岛屿，或针对整个文档 | [岛屿](../rendering/islands.md)，[企业社会责任](../rendering/csr.md) |

在服务器模式下，服务器呈现每一页，`revalidate` 为每个 URL 缓存一页，岛将 JavaScript 添加到一个组件。在客户端模式下，第一个文档在 Node 中呈现，然后在浏览器中进行导航。

`__nexy__/` 保存生成的所有内容：编译页面、客户端条目、构建输出。永远不要编辑它，永远不要提交它；删除它以强制进行干净的构建。

## 前端集成

**Vite 不会取代 Nexy。** Vite 捆绑并提供客户端代码。它不路由请求、渲染 `.nexy` 页面、运行操作或拥有源。浏览器与一个源（Nexy 的）进行通信，并且在开发过程中，Nexy 通过它代理 Vite 的端点，因此无需配置 CORS。

**Nexy 不会取代 React。** Nexy 决定渲染哪个组件、何时渲染以及使用哪些 props；该框架拥有组件模型、反应性和生态系统。 `.nexy` 页面将组件作为孤岛导入；在客户端模式下，路由*是*一个组件。

对于组件路由，Python 仅写入指向该文件的瘦包装器模块。编译和服务器端渲染是 Vite的工作。

## 开发生产

`nx dev` 检查 `nexyconfig.py`，编译页面，当项目有前端框架时启动 Vite，并在保存时重新启动服务器。 `nx build` 提前执行一次相同的工作，并且 `nx start` 提供结果。

| | `nx dev` | `nx build` 然后 `nx start` |
|---|---|---|
| 页数 | 保存时编译 | 提前编译一次 |
| 客户端代码 | Vite 具有热重载功能的开发服务器，位于 Nexy 自己的起源之后 | 捆绑在 `__nexy__/client/` 中，预渲染 HTML |
| Node.js | 在 Python 旁边运行 | 不需要服务 |
| 错误 | 覆盖在浏览器中，每个页面上的工具栏 | 没有详细信息的状态页面 |
| 产地 | 一个端口，`3000` | 一个端口 |

不变的是：相同的路由规则，相同的页面文件，相同的 `nexyconfig.py`。两者之间行为不同的页面是错误，而不是模式。

## Nexy 留给你什么

Nexy 故意停在您的应用程序边缘：

| 关注 | Nexy 提供什么 | 你写的是什么 |
|---|---|---|
| 认证 | 会话中间件，`AuthenticationMiddleware` 启用时 | 登录、用户查找、cookie 策略 |
| 授权 | `dependencies.py`，守卫，每个文件夹继承 | 规则本身 |
| 数据库 | 没有自己的 ORM； `nx new` 可以支架 SQLModel、SQLAlchemy 或 Tortoise、`nx migrate` 运行 Alembic 或 Aerich | 模型和查询（[数据库](../guides/databases.md)） |
| 国际化 | 您的页面没有任何内容；仅翻译 CLI | 库和消息 ([i18n](../guides/i18n.md)) |
| 后台工作 | 无：没有队列，没有调度程序 | 一个工作进程 |
| 电子邮件、付款、搜索 | 什么都没有 | 您选择的服务 |

对于所有六个来说，原因都是相同的：选择 ORM 或身份验证库的框架决定只有您的应用程序才能决定的事情。成本是明确的：没有为您接线，表中链接的指南说明了每个插头的插入位置。

## 后续步骤

- [项目结构](project-structure.md)：每个部分都位于项目中
- [路由](../routing/README.md)：基于文件的、模块化的和自定义的路由器
- [渲染](../rendering/README.md)：SSR、ISR、CSR和岛屿
- [前端](../guides/frontend.md)：Vite，样式和客户端构建
