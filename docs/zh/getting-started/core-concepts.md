# 核心理念

API 之前的心智模型：四个级别的阅读，然后是每一页上出现的概念。每个概念在这里都占一行，并有一个指向更深入页面的链接。

## 如何阅读这些文档

| 级别 | 它回答的问题 | 从 | 开始
|---|---|---|
| 应用程序架构 | 哪一层响应请求，以及它拒绝做什么 | [架构 ](../architecture.md) |
| 应用程序结构 | 代码所在的位置，以及文件的内容 | [项目结构 ](project-structure.md) |
| 呈现和渲染 | 读者看到的内容以及由谁生成 HTML | [视图 ](../views/README.md)、[渲染 ](../rendering/README.md) |
| 应用程序交互 | 阅读器执行的操作以及响应中运行的内容 | [操作 ](../guides/actions.md) |

级别按该顺序读取一次。之后，您需要的页面是查找，而不是课程。

## 应用架构

决定哪些代码响应 URL 的三种方法。它们是替代方案，而不是层：

- **基于文件的路由（FBR）**：`src/routes/` 下的文件是一个路由。默认。
- **模块化路由器**：`src/apps/`下的控制器和模块，用装饰器声明，用于NestJS风格的代码库。
- **自定义路由器**：应用程序中包含的现有 FastAPI `APIRouter`。

选择三者之一就是一个决定。选择前端框架是另一个单独的框架：请参阅[选择路由器](../routing/README.md) 和[视图](../views/README.md)。

## 应用结构

来自 Next.js 的读者通常会将五个概念合并为一个。它们不是同一件事，这种差异解释了大多数“为什么我的页面不渲染”的问题。

| 概念 | 它是什么 | 它不是什么 |
|---|---|---|
| **Route** | 一种 URL 模式，由文件的路径生成 | 一个文件：一个文件可以回答多个 URL (`[slug]`) |
| **Page** | 渲染视图的路由文件： `.nexy`、`.md`、`.mdx`、`.tsx`、`.vue`、`.svelte` | 端点：它响应文档，而不是数据 |
| **View** | 产生页面正文的内容：Jinja2 和 Python、Markdown 或客户端组件 | 路由：同一个视图可以服务多个页面 |
| **组件** | 可重用的部分，页面导入 | 路由：在服务器模式下，组件永远不会单独提供服务 |
| **路由处理程序** | `.py` 路由文件的功能，以HTTP方法命名（`GET`，`POST`，...）| 页面：它返回JSON，文件或 `Response` |
| **端点** | 处理程序应答的一对（URL，方法）| 处理程序：一个文件可以应答多个端点 |

用一句话来说：**页面是一个路由文件，视图是呈现它的内容，组件是页面重用的内容，处理程序回答端点。**

还有两个词随处可见：

- **布局**：一个 `layout.*` 文件，包裹其文件夹下的页面； root 拥有 HTML 文档。请参阅[布局](../routing/fbr/layouts/README.md)。
- **依赖项**：在处理程序之前运行的函数，应用于每个路由或每个文件夹。请参阅[依赖关系](../routing/fbr/dependencies/README.md)。

## 演示和渲染

两个独立的决定，经常混淆：

- **格式** 决定哪个文件呈现页面：[Views](../views/README.md)。
- **模式** 决定谁生成HTML以及何时生成：[渲染](../rendering/README.md)。

| 概念 | 一行 |
|---|---|
| 服务器模式 | 服务器渲染 `.nexy` 和 `.md` 页面；组件是岛屿 ([modes](../routing/fbr/modes.md)) |
| 客户端模式 | `useCSR = True`：框架文件是路由，导航发生在浏览器中 |
| SSR、ISR、CSR、岛屿 | 四种渲染模式，按页面决定，CSR 除外，CSR 是按项目 ([渲染](../rendering/README.md)) |
| Hydration | 浏览器将框架附加到服务器已发送的 HTML ([islands](../rendering/islands.md)) |
| Props | 父级传递给组件的值，在 `.nexy` 文件中声明 `name: prop[type]` ([.nexy 文件](../views/nexy/README.md)) |

## 应用交互

| 概念 | 一行 |
|---|---|
| 操作 | 一个标记为 `@Action` 的 Python 函数，用作 `POST`，可从表单或作为类型化函数调用 ([actions](../guides/actions.md)) |
| 表单 | 一个 HTML 表单，发布到一个 Action，验证错误返回到页面 ([actions](../guides/actions.md)) |
| 导航 | 预取链接，以及读取路径、查询、cookie 和会话的挂钩 ([hooks](../routing/fbr/navigation/hooks.md)) |
| 数据获取 | 由需要它的页面或处理程序完成； Nexy 不提供客户端数据层 ([handlers](../routing/fbr/handlers/README.md)) |

## Nexy 不做什么

身份验证、授权、数据库、国际化、后台作业、电子邮件、付款和搜索是 **您的应用程序的责任**，而不是框架的责任。 Nexy 给出了扩展点并说明了每个扩展点的插入位置：请参阅[边界](../architecture.md#boundaries)。

原因并不是极简主义本身：选择 ORM 或身份验证库的框架已经决定了只有您的应用程序才能决定的事情。

## 后续步骤

- [架构](../architecture.md)：层，以及谁构建什么
- [项目结构](project-structure.md)：项目的每个文件夹和文件
- [词汇表](../reference/glossary.md)：相同的单词，在一个字母索引中
- [Nexy 的工作原理](how-nexy-works.md)：一个请求，一步一步
