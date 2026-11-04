# Démarrage rapide

Vous allez créer un projet Nexy, l'exécuter et voir une page changer au fur et à mesure que vous le modifiez. Il en faut trois
minutes. Le [Tutoriel](tutorial.md) ajoute ensuite un point de terminaison et une version de production.

## Avant de commencer

| Vous avez besoin de | Pourquoi |
|---|---|
| Python 3.12+ | `requires-python` dans `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | fournit `uvx`, crée le projet et installe ses packages |
| Node.js 18+ | uniquement si vous utilisez un framework client (React, Vue, Svelte, Solid, Preact) |

Pas encore d'UV ? Voir [Installation](installation.md).

## 1. Créer le projet

```bash
uvx nexy new my-app
```

`uvx` est livré avec uv, alors installez d'abord uv. Il exécute Nexy dans un environnement temporaire, suffisant pour **créer** le projet. `nexy new` fait alors
le propre `.venv` du projet et y installe ses packages. Quatre invites décident du câblage :

| Invite | Effet |
|---|---|
| Routeur basé sur des fichiers ? | `Yes` analyse `src/routes/` ; `No` échafaude le routeur modulaire dans `src/apps/` |
| Le type de projet | `Web` ajoute une mise en page et des actifs client, `API` démarre sans vues |
| Composant client ? | ajoute un framework et sa configuration Vite |
| ORM/base de données | ajoute une couche de modèle, ou rien |

Vous n'êtes pas sûr ? Répondez `Yes`, `Web` et aucun composant client. Vous pourrez les ajouter plus tard.

## 2. Exécutez-le

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

Ouvrez <http://localhost:3000>. Vous devriez voir la page de démarrage. Le port vient de `usePort`
(par défaut `3000`); `--port` et `--host` le remplacent par exécution.

> [!REMARQUE]
> Exécutez toutes les commandes sauf `new` et `init` dans l'environnement virtuel du projet, ou préfixez-la
> avec `uv run`, comme dans `uv run nexy dev`. En dehors de lui, un projet qui a besoin `sqlmodel` échoue avec
> `No module named 'sqlmodel'`.

## 3. Changer une page

<!-- router:fbr,custom -->
Un fichier sous `src/routes/` est une route. Créer `src/routes/hello.nexy` :

```nexy filename="src/routes/bonjour.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```
<!-- /router -->

<!-- router:modular -->
Un contrôleur renvoie une vue. Créer `src/apps/hello_view.nexy` :

```nexy filename="src/apps/hello_view.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

Déclarez ensuite la page dans `src/apps/app_controller.py` et ajoutez-la au module :

```python filename="src/apps/app_controller.py"
@Controller("/hello")
class HelloController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/hello_view.nexy")})
```

```python filename="src/apps/app_module.py"
from .app_controller import AboutController, AppController, HelloController

controllers = [AppController, AboutController, HelloController]
```
<!-- /router -->

Ouvrez <http://localhost:3000/hello>. Remplacez `"Hello"` par `"Bonjour"` et enregistrez : la page est mise à jour
sans rechargement manuel. Si le code est erroné, le navigateur affiche l'erreur au lieu d'une page vierge.

`prop[str]` déclare une propriété typée. Le balisage sous le frontmatter est Jinja2 - voir
[fichiers .nexy](../views/nexy/README.md).

## Où ensuite

| Vous souhaitez | Lire |
|---|---|
| Ajouter un point de terminaison Python et expédier une build | [Tutoriel](tutorial.md) |
| Savoir où appartient chaque fichier | [Structure du projet](project-structure.md) |
| Comprendre qui construit quoi | [Comment fonctionne Nexy](how-nexy-works.md) |
| Utilisez React, Vue, Svelte, Solid ou Preact | [Views](../views/README.md) |