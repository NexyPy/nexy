# Nexy 文档

**用于全栈 Web 应用程序的 Python 框架。**

Nexy 将您的页面和 API 放在一个 Python 项目中，由一台服务器提供服务。版本 2.2 构建于 FastAPI 之上：每个 API 路由都是 FastAPI 路由，列在 Scalar 在 `/docs` 中显示的 OpenAPI 模式中。

- **Python 首先。** 页面、端点、表单和操作是 Python，页面不需要 JavaScript。
- **当您需要一个前端时，可以使用它。** React、Vue、Svelte、Solid 或 Preact，适用于一个组件或整个站点。
- **一个文件，一个 URL。** `src/routes/` 下的文件是一个路由：`.nexy` 是一个页面，`.py` 是一个 API 端点。
- **成长空间。** 从一个文件开始；当项目增长时，移动到模块，或插入现有的 FastAPI 路由器。

新来的？请阅读[什么是 Nexy？](getting-started/what-is-nexy.md)，然后阅读[快速入门](getting-started/quick-start.md)。

## 开始使用

### 第一步
| 页面 | 你会做什么 |
|---|---|
| [Nexy是什么？](getting-started/what-is-nexy.md) | 了解 Nexy 是什么、它的构建基础以及您能获得什么 |
| [安装](getting-started/installation.md) | 安装 uv 和 Nexy CLI，然后创建您的第一个项目 |
| [快速启动](getting-started/quick-start.md) | 创建一个项目，通过实时重新加载运行它，并构建它以用于生产 |
| [教程](getting-started/tutorial.md) | 一步一步构建一个笔记应用程序，一次一个可运行的部分 |

### 了解模型
| 页面 | 你会做什么 |
|---|---|
| [核心概念](getting-started/core-concepts.md) | 获取心智模型：路由、页面、视图、组件、处理程序、端点 |
| [项目结构](getting-started/project-structure.md) | 了解项目中每个文件夹和文件的用途 |
| [选择路由器](routing/README.md) | 选择基于文件的、模块化的或自定义的路由器 |
| [选择视图格式](views/README.md) | 为页面选择 `.nexy`、Markdown 或客户端框架 |

## 教程

### 第一单元：基础知识
| 页面 | 你将构建什么 |
|---|---|
| [1.创建项目](tutorial/create-the-project.md) | 创建notes项目并在浏览器中运行 |
| [2. 页面和布局](tutorial/pages-and-layouts.md) | 添加注释页面并更改其周围的布局 |
| [3.动态路由和API](tutorial/dynamic-routes.md) | 为每个笔记提供一个 URL 并将笔记作为 JSON 提供 |
| [4. 组件](tutorial/components.md) | 将每个音符变成可重复使用的 `.nexy` 组件 |

### 第二单元：数据
| 页面 | 你将构建什么 |
|---|---|
| [5. 将笔记存储在 SQLite](tutorial/store-the-notes.md) 中 | 添加模型、迁移和种子，并从数据库中读取注释 |
| [6. 从表单创建注释](tutorial/create-a-note.md) | 将表单发布到保存注释的操作 |
| [7. 显示验证错误](tutorial/validation-errors.md) | 拒绝空白便条并在表格上方说明原因 |
| [8.编辑和删除注释](tutorial/edit-and-delete.md) | 添加更改和删除注释的表单 |
| [9. 对笔记进行分页](tutorial/paginate-the-notes.md) | 一次显示五个注释，并在页面之间提供链接 |

### 第三单元：用户
| 页面 | 你将构建什么 |
|---|---|
| [10. 创建帐户并登录](tutorial/accounts.md) | 使用会话 cookie 进行注册、登录和退出 |
| [11. 给每个用户自己的注释](tutorial/own-notes.md) | 将每个注释与其用户联系起来并保护页面、操作和 API |
| [12. 通过电子邮件重置忘记的密码](tutorial/password-reset.md) | 通过电子邮件发送签名链接，一次有效，有效期一小时 |

### 第四单元：互动性
| 页面 | 你将构建什么 |
|---|---|
| [13. 键入时搜索笔记](tutorial/search-the-notes.md) | 使用 React 岛过滤浏览器中的每个注释 |
| [14. 勾选注释而不重新加载页面](tutorial/tick-a-note.md) | 用几行 JavaScript 发送到位的表格标记已完成的注释 |

