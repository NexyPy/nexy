# Comment déployer une application Nexy sur Vercel ?

Exécutez `nx add vercel`, validez les fichiers générés avec votre sortie `nx build` et pointez le runtime Vercel Python sur `src/server.py:app`.

## Ajouter les fichiers de la plateforme

Depuis la racine d'un projet Nexy :

```bash
nx add vercel
nx build
```

`nx add vercel` écrit `src/server.py` et `vercel.json`. Il ajoute également des règles d'ignorance pour les fichiers qui changent pendant l'exécution de l'application : `__nexy__/build-cache.json`, `__nexy__/server.port`, `__nexy__/.temp/` et `__pycache__/`. La nouvelle exécution de la commande conserve les fichiers qui existent déjà et ne duplique pas les règles d'ignorance.

## Point Vercel sur l'appli

Dans les paramètres du projet Vercel, sélectionnez le runtime Python et utilisez `src/server.py:app` comme point d'entrée. Vercel découvre le nom `app` dans ce module ; `nx start` n'est pas impliqué.

Le `src/server.py` généré importe le `nexy.app.app` paresseux après avoir préparé le dossier de travail. Vous pouvez utiliser le même point d'entrée avec `uvicorn src.server:app` localement.

## Valider la sortie de build

Lorsque Vercel n'a pas de commande build, il reçoit uniquement ce que contient le référentiel. Validez `__nexy__/` après chaque `nx build`, avec les routes compilées, le bundle client sous `__nexy__/client/` et le manifeste à `__nexy__/client/.vite/manifest.json`.

Conservez `vite.config.ts` à la racine du projet et validez-le. En production, Nexy lit le manifeste Vite pour écrire la feuille de style et les balises de script, mais il émet ces balises uniquement lorsque `vite.config.ts` existe. Sans ce fichier, la page répond toujours à 200 et arrive sans CSS ni client JavaScript.

Ne validez pas `__nexy__/build-cache.json` : il contient les chemins absolus de la machine qui a exécuté la build. `__nexy__/server.port` appartient à `nx start` et `__nexy__/.temp/` est un espace de travail.

## Accepter un système de fichiers en lecture seule

Vercel monte le projet en lecture seule pendant le démarrage d'une application Python. Nexy écrit les fichiers générés au démarrage, donc un simple `from nexy.app import app` peut échouer avec `OSError: [Errno 30] Read-only file system`.

Le point d'entrée généré copie six éléments du projet dans un dossier temporaire accessible en écriture avant d'importer l'application : `src`, `__nexy__`, `public`, `nexyconfig.py`, `pyproject.toml` et `vite.config.ts`. Il change le répertoire de travail et place la copie en premier sur `sys.path`, car Nexy résout les routes à partir du répertoire courant. Ajoutez manuellement tout autre fichier que votre application lit au moment de l’exécution à cette liste.

## Mettre en cache les actifs statiques

Le `vercel.json` généré contient les deux règles de cache utilisées par un site Nexy déployé : les fichiers sous `/assets/` sont immuables pendant un an, et les images et les polices sous `public/` restent à jour pendant une journée avec une fenêtre périmée d'une semaine pendant la revalidation. Ajoutez d'autres règles dans le même fichier si votre projet en a besoin.

## Vérifier le déploiement

Avant de pousser, importez le point d'entrée et demandez-lui une page :

```bash
uv run python -c "from src.server import app; print(type(app).__name__)"
uv run uvicorn src.server:app
```

Ensuite, ouvrez `/`, une route générée et un fichier sous `/assets/`. Comparez la réponse avec `nx start` localement : le statut, le type de contenu et la taille doivent correspondre. Une page plus petite que la page locale exactement par les deux balises client signifie que `vite.config.ts` manquait dans le projet copié.
