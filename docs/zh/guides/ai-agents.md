# 编码剂

使用 `nx new` 制作的项目包含编码代理按照您的方式编写 Nexy 代码所需的规则：
工作顺序、代码和写作规则以及每个主题的一项技能。此页面说明了您得到的内容，
它去了哪里，以及如何保持最新状态。在 Nexy 上工作本身是一项不同的工作：阅读
存储库的根`AGENTS.md`。

## `nx new` 添加了什么

| 文件 | 由 | 读取并保存 |
|---|---|---|
| `AGENTS.md` | Codex、OpenCode | 项目堆栈、工作顺序、规则、技能列表 |
| `CLAUDE.md` | 克劳德代码 | 一行，`@AGENTS.md`，所以两者读取相同的文本 |
| `.agents/skills/` | Codex、OpenCode | 技能 |
| `.claude/skills/` | Claude Code、OpenCode | 相同的技能 |

`AGENTS.md` 简短且量身定制。客户端路由的 Vue 项目显示为“客户端路由、Vue、样式
顺风”； API 项目被告知没有视图。仅复制适合的技能：
React 项目获得 `nexy-react` 且没有 Vue 技能，服务器项目获得 `.nexy` 和 Markdown
技能，API 项目没有关于视图的技能。

要跳过所有这些，请使用 `nx new --no-agents` 创建项目。

## 技能

| 技能 | 覆盖 |
|---|---|
| `nexy-principles` | 工作顺序、代码规则、编写规则 |
| `nexy-ux-audit` | 在任何视图之前运行的经验和信息架构审核 |
| `nexy-project` | 模式、文件夹、文件约定、配置、命令 |
| `nexy-file` | `.nexy` 页面、道具、挂钩、岛屿 |
| `nexy-markdown` | `.md` 和 `.mdx` 内容 |
| `nexy-react`、`nexy-preact`、`nexy-solid`、`nexy-vue`、`nexy-svelte` | 客户端框架的惯用代码 |
| `nexy-styling` | Tailwind、UnoCSS 或纯 CSS 以及设计标记 |
| `nexy-backend` | API 处理程序、操作、WebSocket、ISR、中间件 |
| `nexy-modular` | 模块化路由器的控制器、模块、注入和防护装置 |
| `nexy-security` | 依赖项、输入、会话、授权、秘密 |
| `nexy-testing` | 测试优先循环和门 |
| `nexy-framework-dev` | 更改 Nexy 本身，而不是使用 Nexy 构建的项目 |

他们执行的规则：在构建视图之前审核体验，首先编写失败的测试，
一个功能做一种治疗，一类承载一种意图，一个文件夹容纳一套
相关意图，没有表情符号，真正的 SVG 图标，为人们编写的纯文本，没有手写
React、Vue、Svelte、Solid 或 Preact 中的 DOM 脚本。

## 将它们添加到现有项目中

```bash
nx skills
```

在项目的根目录下运行它。它读取 `nexyconfig.py` 和 `package.json` 来查找堆栈，
复制匹配的技能，缺少时写`AGENTS.md`和`CLAUDE.md`。

它永远不会覆盖您编写的文件：保留现有的 `AGENTS.md` 或 `CLAUDE.md`，并且
命令告诉你了。如果您需要的话，可以手动将技能列表添加到您自己的文件中。一项技能
你自己的`.claude/skills/`或`.agents/skills/`被保留；只有 `nexy-*` 技能是
神清气爽。

升级 Nexy 后再次运行 `nx skills` 以刷新副本，并提交结果，以便
整个团队分享它。

## 特工如何找到他们

- `AGENTS.md`（或导入它的`CLAUDE.md`）在每个会话开始时读取。它命名
  的技能。
- 每个技能都以名称和描述开头，说明其涵盖的内容以及何时加载。的
  代理首先读取这些内容，并仅在任务匹配时才打开技能。

技能遵循开放的【特工技能格式](https://agentskills.io/specification)，所以其他
读取 `SKILL.md` 文件夹的代理也可以使用它们。

## 他们不做什么

技能告诉代理人如何工作；他们不会使其输出正确。保留自己的支票：

- 了解代理更改的内容。
- 运行`nx check`、`nx test`和`nx build`。技能需要这个并且输出是
  报道，未总结。
- 审核代理添加的依赖项（`nexy-security`解释了如何操作）。

技能中的示例经过 Nexy 自己的测试检查：导入存在、配置
字段存在，命令存在，Python 解析。这抓住了漂移，而不是误判。

## 地图

当代理知道哪个页面包含答案时，它会更快地回答。

|您需要|阅读|
|---|---|
| 产品，一页 | [自述文件 ](../README.md) |
| 运行项目 | [入门](../getting-started/quick-start.md) |
| 文件的 URL | [路由](../routing/README.md) |
| 动态段、布局、错误页面 | [页面](../routing/fbr/pages/README.md) |
| 当前路径、查询、cookie、会话 | [hooks](../routing/fbr/navigation/hooks.md) |
| 编辑页面 | [.nexy 文件](../views/nexy/README.md) 或 [视图](../views/README.md) |
| Markdown 或 MDX | [markdown](../views/nexy/markdown.md) |
| 内置 HTML 帮助器 | [组件 ](../views/nexy/components.md) |
| 渲染模式 | [SSR](../rendering/ssr.md)、[CSR](../rendering/csr.md)、[ISR](../rendering/isr.md) |
| WebSocket | [websocket](../routing/fbr/realtime/websocket.md) |
| 控制器和模块 | [模块化](../routing/modular/README.md) |
| 添加端点 | [API](../routing/fbr/handlers/README.md) |
| 从页面 | [操作 ](actions.md) | 发布的表单
| 请求失败的原因以及哪个页面响应它 | [异常](../reference/exceptions.md) |
| 翻译 | [i18n](i18n.md) |
| 配置字段 | [配置](../reference/config.md) |
| 测试应用程序 | [测试 ](testing.md) |
|客户端构建|[前端](frontend.md)|

## 项目不变量

生成1. `__nexy__/`。永远不要编辑它，永远不要提交它。删除它以强制进行干净的构建。
2. 每个 URL 一个文件。同一路径的 `index.nexy` 和 `index.py` 是一个错误，而不是优先级规则。
3. `src/routes/`内的保留名称：`layout.nexy`、`loading.nexy`、`errors.nexy`、
   `notfound.nexy`、`dependencies.py`、`__init__.py`。不要将它们用于内容。
4. `.nexy` frontmatter 是根据请求运行的 Python。无模块级副作用：无文件
   句柄，没有数据库连接，导入时没有网络调用。
`src/routes/` 中的 5. `.py` 是一个 API 处理程序。方法是函数名称（`GET`、`POST`、...）。
6. 配置位于`nexyconfig.py`中，而不是在环境变量中，也不在分散的环境变量中
   常数。
7. 自动转义在 `.nexy` 模板中已关闭：使用 `| e` 转义不受信任的值。

```bash
nx dev      # development
nx build    # production build
nx start    # production server
nx test     # pytest, --client adds vitest
```

当文档和代码不一致时，请相信代码并这样说：`nexy/core/config.py` 包含每个
选项，`nexy/modules/routers/fbrouter/`路由规则，`nexy/modules/compiler/`如何`.nexy`
文件成为模块。

## 后续步骤

- [CLI](../reference/cli.md)：`nx new` 和 `nx skills`
- [文件约定](../reference/file-conventions.md)：保留名称和路由规则
- [词汇表](../reference/glossary.md)：这些规则所依赖的单词
- [安全](../reference/security.md)：安全技能指向的版本楼层