## 路由

### 基于文件的 {fbr}
| 页面 | 你会做什么 |
|---|---|
| [基于文件的路由](routing/fbr/README.md) | 将文件路径转换为 URL |
| [页数](routing/fbr/pages/README.md) | 写一页 |
| [动态路线](routing/fbr/pages/dynamic-routes.md) | 使用 `[slug]`、`[...path]` 和路由组 |
| [页面元数据](routing/fbr/pages/metadata.md) | 设置页面的标题、描述和共享图像 {new} |
| [布局](routing/fbr/layouts/README.md) | 在页面之间共享框架 |
| [继承](routing/fbr/inheritance.md) | 读取布局、依赖关系和错误页面的解析顺序 |
| [服务器模式和客户端模式](routing/fbr/modes.md) | `useCSR`，以及每种模式允许的内容 |
| [链接和导航](routing/fbr/navigation/linking-and-navigating.md) | 链接页面、在客户端上导航、预取 |
| [挂钩](routing/fbr/navigation/hooks.md) | 读取路径、查询、cookie 和会话 |

### 处理程序和错误 {fbr}
| 页面 | 你会做什么 |
|---|---|
| [路由处理程序](routing/fbr/handlers/README.md) | 添加 Python 端点 |
| [验证和错误](routing/fbr/handlers/validation-and-errors.md) | 回答 `422` 和 `404`，并提出 `HTTPException` |
| [WebSocket 处理程序](routing/fbr/realtime/websocket.md) | 处理 `SOCKET` 连接 |
| [依赖项和守卫](routing/fbr/dependencies/README.md) | 在处理程序之前运行 `dependencies.py` 并继承它 |
| [中间件文件](routing/fbr/middleware/README.md) | 用 `middleware.py` 包装请求，由目录继承 |
| [错误页面](routing/fbr/errors/README.md) | 回答 `notfound.nexy`、`errors.nexy` 和 JSON 错误 |
| [每个文件夹的错误页](routing/fbr/errors/folder-pages.md) | 边缘情况：来自子文件夹的错误 |

### 模块化路由器 {modular}
控制器和模块。
| 页面 | 你会做什么 |
|---|---|
| [模块化路由](routing/modular/README.md) | 安装控制器和模块 |
| [依赖注入](routing/modular/dependency-injection.md) | 定义服务、其范围和容器 |
| [守卫和元数据](routing/modular/guards-and-metadata.md) | 保护和记录路线 |
| [模块化路由器与 NestJS](routing/modular/vs-nestjs.md) | 与 NestJS 比较 |

### 自定义路由器集成 {custom}
| 页面 | 你会做什么 |
|---|---|
| [自定义路由](routing/custom/README.md) | 包含现有的 FastAPI 应用程序 |

## 前端

### 共享合约
| 页面 | 它定义了什么 |
|---|---|
| [操作和导航](views/frontend/actions-and-navigation.md) | 调用键入的操作、链接页面、读取 URL |

### 邻国意见
| 页面 | 你会做什么 |
|---|---|
| [.nexy 文件](views/nexy/README.md) | 使用 Python、Jinja2 和 props 编写一个页面 |
| [组件](views/nexy/components.md) | 使用 `Image`、`Link`、`Audio`、`Video` 和 `Import` |

### 文件中的页面和布局 {fbr,custom}
| 页面 | 它定义了什么 |
|---|---|
| [前端页面](views/frontend/pages.md) | 一个文件，一条路线：道具、渲染、元数据 |
| [前端布局](views/frontend/layouts.md) | 文档外壳、嵌套以及布局不能做的事情 |
| [布局.nexy](views/nexy/layouts.md) | 编写服务器模式布局 |
| [Markdown 和 MDX](views/nexy/markdown.md) | 编写内容页面 |

### 框架差异
| 页面 | 有什么变化 |
|---|---|
| [React 差异](views/react/differences.md) | 组件、挂钩和 `layout.tsx` {new} |
| [Vue 差异](views/vue/differences.md) | 证监会、参考文献和 `layout.vue` {new} |
| [Svelte 差异](views/svelte/differences.md) | 符文、商店和 `layout.svelte` {new} |
| [Solid 差异](views/solid/differences.md) | 信号、访问器和 `layout.tsx` {new} |
| [Preact 差异](views/preact/differences.md) | 钩子、信号和 `layout.tsx` {new} |

