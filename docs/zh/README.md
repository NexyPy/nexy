# Nexy 文档

**用于全栈 Web 应用程序的 Python 框架。**

Nexy 是关于 Python 后端和浏览器前端之间的接缝。不是两台服务器，而是两台
构建系统和两个路由表，您将获得一个来源：FastAPI 和 Starlette 为应用程序提供服务，
Vite构建客户端，`src/routes/`下的文件是一个路由 - `.nexy`是一个页面，`.py`是一个
API 处理程序。

- **Python 首先。** 页面、端点、表单和操作都是 Python，服务器渲染的页面需要
  没有前端框架。
- **三个路由器，一个集成。**基于文件、模块化或现有的 FastAPI `APIRouter`。
- **当你想要一个前端时。** React、Vue、Svelte、Solid 或 Preact，每页作为岛屿，或者用于
  整个项目以客户端模式进行。
- **渲染，一种模型。**服务器渲染，缓存页面和孤岛按页面决定；客户
  路由是一个项目交换机。
- **键入的操作。** 表单发布和键入的客户端调用到达相同的 Python 函数。

从 `src/routes/` 下的一个文件开始，并在项目增长时添加结构。

## 开始

### 第一步
| 页 | 你将做什么 |
|---|---|
| [安装](getting-started/installation.md) | 安装 uv 和 Nexy CLI，然后创建您的第一个项目 |
| [快速启动](getting-started/quick-start.md) | 创建一个项目，通过实时重新加载运行它，并构建它用于生产 |
| [教程](getting-started/tutorial.md) | 在 10 分钟内构建一个带有端点、共享数据和生产版本的注释页面 |

### 理解模型
| 页 | 你将做什么 |
|---|---|
| [核心概念](getting-started/core-concepts.md) | 获取心理模型：路由、页面、视图、组件、处理程序、端点 |
| [Nexy 的工作原理](getting-started/how-nexy-works.md) | 按照从 URL 到响应该请求的文件的一个请求 |
| [架构](architecture.md) | 了解哪一层做什么，以及 Nexy 留给您的应用程序什么 |
| [项目结构](getting-started/project-structure.md) | 了解项目中每个文件夹和文件的用途 |
| [选择路由器](routing/README.md) | 选择基于文件、模块化或自定义的路由器 |
| [选择视图格式](views/README.md) | 为页面选择 `.nexy`、Markdown 或客户端框架 |

### 来自其他地方
| 页 | 你将做什么 |
|---|---|
| [来自另一个框架](getting-started/coming-from-other-frameworks.md) | 将 FastAPI、Next.js 和 Express 习惯翻译成 Nexy |

## 路由

### 基于文件 {fbr}
| 页 | 你将做什么 |
|---|---|
| [基于文件的路由](routing/fbr/README.md) | 将文件路径转换为 URL |
| [页数](routing/fbr/pages/README.md) | 写入一页 |
| [动态路由](routing/fbr/pages/dynamic-routes.md) | 使用 `[slug]`、`[...path]` 和路由组 |
| [页面元数据](routing/fbr/pages/metadata.md) | 设置页面的标题、描述和共享图像 {new} |
| [布局](routing/fbr/layouts/README.md) | 在页面之间共享框架 |
| [继承](routing/fbr/inheritance.md) | 读取布局、依赖项和错误页的解析顺序 |
| [服务器模式和客户端模式](routing/fbr/modes.md) | `useCSR`，以及每种模式允许的内容|
| [链接和导航](routing/fbr/navigation/linking-and-navigating.md) | 链接页面、在客户端上导航、预取 |
| [Hooks](routing/fbr/navigation/hooks.md) | 读取路径、查询、cookie 和会话 |

### 处理程序和错误 {fbr}
| 页 | 您将做什么 |
|---|---|
| [路由处理程序](routing/fbr/handlers/README.md) | 添加 Python 端点 |
| [验证和错误](routing/fbr/handlers/validation-and-errors.md) |回答`422`和`404`，并提出`HTTPException`|
| [WebSocket 处理程序](routing/fbr/realtime/websocket.md) | 处理 `SOCKET` 连接 |
| [依赖项和防护](routing/fbr/dependencies/README.md) | 在处理程序之前运行 `dependencies.py`，并继承它 |
| [中间件文件](routing/fbr/middleware/README.md) | 用 `middleware.py` 包装请求，由目录 | 继承
| [错误页面](routing/fbr/errors/README.md) | 回答 `notfound.nexy`、`errors.nexy` 和 JSON 错误 |
| [每个文件夹的错误页](routing/fbr/errors/folder-pages.md) | 边缘情况：来自子文件夹的错误 |

### 模块化路由器{modular}
控制器和模块。
| 页 | 你将做什么 |
|---|---|
| [模块化路由](routing/modular/README.md) | 安装控制器和模块 |
| [依赖注入](routing/modular/dependency-injection.md) | 定义服务、其范围和容器 |
| [守卫和元数据](routing/modular/guards-and-metadata.md) | 保护和记录路径 |
| [模块化路由器与 NestJS](routing/modular/vs-nestjs.md) | 与 NestJS 的比较 |

