# DOC-06 — Marqueurs de groupe dans la navigation

| | |
|---|---|
| **Phase** | P2 — Navigation |
| **Statut** | `prêt` |
| **Dépend de** | — |
| **Débloque** | DOC-07, DOC-08, DOC-09 |

## Objectif

Remplacer la déduction du routeur par le chemin (F3) par une **déclaration explicite au niveau du groupe**, seul grain qui compte pour la lecture (A4). Une page ne bouge pas, une URL ne change pas.

## Contexte utile

- `read_tracks` lit `### Titre` en `docs_source.py:270-275` puis crée `Group(title, blurb, pages, _router_of_group(pages))`.
- `_router_of_group` (`:230`) ne marque un groupe que si **toutes** ses pages sont sous `routing/<router>/`. Conséquence : impossible de marquer « Advanced », impossible de sortir un groupe du filtre sans déplacer des fichiers.
- Le filtrage réel est CSS (`test_routers.py:168`), donc la nouvelle donnée doit arriver jusqu'au HTML.

## Syntaxe proposée

```md
### Routing {fbr}
### Modular router {modular}
### Custom router integration {custom}
### Advanced {advanced}
### Forms and data
```

Sans marqueur → `core` (toujours visible). Le marqueur est retiré du titre affiché.

## Implémentation

| Fichier | Changement |
|---|---|
| `sites/shared/docs_source.py` | `_SCOPE = re.compile(r"\s*\{([a-z]+)\}\s*$")` ; `Group` gagne `scope: str = "core"` ; `close_group()` retire le marqueur du titre et fixe `scope` ; `router` devient `scope if scope in router keys else None` (compatibilité) |
| `sites/vanilla/build.py` | émettre `data-scope` à côté de `data-router` |
| `sites/nexy/src/content.py` | `_menu_group` transmet `scope` |
| `sites/nexy/src/components/Sidebar.nexy` | `data-scope` sur `<details class="group">` |
| `sites/vanilla/assets/style.css` | règles `html[data-mode=…] [data-scope]:not(…)` |
| `tests/unit/sites/test_routers.py`, `test_docs_source.py` | nouveaux cas : marqueur explicite prioritaire, repli par déduction, titre nettoyé |

## Critère de fin

- [ ] Un groupe déclaré `{modular}` est filtré **même si** ses pages ne sont pas sous `routing/modular/`
- [ ] Un groupe sans marqueur se comporte exactement comme aujourd'hui (repli, zéro régression)
- [ ] Le titre affiché ne contient jamais `{…}`
- [ ] Les tests existants de déduction passent sans modification
- [ ] Aucun déplacement de fichier, aucune URL modifiée

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Syntaxe et points d'implémentation relevés dans le code. |
