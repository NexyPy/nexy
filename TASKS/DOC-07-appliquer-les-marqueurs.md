# DOC-07 — Appliquer les marqueurs aux groupes

| | |
|---|---|
| **Phase** | P2 — Navigation |
| **Statut** | `bloqué` |
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
| `docs/routing/README.md` | Aligner le vocabulaire (DOC-11) |

## Critère de fin

- [ ] En mode FBR : aucun groupe modular/custom visible ; Routing et Route handlers visibles
- [ ] En mode Modular : aucun groupe fbr/custom visible
- [ ] En mode Custom : seul le groupe d'intégration est visible
- [ ] Les groupes frontend restent visibles dans les trois modes
- [ ] Aucune page orpheline (F5, `test_routers.py:70` vert)

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Table de correspondance établie sur les 21 groupes réels. |
