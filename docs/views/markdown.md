# Markdown and MDX

Two formats for content pages: `.md` when you only need Markdown, `.mdx` when you need components.

## `.md`: pure Markdown

A `.md` file is pure content. Nexy renders it with `cmarkgfm` (GFM), adds heading IDs, derives a
table of contents, and wraps it in the nearest `layout.*`.

```md filename="src/routes/about.md"
# About

Nexy is a fullstack Python meta-framework.
```

- Locale variants: `about.fr.md` maps to a locale-specific route.
- Frontmatter in `.md` is not used as Python logic. If you need server logic, use `.nexy`.
- Layout wrapping, error pages and dynamic segments work the same way as other pages.

## `.mdx`: Markdown with components

`.mdx` files are compiled by the framework route pipeline (React or Preact). Components are rendered
in the framework, server-rendered like other component routes.

- Requires `useFF` to be React or Preact.
- The framework is auto-detected from imports; if both are imported, React is used.
- Locale variants are supported.

> **Good to know**: use `.nexy` if you need Python logic in frontmatter.

## Next steps

- [.nexy files](nexyfile.md): the native page format
- [Views](README.md): choose a format
- [i18n](../guides/i18n.md): locale variants
