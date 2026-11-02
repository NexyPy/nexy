# DOC-10 - Synchroniser `llms.txt`

| | |
|---|---|
| **Phase** | P2 - Navigation |
| **Statut** | `fait` |
| **Dépend de** | - |
| **Débloque** | - |

## Objectif

Empêcher le troisième index de diverger : `llms.txt` doit lister chaque page de la documentation, et un oubli doit faire échouer la CI.

## Contexte utile

- `llms.txt` reste écrit à la main : ses 86 pages de navigation et l'index sont recensés, et l'architecture lecteur pointe vers `docs/architecture.md` (F4).
- Il sert d'entrée machine (agents) : il ne connaît pas la notion de mode, donc il doit rester **exhaustif**, pas filtré.
- `test_links.py` valide ses liens relatifs ; `test_llms_index.py` contrôle également couverture et existence.

## Décision de conception

Deux options, à trancher dans la tâche :

| Option | Avantage | Inconvénient |
|---|---|---|
| **A. Le garder manuel + test de couverture** | les lignes restent rédigées (une phrase utile par page) | 86 lignes à maintenir |
| **B. Le générer depuis `read_tracks`** | zéro divergence possible | perd la rédaction par page, devient mécanique |

Décision : **A**, avec un test qui compare l'ensemble des chemins listés à l'ensemble des chemins de la nav.

## Fichiers

| Fichier | Action |
|---|---|
| `llms.txt` | Compléter les pages manquantes, corriger le renvoi architecture |
| `tests/unit/nexy/docs/test_llms_index.py` *(nouveau)* | Comparer les slugs de `llms.txt` à ceux de `read_tracks` |

## Critère de fin

- [x] Chaque page de la nav a une ligne dans `llms.txt`
- [x] Le test échoue si une page est ajoutée sans ligne
- [x] Le test échoue si une ligne pointe vers un fichier absent
- [x] Les liens relatifs restent valides (`test_links.py` vert)
- [x] Le renvoi vers l'architecture pointe vers `docs/architecture.md` (DOC-03)

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Divergence mesurée : ~30 entrées pour 86 pages. |
| 2026-10-31 | Complété l'index manuel pour couvrir les 86 pages de navigation et `docs/README.md`. Ajout d'un test de parité avec la navigation et d'existence des liens ; `docs/architecture.md` est le renvoi lecteur. 112 tests ciblés passent. |
| 2026-10-31 | La suite `tests/unit/nexy/docs tests/unit/sites` passe à 451 tests et échoue sur `test_search_lists_every_page` : une modification non validée de `sites/shared/docs_source.py` ajoute des valeurs `router=None` au schéma du search index. Échec hors périmètre DOC-10 ; aucune modification de ce fichier. |
| 2026-11-01 | Réécrit en sections alignées sur la nav. Les 9 pages ajoutées depuis (4 contrats frontend, 5 pages `differences`) ont leur ligne. Cause de l'échec précédent trouvée et corrigée : `sites/nexy/src/routes/search-index.py` annotait `list[dict[str, str]]` alors que `scope` et `router` peuvent être `None` ; FastAPI renvoyait une page 500. Suite docs + sites : 470 tests verts. |
