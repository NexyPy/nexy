# Concepts de base

Le modèle mental, avant l'API : quatre niveaux de lecture, puis les notions qui reviennent à chaque
page. Chaque notion reçoit ici une ligne et un lien vers la page qui va plus loin.

## Comment lire ces documents

| Niveau | La question à laquelle il répond | Commencez par |
|---|---|---|
| Architecture de l'application | quelle couche répond à une requête et ce qu'elle refuse de faire | [Architecture](../architecture.md) |
| Structure de l'application | où réside le code et ce que devient un fichier | [Structure du projet](project-structure.md) |
| Présentation et rendu | ce que voit le lecteur, et qui produit le HTML | [Vues](../views/README.md), [Rendu](../rendering/README.md) |
| Interaction avec l'application | ce que fait le lecteur et ce qui s'exécute en réponse | [Actions](../guides/actions.md) |

Les niveaux sont lus une fois dans cet ordre. Après cela, une page dont vous avez besoin est une recherche, pas un cours.

## Architecture des applications

Trois façons de décider quel code répond à une URL. Ce sont des alternatives, pas des couches :

- **Routage basé sur des fichiers (FBR)** : un fichier sous `src/routes/` est une route. La valeur par défaut.
- **Routeur modulaire** : contrôleurs et modules sous `src/apps/`, déclarés auprès des décorateurs, pour un
  Base de code de style NestJS.
- **Routeur personnalisé** : un FastAPI existant `APIRouter` inclus dans l'application.

Choisir l’un des trois est une décision. Le choix d’un framework frontend en est un autre, distinct :
voir [Choisir un routeur](../routing/README.md) et [Vues](../views/README.md).

## Structure des candidatures

Cinq notions qu'un lecteur venant de Next.js fusionne généralement en une seule. Ce n'est pas la même chose,
et la différence explique la plupart des questions « pourquoi ma page ne s'affiche-t-elle pas ».

| Notion | Ce que c'est | Ce que ce n'est pas |
|---|---|---|
| **Route** | un modèle d'URL, produit par le chemin d'un fichier | un fichier : un fichier peut répondre à plusieurs URL (`[slug]`) |
| **Page** | un fichier de route qui restitue une vue : `.nexy`, `.md`, `.mdx`, `.tsx`, `.vue`, `.svelte` | un point de terminaison : il répond à un document, pas à des données |
| **Voir** | ce qui produit le corps d'une page : Jinja2 et Python, Markdown, ou un composant client | un itinéraire : une même vue peut servir plusieurs pages |
| **Composant** | un morceau réutilisable une page importe | une route : en mode serveur un composant n'est jamais servi seul |
| **Route handler** | la fonction d'un `.py` fichier de route, nommé d'après la méthode HTTP (`GET`, `POST`, …) | une page : il renvoie du JSON, un fichier ou un `Response` |
| **Endpoint** | le couple (URL, méthode) auquel un handler répond | un handler : un fichier peut répondre à plusieurs endpoints |

En une phrase : **une page est un fichier de route, une vue est ce qui la restitue, un composant est ce qu'une page
réutilise, un gestionnaire répond à un point de terminaison.**

Encore deux mots qui reviennent partout :

- **Layout** : un fichier `layout.*` qui enveloppe les pages sous son dossier ; la racine possède le code HTML
  documenter. Voir [Mise en page](../routing/fbr/layouts/README.md).
- **Dépendance** : une fonction qui s'exécute avant un gestionnaire, appliquée par route ou par dossier. Voir
  [Dépendances](../routing/fbr/dependencies/README.md).

## Présentation et rendu

Deux décisions indépendantes, souvent confondues :

- **Le format** décide quel fichier restitue la page : [Views](../views/README.md).
- **Le mode** décide qui produit le HTML et quand : [Rendu](../rendering/README.md).

| Notion | Une ligne |
|---|---|
| Mode serveur | le serveur restitue les pages `.nexy` et `.md` ; les composants sont des îlots ([modes](../routing/fbr/modes.md)) |
| Mode client | `useCSR = True` : les fichiers du framework sont les itinéraires, et la navigation se fait dans le navigateur |
| SSR, ISR, CSR, îles | quatre modes de rendu, décidés par page sauf CSR, qui est par projet ([rendu](../rendering/README.md)) |
| Hydratation | le navigateur attachant un framework au HTML que le serveur a déjà envoyé ([îles](../rendering/islands.md)) |
| Props | les valeurs qu'un parent transmet à un composant, déclarées `name: prop[type]` dans un fichier `.nexy` ([fichiers .nexy](../views/nexy/README.md)) |

## Interaction avec les applications

| Notion | Une ligne |
|---|---|
| Action | une fonction Python marquée `@Action`, servie de `POST`, appelable depuis un formulaire ou comme fonction typée ([actions](../guides/actions.md)) |
| Formulaire | un formulaire HTML qui publie sur une action, avec des erreurs de validation revenant sur la page ([actions](../guides/actions.md)) |
| Liens de navigation | qui prélevent et hooks qui lisent le chemin, la requête, les cookies et la session ([hooks](../routing/fbr/navigation/hooks.md)) |
| Récupération des données | effectuée par la page ou le gestionnaire qui en a besoin ; Nexy ne fournit aucune couche de données client ([handlers](../routing/fbr/handlers/README.md)) |

## Ce que Nexy ne fait pas

Authentification, autorisation, base de données, internationalisation, tâches en arrière-plan, courrier électronique, paiements et
la recherche relève de la **responsabilité de votre application**, et non de celle du framework. Nexy donne la prolongation
pointe et dit où brancher chacun d'eux : voir [les limites](../architecture.md#boundaries).

La raison n'est pas le minimalisme en soi : un framework qui sélectionne votre ORM ou votre bibliothèque d'authentification
a décidé quelque chose que seule votre application peut décider.

## Étapes suivantes

- [Architecture](../architecture.md) : les couches, et qui construit quoi
- [Structure du projet](project-structure.md) : chaque dossier et fichier d'un projet
- [Glossaire](../reference/glossary.md) : les mêmes mots, dans un seul index alphabétique
- [Comment fonctionne Nexy](how-nexy-works.md) : une requête, étape par étape