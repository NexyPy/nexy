# Installation

## Exigences

| Exigence | Pourquoi |
|---|---|
| Python 3.12+ | `requires-python` dans `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | crée le projet, installe ses packages et exécute Nexy |
| Node.js 18+ | uniquement pour un framework client (React, Vue, Svelte, Solid, Preact) |

Un projet sans framework client n'a pas besoin du tout de Node.js.

## Installez d'abord UV

`uvx` n'est pas un outil séparé : il est livré avec uv, alors installez uv avant toute autre chose.

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Vérifiez-le avec `uv --version` et `uvx --version`.

## Créer un projet

```bash
uvx nexy new my-app
```

`uvx` exécute Nexy dans un environnement temporaire et ne laisse rien derrière lui. Cela suffit pour **créer** un
projet (`new`, `init`) et rien de plus : l'environnement temporaire contient Nexy et aucun autre
paquet. `nexy new` crée le propre environnement virtuel du projet, `.venv`, et installe ses packages
là.

`nexy new my-app` pose quatre questions : routeur (basé sur des fichiers ou modulaire), type de projet (web ou API),
cadre client, ORM. L'installation des dépendances Python et Node s'exécute ensuite avec une ligne par
étape et sa durée. Voir [CLI](../reference/cli.md).

Ignorez les invites avec un modèle enregistré :

```bash
uvx nexy new my-app --template <name>
```

## Travailler dans l'environnement virtuel du projet

Toutes les autres commandes (`nexy dev`, `nexy build`, `nexy migrate`...) doivent être exécutées **dans le fichier du projet.
environnement virtuel**. C'est là que vivent vos propres packages : votre ORM, vos bibliothèques et Nexy.
le projet a été construit avec. En dehors de lui, un projet qui a besoin `sqlmodel` échoue avec
`ModuleNotFoundError: No module named 'sqlmodel'`.

Activez-le une fois par terminal, depuis le dossier du projet :

| Shell | Commande |
|---|---|
| PowerShell, cmd (Windows) | `.venv\Scripts\activate` |
| macOS, Linux | `source .venv/bin/activate` |

L'invite commence alors par `(.venv)`. A partir de là :

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

Ouvrez <http://localhost:3000>.

Pour ignorer l'activation, laissez uv le faire pour une seule commande : `uv run nexy dev`.

> [!REMARQUE]
> `nexy` et `nx` sont le même binaire. Une copie installée avec `uv tool install
> nexy` lives in its own environment, like `uvx`, alors utilisez-le pour créer des projets et tout exécuter
> autrement de l'environnement du projet.

## Ajouter Nexy à un projet existant

Exécutez-le depuis l'environnement virtuel du projet, avec Nexy parmi ses packages (`uv add nexy`) :

```bash
nexy init
```

## Prochaines étapes

- [Démarrage rapide](quick-start.md)
- [Tutoriel](tutorial.md)
- [Structure du projet](project-structure.md)
- [Dépannage](../guides/troubleshooting.md)