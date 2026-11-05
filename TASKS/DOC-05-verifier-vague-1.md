# DOC-05 - Vérifier la vague 1

| | |
|---|---|
| **Phase** | P1 - Fondations |
| **Statut** | `fait` |
| **Dépend de** | DOC-01, DOC-02, DOC-03, DOC-04 |
| **Débloque** | P2 |

## Objectif

S'assurer que les quatre pages de fondation forment un ensemble cohérent **avant** d'ouvrir le chantier navigation, et que rien n'a été cassé dans la nav ou les index.

## Contrôles

### 1. Automatiques

| Commande | Résultat (2026-10-31) |
|---|---|
| `python -m pytest tests/unit/nexy/docs tests/unit/sites -q` | `438 passed` |
| `python scripts/verify.py` | `lint`, `format`, `typecheck`, `structure`, `test` : verts - `3225 passed, 13 deselected` |

### 2. Cohérence croisée

| Contrôle | Résultat |
|---|---|
| README → Core Concepts → Architecture → How Nexy Works | **Conforme.** README liste les trois pages dans « Understand the model » ; Core Concepts renvoie à Architecture, Project structure, Glossary et How Nexy works ; Architecture renvoie à How Nexy works, Project structure, Routing, Rendering ; How Nexy works renvoie à Architecture, Rendering, Frontend, Routing. Aucun retour en arrière nécessaire. |
| Le diagramme de DOC-03 | **Conforme, et il n'y en a qu'un.** `docs/architecture.md` porte le diagramme en cinq couches ; DOC-04 §1 le décrit en une phrase (Uvicorn, middleware, router, renderer, client) et renvoie à la page au lieu de redessiner. |
| Les définitions de DOC-02 | **Écart assumé.** DOC-02 et `views/README.md` disent la même chose d'une vue dans deux formulations (« what produces the body of a page » / « renders the response body for a page »). Les rendre identiques mot pour mot aurait créé deux copies d'une même définition, ce que A9 interdit. Le contrôle réellement passé : aucune contradiction entre les deux pages, et chaque notion n'est définie qu'une fois (modèle dans DOC-02, index dans le glossaire). |
| La promesse de DOC-01 | **Conforme.** Python first → `.nexy` et `.py` (How Nexy works §4) ; trois routeurs → `routing/README.md` ; frontend par page ou par projet → `rendering/islands.md`, `rendering/csr.md` ; modèle de rendu → `rendering/README.md` ; actions typées → `guides/actions.md` (`__nexy__/src/actions.ts` est écrit depuis les signatures). |
| Le vocabulaire | **Conforme, après une correction.** Aucun routeur n'est appelé « fichier » et aucune vue n'est appelée « endpoint ». Une seule imprécision trouvée : `views/README.md:14` étiquetait le fichier `.py` « Python endpoint » alors qu'un endpoint est un couple (URL, méthode) ; corrigé en « API handler », le terme qu'emploient déjà `pages.md:94` et `docs/README.md:64`. |

### 3. Index

- [x] Les pages créées par P1 figurent dans les tableaux de `docs/README.md` (F5) - `architecture.md` et `getting-started/core-concepts.md`, les deux seules pages nouvelles ; le brief en annonçait trois, la troisième était la tête du README, qui n'est pas une entrée de nav.
- [x] Les mêmes pages figurent dans `llms.txt` (F4) - `Core concepts` (ligne 12) et `Architecture` (ligne 15).
- [x] `llms.txt` ne renvoie plus à `ARCHITECTURE.md` pour l'architecture (DOC-03) - le lecteur a `docs/architecture.md` ligne 15 ; `ARCHITECTURE.md` reste ligne 49, sous « Source », étiqueté « for contributors ».

## Critère de fin

- [x] Les deux commandes sont vertes
- [x] Les 3 tableaux de contrôle ci-dessus sont remplis sans écart non justifié
- [x] Le journal de chaque tâche P1 est à jour

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Sert de porte de sortie à P1. |
| 2026-10-31 | **Fait.** Les deux commandes sont vertes (`438 passed`, puis `scripts/verify.py` : 3225 tests). Deux points méritent d'être retenus pour la suite. (1) Le contrôle « définitions identiques mot pour mot » a été ramené à « aucune contradiction, une définition par endroit » : le littéral aurait dupliqué DOC-02 dans `views/README.md` et contredit A9. (2) Une seule imprécision de vocabulaire dans tout `docs/` : le `.py` étiqueté « Python endpoint » dans le diagramme de `views/README.md` ; corrigé en « API handler ». Le brief parlait de trois pages nouvelles en P1 ; il y en a deux (`architecture.md`, `core-concepts.md`) - la troisième ligne était la tête du README, qui est la page d'accueil, pas une entrée de nav. P2 peut s'ouvrir. |
