# layout.nexy

Le fichier de mise en page du mode serveur (`useCSR = False`). La racine est propriétaire du document HTML.

## Disposition racine

```nexy filename="src/routes/layout.nexy"
---
from nexy import Vite

children: prop[NexyElement]
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My app</title>
  <Vite />
</head>
<body>
  <main>{{ children | safe }}</main>
</body>
</html>
```

- `<!DOCTYPE html>`, `<html>`, `<head>` et `<body>` vivent ici et nulle part ailleurs.
- `<Vite />` injecte les scripts et styles client une fois, dans le `<head>`.
- `{{ children | safe }}` est l'endroit où la page, ou la mise en page imbriquée suivante, s'affiche.

## Mise en page imbriquée

Un `layout.nexy` dans un sous-répertoire enveloppe ce sous-arbre et s'affiche à l'intérieur de son parent. Cela ne se répète pas
les balises du document :

```nexy filename="src/routes/blog/layout.nexy"
---
children: prop[NexyElement]
---
<nav>...</nav>
<article>{{ children | safe }}</article>
```

`blog/[slug].nexy` s'affiche sous la forme `layout.nexy > blog/layout.nexy > page`.

## Composants et îlots

Une mise en page peut importer des composants `.nexy` (un en-tête, un pied de page) et des composants clients. Un client
Le composant dans une mise en page est un [îlot](../../rendering/islands.md) comme les autres :

```nexy
---
from "@/components/Header.nexy" import Header
from "@/components/theme/theme.tsx" import Theme
---
<Header />
<Theme directive="client:idle" />
```

## Sans mise en page

Un projet sans `layout.nexy` répond quand même par un document valide : Nexy se rabat sur un minimum
shell avec `<!DOCTYPE html>`, la méta de la fenêtre d'affichage et les balises Vite. Ajoutez une mise en page dès que vous en avez besoin
un titre, des polices ou une navigation.

## Dans le routeur modulaire

Les contrôleurs choisissent leurs vues, ils composent donc eux-mêmes la mise en page :

```python
return useViews("src/apps/layout.nexy", context={"children": useViews("src/apps/app_view.nexy")})
```

## Ce qu'il ne peut pas faire

- Il ne peut pas coexister avec `layout.tsx`, `layout.vue` ou `layout.svelte` : un projet en mode serveur a
  aucune route client ([modes](../../routing/fbr/modes.md)).
- Il ne fonctionne pas sur le client : utilisez un îlot pour l'interactivité.

## Prochaines étapes

- [Mise en page](../../routing/fbr/layouts/README.md)
- [Héritage](../../routing/fbr/inheritance.md)
- [Fichiers .nexy](README.md)