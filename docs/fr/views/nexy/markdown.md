# Markdown et MDX

Deux formats pour les pages de contenu : `.md` lorsque vous n'avez besoin que de Markdown, `.mdx` lorsque vous avez besoin de composants.

## `.md` : pur Markdown

Un fichier `.md` est du pur contenu. Nexy le restitue avec `cmarkgfm` (GFM), ajoute des identifiants de titre, dérive une table des matières et l'enveloppe dans le `layout.*` le plus proche.

```md filename="src/routes/about.md"
# About

Nexy is a fullstack Python meta-framework.
```

- Frontmatter dans `.md` n'est pas utilisé comme logique Python. Si vous avez besoin d'une logique serveur, utilisez `.nexy`.
- L'habillage de la mise en page, les pages d'erreur et les segments dynamiques fonctionnent de la même manière que les autres pages.

## `.mdx` : Markdown avec composants

Les fichiers `.mdx` sont compilés par **Vite**, via le pipeline framework route (React ou Preact). Python écrit uniquement le wrapper mince qui dessert la route ; il ne compile ni ne restitue jamais MDX lui-même. Les composants sont rendus par le framework, rendus par le serveur comme les autres routes de composants et pré-rendus au format HTML par `nx build`.

- Nécessite que `useFF` soit React ou Preact.
- Nécessite les packages facultatifs `@mdx-js/rollup`, `remark-gfm` et `@mdx-js/react` (et `@mdx-js/esbuild` pour la build). Vite vous indique lequel manque.
- Le framework est auto-détecté à partir des importations : Preact lorsque le fichier importe `preact`, React sinon.

> [!REMARQUE]
> utilisez `.nexy` si vous avez besoin de la logique Python en premier lieu.

## Prochaines étapes

- [fichiers .nexy](README.md) : le format de page natif
- [Vues](../README.md) : choisissez un format
- [i18n](../../guides/i18n.md) : internationalisation
