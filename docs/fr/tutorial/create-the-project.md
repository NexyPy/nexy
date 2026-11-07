# Créer une application de notes avec Nexy, partie 1 : créer le projet

La première partie du didacticiel crée le projet que vous allez transformer en une application de notes et l'exécute dans votre navigateur en cinq minutes environ.

**Avant de commencer :** [uv](https://docs.astral.sh/uv/) et Node.js 20 ou plus récent. Le tutoriel suit le routeur choisi en haut du menu : basculez-le là et chaque partie montre les fichiers de ce routeur.

## Ce que vous construirez

À la fin du didacticiel, l'application comporte des pages et une API JSON pour les notes, une base de données, des comptes, des notes partagées par e-mail, des mises à jour en direct, des tests et une version de production. Chaque partie se termine par une application qui s'exécute, vous pouvez donc vous arrêter après n'importe laquelle d'entre elles.

## Créer le projet

```bash
uvx nexy new notes
```

Répondez aux questions de cette façon :

| Question | Réponse |
|---|---|
| Routeur basé sur des fichiers ? | `Yes` pour les routeurs basés sur des fichiers et personnalisés, `No` pour le routeur modulaire |
| Type de projet | `Web` |
| Routage côté client | `No` : le serveur restitue les pages |
| Cadre client | `React` : il revient dans l'unité 4, pour les îles |
| Style | `Tailwind CSS` |
| Importer un alias | `@` |
| ORM | `No database` : la partie 5 en ajoute un |

<!-- router:custom -->
Le routeur personnalisé est celui basé sur un fichier plus un `APIRouter` que vous possédez déjà. Le didacticiel crée l'application avec des fichiers ; [Inclure un FastAPI routeur](../routing/custom/README.md) existant montre comment monter le vôtre à côté d'eux.
<!-- /router -->

## Exécutez-le

```bash
cd notes
source .venv/bin/activate    # Windows: .venv\Scripts\activate
nexy dev
```

Ouvrez <http://localhost:3000>. Vous devriez voir la page d'accueil. Laissez `nexy dev` tourner : désormais, chaque fichier que vous enregistrez recharge le navigateur.

## Ce que tu as appris

- `uvx nexy new` crée un projet et installe ses packages Python et JavaScript.
- `nexy dev` le sert et recharge lors de la sauvegarde.
<!-- router:fbr,custom -->
- Les pages vivent dans `src/routes/` : la partie suivante en ajoute une.
<!-- /router -->
<!-- router:modular -->
- Les contrôleurs et leurs vues vivent dans `src/apps/` : la partie suivante en ajoute une.
<!-- /router -->

## Prochaines étapes

- [Partie 2 : pages et mises en page](pages-and-layouts.md)
- [Structure du projet](../getting-started/project-structure.md) : à quoi sert chaque fichier du projet
