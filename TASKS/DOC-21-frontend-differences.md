# DOC-21 — Une page « differences » par framework

| | |
|---|---|
| **Phase** | P4 — Frontend |
| **Statut** | `bloqué` |
| **Dépend de** | DOC-20 |
| **Débloque** | DOC-22 |

## Objectif

Réduire chaque dossier de framework à ce qui lui est **propre** : nommage, réactivité, hydratation, layout, pièges.

## Contenu attendu par page

| Section | Exemple de différence réelle |
|---|---|
| Setup | paquet à installer, extension de fichier, config Vite |
| Reactivity model | signals (Solid/Preact), refs (Vue), stores (Svelte), hooks (React) |
| Layout file | `layout.tsx` vs `layout.vue` vs `layout.svelte` |
| Hydration | ce que l'îlot reçoit et comment il se réveille |
| Gotchas | ce qui surprend un développeur venant d'un autre framework |
| What is identical | renvoi aux 4 contrats (DOC-20) |

## Règle

Une page « differences » ne réexplique **jamais** un contrat. Si une phrase est vraie pour les cinq, elle appartient à DOC-20.

## Fichiers

| Fichier | Action |
|---|---|
| `docs/views/{react,vue,svelte,solid,preact}/differences.md` (5) | Créer |
| `docs/views/{framework}/README.md` | Réduire à : ce framework en 5 lignes + lien vers differences + liens vers les contrats |
| `docs/views/{framework}/{pages,layouts,islands,actions-and-navigation}.md` (20) | Supprimer après redirection (DOC-22) |

## Critère de fin

- [ ] Aucune phrase commune aux 5 frameworks ne subsiste dans une page « differences »
- [ ] Chaque page tient en moins de 400 mots
- [ ] Les pièges listés sont réels (vérifiés dans les templates de `nexy/modules/cli/templates/`)
- [ ] Chaque README de framework renvoie aux 4 contrats

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Les différences réelles sont vérifiables dans les templates du CLI. |
