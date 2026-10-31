# Markdown and MDX

Two formats for content pages: `.md` when you only need Markdown, `.mdx` when you need components.

## `.md`: pure Markdown

A `.md` file is pure content. Nexy renders it with `cmarkgfm` (GFM), adds heading IDs, derives a
table of contents, and wraps it in the nearest `layout.*`.

```md filename="src/routes/about.md"
# About

Nexy is a fullstack Python meta-framework.
```

- Frontmatter in `.md` is not used as Python logic. If you need server logic, use `.nexy`.
- Layout wrapping, error pages and dynamic segments work the same way as other pages.

## `.mdx`: Markdown with components

`.mdx` files are compiled by **Vite**, through the framework route pipeline (React or Preact). Python
only writes the thin wrapper that serves the route; it never compiles or renders MDX itself.
Components are rendered by the framework, server-rendered like other component routes, and
pre-rendered to HTML by `nx build`.

- Requires `useFF` to be React or Preact.
- Requires the optional packages `@mdx-js/rollup`, `remark-gfm` and `@mdx-js/react` (and
  `@mdx-js/esbuild` for the build). Vite tells you which one is missing.
- The framework is auto-detected from imports: Preact when the file imports `preact`, React
  otherwise.

> [!NOTE]
> use `.nexy` if you need Python logic in frontmatter.

## Next steps

- [.nexy files](README.md): the native page format
- [Views](../README.md): choose a format
- [i18n](../../guides/i18n.md): internationalization
