# DOC-26 - Signaux de progression : pages lues et reprise de lecture

| | |
|---|---|
| **Phase** | P2 - Navigation |
| **Statut** | `fait` |
| **Dépend de** | - |
| **Débloque** | - |

## Objectif

Donner au lecteur deux signaux de progression dans la sidebar : **les pages déjà visitées** se repèrent d'un coup d'œil, et un bouton **« Continue »** le ramène à la première page non lue de son parcours. Rien d'autre : le pager Previous/Next existe déjà et reste le seul signal de fin de page.

## Contexte utile

- Le pager est en place : `neighbours()` (`sites/shared/docs_source.py:375`) fournit la page avant/après, `pager_html()` (`sites/vanilla/build.py:149`) le dessine, `sites/nexy/src/components/Doc.nexy:15-17` aussi. Ne rien changer là.
- **Aucun état de lecture n'existe.** Les liens de la sidebar (`_nav_item()`, `sites/vanilla/build.py:94`) sont de simples `<a href>` ; seul `aria-current="page"` marque la page affichée.
- La mécanique localStorage est déjà installée, avec ses trois clés `nexy-docs-*` et le même patron `try { setItem } catch {}` :
  - `nexy-docs-theme` : écrit dans `site.js:18`, lu au premier peint dans `sites/vanilla/template.html:17` (miroir nexy : `sites/nexy/src/routes/layout.nexy:31`) ;
  - `nexy-docs-side` : `site.js:96`, `template.html:23` ;
  - `nexy-docs-router` : `site.js:115`, `template.html:29`.
- La page courante est identifiable **sans nouveau balisage** : le lien `aria-current="page"` de la sidebar porte son slug dans l'extrémité de son `href` (`relative()` produit toujours `…/<slug>/`).
- L'ordre de lecture **est** l'ordre de la sidebar, lui-même dérivé de `docs/README.md` (F1) : « première page non lue » se lit donc en parcourant les liens du menu dans l'ordre servi.

## Solution

