# DOC-17 — Islands

| | |
|---|---|
| **Phase** | P3 — Rendu |
| **Statut** | `prêt` |
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
- **Quand ne pas l'utiliser** : une page entièrement interactive doit être CSR, pas une page d'îlots.

## Fichiers

| Fichier | Action |
|---|---|
| `docs/rendering/islands.md` | Réécrire sur le squelette |
| `docs/views/{framework}/islands.md` | Vérifier la cohérence (DOC-21 les réduira aux différences) |

## Critère de fin

- [ ] Le déclencheur par défaut est nommé
- [ ] Ce qui est sérialisable dans les props est explicite
- [ ] La section « quand ne pas l'utiliser » existe
- [ ] Aucune duplication du contrat avec les pages par framework

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. |
