# 升级到2.2

当您从 2.1 迁移到 2.2 时，现有项目会发生哪些变化，以及如何处理。完整列表位于[变更日志](../../CHANGELOG.md)中。

```bash
uv add "nexy>=2.2"            # or: uv tool upgrade nexy
nx build
nx test
```

## 你可能需要改变什么

| 更改 | 执行此操作 |
|---|---|
| **`.mdx` 仅由 Vite 编译。** Python 编译器不再渲染它 | 将 React 或 Preact 保留在 `useFF` 中并安装 `@mdx-js/rollup`、`remark-gfm` 和 `@mdx-js/react`。没有组件的页面可以是 `.md` 文件，而不是 |
| **`useBadge` 消失了。** “Built with Nexy”标签不再存在 | 从 `nexyconfig.py` 中删除该行。剩余的行将被忽略 |
| **`nx check` 不再编译 `.mdx`** | 没有：Vite 在构建 | 时报告 MDX 错误

## 什么保持不变

- 您的路线、布局、操作和配置。
- 现有项目保留自己的起始页。新的入门设计仅适用于升级后创建的项目。
- 开发工具栏和 `useDevTools`。

## 2.2 中的新功能

- **代理文件。** `nx new` 写入 `AGENTS.md`、`CLAUDE.md` 以及编码代理的技能。对于您已有的项目，请运行 `nx skills`。它永远不会覆盖您编写的文件。参见[编码剂](../guides/ai-agents.md)。
- **持续运行的开发服务器。** 当您的应用程序无法启动时，`nx dev` 会报告原因并等待下一次更改而不是退出。
- **为 Tailwind 或 UnoCSS 中的每个框架提供一个新的启动器**，具有相同的页面和组件。
- **UnoCSS 读取服务器项目中的 `.nexy` 文件**。如果将 UnoCSS 与 `.nexy` 页面一起使用，请添加 [[疑难解答]](../guides/troubleshooting.md) 中所示的 `content` 块。

## 更正文档

三页纸说了一些代码不做的事情。如果您关注了他们，请检查您的文件：

- `.nexy` 组件将其子组件放置为 `<Slot />`（大写 S），而不是 `<slot />`。
- `.nexy` 组件文件以 PascalCase 命名：它作为 Python 模块导入，因此连字符无法编译。
- 对于 `.mdx`，当文件导入 `preact` 时，框架为 Preact，否则为 React。

## 下一步去哪里

- [文档索引](../README.md)：您正在构建的页面
- [故障排除](../guides/troubleshooting.md)：人们首先遇到的问题
- [配置](../reference/config.md)：每个 `use*` 字段及其默认值