## 渲染

### 模式
| 页面 | 你将决定什么 |
|---|---|
| [渲染](rendering/README.md) | 哪种渲染模式适合页面 |
| [苏维埃社会主义共和国](rendering/ssr.md) | 服务器渲染，默认 |
| [岛屿](rendering/islands.md) | 空闲、可见或媒体查询时进行水合 |

### 文件页面模式 {fbr,custom}
| 页面 | 你将决定什么 |
|---|---|
| [情监侦](rendering/isr.md) | 使用 stale-while-revalidate 缓存页面 |
| [企业社会责任](rendering/csr.md) | 客户端路由 |

## 指南

### 表格和数据
| 页面 | 你会做什么 |
|---|---|
| [行动](guides/actions.md) | 从表单或类型化的 TypeScript 函数调用 Python 函数 |
| [数据库](guides/databases.md) | 选择 ORM 并运行迁移 |

### 安全与部署
| 页面 | 你会做什么 |
|---|---|
| [中间件和安全性](guides/middleware-and-security.md) | 设置 CORS、GZip、可信主机和会话 |
| [部署](deployment/README.md) | 构建、容器化和服务 |
| [性能](deployment/performance.md) | 测量和调整默认值 |

### 构建和测试
| 页面 | 你会做什么 |
|---|---|
| [Vite 和样式](guides/frontend.md) | 设置 Vite、样式和客户端构建 |
| [测试](guides/testing.md) | 使用 pytest、`TestClient` 和 vitest 进行测试 |

### 工具和帮助
| 页面 | 你会做什么 |
|---|---|
| [开发工具栏](guides/devtools.md) | 使用 `nexy dev`的工具栏，然后将其关闭 |
| [编码剂](guides/ai-agents.md) | 给出 Claude Code、Codex 和 OpenCode 项目的规则 |
| [故障排除](guides/troubleshooting.md) | 解决人们遇到的第一个问题 |

## 数据库

### SQL数据库
| 页面 | 你会做什么 |
|---|---|
| [SQLite](databases/sqlite.md) | 使用一个文件，无服务器：引擎、编译指示、迁移和测试 |
| [PostgreSQL](databases/postgresql.md) | 与 psycopg 连接，使用 JSONB、数组、搜索和更新插入 |
| [霓虹灯](databases/neon.md) | 使用无服务器 PostgreSQL：池化主机、自动挂起和分支 |
| [MySQL 和 MariaDB](databases/mysql-mariadb.md) | 与pymysql连接，使用utf8mb4、upserts和全文搜索 |

## 来自

相同的任务，先用您熟悉的框架编写，然后再用 Nexy 编写。

### 概述
| 页面 | 你会做什么 |
|---|---|
| [来自另一个框架](getting-started/coming-from-other-frameworks.md) | 将 FastAPI、Next.js 和 Express 习惯翻译成 Nexy |

### Python 框架 {fbr}
| 页面 | 你会做什么 |
|---|---|
| [来自 FastAPI](coming-from/fastapi.md) | 保留您的 FastAPI 代码：只有 `@app.get` 成为文件 |
| [来自 Flask](coming-from/flask.md) | 将视图、蓝图、模板和表单转变为 Nexy 路线 |
| [来自 Django](coming-from/django.md) | 将视图、模板、模型、表单和设置映射到 Nexy |

### JavaScript 后端 {fbr}
| 页面 | 你会做什么 |
|---|---|
| [来自快递](coming-from/express.md) | 将路由、中间件和 `req`/`res` 转换为 Python 处理程序 |
| [来自 Fastify](coming-from/fastify.md) | 将模式、插件和挂钩转换为模型、文件夹和文件 |
| [来自艾丽西亚](coming-from/elysia.md) | 将 `t` 模式、守卫和 Eden 映射到 Pydantic 并键入操作 |
| [从霍诺出发](coming-from/hono.md) | 将路由、中间件和 `hc` 客户端映射到 Nexy |

