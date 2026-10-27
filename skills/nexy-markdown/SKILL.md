---
name: nexy-markdown
description: Writing .md and .mdx content pages in Nexy. Markdown is rendered by Nexy; MDX is compiled by Vite and never by Python. Load it for any content page.
---

# Markdown and MDX

| Format | Use it for | Compiled by |
|---|---|---|
| `.md` | pure content | Nexy, at request time, with GFM |
| `.mdx` | content with components | **Vite**, through the framework route pipeline |

## `.md`

Nexy renders `.md` files, adds heading ids, derives a table of contents and wraps the page in the
nearest `layout.*`. Frontmatter is not Python. When a page needs server logic, write a `.nexy` page.

## `.mdx`

An `.mdx` file is a framework route (React or Preact). The Python side only writes a thin wrapper
module that serves it; Vite compiles the MDX and the build pre-renders it to HTML.

- Never compile, render or transform MDX in Python. If a task seems to need it, the task belongs in
  `nexy/modules/frontend/` (TypeScript), not in the compiler.
- It needs optional packages in the project: `@mdx-js/rollup`, `remark-gfm` and `@mdx-js/react`
  (`@mdx-js/esbuild` for the build).
- The framework is detected from the imports; React wins when both appear.

## Write for readers

Run [nexy-ux-audit](../nexy-ux-audit/SKILL.md) for content pages too: one page, one job, the answer
first, headings that are questions or tasks a person would recognise, and a title that matches the
link that leads to it.
