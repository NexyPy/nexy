# Markdown 和 MDX

内容页面有两种格式：当您只需要 Markdown时为 `.md`，当您需要组件时为 `.mdx`。

## `.md`：纯 Markdown

`.md` 文件是纯内容。 Nexy 将其呈现为 GitHub 风格的 Markdown（表格、任务列表、删除线、链接），添加标题 ID，派生目录，并将其包装在最近的 `layout.*` 中。

```md filename="src/routes/about.md"
# About

Nexy is a fullstack Python meta-framework.
```

- `.md` 中的 Frontmatter 不用作 Python 逻辑。如果您需要服务器逻辑，请使用 `.nexy`。
- `.md` 页面中的原始 HTML 显示为文本，从不运行。如果您需要 HTML，请使用 `.nexy`。
- 布局换行、错误页面和动态段的工作方式与其他页面相同。

## `.mdx`: Markdown 与组件

`.mdx` 文件由 **Vite** 通过框架路由管道（React 或 Preact）编译。 Python 只编写为路由提供服务的瘦包装器；它从不编译或渲染 MDX 本身。组件由框架渲染，像其他组件路由一样进行服务器渲染，并由 `nx build` 预渲染为 HTML。

- 要求 `useFF` 为 React 或 Preact。
- 需要可选包 `@mdx-js/rollup`、`remark-gfm` 和 `@mdx-js/react`（以及用于构建的 `@mdx-js/esbuild`）。 Vite 告诉您缺少哪一个。
- 当文件导入 `preact` 时，框架会从导入中自动检测：Preact，否则导入 React。

> [!NOTE]
> 如果您需要在 frontmatter 中使用 Python 逻辑，请使用 `.nexy`。

## 后续步骤

- [.nexy 文件](README.md)：本机页面格式
- [视图](../README.md)：选择格式
- [i18n](../../guides/i18n.md)：国际化