### 全栈框架 {fbr}
| 页面 | 你会做什么 |
|---|---|
| [来自 Next.js](coming-from/nextjs.md) | 保留您的 React 页面并将服务器代码移至 Python |
| [来自 Remix](coming-from/remix.md) | 将加载程序和操作转换为 Python 处理程序和操作 |
| [来自 Nuxt](coming-from/nuxt.md) | 保留 Vue 页面并将 `server/` 移至 Python |
| [来自 SvelteKit](coming-from/sveltekit.md) | 保留您的 Svelte 页面并将负载、操作和挂钩移至 Python |
| [来自 Astro](coming-from/astro.md) | 将 Astro 页写入 `.nexy` 页，具有相同的岛 |
| [来自 Laravel](coming-from/laravel.md) | 将路由、控制器、Blade、Eloquent 和队列映射到 Nexy |
| [来自 Ruby on Rails](coming-from/rails.md) | 将路线、控制器、ERB、Active Record 和作业映射到 Nexy |

### 控制器框架 {modular}
| 页面 | 你会做什么 |
|---|---|
| [来自 NestJS](coming-from/nestjs.md) | 将控制器、模块、提供程序和防护程序移至模块化路由器 |
| [来自 Spring Boot](coming-from/spring-boot.md) | 将控制器、服务和过滤器移至模块化路由器 |

## 参考

### 命令和配置
| 页面 | 它列出了什么 |
|---|---|
| [CLI](reference/cli.md) | 命令、标志、提示和退出代码 |
| [配置](reference/config.md) | 每个 `nexyconfig.py` 字段及其默认值 |

### Python API 和错误
| 页面 | 它列出了什么 |
|---|---|
| [Python API](reference/python-api.md) | Nexy 按模块导出的每个名称 |
| [异常和错误](reference/exceptions.md) | 每个故障、其状态以及解决该故障的文件 |

### 文件约定 {fbr,custom}
| 页面 | 你会做什么 |
|---|---|
| [文件约定](reference/file-conventions.md) | 保留文件和路由规则 |

### 惯例和概念
| 页面 | 你会做什么 |
|---|---|
| [术语表](reference/glossary.md) | 这些文档使用的词语 |
| [安全](reference/security.md) | 版本底线、Nexy 遵循的规则、审核 |

## 布局
```text
docs/
├─ README.md
├─ getting-started/     what is Nexy, installation, quick start, tutorial, core concepts,
│                       project structure, how Nexy works, migration
├─ coming-from/         one page per framework: FastAPI, Django, Express, Next.js...
├─ databases/           one page per database: SQLite, PostgreSQL, Neon, MySQL
├─ routing/             FBR Router, Modular Router, Custom Router
│  ├─ fbr/              file-based routing
│  │  ├─ modes.md       server mode and client mode
│  │  ├─ inheritance.md layouts, dependencies, error pages
│  │  ├─ pages/         pages, dynamic routes, route groups, metadata
│  │  ├─ layouts/       layout resolution, layout.tsx, layout.vue, layout.svelte
│  │  ├─ handlers/      .py route handlers, validation and errors
│  │  ├─ dependencies/  dependencies.py, guards
│  │  ├─ middleware/    middleware.py
│  │  ├─ errors/        not-found and error pages
│  │  ├─ navigation/    links, hooks
│  │  └─ realtime/    WebSocket
│  ├─ modular/          controllers, injection, guards, NestJS comparison
│  └─ custom/           include an existing FastAPI router
├─ rendering/           SSR, ISR, CSR, islands
├─ views/               choose a format, one page per client framework
│  ├─ frontend/         the four contracts every framework shares
│  └─ nexy/             .nexy files, components, layouts, Markdown and MDX
├─ guides/              actions, i18n, databases, middleware, frontend, testing
├─ deployment/          deploy, performance
└─ reference/           CLI, config, Python API, exceptions, file conventions, glossary,
                        security, agents
```

## 高级

### 高级 {advanced}

| 页面 | 你会做什么 |
|---|---|
| [Nexy 的工作原理](getting-started/how-nexy-works.md) | 查看文件和页面之间发生的情况，以及 Nexy 留给您的内容 |
| [升级到2.2](getting-started/upgrading.md) | 从 2.1 迁移到 2.2 |
| [国际化 (i18n)](guides/i18n.md) | 使用您选择的库添加翻译 |
| [食谱](guides/recipes.md) | 示例和模式，而不是教程 |

*这些页面不属于默认阅读路径。 “所有文档”链接可让您查看所有内容。*
