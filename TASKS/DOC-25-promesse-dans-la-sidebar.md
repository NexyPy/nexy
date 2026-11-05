# DOC-25 - La promesse d'action dans la sidebar

| | |
|---|---|
| **Phase** | P2 - Navigation |
| **Statut** | `bloqué` - abandonnée sous A11 (2026-11-01), diff reverté |
| **Dépend de** | - (côtoie DOC-09 pour le filtrage du texte) |
| **Débloque** | - |

## Objectif

Montrer, sous le label de chaque page du menu, la promesse d'action de cette page - la deuxième colonne du tableau de `docs/README.md` (« What you will do ») - pour qu'un lecteur choisisse une page en la lisant dans la sidebar, sans devoir repasser par l'accueil.

## Problème

La promesse est écrite, extraite, et jetée.

- `_summary()` (`sites/shared/docs_source.py:258`) découpe la cellule suivante la ligne du tableau ; `read_tracks()` l'affecte à `Page.summary` (`docs_source.py:165`, alimenté en `:327`). Le docstring de `Page` promet pourtant « the words the menu shows for it ».
- Côté vanilla, `_nav_item()` (`sites/vanilla/build.py:94-96`) n'émet que `escape(page.label)`. Côté nexy, `_menu_group()` (`sites/nexy/src/content.py:114-117`) ne construit que `{href, label, current}` et `Sidebar.nexy:54` n'imprime que `page.label`.
- Résultat : le texte « What you will do » n'apparaît **que** sur la page d'accueil des docs, là où le Markdown de `docs/README.md` est rendu. Le menu, lui, est une liste de 95 labels sans verbe.

## Contexte utile

- La grammaire de la nav est figée (F1) : `##` section, `###` groupe, une ligne de tableau = une page, **pas de sous-niveau**. La promesse n'est pas un nouveau niveau : c'est déjà la deuxième colonne de la ligne existante. **Cette tâche ne touche donc pas `docs/README.md`.**
- Mesure sur les 95 lignes de la nav : **7 mots par promesse** (médiane), 16 mots et 85 caractères au maximum (« Build a notes page with an endpoint, shared data and a production build in 10 minutes »). La densité est le vrai risque, pas la donnée.
- Un groupe est déjà un accordéon : seul celui qui porte la page courante est ouvert (`build.py:99-111`, `Sidebar.nexy:47`). C'est le levier KISS de la densité.
- Deux tests verrouillent le contenu exact d'une ligne de menu, et ils doivent rester verts :
  - `test_the_menu_marks_the_current_page` : regex `<a [^>]*aria-current="page"[^>]*>Actions</a>` (`tests/unit/sites/test_vanilla_build.py:77` et `tests/unit/sites/test_nexy_site.py:59`) - le texte **du lien** doit rester le label seul.
  - `test_a_section_lists_all_its_pages` : compte les `<li>` (`test_vanilla_build.py:101`) - la promesse n'est pas un élément de liste de plus.
- `test_a_section_carries_no_sentence` (`test_vanilla_build.py:103`) interdit la **phrase de groupe** (`class="group-note"`) dans l'accordéon : la prose du groupe reste sur l'accueil. Ce n'est pas la même chose qu'une promesse par page ; la distinction est à écrire dans le test, pas à contourner.
- Le filtre du menu lit `item.textContent` (`sites/vanilla/assets/site.js:148`) : ajouter du texte dans le `<li>` élargit silencieusement les correspondances. C'est une décision, pas un effet de bord - DOC-09 est propriétaire du périmètre de recherche.

## Solution

La promesse devient un frère du lien, pas son contenu.

1. Un seul format, dans les deux sites : `<li><a>label</a><small class="page-summary">promesse</small></li>`. Le `<a>` garde le label pour seul texte (les deux tests ci-dessus restent verts), le `<small>` porte le `page.summary` déjà calculé.
2. **Densité réglée par l'accordéon, pas par un interrupteur** : la promesse n'est dessinée que dans le groupe ouvert. Les autres groupes repliés gardent leurs labels invisibles - rien de nouveau à scanner. C'est l'option par défaut ; l'affichage systématique ne se décide que si la version par défaut est jugée trop discrète.
3. CSS : `line-clamp` sur 2 lignes maximum, couleur `--muted`, taille déjà utilisée par `.side a` (`sites/vanilla/assets/style.css:519`). Aucun nouveau token de style.
4. Une promesse vide (`_summary` renvoie `""` sur une ligne sans deuxième cellule) n'émet pas de `<small>` : pas de ligne vide dans le menu.
5. Pas de générateur de site doc supplémentaire (gotcha `docs/` des agents.md) : les deux sites consomment la même `Page.summary`, comme ils consomment déjà `Page.label`.

## Fichiers

