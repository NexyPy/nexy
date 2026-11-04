# Markdown 和 MDX

内容页面有两种格式：当您只需要 Markdown 时为 `.md`，当您需要组件时为 `.mdx`。

## `.md`：纯 Markdown

`.md` 文件是纯内容。 Nexy 使用 `cmarkgfm` (GFM) 渲染它，添加标题 ID，导出
目录，并将其包装在最近的 `layout.*` 中。

```md filename="src/routes/about.md"
# About

Nexy is a fullstack Python meta-framework.
```

`.md` 中的 - Frontmatter 不用作 Python 逻辑。如果您需要服务器逻辑，请使用`.nexy`。
- 布局换行、错误页面和动态段的工作方式与其他页面相同。

## `.mdx`：带有组件的 Markdown

`.mdx` 文件由 **Vite** 通过框架路由管道（React 或 Preact）编译。蟒蛇
只编写为路由提供服务的薄包装器；它从不编译或渲染 MDX 本身。
组件由框架渲染，像其他组件路由一样由服务器渲染，并且
由 `nx build` 预渲染为 HTML。

- 要求`useFF`是React或Preact。
- 需要可选包 `@mdx-js/rollup`、`remark-gfm` 和 `@mdx-js/react`（以及
  `@mdx-js/esbuild` 用于构建）。 Vite 告诉你缺少哪一项。
- 框架是从导入中自动检测的：当文件导入时Preact `preact`，React
  否则。

> [！注意]
> 如果你需要在 frontmatter 中使用 Python 逻辑，请使用 `.nexy`。

## 后续步骤

- [.nexy 文件](README.md)：本机页面格式
- [视图](../README.md)：选择格式
- [i18n](../../guides/i18n.md)：国际化