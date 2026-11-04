# 核心概念

The mental model, before the API: four levels of reading, then the notions that come back on every
页。 Each notion gets one line here and a link to the page that goes deeper.

## 如何阅读这些文档

| Level | The question it answers | Start with |
|---|---|---|
| Application architecture | which layer answers a request, and what it refuses to do | [Architecture](../architecture.md) |
| Application structure | where the code lives, and what a file becomes | [Project structure](project-structure.md) |
| Presentation and rendering | what the reader sees, and who produces the HTML | [Views](../views/README.md), [Rendering](../rendering/README.md) |
| Application interaction | what the reader does, and what runs in response | [Actions](../guides/actions.md) |

级别按该顺序读取一次。 After that, a page you need is a lookup, not a course.

## 应用架构

决定哪些代码响应 URL 的三种方法。它们是替代方案，而不是层：

- **File-based routing (FBR)**: a file under `src/routes/` is a route.默认。
- **Modular router**: controllers and modules under `src/apps/`, declared with decorators, for a
  NestJS 风格的代码库。
- **Custom router**: an existing FastAPI `APIRouter` included in the application.

选择三者之一就是一个决定。 Choosing a frontend framework is another, separate one:
请参阅[选择路由器](../routing/README.md)和[视图](../views/README.md)。

## 应用程序结构

Five notions that a reader coming from Next.js usually merges into one.它们不是同一个东西，
这种差异解释了大多数“为什么我的页面没有渲染”的问题。

| Notion | What it is | What it is not |
|---|---|---|
| **路由** | 一种 URL 模式，由文件路径生成 | 文件：一个文件可以响应多个 URL (`[slug]`) |
| **Page** | 渲染视图的路由文件：`.nexy`、`.md`、`.mdx`、`.tsx`、`.vue`、`.svelte` | 端点：它应答文档，而不是数据 |
| **View** | 生成页面主体的内容：Jinja2 和 Python、Markdown 或客户端组件 | 路线：同一个视图可以服务多个页面 |
| **组件** | 可重用的部分，页面导入 | 路由：在服务器模式下，组件永远不会单独提供服务 |
| **路由处理程序** | `.py`路由文件的功能，以HTTP方法命名（`GET`，`POST`，...）|页面：它返回JSON，文件或`Response` |
| **端点** | 处理程序应答的一对（URL、方法） | 处理程序：一个文件可以应答多个端点 |

用一句话来说：**页面是一个路由文件，视图是呈现它的东西，组件是页面的东西
重用，处理程序应答端点。**

还有两个词随处可见：

- **布局**：一个`layout.*`文件，包裹其文件夹下的页面； root 拥有 HTML
  文档。请参阅[布局](../routing/fbr/layouts/README.md)。
- **Dependency**：在处理程序之前运行的函数，按路由或每个文件夹应用。参见
  [依赖关系](../routing/fbr/dependencies/README.md)。

## 演示和渲染

两个独立的决定，经常混淆：

- **The format** decides which file renders the page: [Views](../views/README.md).
- **模式**决定谁生成HTML以及何时生成：[渲染](../rendering/README.md)。

| 概念 | 一行 |
|---|---|
| Server mode | the server renders `.nexy` and `.md` pages;组件是岛屿 ([modes](../routing/fbr/modes.md)) |
|客户端模式|`useCSR = True`：框架文件是路由，导航发生在浏览器中|
| SSR、ISR、CSR、岛屿 | 四种渲染模式，按页面决定，CSR 除外，这是每个项目 ([渲染](../rendering/README.md)) |
| Hydration | 浏览器将框架附加到服务器已发送的 HTML ([islands](../rendering/islands.md)) |
| Props | 父级传递给组件的值，在 `.nexy` 文件 ([.nexy files](../views/nexy/README.md)) | 中声明 `name: prop[type]`

## 应用程序交互

| 概念 | 一行 |
|---|---|
| Action | a Python function marked `@Action`, served as a `POST`, callable from a form or as a typed function ([actions](../guides/actions.md)) |
| 表单 | 发布到操作的 HTML 表单，验证错误返回到页面 ([actions](../guides/actions.md)) |
| 导航 | 预取链接，以及读取路径、查询、cookie 和会话的挂钩 ([hooks](../routing/fbr/navigation/hooks.md)) |
| 数据获取 | 由需要它的页面或处理程序完成； Nexy 不提供客户端数据层 ([handlers](../routing/fbr/handlers/README.md)) |

## Nexy 不做什么

身份验证、授权、数据库、国际化、后台作业、电子邮件、支付和
搜索是**您的应用程序的责任**，而不是框架的责任。 Nexy 给出了扩展名
指出并说明在哪里插入每个：请参阅[边界](../architecture.md#boundaries)。

原因并不是极简主义本身：一个选择 ORM 或身份验证库的框架
已经决定了只有您的应用程序才能决定的事情。

## 后续步骤

- [架构](../architecture.md)：层，以及谁构建什么
- [项目结构](project-structure.md)：项目的每个文件夹和文件
- [词汇表](../reference/glossary.md)：相同的单词，在一个字母索引中
- [Nexy 的工作原理](how-nexy-works.md)：一个请求，一步一步