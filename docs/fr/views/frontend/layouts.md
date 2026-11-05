# Dispositions frontales

Un **Layout** est un wrapper qui définit la structure partagée autour d'une ou plusieurs pages. Les mises en page permettent une expérience « semblable à celle d'une application » en préservant l'état et en évitant les rechargements d'une page entière pendant la navigation.

## Logique d'imbrication

Les mises en page suivent une structure hiérarchique basée sur l'arborescence des répertoires sous `src/routes/`.

1.  **Disposition racine** : chaque projet a une disposition racine (par exemple, `src/routes/layout.nexy`). Il s'agit de la seule mise en page responsable de la définition du shell du document : `<html>`, `<head>` et `<body>`.
2.  **Mises en page imbriquées** : n'importe quel dossier peut contenir son propre fichier `layout.*`. Cette mise en page enveloppe toutes les pages et sous-mises en page de ce dossier.
3.  **Héritage** : une page est enveloppée par toutes les mises en page depuis la racine jusqu'à son propre dossier.

## État partagé et composition

Les mises en page sont conçues pour être stables. Lors de la navigation entre deux pages partageant la même mise en page, la mise en page n'est **pas** restituée ; seul le contenu enfant change.

- **Slots** : les mises en page fournissent un "slot" (généralement `children` dans JSX ou `{{ content }}` dans Jinja2) où la page imbriquée est injectée.
- **Préservation de l'état** : étant donné que la mise en page reste montée, tout état qu'elle contient (par exemple, une requête de recherche dans un en-tête) est préservé pendant la navigation.

## Contraintes statiques

Pour les itinéraires pré-rendus (SSG), la disposition racine ne peut pas dépendre des données de temps de requête telles que les cookies ou les en-têtes. Il doit être représentable comme une coque statique que le client hydrate ensuite.

## Mise en œuvre du cadre

La mise en œuvre des slots et de l’imbrication varie légèrement selon le framework. Consultez le guide des **Différences** pour la technologie que vous avez choisie :

- [React Différences](../react/differences.md)
- [Vue Différences](../vue/differences.md)
- [Svelte Différences](../svelte/differences.md)
- [Solid Différences](../solid/differences.md)
- [Preact Différences](../preact/differences.md)