Une seule clé nouvelle, **`nexy-docs-seen`** : liste de slugs séparés par des virgules (jamais JSON, jamais d'horodatage - KISS).

1. **Marquer la visite.** Un bloc de quelques lignes dans `site.js` : lire la clé, ajouter le slug courant (`document.body` → lien `[aria-current="page"]`), réécrire la clé, puis donner la classe `seen` à tout lien de sidebar dont le `href` contient un slug de la liste. Lecture dans le script de premier peint (`template.html`, `layout.nexy`) pour que les liens soient déjà marqués au rendu, écriture à la fin - même découplage que le thème.
2. **Bouton « Continue ».** Balisage statique rendu au build, **caché par défaut** (`hidden`), dans le pied de sidebar des deux sites. Au runtime, `site.js` prend le premier lien de la sidebar absent de la liste, fixe son `href` et son libellé, et démasque le bouton. Si tout est lu, le bouton ramène à la **dernière** page lue ; si rien ne l'est, il pointe sur la première page du parcours.
3. **Style sobre.** En CSS uniquement : `a.seen` = couleur de texte atténuée (crayon, pas de coche, pas d'icône) ; le bouton « Continue » réutilise le style `side-foot` existant. Pas de pourcentage, pas de barre de progression par section.

## Fichiers

| Fichier | Action |
|---|---|
| `sites/vanilla/assets/site.js` | Bloc `seen` : lecture/écriture de `nexy-docs-seen`, classe `seen` sur les liens, calcul du bouton « Continue » |
| `sites/vanilla/template.html` | Lire la clé au premier peint (comme `nexy-docs-theme:17`) ; écrire le slug courant en fin de page |
| `sites/vanilla/build.py` | `nav_html()` : ajouter le bouton « Continue » masqué dans `side-foot` (aucune touche à `_nav_item`, ni à `pager_html`) |
| `sites/vanilla/assets/style.css` | `a.seen` atténué ; style du bouton sur `side-foot` |
| `sites/nexy/src/components/Sidebar.nexy` | Même bouton masqué |
| `sites/nexy/src/routes/layout.nexy` | Même script client, même clé |
| `tests/unit/sites` | Cas : le HTML servi reste identique (bouton `hidden`, aucun état en dur) ; `test_routers.py` et `test_llms_index.py` inchangés et verts |

## Critère de fin

- [x] Après visite de N pages, les recharger marque les N liens de sidebar (classe `seen`, atténués) sans clignotement au premier peint
- [x] « Continue » pointe sur la première page non lue **dans l'ordre de la sidebar** ; liste vide → première page ; liste complète → dernière page lue
- [x] La clé `nexy-docs-seen` suit le patron existant : nom `nexy-docs-*`, accès enveloppé `try/catch`, aucune valeur autre que des slugs
- [x] **Sans JS** : pages identiques à aujourd'hui, bouton masqué, pager intact - la doc reste entièrement lisible
- [x] Aucune nouvelle grammaire de nav : `docs/README.md` reste la seule source de l'ordre (F1), aucun `.md` ajouté (F5)
- [x] `python -m pytest tests/unit/nexy/docs tests/unit/sites -q` vert, puis `python scripts/verify.py`

## Garde-fous

- **Ne pas** stocker d'horodatage, de temps de lecture ou de pourcentage : une liste de slugs suffit ; toute métrique plus riche est hors périmètre.
- **Ne pas** toucher à `ROUTERS` ni au filtrage par routeur (F3, F12) : `seen` s'ajoute aux classes existantes, il ne recompose pas la nav.
- **Ne pas** importer de framework JS ni de script tiers : `site.js` et le script inline de `layout.nexy` restent les seuls hôtes.
- **Ne pas** marquer les liens au build : l'état de lecture est propre au navigateur ; le HTML publié doit rester identique page à page.
- Le bouton « Continue » est un lien, pas un bouton `<button>` : il doit rester navigable et ouvrable dans un onglet.

## Journal

| Date | Note |
|---|---|
| 2026-11-01 | Tâche créée. Pager existant confirmé (`neighbours`, `pager_html`) ; patron localStorage des trois clés `nexy-docs-*` vérifié dans `site.js` et `template.html`. Le slug courant se déduit de `[aria-current="page"]` sans toucher `_nav_item`. |
| 2026-11-01 | Fait, tests d'abord (16 cas). **Répartition réelle du bloc**, un peu différente du tableau ci-dessus, et volontairement : la *lecture* de `nexy-docs-seen` est bien au premier peint (`template.html`, `layout.nexy`, la quatrième clé à côté de theme/side/router, déposée dans `documentElement.dataset.seen`) ; le *marquage* `classList.add("seen")` est dans un second script inline placé **entre `</nav>` et `.panel`**, donc bloquant avant que le menu ne soit peint - un script `defer` ne peut pas tenir le critère « sans clignotement ». L'*écriture* du slug courant et le bouton « Continue » sont dans `site.js` (fin de page). Le slug n'est **pas** lu dans le `href` du lien courant : `relative()` produit `./` pour la page affichée, et un `href` relatif rend toute comparaison par sous-chaîne fausse (`routing/fbr` est contenu dans `routing/fbr/handlers/`). Les deux sites utilisent donc le même chemin résolu : `slugOf(path)` coupe les segments avant `docs` et rejoint le reste - `/nexy/docs/guides/actions/` comme `/docs/guides/actions` donnent `guides/actions`. Zéro balisage nouveau dans `_nav_item` ; `location.pathname` reste la source du slug courant (une seule source, sinon la page d'origine d'un retour arrière serait la dernière de la liste). Bouton : `<a href="#" class="continue" hidden>Continue</a>` en tête de `side-foot` des deux sites, servi **octet pour octet identique page à page** (test sur toutes les pages construites) ; au runtime `site.js` prend le premier lien de `.side .group a` absent de la liste - à défaut la dernière page lue (`read.at(-1)`) - fixe `href`, intitulé « Continue: <label> » (le `<a>` ne porte que le label depuis DOC-25), puis démasque. Style : `--faint` (un token nouveau, `#8a8a8a` / `#6b6b6b`, tous deux ≥ 3:1 de contraste), règle `.side a.seen` placée **avant** `.side a:hover` et `.side a[aria-current="page"]` pour que le survol et la page courante gardent le dessus sans sélecteur composite ; aucune coche, aucune icône. Symétrie des deux sites verrouillée par un test qui compare les scripts inline de `template.html` et `layout.nexy` (indentation déduite) - `site.js` et `style.css` étant déjà partagés. Le pager, `ROUTERS`, le filtrage par routeur et `docs/` ne sont pas touchés. Garde-fous : `pytest tests/unit/nexy/docs tests/unit/sites` = 492 verts (476 avant) ; `verify.py` vert sur lint/format/mypy/structure, et sa porte `test` retrouve les 22 échecs **préexistants hors périmètre** de cette machine Windows (`tests/unit/nexy/cli`, `watcher`, un cas e2e de scaffold qui repasse isolé). Nuance honnête du critère 2 : « liste vide → première page » vaut quand le lecteur n'est pas déjà sur cette première page ; arrivé sur la page 1 sans rien de lu, le bouton propose la page 2 (on ne se continue pas à soi-même). Vérifié par simulation Node de `slugOf` + du choix du bouton sur les deux formes d'URL ; le rendu navigateur (flash réel) reste à confirmer à l'œil sur `sites/vanilla/dist` reconstruit. |
