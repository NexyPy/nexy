# DOC-11 - Routing : deux routeurs, une intégration

| | |
|---|---|
| **Phase** | P3 - Terminologie |
| **Statut** | `prêt` |
| **Dépend de** | - |
| **Débloque** | - |

## Objectif

Mettre fin à l'ambiguïté « Nexy a deux routeurs » vs trois entrées de navigation, et aligner le libellé du sélecteur sur le contenu réel de la page.

## Contexte utile

- Le brief relève : la nav montre FBR / Modular / Custom Router, la page dit « Nexy has two routers ».
- F9 : le sélecteur annonce « Custom Router - *Create your own router* » ; la page s'intitule « Custom routing - *Include an existing FastAPI app* ». Ce ne sont pas les mêmes promesses.
- F12 : `ROUTERS` est asserté à l'identique dans `test_routers.py:36-41` - changer un libellé **casse un test**, à mettre à jour dans le même commit.

## Terminologie cible

| Concept | Définition | Statut |
|---|---|---|
| File-Based Router (FBR) | routage natif par fichiers sous `src/routes/` | natif, défaut |
| Modular Router | routage natif par contrôleurs et modules | natif, optionnel |
| Custom Router Integration | inclusion d'un routeur FastAPI existant | intégration, pas un troisième routeur |

## Points à couvrir dans la page

1. Les deux routeurs natifs, et pourquoi ils coexistent.
2. Ce que « coexistence » veut dire concrètement : ordre d'enregistrement, priorité, et ce qui se passe en cas de collision d'URL (aujourd'hui : aucun diagnostic - à documenter comme comportement, pas comme garantie).
3. Le Custom Router comme intégration : ce qu'on garde de Nexy, ce qu'on perd.
4. Quand changer de routeur, et quand ne pas changer.

## Fichiers

| Fichier | Action |
|---|---|
| `docs/routing/README.md` | Réécrire la présentation et le vocabulaire |
| `docs/routing/custom/README.md` | Aligner titre et résumé sur « integration » |
| `sites/shared/docs_source.py:119-123` | Blurb du custom : « Include an existing FastAPI router » |
| `tests/unit/sites/test_routers.py:36-41` | Mettre à jour le tuple attendu (F12) |

## Critère de fin

- [ ] Le mot « router » ne désigne plus trois choses équivalentes
- [ ] La page dit explicitement ce que fait Nexy en cas de collision d'URL, sans le présenter comme une garantie
- [ ] Le libellé du sélecteur et le titre de la page disent la même chose
- [ ] `test_routers.py` mis à jour et vert

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Incohérence F9 confirmée dans le code. |
