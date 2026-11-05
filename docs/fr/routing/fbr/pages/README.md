# Pages

Un fichier d'échange renvoie du HTML. Le type de fichier que vous utilisez modifie la façon dont il est produit : voir [vues](../../../views/README.md). Cette section couvre les règles de routage qui s'appliquent à chaque format de page.

| Page | Ce qu'il couvre |
|---|---|
| [Routes dynamiques](dynamic-routes.md) | `[slug]`, `[...path]`, groupes de routes, segments typés |
| [Pages d'erreur](../errors/README.md) | `notfound.nexy`, `errors.nexy`, JSON pour les clients API |
| [Mise en page](../layouts/README.md) | Une page par type de fichier de mise en page |
| [Héritage](../inheritance.md) | Comment les mises en page et les dépendances s'empilent |

## Une page minimale

```nexy filename="src/routes/about.nexy"
---
title: prop[str] = "About"
---
<h1>{{ title }}</h1>
```

Il est servi à `/about`. Le frontmatter entre les lignes `---` est Python ; le balisage en dessous est Jinja2. Voir [fichiers .nexy](../../../views/nexy/README.md).

## Formats de pages

| Mode | Fichier | Produit |
|---|---|---|
| Serveur | `.nexy` | HTML rendu par le serveur à partir de Python et Jinja2 |
| Serveur | `.md`, `.mdx` | pages de contenu |
| Composants du framework client | `.tsx`, `.jsx`, `.vue`, `.svelte` | rendus et parcourus dans le navigateur |

Les deux modes ne peuvent pas être mélangés dans un seul projet. Voir [Mode serveur et mode client](../modes.md). Les composants clients peuvent toujours apparaître en mode serveur, sous forme d'[îlots](../../../rendering/islands.md) dans une page `.nexy`.

## Mise en cache incrémentielle

Ajoutez `revalidate = 60` à une page `.nexy` pour la mettre en cache avec une revalidation obsolète. Voir [ISR](../../../rendering/isr.md).

## Lecture de la demande

Une page lit le chemin, la chaîne de requête, les cookies et la session via des hooks. Voir [Crochets](../navigation/hooks.md).

## Prochaines étapes

- [Itinéraires dynamiques](dynamic-routes.md)
- [Pages d'erreur](../errors/README.md)
- [Routage modulaire](../../modular/README.md) : des contrôleurs au lieu de fichiers
