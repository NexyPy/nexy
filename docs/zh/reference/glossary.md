# 词汇表

这些文档使用的单词，每行一行，按字母顺序排列。需要多行的术语有一个页面：点击链接。有关这些概念如何组合在一起的信息，请阅读[核心概念](../getting-started/core-concepts.md)。

## 条款

| 期限 | 在一行中 |
|---|---|
| 行动 | 标记为 `@Action` 的 Python 函数，充当 `POST` 并可从客户端调用 ([操作](../guides/actions.md)) |
| ASGI | 接口 Uvicorn 说话，由 FastAPI 和 Starlette 实现 |
| 客户端模式 | `useCSR = True`：框架文件是路由和浏览器导航（[模式](../routing/fbr/modes.md)） |
| 组件 | 用于组成视图的可重用 UI 构建块 ([视图](../views/README.md)) |
| 企业社会责任 | 客户端渲染：浏览器在第一个文档之后渲染页面（[CSR](../rendering/csr.md)） |
| 依赖性 | 函数 FastAPI 在处理程序之前运行，每个路由或每个文件夹（[依赖关系](../routing/fbr/dependencies/README.md)） |
| 文件壳 | 页面周围的 `<html>`、`<head>` 和 `<body>`，由最近的布局或 Nexy ([布局](../routing/fbr/layouts/README.md)) 拥有 |
| 端点 | URL 和 HTTP 方法的唯一组合 ([视图](../views/README.md)) |
| 流化床反应器 | 基于文件的路由：`src/routes/` 下的文件是一个路由（[路由](../routing/fbr/README.md)） |
| 前题 | `.nexy` 或 `.md` 文件（[.nexy 文件](../views/nexy/README.md)）的两个 `---` 行之间的 Python 块 |
| 守卫 | 通过引发 `HTTPException` ([守卫](../routing/modular/guards-and-metadata.md)) 拒绝请求的依赖项 |
| 处理程序 | 处理特定方法的 HTTP 请求的 Python 函数 ([视图](../views/README.md)) |
| HMR | 热模块替换：开发服务器交换已更改的模块，无需完全重新加载（[前端](../guides/frontend.md)） |
| 保湿 | 浏览器将框架附加到服务器已发送的 HTML ([岛屿](../rendering/islands.md)) |
| 岛 | 安装在服务器渲染页面内的客户端组件 ([岛屿](../rendering/islands.md)) |
| 情报监视与侦察 | 增量静态重新生成：每个路径一个缓存页面，在后台刷新 ([ISR](../rendering/isr.md)) |
| 布局 | 一个 `layout.*` 文件，包含其文件夹下的页面 ([布局](../routing/fbr/layouts/README.md)) |
| 模块化路由器 | 在 `src/apps/` ([模块化](../routing/modular/README.md)) 下使用 `@Module` 和 `@Controller` 声明的路由 |
| 页面 | 由 `src/routes/` ([视图](../views/README.md)) 下的文件定义的 URL 可寻址资源 |
| 预取 | 在读者点击链接之前加载链接后面的页面 ([链接](../routing/fbr/navigation/linking-and-navigating.md)) |
| 道具 | 父级传递给组件的值 ([.nexy 文件](../views/nexy/README.md)) |
| 重新验证 | 在后台重建 ISR 页面之前的秒数 ([ISR](../rendering/isr.md)) |
| 路线 | 由路由文件的路径生成的 URL 模式 ([路由](../routing/README.md)) |
| 航线组 | 括号中的文件夹，用于对路由进行分组而不添加段（[动态路由](../routing/fbr/pages/dynamic-routes.md)） |
| 路线处理程序 | `GET`, `POST`, … `.py` 路由文件的函数 ([处理函数](../routing/fbr/handlers/README.md)) |
| 服务器模式 | `useCSR = False`，默认：服务器渲染 `.nexy` 和 `.md` 页面（[模式](../routing/fbr/modes.md)） |
| 技能 | 带有 `SKILL.md` 的文件夹，用于教导编码代理 Nexy 的一部分（[编码代理](../guides/ai-agents.md)） |
| SSG | 静态站点生成； **不是 Nexy 模式**：提前构建的 HTML 总是由服务器读回（[渲染](../rendering/README.md)） |
| 固态继电器 | 服务器端渲染：服务器为其请求渲染每个页面，这是默认的（[SSR](../rendering/ssr.md)） |
| 查看 | 生成页面响应正文的过程 ([视图](../views/README.md)) |

## 文件和文件夹

| 名称 | 在一行中 |
|---|---|
| `__nexy__/` | 生成的输出：编译页面、客户端入口和客户端动作；从未编辑，从未提交 |
| `nexyconfig.py` | 项目配置，一类 `use*` 字段 ([配置](config.md)) |
| `public/` | 根目录下的文件，例如 `public/logo.svg` → `/logo.svg` ([文件约定](file-conventions.md)) |
| `src/apps/` | 模块化路由器的控制器和模块（[模块化](../routing/modular/README.md)） |
| `src/components/` | 页面导入的组件；从不路由（[文件约定](file-conventions.md)） |
| `src/routes/` | 应用程序的路由（[文件约定](file-conventions.md)） |

## 后续步骤

- [核心概念](../getting-started/core-concepts.md)：这些词所属的模型
- [文档索引](../README.md)：当前任务的页面
- [文件约定](file-conventions.md)：这些定义背后的保留名称
- [对于 AI 代理](../guides/ai-agents.md)：相同的不变量，为代理编写
