# DOC-06 - Marqueurs de groupe dans la navigation

| | |
|---|---|
| **Phase** | P2 - Navigation |
| **Statut** | `fait` |
| **Dépend de** | - |
| **Débloque** | DOC-07, DOC-08, DOC-09 |

## Objectif

Remplacer la déduction du routeur par le chemin (F3) par une **déclaration explicite au niveau du groupe**, seul grain qui compte pour la lecture (A4). Une page ne bouge pas, une URL ne change pas.

## Contexte utile

- `read_tracks` lit `### Titre` en `docs_source.py:270-275` puis crée `Group(title, blurb, pages, _router_of_group(pages))`.
- `_router_of_group` (`:230`) ne marque un groupe que si **toutes** ses pages sont sous `routing/<router>/`. Conséquence : impossible de marquer « Advanced », impossible de sortir un groupe du filtre sans déplacer des fichiers.
- Le filtrage réel est CSS (`test_routers.py:168`), donc la nouvelle donnée doit arriver jusqu'au HTML.

## Syntaxe retenue

```md
### Routing {fbr}
### Modular router {modular}
### Custom router integration {custom}
### Advanced {advanced}
### Forms and data
```

Sans marqueur → déduction par le chemin, puis `core` (toujours visible). Le marqueur est retiré du titre affiché **et du titre rendu** : sans cela, la page d'accueil afficherait `Routing {fbr}` et son ancre serait `routing-fbr`.

Les valeurs acceptées sont `SCOPES = ("core", "fbr", "modular", "custom", "advanced")`. Un marqueur inconnu (`{advnaced}`) n'est pas retiré : il reste visible dans le menu et `test_no_group_title_carries_a_marker` échoue. C'est volontaire - un marqueur qui ne s'applique pas en silence est pire qu'une faute visible.

## Implémentation

| Fichier | Changement |
|---|---|
| `sites/shared/docs_source.py` | `SCOPES`, `_SCOPE`, `Group.scope` ; `close_group()` retire le marqueur et fixe `scope` ; `router = scope` si c'est un routeur, sinon `None` ; `_identify()` retire le marqueur du titre rendu |
| `sites/vanilla/build.py` | `data-scope` sur `<details class="group">` |
| `sites/nexy/src/content.py` | `_menu_group` transmet `scope` |
| `sites/nexy/src/components/Sidebar.nexy` | `data-scope` sur `<details class="group">` |
| `sites/vanilla/assets/style.css` | deux règles : la face du routeur par `data-router`, les groupes par `data-scope` |
| `tests/unit/sites/test_docs_source.py` | `TestGroupScope` (6 cas) + marqueur invisible au rendu + aucun titre de groupe avec `{` |
| `tests/unit/sites/test_routers.py`, `test_vanilla_build.py`, `test_nexy_site.py` | `data-scope` émis par les deux sites ; règle CSS par scope |

## Critère de fin

- [x] Un groupe déclaré `{modular}` est filtré **même si** ses pages ne sont pas sous `routing/modular/` (`test_a_marker_wins_over_the_folder_of_the_pages`)
- [x] Un groupe sans marqueur se comporte exactement comme aujourd'hui (repli, zéro régression)
- [x] Le titre affiché ne contient jamais `{…}`
- [x] Les tests existants de déduction passent sans modification
- [x] Aucun déplacement de fichier, aucune URL modifiée

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Syntaxe et points d'implémentation relevés dans le code. |
| 2026-10-31 | **Fait.** `Group` gagne `scope` ; `router` reste dérivé de `scope`, donc le pager et le filtre de page ne changent pas et les tests de déduction passent tels quels. Deux écarts au plan, tous deux justifiés par le code : (1) la règle CSS unique `[data-router]` ne pouvait pas devenir `[data-scope]` seule, parce que la face du sélecteur (`.area-face`) porte `data-router` et non `data-scope` - d'où deux règles, une par élément ; (2) le marqueur est aussi retiré dans `_identify()`, sinon `docs/README.md`, qui est aussi la page d'accueil, afficherait `Routing {fbr}` avec l'ancre `routing-fbr`. Le regex est limité aux cinq valeurs connues pour ne pas manger un titre qui finirait par `{slug}`. Conséquence à porter en DOC-08 : un groupe `{advanced}` est masqué dans les trois modes routeur, et rien ne le rouvre avant le mode « All documentation » - aucun groupe n'est marqué `{advanced}` aujourd'hui, donc l'arbre reste utilisable. `site.js` continue d'indexer les groupes masqués pour la recherche : c'est DOC-09. 449 tests verts sur `tests/unit/sites` + `tests/unit/nexy/docs`. |
