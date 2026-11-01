# DOC-22 - Redirections des anciennes URL

| | |
|---|---|
| **Phase** | P4 - Frontend |
| **Statut** | `bloqué` |
| **Dépend de** | DOC-21 |
| **Débloque** | - |

## Objectif

Supprimer 20 pages sans casser une seule URL publiée ni un seul lien entrant.

## Contexte utile

- Les deux sites servent les mêmes pages depuis `docs/` : `sites/vanilla` (GitHub Pages) et `sites/nexy`.
- Le site Nexy route `/docs/[...path]` : une page absente donne un 404, pas une redirection.
- `test_links.py` (F10) valide les liens **internes au dépôt** ; il ne verra pas les liens externes ni les favoris. D'où une table explicite.

## Table de redirections (à générer depuis DOC-21)

| Ancienne URL | Nouvelle URL |
|---|---|
| `/docs/views/react/pages` | `/docs/views/frontend/pages` |
| `/docs/views/react/layouts` | `/docs/views/frontend/layouts` |
| `/docs/views/react/islands` | `/docs/views/frontend/islands` |
| `/docs/views/react/actions-and-navigation` | `/docs/views/frontend/actions-and-navigation` |
| *(idem × vue, svelte, solid, preact)* | idem |
| `/docs/views/react` | `/docs/views/react/differences` (ou README conservé) |

## Fichiers

| Fichier | Action |
|---|---|
| `sites/vanilla/build.py` | Écrire une page HTML de redirection (meta refresh + canonical) pour chaque ancienne URL |
| `sites/nexy/src/routes/docs/[...path].nexy` | Répondre 301 quand le slug est dans la table |
| `sites/shared/docs_source.py` | Exposer la table (`REDIRECTS`) pour les deux sites |
| `tests/unit/sites/` | Un test par ancienne URL : statut 301 et destination |

## Critère de fin

- [ ] Chaque ancienne URL répond une redirection, pas un 404
- [ ] Un test couvre chaque ligne de la table
- [ ] Aucun lien interne du dépôt ne pointe encore vers une ancienne URL (`test_links.py` vert)
- [ ] Les redirections ne créent pas de boucle

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Table initiale déduite de DOC-21. |
