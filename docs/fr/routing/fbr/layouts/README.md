# Mises en page

Une mise en page enveloppe chaque page sous son répertoire. Les mises en page s'imbriquent : la page s'affiche à l'intérieur de la mise en page de son répertoire, qui s'affiche à l'intérieur de la mise en page du répertoire parent, jusqu'à la mise en page racine.

Il y a une page par type de fichier de mise en page :

| Fichier | Mode | Propriétaire du document HTML | Page |
|---|---|---|---|
| `layout.nexy` | serveur (`useCSR = False`) | oui, à la racine | [layout.nexy](../../../views/nexy/layouts.md) |
| `layout.tsx` | client (`useCSR = True`) | oui, à la racine (React, Solid, Preact) | [React](../../../views/react/differences.md), [Solid](../../../views/solid/differences.md), [Preact](../../../views/preact/differences.md) |
| `layout.vue` | client | oui, à la racine | [layout.vue](../../../views/vue/differences.md) |
| `layout.svelte` | client | oui, à la racine | [layout.svelte](../../../views/svelte/differences.md) |

Un projet utilise une famille. `layout.nexy` et `layout.tsx` ne peuvent pas vivre dans le même projet : le mode serveur a des mises en page `.nexy` et le mode client a des mises en page de framework. Voir [Mode serveur et mode client](../modes.md).

## Comment le navigateur reprend le document

En mode client, Nexy restitue la disposition racine dans Node, la première réponse est donc un document complet. Le navigateur le prend ensuite en charge de deux manières :

| Cadre | Reprise | Ce que cela signifie |
|---|---|---|
| React, Solid | **hydratation** de l'ensemble du document | le HTML du serveur est réutilisé tel quel |
| Preact, Vue, Svelte | **prise de contrôle du corps** | le framework construit le corps de la page et l'échange contre celui envoyé par le serveur |

Preact, Vue et Svelte ne peuvent pas hydrater un document entier : le `hydrate` de Preact construit un deuxième élément `<html>`, le compilateur de Vue supprime un `<script>` d'un modèle client et Svelte ne peut pas créer `<html>`, `<head>` ou `<body>` dans le navigateur. Donc pour eux les attributs `<html>`, `<head>` et `<body>` sont ceux envoyés par le serveur, et seul le corps est construit par le navigateur. En pratique :

- Placez le titre, les balises méta, les polices et le script du thème dans la mise en page racine : ils sont rendus par le serveur et restent tels quels.
- Une liaison sur `<html>`, `<head>` ou `<body>` (par exemple une classe réactive) est appliquée par le serveur mais ne se met pas à jour dans le navigateur. Modifiez-les à partir d'un script, comme le fait le script de thème.
- Le navigateur restitue le corps à partir de zéro au lieu de réutiliser le balisage du serveur, de sorte que le corps est remplacé une fois, dans la même tâche que le premier rendu.

## La disposition racine

La disposition racine est `src/routes/layout.<ext>`. Il est créé par `nx new` et c'est le seul endroit qui écrit `<!DOCTYPE html>`, `<html>`, `<head>` et `<body>` (chaque framework et `.nexy`). Les pages et les mises en page imbriquées ne les répètent jamais.

```text
src/routes/
├─ layout.*              root: the document
├─ index.*
└─ dashboard/
   ├─ layout.*           nested: UI only
   ├─ index.*
   └─ settings.*
```

`dashboard/index` s'affiche sous la forme `root layout > dashboard layout > page`.

## Groupes d'itinéraires

Un répertoire entre parenthèses peut avoir sa propre présentation sans changer d'URL :

```text
src/routes/
├─ layout.nexy
├─ (marketing)/
│  ├─ layout.nexy        wraps /pricing and /about only
│  ├─ pricing.nexy
│  └─ about.nexy
└─ (app)/
   └─ dashboard.nexy     only the root layout
```

## Persistance

En mode client une mise en page reste montée pendant que l'utilisateur navigue entre les pages qui la partagent : son DOM, son état et sa position de défilement sont conservés. En mode serveur, chaque navigation est un nouveau document.

## Prochaines étapes

- [layout.nexy](../../../views/nexy/layouts.md)
- [layout.tsx](../../../views/react/differences.md)
- [Héritage](../inheritance.md)
