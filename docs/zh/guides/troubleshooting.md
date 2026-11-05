# 故障排除

人们首先遇到的问题是你所看到的和要做的事情。每一个都来自真实的跑步。

## 页面回答 404 但其文件存在

查看运行 `nx dev` 或 `nx start` 的终端。当无法导入页面时，Nexy 会报告其文件和行错误，并且路由未注册：

```text
nexy » error __nexy__/src/routes/index.py:18  ImportError: cannot import name 'FrameworkLogo' ...
```

修复此处命名的导入。通常的原因是组件的函数名称与您导入的名称不匹配（请参阅下一项）以及路径中的拼写错误。

## `.nexy` 页面无法编译：“逻辑解析错误”

```text
src/components/live-panel.nexy - Logic Parse Error: invalid syntax
```

`.nexy` 组件作为 Python 模块导入，因此其文件名必须是有效的名称。连字符不是。以 PascalCase 命名它，`LivePanel.nexy`，并使用相同的名称导入它：

```nexy
from "@/components/LivePanel.nexy" import LivePanel
```

## 组件将其子组件呈现为文本 `<slot />`

`.nexy` 组件将其子组件放置在 `<Slot />` 中，其中 S 大写。小写的 `<slot />` 按原样保留在页面中。 Vue 有自己的 `<slot />`，不受影响。

## prop 显示变量的名称

```nexy
<Icon path=icon />          renders: icon
<Icon path="{{ icon }}" />  renders: the value of icon
```

没有大括号的属性是文本。将 Jinja 表达式放入属性中以传递计算值。

## `{{ ... }}` 中的值呈现为空

Jinja2 隐藏未定义的变量。声明您在 frontmatter (`title: prop[str] = ""`) 中使用的每个属性，并检查拼写。

## 实用程序类在 `.nexy` 页面 (UnoCSS) 中无效

UnoCSS 仅当文件扩展名位于其内容管道中时才读取文件。 `nx new` 使用 UnoCSS 创建的服务器项目已列出 `.nexy`；较旧的需要在 `uno.config.ts` 中使用它：

```ts
content: {
  filesystem: ['src/**/*.nexy'],
  pipeline: { include: [/\.(vue|svelte|[jt]sx|mdx?|astro|html|nexy)($|\?)/] },
},
```

Tailwind 自行查找 `.nexy` 文件。

## `.mdx` 页面请求包

```text
[nexy] MDX support requires optional packages that are not installed.
```

将它们安装在项目中：`@mdx-js/rollup`、`remark-gfm` 和 `@mdx-js/react`（加上 `nx build` 的 `@mdx-js/esbuild`）。 MDX 需要 `useFF` 中的 React 或 Preact。如果没有客户端框架，则将页面编写为 `.md`。参见[Markdown 和 MDX](../views/nexy/markdown.md)。

## 命令启动时的 `No module named 'sqlmodel'` （或任何包）

```text
nexy » nexyconfig.py cannot be loaded: No module named 'sqlmodel'. If it is a package, install it
in this Python (...) or activate the project's virtual environment.
```

该命令运行在错误的 Python中。你的项目的包（你的 ORM、你的库）位于它的 `.venv` 中，并且 `uvx nexy` 或全局 `nexy` 在它自己的没有它们的环境中运行。

从项目文件夹激活项目的虚拟环境，然后再次运行命令：

```bash
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

当提示符处于活动状态时，该提示符以 `(.venv)` 开头。或者使用 `uv run nexy dev` 跳过激活。如果项目中确实缺少该包，请使用 `uv add sqlmodel` 添加它。

## `nx dev` 显示错误并等待

当您的应用程序无法启动时，`nx dev` 会报告原因并等待下一个文件更改；它不退出。修复文件并保存。只有 Ctrl+C 才能停止它。

## 港口繁忙

`nx dev` 获取下一个空闲端口并打印它。要选择其中之一，请使用 `--port` 或在 `nexyconfig.py` 中设置 `usePort`。

## 主题在深色页面上闪烁白色

保存的主题必须在第一次绘制之前应用。将启动器的小脚本保留在根布局的 `<head>` 中，并将 `suppressHydrationWarning` 放在 React中的 `<html>` 上。

## 仍然卡住

- 阅读[文档索引](../README.md)中的功能页面。
- 如果文档和代码不一致，则代码是正确的：请打开一个命名页面的 [问题](https://github.com/NexyPy/nexy/issues)。
