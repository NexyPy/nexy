# DOC-19 - Getting Started : prérequis et résultat

| | |
|---|---|
| **Phase** | P3 - Entrée |
| **Statut** | `prêt` |
| **Dépend de** | - |
| **Débloque** | - |

## Objectif

Que le lecteur sache **ce qu'il installe**, **ce qu'il vient de construire**, et **pourquoi** un fichier `.nexy` devient une route - sans quitter le parcours de démarrage.

## Contexte utile

- Les pages sont déjà bonnes pédagogiquement (créer → lancer → modifier) ; trois manques : prérequis mélangés, résultat non montré, pont absent vers le modèle.
- **F11 est un verrou dur** : `test_setup_guidance.py` impose l'activation du venv, interdit `uvx nexy dev`, exige `uv run nexy dev` et l'ordre activation → `nexy dev`. Toute réécriture doit conserver ces formulations.
- Le Quick Start doit montrer un **résultat visuel**, pas seulement affirmer qu'une page existe.

## Travail

### 1. Matrice des prérequis (installation)

| Besoin | Outil | Quand |
|---|---|---|
| Toujours | Python ≥ 3.12 | installation |
| Toujours | `uv` (fournit `uvx`) | installation |
| Uniquement projet frontend | Node + pnpm | si React/Vue/Svelte/Solid/Preact |
| Développement | CLI `nexy`, dev toolbar | `nexy dev` |
| Production | build de production, serveur ASGI | `nexy build` / `nexy start` |

### 2. Résultat visible (quick start)

Décrire ce que le navigateur affiche après `nexy dev`, et à quel fichier cela correspond. Si possible, une capture ou un bloc de HTML minimal.

### 3. Pont vers le modèle

Trois phrases à la fin du Quick Start : ce fichier est devenu cette URL parce que… → renvoi vers DOC-04 (How Nexy Works).

## Fichiers

| Fichier | Action |
|---|---|
| `docs/getting-started/installation.md` | Ajouter la matrice |
| `docs/getting-started/quick-start.md` | Ajouter le résultat + le pont |
| `docs/getting-started/tutorial.md` | Vérifier la continuité (DOC-23 le réécrira) |

## Critère de fin

- [ ] La matrice distingue les 4 cas (toujours / frontend / dev / prod)
- [ ] Le Quick Start montre un résultat concret
- [ ] Le pont vers How Nexy Works existe
- [ ] `python -m pytest tests/unit/nexy/docs/test_setup_guidance.py -q` vert (F11)

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Contraintes F11 relevées avant toute rédaction. |
| 2026-11-01 | `tutorial.md` avait été remplacé par un brouillon hors périmètre qui cassait F11 ; restauré depuis HEAD. `installation.md` et `quick-start.md` n'ont pas encore reçu la matrice des prérequis ni le résultat visible. Tâche inchangée : `prêt`. |
