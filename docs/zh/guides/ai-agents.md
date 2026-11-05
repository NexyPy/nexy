# 编码剂

使用 `nx new` 制作的项目包含编码代理按照您的方式编写 Nexy 代码所需的规则：工作顺序、代码和编写规则以及每个主题的一项技能。此页面介绍了您获得的内容、其去向以及如何保持最新状态。在 Nexy 上工作本身是一项不同的工作：读取存储库的根 `AGENTS.md`。

## `nx new` 添加了什么

| 文件 | 阅读者 | 持有 |
|---|---|---|
| `AGENTS.md` | Codex，OpenCode | 项目堆栈、工作顺序、规则、技能列表 |
| `CLAUDE.md` | Claude Code | 一行，`@AGENTS.md`，所以两者读取相同的文本 |
| `.agents/skills/` | Codex，OpenCode | 技能 |
| `.claude/skills/` | Claude Code，OpenCode | 相同的技能 |

`AGENTS.md` 简短且量身定制。客户端路由的 Vue 项目显示为“客户端路由，Vue，样式为 Tailwind”； API 项目被告知没有视图。仅复制适合的技能：React 项目获得 `nexy-react` 但没有 Vue 技能，服务器项目获得 `.nexy` 和 Markdown 技能，API 项目没有关于视图的技能。

要跳过所有这些，请使用 `nx new --no-agents` 创建项目。

## 技能

| 技能 | 封面 |
|---|---|
| `nexy-principles` | 工作顺序、代码规则、编写规则 |
| `nexy-ux-audit` | 在任何视图之前运行的体验和信息架构审核 |
| `nexy-project` | 模式、文件夹、文件约定、配置、命令 |
| `nexy-file` | `.nexy` 页面、道具、挂钩、岛屿 |
| `nexy-markdown` | `.md` 和 `.mdx` 内容 |
| `nexy-react`、`nexy-preact`、`nexy-solid`、`nexy-vue`、`nexy-svelte` | 客户端框架的惯用代码 |
| `nexy-styling` | Tailwind、UnoCSS 或纯 CSS，以及设计标记 |
| `nexy-backend` | API 处理程序、操作、WebSocket、ISR、中间件 |
| `nexy-modular` | 模块化路由器的控制器、模块、注入和防护 |
| `nexy-security` | 依赖项、输入、会话、授权、秘密 |
| `nexy-testing` | 测试优先循环和门 |
| `nexy-framework-dev` | 改变 Nexy 本身，而不是用 Nexy 构建的项目 |

他们执行的规则是：在构建视图之前审核体验，首先编写失败的测试，一个函数执行一种处理，一个类承载一种意图，一个文件夹包含一组相关意图，没有表情符号，真正的 SVG 图标，为人们编写的纯文本，并且 React、Vue、Svelte、Solid 或 Preact 中没有手写的 DOM 脚本。

## 将它们添加到现有项目中

```bash
nx skills
```

在项目的根目录下运行它。它读取 `nexyconfig.py` 和 `package.json` 来查找堆栈，复制匹配的技能，并在缺少时写入 `AGENTS.md` 和 `CLAUDE.md`。

它永远不会覆盖您编写的文件：保留现有的 `AGENTS.md` 或 `CLAUDE.md`，并且命令会告诉您这一点。如果您需要的话，可以手动将技能列表添加到您自己的文件中。你自己的 `.claude/skills/` 或 `.agents/skills/` 技能被保留；仅刷新 `nexy-*` 技能。

升级 Nexy 后再次运行 `nx skills` 以刷新副本，并提交结果以便整个团队共享。

## 代理人如何找到他们

- `AGENTS.md`（或导入它的 `CLAUDE.md`）在每个会话开始时读取。它命名了技能。
- 每个技能都以名称和描述开头，说明其涵盖的内容以及何时加载。代理首先读取这些内容，并仅在任务匹配时才打开技能。

这些技能遵循开放的[特工技能格式](https://agentskills.io/specification)，因此读取 `SKILL.md` 文件夹的其他特工也可以使用它们。

## 他们不做什么

技能告诉代理人如何工作；他们不会使其输出正确。保留自己的支票：

- 阅读代理更改的内容。
- 运行 `nx check`、`nx test` 和 `nx build`。技能要求这一点并报告输出，而不是总结。
- 审核代理添加的依赖项（`nexy-security` 解释了如何进行）。

技能中的示例通过 Nexy 自己的测试进行检查：导入存在、配置字段存在、命令存在、Python 解析。这抓住了漂移，而不是误判。

## 地图

当代理知道哪个页面包含答案时，它会更快地回答。

| 你需要 | 阅读 |
|---|---|
| 产品，在一页中 | [自述文件](../README.md) |
| 运行一个项目 | [入门](../getting-started/quick-start.md) |
| 文件的 URL | [路由](../routing/README.md) |
| 动态段、布局、错误页面 | [页数](../routing/fbr/pages/README.md) |
| 当前路径、查询、cookies、会话 | [钩子](../routing/fbr/navigation/hooks.md) |
| 编辑页面 | [.nexy 文件](../views/nexy/README.md) 或 [视图](../views/README.md) |
| Markdown 或 MDX | [降价](../views/nexy/markdown.md) |
| 内置 HTML 帮助器 | [组件](../views/nexy/components.md) |
| 渲染模式 | [SSR](../rendering/ssr.md)、[CSR](../rendering/csr.md)、[ISR](../rendering/isr.md) |
| 一个 WebSocket | [网络套接字](../routing/fbr/realtime/websocket.md) |
| 控制器和模块 | [模块化](../routing/modular/README.md) |
| 添加端点 | [API](../routing/fbr/handlers/README.md) |
| 从页面发布的表单 | [行动](actions.md) |
| 请求失败的原因以及哪个页面应答了该请求 | [例外情况](../reference/exceptions.md) |
| 翻译 | [国际化](i18n.md) |
| 一个配置字段 | [配置](../reference/config.md) |
| 测试应用程序 | [测试](testing.md) |
| 客户端构建 | [前端](frontend.md) |

## 项目不变量

1. 生成 `__nexy__/`。永远不要编辑它，永远不要提交它。删除它以强制进行干净的构建。
2. 每个 URL 一个文件。同一路径的 `index.nexy` 和 `index.py` 是一个错误，而不是优先级规则。
3. `src/routes/` 内的保留名称：`layout.nexy`、`loading.nexy`、`errors.nexy`、`notfound.nexy`、`dependencies.py`、`__init__.py`。不要将它们用于内容。
4. `.nexy` frontmatter 是根据请求运行的 Python。无模块级副作用：无文件句柄、无数据库连接、导入时无网络调用。
5. `src/routes/` 中的 `.py` 是 API 处理程序。方法是函数名称（`GET`、`POST`、...）。
6. 配置存在于 `nexyconfig.py` 中，而不是在环境变量中，也不在分散的常量中。
7. `.nexy` 模板中自动转义已关闭：使用 `| e` 转义不受信任的值。

```bash
nx dev      # development
nx build    # production build
nx start    # production server
nx test     # pytest, --client adds vitest
```

当文档和代码不一致时，请相信代码并这样说：`nexy/core/config.py` 包含每个选项，`nexy/modules/routers/fbrouter/` 路由规则，`nexy/modules/compiler/` `.nexy` 文件如何成为模块。

## 后续步骤

- [CLI](../reference/cli.md)：`nx new` 和 `nx skills`
- [文件约定](../reference/file-conventions.md)：保留名称和路由规则
- [词汇表](../reference/glossary.md)：这些规则所依赖的单词
- [安全](../reference/security.md)：安全技能指向的版本
