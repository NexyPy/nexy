# DOC-09 — Recherche contextuelle

| | |
|---|---|
| **Phase** | P2 — Navigation |
| **Statut** | `bloqué` |
| **Dépend de** | DOC-06 |
| **Débloque** | — |

## Objectif

Faire suivre le mode choisi à la recherche : un lecteur en parcours FBR ne voit pas d'abord des résultats modulaires, mais peut demander explicitement « chercher partout ».

## Contexte utile

- `search_entry()` (`docs_source.py:685`) produit `{title, section, url, headings, text}` — **aucun champ de périmètre**.
- `sites/nexy/src/content.py:170` (`search_entries`) agrège sans filtrer.
- `tests/unit/sites/test_nexy_site.py:183` vérifie que le nombre d'entrées égale le nombre de `.md` : ajouter un champ ne casse rien, en retirer une entrée casserait.
- La recherche doit rester **complète par défaut dans le fichier d'index** ; c'est l'affichage qui filtre.

## Fichiers

| Fichier | Action |
|---|---|
| `sites/shared/docs_source.py` | `search_entry()` gagne `"scope": page.scope or "core"` (via `Group.scope` de DOC-06) |
| `sites/nexy/src/content.py` | Transmettre le champ tel quel |
| `sites/nexy/src/components/SearchDialog.nexy` | Filtrer sur le mode actif + bascule « Search all documentation » |
| `sites/vanilla/assets/site.js` | Même logique si le site vanilla expose une recherche |
| `tests/unit/sites/test_nexy_site.py` | Cas : un résultat hors mode n'apparaît qu'avec la bascule |

## Critère de fin

- [ ] L'index de recherche contient toujours **toutes** les pages (test existant vert)
- [ ] En mode FBR, un résultat `{modular}` est masqué par défaut
- [ ] La bascule « partout » révèle l'ensemble, avec une indication visuelle du périmètre de chaque résultat
- [ ] La recherche par titre reste prioritaire sur le corps de page

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Champ manquant identifié dans `search_entry`. |
