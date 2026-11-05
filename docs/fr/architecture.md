# Architecture

## Définition

Nexy est composé de cinq couches, et chacune a un travail que les autres ne font pas. Connaître la limite répond à la plupart des questions « pourquoi ça marche comme ça » : une page lente est une question de rendu, une mauvaise page est une question de routeur, une page qui n'apparaît jamais est une question de client.

Cette page est destinée aux personnes qui rédigent une candidature. Les packages de Nexy lui-même, et les mécanismes qui les sous-tendent, sont décrits dans `ARCHITECTURE.md` à la racine du référentiel, pour les contributeurs.

## Les couches

```diagram filename="Une demande, cinq niveaux"
Browser
   │
   ▼
Uvicorn ───── ASGI transport
   │
   ▼
Middleware ── sessions, CORS, gzip, trusted hosts, your own
   │
   ▼
Router ────── FBR | Modular | Custom ── picks the file that answers
   │
   ▼
Renderer ──── HTML (Jinja2, Markdown, Node) or JSON
   │
   ▼
Response
```

| Couche | Responsabilité | Ne fait pas |
|---|---|---|
| Uvicorn | accepter la connexion, parler ASGI | savoir ce qu'est une page |
| Middleware | décore la requête : session, CORS, gzip, hôtes de confiance, redirection HTTPS, le vôtre | choisissez une route |
| Le routeur | fait correspondre l'URL d'un fichier, avec ses mises en page, ses dépendances et ses pages d'erreur | produit du contenu |
| Le moteur de rendu | exécute la page et transforme son résultat en HTML ou JSON | récupère vos données |
| Le client | Vite et votre framework : bundles, hydratation, navigation client | répondre à une requête serveur |

## Qui construit quoi

| Acteur | Possède | Ne possède pas |
|---|---|---|
| Nexy | routage, rendu serveur, Actions, `.nexy` compilation, composants one origin | réactivité, données |
| Vite | bundles clients, le serveur de développement, le routage de rechargement à chaud | le rendu du serveur, les actions |
| Votre framework | les composants, la réactivité, l'écosystème | le routage, le document (Nexy le demande sa mise en page) |
| Votre application | données, authentification, autorisation, règles métier | transport, rendu |

La règle derrière le tableau : **Nexy construit ce qu'il possède et ne compile jamais ce que Vite compile.** Pour une route de composant, Python écrit un module wrapper mince qui pointe vers le fichier.

## Où une demande est décidée

1. Le middleware s'exécute et peut modifier la requête ou l'arrêter.
2. Le routeur sélectionne un fichier et les dispositions qui l'entourent.
3. Le moteur de rendu exécute ce fichier avec les données qu'il lit lui-même.
4. La réponse revient et la couche client prend le relais si la page a JavaScript.

Chaque étape, avec la priorité exacte entre les routeurs et l'ordre de `nx dev`, se trouve dans [Comment fonctionne Nexy](getting-started/how-nexy-works.md). Cette page ne le répète pas.

## Développement et production

Les mêmes cinq couches, assemblées deux fois :

| Calque | `nx dev` | `nx build` puis `nx start` |
|---|---|---|
| Le compilateur | s'exécute lorsque vous enregistrez | s'exécute une fois, à l'avance |
| Vite | serveur de développement, rechargement à chaud, proxy via le bundle d'origine | de Nexy écrit sur `__nexy__/client/`, pas de serveur de développement |
| Le nœud | restitue les documents client à la demande | les restitue lors de la construction, pas pendant la diffusion |
| Watcher | redémarre uvicorn lors d'un changement | absent |
| Origine | un port | un port |

Ce qui change, c'est *quand* le travail a lieu, et non *qui* le fait. Une page qui se comporte différemment entre les deux est un bug de la page, pas une propriété du mode.

## Limites

Nexy s'arrête volontairement en bordure de votre application :

| Préoccupation | Ce que Nexy propose | Ce que vous écrivez |
|---|---|---|
| Authentification | middleware de session, `AuthenticationMiddleware` lorsqu'elle est activée | la connexion, la recherche d'utilisateur, la politique en matière de cookies |
| Autorisation | `dependencies.py`, gardes, héritage par dossier | la règle elle-même |
| Base de données | rien : pas d'ORM, pas de migrations | la couche modèle ([Bases de données](guides/databases.md)) |
| Internationalisation | rien pour vos pages ; seule la CLI est traduite | la bibliothèque et les messages ([i18n](guides/i18n.md)) |
| Travaux en arrière-plan | rien : pas de file d'attente, pas de planificateur | un processus de travail |
| E-mail, paiements, recherche | rien | le service que vous choisissez |

La raison est la même pour les six : un framework qui sélectionne votre ORM ou votre bibliothèque d'authentification décide des choses que seule votre application peut décider. Le coût est explicite : rien n’est câblé pour vous, et les pages de guide ci-dessus indiquent où brancher chacun d’eux.

## Prochaines étapes

- [Comment fonctionne Nexy](getting-started/how-nexy-works.md) : une requête, étape par étape
- [Structure du projet](getting-started/project-structure.md) : où vit chaque couche dans un projet
- [Routing](routing/README.md) : les trois routeurs, et comment choisir
- [Rendu](rendering/README.md) : d'où vient le HTML
