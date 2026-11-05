# DOC-27 - Badges de nouveauté dans la navigation

| | |
|---|---|
| **Phase** | P2 - Navigation |
| **Statut** | `fait` |
| **Dépend de** | - (réutilise le précédent de marqueur posé par DOC-06) |
| **Débloque** | - |

## Arbitrage KISS (préambule)

Une badge de nouveauté est un mécanisme de **rétention** : il sert à faire revenir le lecteur. C'est exactement le type de fonctionnalité qui dérive en mini-générateur (dates, expiration, parsing de changelog, état persisté). L'arbitrage posé avant toute ligne de code : **le gain doit tenir dans un seul token de navigation, sans nouvel état et sans nouvel outil.** Si le mécanisme dépasse ce cadre, il est abandonné (critère d'abandon en fin de carte), parce qu'un « What's new » mal fait — périmé, daté, faux — est pire que son absence.

## Problème

Rien aujourd'hui n'invite le lecteur qui est déjà passé à revenir voir ce qui a changé : la sidebar (`read_tracks`, `docs_source.py:268`) rend les pages sans aucun signal de fraîcheur, et il n'existe ni badge New/version, ni entrée « What's new ». Pourtant le projet tient déjà un journal vivant : `CHANGELOG.md` à la racine, au format Keep a Changelog, avec une section `## [Unreleased]` alimentée à chaque changement notable (`cliff.toml` le publie à la release). **La source de vérité existe ; seule la signalisation dans la navigation manque.**

## Solution proposée (un seul mécanisme)

Un token de nouveauté en fin de cellule résumé d'une ligne de tableau de `docs/README.md`, calqué sur le marqueur de groupe `{fbr}` de DOC-06 :

```md
| [Page metadata](routing/fbr/pages/metadata.md) | Set the title, description and share image of a page {new} |
```

- `read_tracks` retire le token du résumé (sinon il fuirait dans la recherche, `search_entry`, et dans le texte de la page) et le publie comme champ `badge` sur `Page`.
- Les deux sidebars affichent une pastille sobre, neutre, libellée **« New »**. Un seul libellé possible : pas de `Updated`, pas de numéro de version, pas de date.
- **Adossement au CHANGELOG, à la main** : le token vit le temps que son entrée reste dans `[Unreleased]` ; le geste de release — celui qui coupe la version dans `CHANGELOG.md` — retire en même temps les tokens `{new}` des lignes publiées. Aucun script ne fait ce lien.
- Aucune nouvelle page, aucun nouveau groupe : la grammaire F1 (`##` section, `###` groupe, une ligne = une page) est étendue d'un token **en fin de cellule**, rien d'autre. F5 et F4 ne bougent pas (aucun `.md` créé, `llms.txt` ignore la badge — les agents ne connaissent pas la nouveauté du menu).

Le piège à traiter explicitement : `docs/README.md` est **aussi** la page d'accueil rendue (`home()`, `docs_source.py:248`). Son tableau s'affiche en HTML ; sans retrait du token au rendu — ce que `_identify()` fait déjà pour les marqueurs de titre (`docs_source.py:747`) — la page d'accueil afficherait `{new}` en clair.

## Alternatives écartées

| Alternative | Pourquoi écartée |
|---|---|
| Page `docs/whats-new.md` régénérée depuis `CHANGELOG.md` par un script | Un deuxième index à synchroniser (viole l'esprit de F4/F5), du contenu dupliqué, et un générateur dès le premier jour |
| Dates par page (frontmatter) avec expiration automatique (« New pendant 30 jours ») | Datation lourde : horloge au rendu, pages périmées silencieusement, nouvelle surface de frontmatter non contractée par `CONTEXT.md` |
| Badge de version (`v0.4`) ou vocabulaire multiple (New / Updated / Changed) | Deux vocaux à tenir cohérents, et le lecteur ne peut pas comparer des numéros qu'il ne voit pas ailleurs ; un seul type de badge est le maximum gérable |
| Parsing de `CHANGELOG.md` pour déduire les pages marquées | Le changelog est narratif, sans chemin de page garanti ; le lien devient un parseur, c'est-à-dire le mini-générateur interdit |

## Fichiers

| Fichier | Action |
|---|---|
| `docs/README.md` | Adopter la convention `{new}` en fin de cellule résumé sur les lignes concernées ; aucune ligne structurelle ajoutée |
| `sites/shared/docs_source.py` | `Page.badge` ; regex `_NEW` en fin de dernier cellule (repli sur `_SCOPE:152`) ; retrait du token dans `_summary`/`_page` et au rendu de l'accueil (via `_identify`, `:747`) |
| `sites/vanilla/build.py` | Pastille `New` après le lien, dans le menu seulement |
| `sites/vanilla/assets/style.css` | Une classe neutre pour la pastille |
| `sites/nexy/src/content.py` | Transmettre `badge` avec la page du menu |
| `sites/nexy/src/components/Sidebar.nexy` | Même pastille |
| `tests/unit/sites/test_docs_source.py` | Badge posée ; token absent du résumé et de la recherche ; token inconnu reste visible (échec visible, comme DOC-06) |
| `tests/unit/sites/test_vanilla_build.py`, `test_nexy_site.py` | Les deux sites émettent la pastille ; `{new}` n'apparaît dans aucun HTML rendu, accueil compris |
| `tests/unit/sites/test_routers.py` | Budget : au plus 6 tokens `{new}` actifs ; grammaire F1 inchangée |

## Critères d'acceptation

- [x] Une ligne marquée `{new}` affiche la pastille « New » dans les deux sidebars
- [x] Le token est invisible partout ailleurs : résumé, page d'accueil rendue, index de recherche
- [x] Une navigation sans aucun token produit un HTML **identique à aujourd'hui** (zéro régression F1)
- [x] Un token inconnu (`{neww}`) n'est pas retiré et fait échouer un test — même faute visible qu'en DOC-06
- [x] Le budget « au plus 6 badges actives » est asserté
- [x] Le geste de retrait des badges publiées est décrit dans le Journal de la carte (le CHANGELOG et sa section `[Unreleased]` existent déjà, rien à créer)

## Garde-fous

- **Un seul type de badge** : le vocabulaire est exactement `new`. Pas de `Updated`, pas de version, pas de couleur d'alerte.
- **Pas de datation lourde** : aucune date, aucun timestamp, aucune expiration calculée dans le code ; l'expiration est le geste manuel à la release.
- **Pas de régression de la grammaire F1** : `##`, `###` et la ligne `| [label](page.md) | résumé |` doivent rester parsées exactement comme aujourd'hui ; le token ne touche ni `_ROW_LINK` (`docs_source.py:26`) ni la structure des tableaux.
- **Périmètre A7** : `docs/` + `sites/` + `tests/unit/sites/` uniquement ; `nexy/` et `CHANGELOG.md` ne sont pas modifiés par cette tâche.

## Critère d'abandon

Si l'implémentation ou la revue exige l'un de ces éléments, la solution a dérivé en mini-générateur et **la carte est abandonnée** :

- parser `CHANGELOG.md` (ou un futur fichier de données) pour décider ce qui est neuf ;
- un script, un job ou une étape de build qui génère ou régénère du contenu de nouveauté ;
- une date, une durée ou une expiration évaluée quelque part dans le rendu ;
- un état persisté (JSON, cache) hors `docs/README.md` ;
- plus d'un token dans le vocabulaire des badges.

Abandon concret : diff reverté, statut `bloqué`, la déviation constatée est consignée au Journal et la décision correspondante est écrite dans `TASKS/README.md` (§Décisions) avant toute reprise.

## Journal

| Date | Note |
|---|---|
| 2026-11-01 | Tâche créée. Syntaxe `{new}` calquée sur le marqueur de groupe de DOC-06 ; adossement au CHANGELOG réduit à un geste humain à la release. Piège relevé dans le code : `docs/README.md` étant aussi la page rendue de l'accueil, le token doit être retiré au rendu comme `_identify()` le fait pour les titres. |
| 2026-11-01 | **Fait.** `Page.badge` (« new » ou vide), `_NEW` en fin de cellule résumé (repli sur `_SCOPE`), retiré de `_summary`, du `search_entry` et du HTML : `render()` nettoie `{new}` avant les figures, donc l'accueil rendu, la recherche et les deux menus l'ignorent. Pastille « New » après le lien dans les deux sidebars (`build._nav_item`, `Sidebar.nexy` + `content._menu_group`), une classe neutre `.side .badge-new` dans l'unique `style.css`. **Geste de release** : quand une section `## [x.y]` est coupée de `[Unreleased]` dans `CHANGELOG.md`, la même personne retire `{new}` des lignes publiées de `docs/README.md` — aucun script ne fait ce lien. **Pages marquées (6, budget max)** : `routing/fbr/pages/metadata` (feature « Page metadata » listée dans `[Unreleased]`, et exemple énoncé de la carte) ; les cinq pages « differences » du groupe Framework differences (`views/{react,vue,svelte,solid,preact}/differences`), créé intégralement par DOC-21 dans ce chantier — marquer le groupe entier évite le caractère arbitraire d'une sélection partielle. `llms.txt` ignore la badge (F4) ; aucun nouveau fichier `.md` ; pas de parseur, pas de date, pas d'état persisté → critère d'abandon non déclenché. |
| 2026-11-01 | **Ajustement A11.** La pastille se pose sur la ligne du label, plus sous celle-ci : `.side li` en `display: flex` avec l'ancre en `flex: 1 1 auto`, `.badge-new` en `flex: none` en fin de ligne. Markup inchangé (`</a><span class="badge-new">New</span>` dans le même `<li>`), verrouillé par `test_the_pill_sits_on_the_label_line`. Le retrait des descriptions (DOC-25 revertée) ne change rien au token ni au budget. |
