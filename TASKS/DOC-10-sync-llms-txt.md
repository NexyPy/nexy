# DOC-10 — Synchroniser `llms.txt`

| | |
|---|---|
| **Phase** | P2 — Navigation |
| **Statut** | `bloqué` (D1) |
| **Dépend de** | D1 |
| **Débloque** | — |

## Objectif

Empêcher le troisième index de diverger : `llms.txt` doit lister chaque page de la documentation, et un oubli doit faire échouer la CI.

## Contexte utile

- `llms.txt` est écrit à la main : ~30 entrées pour 86 pages, et il renvoie à `ARCHITECTURE.md` pour l'architecture alors que DOC-03 crée une page lecteur (F4).
- Il sert d'entrée machine (agents) : il ne connaît pas la notion de mode, donc il doit rester **exhaustif**, pas filtré.
- `test_links.py` valide déjà ses liens relatifs ; rien ne valide sa couverture.

## Décision de conception

Deux options, à trancher dans la tâche :

| Option | Avantage | Inconvénient |
|---|---|---|
| **A. Le garder manuel + test de couverture** | les lignes restent rédigées (une phrase utile par page) | 86 lignes à maintenir |
| **B. Le générer depuis `read_tracks`** | zéro divergence possible | perd la rédaction par page, devient mécanique |

Recommandation : **A**, avec un test qui compare l'ensemble des slugs listés à l'ensemble des slugs de la nav.

## Fichiers

| Fichier | Action |
|---|---|
| `llms.txt` | Compléter les pages manquantes, corriger le renvoi architecture |
| `tests/unit/nexy/docs/test_llms_index.py` *(nouveau)* | Comparer les slugs de `llms.txt` à ceux de `read_tracks` |

## Critère de fin

- [ ] Chaque page de la nav a une ligne dans `llms.txt`
- [ ] Le test échoue si une page est ajoutée sans ligne
- [ ] Le test échoue si une ligne pointe vers un fichier absent
- [ ] Les liens relatifs restent valides (`test_links.py` vert)
- [ ] Le renvoi vers l'architecture pointe vers `docs/architecture.md` (DOC-03)

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Divergence mesurée : ~30 entrées pour 86 pages. |
