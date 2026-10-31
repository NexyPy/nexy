# DOC-13 — Rendering : matrice de comparaison

| | |
|---|---|
| **Phase** | P3 — Rendu |
| **Statut** | `prêt` |
| **Dépend de** | — |
| **Débloque** | DOC-14, DOC-15, DOC-16, DOC-17 |

## Objectif

Donner une page où les quatre modes se comparent **ligne à ligne**, sans que le lecteur reconstruise mentalement les différences à partir de quatre pages séparées.

## Contexte utile

- La page actuelle décrit les modes en une ligne chacun : correct pour une introduction, insuffisant pour une décision.
- Les quatre pages de mode (DOC-14 → DOC-17) suivront un squelette commun ; cette page est la **surface de comparaison**, pas un résumé des quatre.
- Règle : aucune duplication de prose entre la matrice et les pages de mode. La matrice compare, les pages expliquent.

## Matrice cible

| Critère | SSR | ISR | CSR | Islands |
|---|---|---|---|---|
| Quand les données sont lues | requête | requête de régénération | navigateur | requête |
| Où le HTML est produit | serveur | serveur, puis cache | navigateur | serveur |
| JavaScript envoyé | selon la vue | selon la vue | oui | uniquement pour les îlots |
| Hydratation | non (vue serveur) | non | complète | ciblée |
| Cache | aucun par défaut | par URL, fenêtre `revalidate` | aucun | aucun |
| Invalidation | n/a | après mutation, explicite | n/a | n/a |
| Cas d'usage | contenu personnalisé | contenu rarement modifié | application interactive | page riche, peu d'interactivité |

## Questions à traiter explicitement

- **SSR vs SSG** : Nexy n'a pas de SSG séparé ; expliquer comment obtenir un rendu statique (ISR avec une grande fenêtre, ou prérendu au build) sans inventer une fonctionnalité.
- **CSR n'implique pas SPA** : une page CSR n'oblige pas à faire de toute l'application une SPA.
- **ISR n'est pas un simple cache** : c'est un problème de cohérence des données — renvoyer à DOC-15 pour les limites.
- **Qui décide du mode** : par page, pas par application.

## Fichiers

| Fichier | Action |
|---|---|
| `docs/rendering/README.md` | Réécrire autour de la matrice |

## Critère de fin

- [ ] La matrice a une ligne par critère et une colonne par mode, sans cellule vide
- [ ] Chaque cellule renvoie, si besoin, à la page de mode correspondante
- [ ] Les quatre questions ci-dessus ont une réponse dans la page
- [ ] Aucun paragraphe dupliqué avec DOC-14 → DOC-17

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Matrice construite à partir des pages existantes et du brief. |
