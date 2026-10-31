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

- **SSR vs SSG** : **Nexy n'a pas de mode SSG.** Ne pas en inventer un. Ce qui existe, vérifié
  dans le code, est un **prérendu au build** qui ne se substitue jamais au serveur :
  - en mode serveur, chaque composant (`.tsx`, `.vue`, `.svelte`, `.mdx`) est rendu en HTML au build
    et réinjecté dans la page `.nexy` à la requête (c'est le mécanisme des islands) ;
  - en mode client (`useCSR = True`), chaque route est rendue en document HTML complet au build
    (`.document.html`, `.shell.html`, ou un fichier par valeur de `getStaticParams`), puis **relu
    par le serveur Python** qui y injecte les assets et l'état de démarrage.
  Conséquence à écrire noir sur blanc : il n'y a ni commande d'export, ni dossier de HTML autonome,
  ni hébergement statique possible ; la page doit dire comment obtenir du contenu figé
  (ISR avec une grande fenêtre, ou prérendu client) sans appeler cela SSG.
- **CSR n'implique pas SPA** : une page CSR n'oblige pas à faire de toute l'application une SPA.
- **ISR n'est pas un simple cache** : c'est un problème de cohérence des données — renvoyer à DOC-15 pour les limites.
- **Qui décide du mode** : **pas au même grain.** SSR est le défaut, ISR et islands se décident
  **page par page** (`revalidate`, `directive`). CSR est un choix **de projet** (`useCSR` dans
  `nexyconfig.py`) : un projet est en mode serveur *ou* en mode client, jamais les deux. La phrase
  « le mode se choisit par page » est donc fausse pour CSR — à corriger, pas à recopier.
- **Deux pages mentent aujourd'hui** : `docs/views/README.md:24-26` annonce « framework SSR / SSG »
  pour `.tsx`/`.vue`/`.svelte`, et `docs/reference/glossary.md:22` définit SSG, alors qu'aucune page
  de `docs/rendering/` ne décrit ce mode (F13). Les deux doivent être alignées dans le même commit
  que cette page, sinon la contradiction survit.

## Fichiers

| Fichier | Action |
|---|---|
| `docs/rendering/README.md` | Réécrire autour de la matrice |
| `docs/views/README.md` | Remplacer « framework SSR / SSG » par le rendu réel (F13) |
| `docs/reference/glossary.md` | Redéfinir SSG comme « non fourni ; voir prérendu » ou retirer l'entrée |

## Critère de fin

- [ ] La matrice a une ligne par critère et une colonne par mode, sans cellule vide
- [ ] Chaque cellule renvoie, si besoin, à la page de mode correspondante
- [ ] Chaque question ci-dessus a une réponse dans la page
- [ ] Aucun paragraphe dupliqué avec DOC-14 → DOC-17
- [ ] Aucune occurrence de « SSG » dans `docs/` sans la mention explicite que ce n'est pas un mode
- [ ] La page dit au bon grain qui décide : page par page pour SSR/ISR/islands, projet pour CSR

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Matrice construite à partir des pages existantes et du brief. |
| 2026-10-31 | Question « est-ce que Nexy fait SSG » tranchée dans le code : non (F13, F14). Prérendu au build documenté comme mécanisme interne, pas comme mode. Correction ajoutée : CSR est un choix de projet, pas de page. |
