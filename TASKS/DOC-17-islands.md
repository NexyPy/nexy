# DOC-17 — Islands

| | |
|---|---|
| **Phase** | P3 — Rendu |
| **Statut** | `fait` |
| **Dépend de** | DOC-13 |
| **Débloque** | — |

## Objectif

Expliquer l'hydratation ciblée : ce qui est rendu par le serveur, ce qui est hydraté, quand, et ce que cela change pour le développeur.

## Squelette imposé (A1)

1. Definition · 2. How it works · 3. Rendering lifecycle · 4. When to use · 5. Configuration · 6. Example · 7. Limitations · 8. Related.

## Points obligatoires

- **Définition** : le HTML est rendu par le serveur ; seuls les composants interactifs reçoivent du JavaScript.
- **Déclencheurs d'hydratation** : idle, visible, media query — dire lequel est le défaut et comment le choisir.
- **Ce que l'îlot reçoit** : ses props, sérialisées ; dire ce qui est sérialisable et ce qui ne l'est pas (fonctions, instances).
- **Limites** : un îlot n'est pas un composant client ordinaire — pas d'état partagé entre îlots sans mécanisme explicite ; pas de re-rendu serveur de l'îlot.
- **`client:only` et `client:manual` ne s'hydratent jamais** (F16). Le brief et `skills/nexy-file/SKILL.md` les recommandaient encore : à corriger, et à signaler comme bug du Chantier 2.
- **Quand ne pas l'utiliser** : une page entièrement interactive doit être CSR, pas une page d'îlots.

## Fichiers

| Fichier | Action |
|---|---|
| `docs/rendering/islands.md` | Réécrire sur le squelette |
| `docs/views/{framework}/islands.md` | Vérifier la cohérence (DOC-21 les réduira aux différences) |
| `skills/nexy-file/SKILL.md` | Retirer `client:only` de la liste des directives conseillées (F16) |

## Critère de fin

- [x] Le déclencheur par défaut est nommé
- [x] Ce qui est sérialisable dans les props est explicite
- [x] La section « quand ne pas l'utiliser » existe
- [x] Aucune duplication du contrat avec les pages par framework
- [x] Aucune recommandation de `client:only` ni de `client:manual`

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. |
| 2026-10-31 | **Fait.** Squelette A1. Faits vérifiés dans `islands/islands.js` et `islands/react.js` : défaut = hydratation immédiate, `client:idle` (requestIdleCallback, timeout 2 s), `client:visible` (IntersectionObserver, marge 200 px, repli idle), `client:media` (défaut `(min-width: 768px)`). `client:only` et `client:manual` sont ignorés par le runtime : `client:only` laisse le HTML du build inerte, `client:manual` n'a pas de déclencheur public (F16). Les cinq pages `views/*/islands.md` n'en parlent plus (commit `affe6b2`) ; `skills/nexy-file/SKILL.md` le recommandait encore — corrigé ici. Limite ajoutée : des props non sérialisables sont remplacées par `{}` sans erreur. |
