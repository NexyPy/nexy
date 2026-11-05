# 词汇表

这些文档使用的单词，每行一行，按字母顺序排列。需要多行的术语有一个页面：点击链接。有关这些概念如何组合在一起的信息，请阅读[核心概念](../getting-started/core-concepts.md)。

## 条款

| 术语 | 在一行 |
|---|---|
| 操作 | 是一个标记为 `@Action` 的 Python 函数，充当 `POST` 并可从客户端调用 ([actions](../guides/actions.md)) |
| ASGI | 接口 Uvicorn 说话，由 FastAPI 和 Starlette | 实现
| 客户端模式 | `useCSR = True`：框架文件是路由，浏览器导航 ([modes](../routing/fbr/modes.md)) |
| 组件 | 一个可重用的 UI 构建块，用于组成视图 ([views](../views/README.md)) |
| CSR | 客户端渲染：浏览器在第一个文档 ([CSR](../rendering/csr.md)) | 之后渲染页面
| 依赖项 | 函数 FastAPI 在处理程序之前运行，每个路由或每个文件夹 ([依赖项 ](../routing/fbr/dependencies/README.md)) |
| 文档外壳 | 页面周围的 `<html>`、`<head>` 和 `<body>`，由最近的布局或 Nexy ([layouts](../routing/fbr/layouts/README.md)) | 拥有
| 端点 | URL 和 HTTP 方法的唯一组合 ([views](../views/README.md)) |
| FBR | 基于文件的路由：`src/routes/` 下的文件是路由 ([routing](../routing/fbr/README.md)) |
| Frontmatter | `.nexy` 或 `.md` 文件 ([.nexy 文件 ](../views/nexy/README.md)) | 的两 `---` 行之间的 Python 块
| 通过引发 `HTTPException` ([guards](../routing/modular/guards-and-metadata.md)) | 来保护 | 拒绝请求的依赖项
| 处理程序 | 一个 Python 函数，用于处理特定方法 ([views](../views/README.md)) | 的 HTTP 请求
| HMR | 热模块替换：开发服务器交换已更改的模块，无需完全重新加载 ([frontend](../guides/frontend.md)) |
| Hydration | 浏览器将框架附加到服务器已发送的 HTML ([islands](../rendering/islands.md)) |
| Island | 安装在服务器渲染页面内的客户端组件 ([islands](../rendering/islands.md)) |
| ISR | 增量静态重新生成：每个路径一个缓存页面，在后台刷新 ([ISR](../rendering/isr.md)) |
| 布局 | 一个 `layout.*` 文件，将页面包含在其文件夹 ([layouts](../routing/fbr/layouts/README.md)) | 下
| 模块化路由器 | 在 `src/apps/` 下使用 `@Module` 和 `@Controller` 声明的路由 ([模块化](../routing/modular/README.md)) |
| 页面 | 由 `src/routes/` ([views](../views/README.md)) | 下的文件定义的 URL 可寻址资源
| 在读者点击链接之前预取 | 加载链接后面的页面 ([linking](../routing/fbr/navigation/linking-and-navigating.md)) |
| Props | 父级传递给组件的值 ([.nexy files](../views/nexy/README.md)) |
| 重新验证 | 在后台重建 ISR 页面之前的秒数 ([ISR](../rendering/isr.md)) |
| 路由 | 一个 URL 模式，由路由文件的路径生成 ([路由](../routing/README.md)) |
| 路由组 | 括号中的文件夹，用于对路由进行分组而不添加分段 ([动态路由](../routing/fbr/pages/dynamic-routes.md)) |
| 路由处理程序 | `GET`、`POST`、… `.py` 路由文件的函数 ([handlers](../routing/fbr/handlers/README.md)) |
| 服务器模式 | `useCSR = False`，默认：服务器渲染 `.nexy` 和 `.md` 页面 ([modes](../routing/fbr/modes.md)) |
| 技能 | 一个带有 `SKILL.md` 的文件夹，用于教导编码代理 Nexy 的一部分（[编码代理](../guides/ai-agents.md)）|
| SSG | 静态站点生成； **不是 Nexy 模式**：提前构建的 HTML 总是由服务器读回（[渲染](../rendering/README.md)）|
| SSR | 服务器端渲染：服务器为其请求渲染每个页面，这是默认的 ([SSR](../rendering/ssr.md)) |
| 查看 | 生成页面响应正文的过程 ([views](../views/README.md)) |

## 文件和文件夹

| 姓名 | 一行 |
|---|---|
| `__nexy__/` | 生成的输出：编译页面、客户端条目和操作客户端；从未编辑，从未提交 |
| `nexyconfig.py` | 项目配置，一类 `use*` 字段 ([config](config.md)) |
| `public/` | 文件位于根目录，例如 `public/logo.svg` → `/logo.svg` ([文件约定](file-conventions.md)) |
| `src/apps/` | 模块化路由器的控制器和模块 ([模块化](../routing/modular/README.md)) |
| `src/components/` | 页面导入的组件；从不路由 ([文件约定](file-conventions.md)) |
| `src/routes/` | 应用程序的路由（[文件约定](file-conventions.md)）|

## 后续步骤

- [核心概念](../getting-started/core-concepts.md)：这些词所属的模型
- [文档索引](../README.md)：当前任务的页面
- [文件约定](file-conventions.md)：这些定义背后的保留名称
- [对于 AI 代理](../guides/ai-agents.md)：相同的不变量，为代理编写
