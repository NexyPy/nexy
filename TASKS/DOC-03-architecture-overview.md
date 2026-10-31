# DOC-03 — Architecture Overview

| | |
|---|---|
| **Phase** | P1 — Fondations |
| **Statut** | `prêt` |
| **Dépend de** | — |
| **Débloque** | DOC-05 |

## Objectif

Une page qui montre comment les parties de Nexy s'articulent, avec pour chaque couche : sa responsabilité, ce dont elle dépend, et **ce qu'elle ne fait pas**.

## Contexte utile

- `ARCHITECTURE.md` (racine) contient déjà des diagrammes mermaid, mais il parle VFS, importlib, watcher, uvicorn : c'est un document de contributeur, pas de lecteur.
- Le lecteur a besoin d'un diagramme stable et de relations, pas d'un schéma de séquence par mécanisme interne.
- La question à laquelle la page doit répondre : *pourquoi Vite ne remplace pas Nexy, pourquoi Nexy ne remplace pas React, et comment les deux se parlent.*

## Diagramme de départ (à valider)

```diagram
Browser → Nexy Server → Middleware → Dispatcher → FBR | Modular | Custom → Rendering → Response
```

## Structure proposée

1. **The layers** — le diagramme + un tableau couche / responsabilité / ne fait pas.
2. **Who builds what** — Nexy (routage, rendu serveur, Actions, compilation `.nexy`), Vite (client, HMR, bundles), le framework frontend (composants, réactivité), l'application (données, authz).
3. **Where a request is decided** — renvoi vers DOC-04 (How Nexy Works) plutôt que duplication.
4. **Dev vs production** — deux colonnes, pas deux pages.
5. **Boundaries** — ce que Nexy ne fait pas (authz, ORM, i18n, file d'attente) et où brancher le reste.

## Fichiers

| Fichier | Action |
|---|---|
| `docs/architecture.md` | Créer (option A de D2) |
| `docs/README.md` | Ajouter au groupe « Understand the model » (F5) |
| `llms.txt` | Ajouter une ligne + remplacer le renvoi brut vers `ARCHITECTURE.md` |
| `ARCHITECTURE.md` | Ajouter un renvoi vers `docs/architecture.md` en tête, garder le contenu contributeur |

## Critère de fin

- [ ] Chaque couche du diagramme a une ligne de tableau avec « ne fait pas »
- [ ] La page ne décrit aucun mécanisme interne (VFS, importlib, watcher) — c'est le rôle de `ARCHITECTURE.md`
- [ ] Une seule source de vérité par couche ; aucun diagramme dupliqué avec `ARCHITECTURE.md`
- [ ] `docs/getting-started/how-nexy-works.md` renvoie ici au lieu de re-décrire l'architecture

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Diagramme en couches repris du brief ; écriture suspendue à D2. |
