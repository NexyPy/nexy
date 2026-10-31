# DOC-07 — Appliquer les marqueurs aux groupes

| | |
|---|---|
| **Phase** | P2 — Navigation |
| **Statut** | `fait` |
| **Dépend de** | DOC-06 |
| **Débloque** | DOC-08 |

## Objectif

Déclarer le périmètre des 21 groupes de `docs/README.md` pour que le sélecteur produise un parcours lisible.

## Contexte utile — à lire avant de promettre trois parcours

Le dépôt n'a **que deux routeurs natifs** et une intégration (F3, DOC-11). Sur 21 groupes, 17 sont communs. Le sélecteur ne peut donc pas produire trois documentations distinctes : son plafond réel est **2 à 3 groupes masqués**. Les vrais gains de charge cognitive viendront de DOC-08 (bucket Advanced) et de DOC-20 (25 → 11 pages frontend), pas de ce filtrage. Cette tâche doit rester honnête là-dessus, y compris dans le texte de la sidebar.

## Table de correspondance

| Groupe (README) | Marqueur |
|---|---|
| First steps | *(core)* |
| Understand the model | *(core)* |
| Coming from elsewhere | *(core)* |
| Routing | `{fbr}` |
| Route handlers | `{fbr}` |
| Modular router | `{modular}` |
| Custom router integration | `{custom}` |
| React · Vue · Svelte · Solid · Preact | *(core)* — axe séparé (A3) |
| Nexy views | *(core)* |
| Rendering | *(core)* |
| Forms and data | *(core)* |
| Security and deployment | *(core)* |
| Frontend and testing | *(core)* |
| Tooling and help | *(core)* |
| Commands and config | *(core)* |
| Python API and errors | *(core)* |
| Conventions and concepts | *(core)* |

## Fichiers

| Fichier | Action |
|---|---|
| `docs/README.md` | Ajouter 4 marqueurs (`{fbr}` ×2, `{modular}`, `{custom}`) ; renommer « Custom router » en « Custom router integration » |
| `tests/unit/sites/test_routers.py` | Figer les quatre groupes marqués, pour qu'un marqueur perdu se voie |
| `docs/routing/README.md` | Aligner le vocabulaire (DOC-11) — **hors de cette tâche** |

## Critère de fin

- [x] En mode FBR : aucun groupe modular/custom visible ; Routing et Route handlers visibles
- [x] En mode Modular : aucun groupe fbr/custom visible
- [x] En mode Custom : seul le groupe d'intégration est visible
- [x] Les groupes frontend restent visibles dans les trois modes
- [x] Aucune page orpheline (F5, `test_routers.py:70` vert)

## Vérification

Groupes masqués, calculés depuis le HTML produit (`data-scope`) :

| Mode | Groupes masqués |
|---|---|
| `fbr` | Modular router, Custom router integration |
| `modular` | Routing, Route handlers, Custom router integration |
| `custom` | Routing, Route handlers, Modular router |

Deux ou trois groupes masqués par mode, jamais plus : c'est le plafond annoncé dans le contexte, et il est tenu. Les 17 autres groupes sont `core`, donc visibles partout — y compris les cinq groupes frontend, qui restent un axe séparé (A3).

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Table de correspondance établie sur les 21 groupes réels. |
| 2026-10-31 | **Fait.** Quatre marqueurs posés, un renommage. `test_only_the_routing_groups_declare_a_scope` fige le résultat : quatre groupes sur vingt-et-un portent un périmètre, et les nommer dans le test fait échouer la suite si un marqueur disparaît. Le plafond annoncé est vérifié plutôt que supposé : 2 groupes masqués en FBR, 3 en Modular, 3 en Custom. Aucune page ne bouge, aucune URL ne change, `test_every_page_is_in_the_menu_of_exactly_one_track` reste vert. Deux points restent pour DOC-11, hors périmètre ici : le sélecteur nomme toujours le troisième choix « Custom Router » alors que le groupe dit « Custom router integration », et `docs/routing/README.md:3` annonce « two routers » sans mentionner l'intégration. 450 tests verts sur `tests/unit/sites` + `tests/unit/nexy/docs`. |
