# Markdown et MDX

Deux formats pour les pages de contenu : `.md` lorsque vous n'avez besoin que de Markdown, `.mdx` lorsque vous avez besoin de composants.

## `.md` : pur Markdown

Un fichier `.md` est du pur contenu. Nexy renders it as GitHub-flavoured Markdown (tables, task lists, strikethrough, links), adds heading IDs, derives a table of contents, and wraps it in the nearest `layout.*`.

```md filename="src/routes/about.md"
# About

Nexy is a fullstack Python meta-framework.
```

- Frontmatter dans `.md` n'est pas utilisé comme logique Python. Si vous avez besoin d'une logique serveur, utilisez `.nexy`.
- Raw HTML in a `.md` page is shown as text, never run. Si vous avez besoin de HTML, utilisez `.nexy`.
- L'habillage de la mise en page, les pages d'erreur et les segments dynamiques fonctionnent de la même manière que les autres pages.

## `.mdx` : Markdown avec composants

`.mdx` files are compiled by **Vite**, through the framework route pipeline (React or Preact). Python only writes the thin wrapper that serves the route; il ne compile ni ne restitue jamais MDX lui-même. Components are rendered by the framework, server-rendered like other component routes, and pre-rendered to HTML by `nx build`.

- Nécessite que `useFF` soit React ou Preact.
- Requires the optional packages `@mdx-js/rollup`, `remark-gfm` and `@mdx-js/react` (and `@mdx-js/esbuild` for the build). Vite vous indique lequel manque.
- The framework is auto-detected from imports: Preact when the file imports `preact`, React otherwise.

> [!NOTE]
> use `.nexy` if you need Python logic in frontmatter.

## Prochaines étapes

- [Fichiers .nexy](README.md) : le format de page natif
- [Vues](../README.md) : choisissez un format
- [i18n](../../guides/i18n.md) : internationalisation
