# DOC-08 — Bucket Advanced + « All documentation »

| | |
|---|---|
| **Phase** | P2 — Navigation |
| **Statut** | `prêt` |
| **Dépend de** | — |
| **Débloque** | DOC-09 |

## Objectif

Sortir du chemin de lecture principal les pages qui ne servent qu'à un lecteur déjà engagé, **sans les cacher** : un lien « All documentation » doit toujours permettre de tout retrouver.

## Contenu à déplacer en `{advanced}`

| Page | Pourquoi |
|---|---|
| `routing/modular/vs-nestjs.md` | comparaison, pas un prérequis |
| `routing/fbr/errors/folder-pages.md` | cas limite |
| `getting-started/upgrading.md` | concerne un projet existant |
| `guides/i18n.md` | dépend d'une bibliothèque externe |
| `guides/recipes.md` | exemples, pas un parcours |
| `reference/agents.md` | public spécifique |

Chaque page reste accessible, et son lien reste valide : aucun fichier ne bouge.

## Fichiers

| Fichier | Action |
|---|---|
| `docs/README.md` | Regrouper ces pages dans un groupe `### Advanced {advanced}` en fin de section concernée, ou une section dédiée en fin de nav |
| `sites/vanilla/build.py` | Émettre le lien « All documentation » (mode « tout ») |
| `sites/nexy/src/components/Sidebar.nexy` | Même lien |
| `sites/vanilla/assets/style.css` | `html[data-mode="all"] [data-scope] { display: block }` |

## Critère de fin

- [ ] Les 6 pages ne sont plus dans le parcours par défaut
- [ ] Un clic sur « All documentation » révèle tous les groupes, tous modes confondus
- [ ] Le mode choisi est visible en permanence dans la sidebar (pas seulement dans le menu déroulant)
- [ ] Les liens entrants vers ces pages restent valides (F10)
- [ ] `llms.txt` continue de les lister (les agents ne connaissent pas la notion de mode)

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Liste des pages candidates arrêtée. |