| Fichier | Action |
|---|---|
| `sites/vanilla/build.py` | `_nav_item()` émet `<small class="page-summary">` quand `page.summary` est non vide |
| `sites/nexy/src/content.py` | `_menu_group()` ajoute `"summary": p.summary` au dictionnaire de page |
| `sites/nexy/src/components/Sidebar.nexy` | Ligne 54 : même balise après le lien, sous `{% if page.summary %}` |
| `sites/vanilla/assets/style.css` | `.side .page-summary` : 2 lignes max, `--muted`, visible seulement dans `details[open]` - **une seule feuille pour les deux sites** (`content.py:21` sert `vanilla/assets`, `layout.nexy:28` la charge) |
| `sites/vanilla/assets/site.js` | Le filtre ne matcher que le label (lire `.page-name`/le `<a>`, pas `textContent` du `<li>`), ou assumer le contraire explicitement |
| `tests/unit/sites/test_vanilla_build.py` | Cas : une ligne ouverte porte sa promesse ; le lien garde le label seul ; préciser l'intention de `test_a_section_carries_no_sentence` |
| `tests/unit/sites/test_nexy_site.py` | Cas miroir sur le menu rendu par le site nexy |

## Critère de fin

- [x] `Page.summary` est affiché dans la sidebar des **deux** sites, sans nouvelle lecture de `docs/README.md`
- [x] La grammaire F1 est intacte : `docs/README.md` n'a pas changé, aucun sous-niveau ajouté
- [x] Le texte du lien reste exactement le label (`test_the_menu_marks_the_current_page` vert tel quel)
- [x] Une section du menu contient toujours exactement `len(group.pages)` `<li>`
- [x] Un groupe replié ne montre aucune promesse ; le groupe ouvert montre les siennes, coupées à 2 lignes
- [x] Une page sans deuxième cellule de tableau n'affiche pas de `<small>` vide
- [x] Le comportement du filtre du menu est décidé et testé, pas subi
- [x] `python -m pytest tests/unit/nexy/docs tests/unit/sites -q` vert, puis `python scripts/verify.py`

## Garde-fous

- **F1** : rien dans cette tâche n'ajoute une ligne, une colonne ou un niveau à la nav. La donnée est déjà là ; seul le rendu change.
- **Densité** : la sidebar est l'objet le plus scanné du site. Si l'affichage « groupe ouvert » suffit, on s'y tient - ne pas ajouter de bascule « show descriptions ».
- **Paraphrase interdite** : la promesse affichée est la cellule du tableau, mot pour mot. Aucune réécriture, aucun troncature en Python (le CSS coupe).
- **Les deux sites rendent la même chose** : `sites/vanilla` et `sites/nexy` partagent `docs_source.py` ; une divergence de rendu entre les deux est un bug, pas une préférence.
- **Hors périmètre** : la phrase de groupe (`group_blurb`) et le badge de périmètre des résultats de recherche (DOC-09).

## Journal

| Date | Note |
|---|---|
| 2026-11-01 | Tâche créée. Donnée déjà extraite (`_summary`, `docs_source.py:258`) et non affichée : le travail est du rendu, pas de l'écriture. Density mesurée sur les 95 lignes (médiane 7 mots, max 16). Deux tests (`aria-current` sur le texte du lien, comptage des `<li>`) imposent le `<small>` comme frère du lien ; l'accordéon existant règle la densité. |
| 2026-11-01 | Fait, tests d'abord. Rendu : `_nav_item()` (vanilla) et `Sidebar.nexy` + `_menu_group()` (nexy) émettent `<small class="page-summary">` après le `<a>`, seulement si `page.summary` est non vide ; le `<a>` garde le label seul. CSS : `.side .page-summary` masqué, visible dans `details[open]` avec `line-clamp: 2` et `--muted`, taille de `.side a` (13.5px) — une seule feuille pour les deux sites. **Décision filtre** : `site.js` lit `item.querySelector('a').textContent`, le filtre ne matche que le label, jamais la promesse ; verrouillé par `test_the_menu_filter_reads_the_label_not_the_promise`. Quatre tests vanilla ajoutés (promesse de la page courante, format strict de l'item, pas de `<small>` sur résumé vide, règle CSS) + un miroir nexy ; `test_a_section_carries_no_sentence` précise son intention : la prose de groupe (`group-note`) reste bannie, la promesse par page est de la donnée. Garde-fous : `pytest tests/unit/nexy/docs tests/unit/sites` = 476 verts ; `verify.py` vert sur lint/format/mypy/structure. La porte `test` de `verify.py` échoue sur 22 échecs **préexistants et hors périmètre** sur cette machine Windows (`tests/unit/nexy/cli`, `watcher`, `test_testing.py` : encodage console des glyphes, spinner, prompts TTY) — aucun n'importe `sites/` ni les fichiers touchés ici ; à confirmer par le CI Linux. Rien à faire sur les 95 pages : toutes portent déjà une promesse (`_summary` n'est jamais vide sur l'état actuel de `docs/README.md`), le cas vide reste couvert par le test. |
| 2026-11-01 | **Revertée sous A11.** Décision utilisateur : pas de description sous les liens dans les accordéons de la sidebar. Diff retiré des deux sites (`_nav_item`, `Sidebar.nexy`, `_menu_group`), règles `.page-summary` supprimées, tests remplacés par `test_a_menu_item_is_the_link_then_the_pill` / `test_the_menu_draws_no_description` (+ miroir nexy) qui verrouillent l'inverse. Le filtre label-only de `site.js` est conservé (test `test_the_menu_filter_reads_the_label`). `Page.summary` reste dans la donnée — d'autres surfaces peuvent la prendre. 514 tests sites+docs verts. |