### 自定义路由器集成{custom}
| 页 | 您将做什么 |
|---|---|
| [自定义路由](routing/custom/README.md) | 包括现有的 FastAPI 应用程序 |

## 前端

### 共享合约
| 页面 | 它定义了什么 |
|---|---|
| [前端页面](views/frontend/pages.md) | 一个文件，一条路线：道具、渲染、元数据 |
| [前端布局](views/frontend/layouts.md) | 文档外壳、嵌套以及布局无法执行的操作 |
| [操作和导航](views/frontend/actions-and-navigation.md) | 调用键入的操作、链接页面、读取 URL |

### 最近的观点
| 页 | 您将做什么 |
|---|---|
| [.nexy 文件](views/nexy/README.md) | 使用 Python、Jinja2 和 props 编写页面 |
| [组件](views/nexy/components.md) | 使用 `Image`、`Link`、`Audio`、`Video` 和 `Import` |
| [layout.nexy](views/nexy/layouts.md) | 写入服务器模式布局 |
| [Markdown 和 MDX](views/nexy/markdown.md) | 写入内容页面 |

### 框架差异
| 页面 | 发生了什么变化 |
|---|---|
| [反应差异](views/react/differences.md) | 组件、钩子和 `layout.tsx` {new} |
| [Vue 差异](views/vue/differences.md) | SFC、参考文献和 `layout.vue` {new} |
| [细小的差异](views/svelte/differences.md) |符文、商店和`layout.svelte` {new} |
| [固定差异](views/solid/differences.md) |信号、访问器和`layout.tsx` {new} |
| [Preact 差异](views/preact/differences.md) | 钩子、信号和 `layout.tsx` {new} |

## 渲染

### 模式
| 页 | 您将决定什么 |
|---|---|
| [渲染](rendering/README.md) | 哪种渲染模式适合页面 |
| [SSR](rendering/ssr.md) | 服务器渲染，默认 |
| [ISR](rendering/isr.md) | 缓存具有 stale-while-revalidate 的页面 |
| [CSR](rendering/csr.md) | 客户端路由 |
| [岛屿](rendering/islands.md) | 空闲、可见或媒体查询时水合|

## 指南

### 表格和数据
| 页 | 您将做什么 |
|---|---|
| [操作](guides/actions.md) | 从表单或类型化的 TypeScript 函数调用 Python 函数 |
| [数据库](guides/databases.md) | 选择 ORM 并运行迁移 |

### 安全和部署
| 页 | 您将做什么 |
|---|---|
| [中间件和安全性](guides/middleware-and-security.md) | 设置 CORS、GZip、可信主机和会话 |
| [部署](deployment/README.md) |构建、容器化和服务|
| [性能](deployment/performance.md) | 测量和调整默认值 |

### 构建和测试
| 页 | 你将做什么 |
|---|---|
| [Vite 和样式](guides/frontend.md) | 设置 Vite、样式和客户端构建 |
| [测试](guides/testing.md) | 使用 pytest、`TestClient` 和 vitest | 进行测试

### 工具和帮助
| 页 | 您将做什么 |
|---|---|
| [开发工具栏](guides/devtools.md) | 使用`nexy dev`的工具栏，并将其关闭|
| [编码代理](guides/ai-agents.md) | 为 Claude Code、Codex 和 OpenCode 提供您项目的规则 |
| [故障排除](guides/troubleshooting.md) | 修复人们遇到的第一个问题 |

## 参考

### 命令和配置
| 页面 | 列出的内容 |
|---|---|
| [CLI](reference/cli.md) | 命令、标志、提示和退出代码 |
| [配置](reference/config.md) | 每个 `nexyconfig.py` 字段及其默认 |

### Python API 和错误
| 页面 | 列出的内容 |
|---|---|
| [Python API](reference/python-api.md) | Nexy 按模块导出的每个名称 |
| [异常和错误](reference/exceptions.md) | 每个故障、其状态以及回答它的文件 |

### 惯例和概念
| 页 | 你将做什么 |
|---|---|
| [文件约定](reference/file-conventions.md) | 保留文件和路由规则 |
| [词汇表](reference/glossary.md) | 这些文档使用的单词 |
| [安全](reference/security.md) | 版本楼层、Nexy 遵循的规则、审核 |

## 布局
```text
docs/
├─ README.md
├─ architecture.md       the layers, and what Nexy leaves to the application
├─ getting-started/     installation, quick start, tutorial, core concepts, project structure,
│                       migration
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

### 高级{advanced}

| 页 | 你将做什么 |
|---|---|
| [升级到 2.2](getting-started/upgrading.md) | 从 2.1 迁移到 2.2 |
| [国际化 (i18n)](guides/i18n.md) | 使用您选择的库添加翻译 |
| [食谱](guides/recipes.md) | 示例和模式，而不是教程 |

*这些页面不属于默认阅读路径。 “所有文档”链接可让您查看所有内容。*