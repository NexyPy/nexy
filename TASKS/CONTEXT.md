# CONTEXT - faits vérifiés dans le dépôt

À lire avant toute tâche. Chaque fait a été lu dans le code, pas déduit du site. Si un fait devient faux, le corriger ici **et** dans les tâches qui le citent.

## Faits

| # | Fait | Preuve |
|---|---|---|
| F1 | `docs/README.md` est **à la fois** la page d'accueil et la source de la navigation. `##` = section, `###` = groupe, chaque ligne de tableau `\| [label](page.md) \| résumé \|` = une page. | `sites/shared/docs_source.py:235` (`read_tracks`) |
| F2 | Réécrire l'intro = réécrire les 3 lignes de tête de `README.md`, **sans toucher** la grammaire des tableaux. | `docs/README.md:1-5` |
| F3 | Le sélecteur de routeur filtre **au plus 3 groupes sur 21** : 4 groupes portent un routeur (Routing et Route handlers → `fbr`, Modular, Custom), les 17 autres restent visibles dans tous les modes. `router_of()` déduit le routeur **du chemin** (`routing/<router>/…`) ; un groupe n'est marqué que si 100 % de ses pages sont sous un seul routeur ; le filtrage est CSS pur. | `docs_source.py:183`, `:230` ; `sites/vanilla/assets/site.js:107-125` ; `test_routers.py:168` |
| F4 | **Trois index à synchroniser** : tableaux de `README.md`, `llms.txt` (manuel, déjà divergent : ~30 pages, renvoie à `ARCHITECTURE.md` pour l'archi), tests. | `llms.txt:9-51` |
| F5 | **Aucun `.md` non listé n'est autorisé dans `docs/`** : un guide de style interne y ferait échouer la suite. | `tests/unit/sites/test_routers.py:70` |
| F6 | Le code des docs est **déjà exécuté** : chaque bloc ```` ```py filename="…" ```` de `guides/recipes.md` est scaffolé dans un vrai projet et testé en e2e. | `tests/unit/nexy/docs/test_recipes.py` |
| F7 | Pages **courtes** : médiane ~450 mots, 86 fichiers, max 1 650 (`reference/exceptions.md`). | mesure sur `docs/**/*.md` |
| F8 | `views/*` = **25 pages sur 86 (29 %)**, 4 sections identiques par framework. | `docs/views/` |
| F9 | Incohérence : le sélecteur annonce « Custom Router - *Create your own router* », la page dit « Custom routing - *Include an existing FastAPI app* ». | `docs_source.py:122` vs `docs/routing/custom/README.md` |
| F10 | Tout lien relatif de `docs/`, `skills/` et des entrées racine doit résoudre ; test paramétré par fichier. | `tests/unit/nexy/docs/test_links.py` |
| F11 | Getting Started est verrouillé par des tests : pas de `uvx nexy dev`, activation du venv, `uv run nexy dev`, ordre activation → serveur. | `tests/unit/nexy/docs/test_setup_guidance.py` |
| F12 | `ROUTERS` est asserté à l'identique dans les tests : changer un libellé casse `test_routers.py:36-41`. | `tests/unit/sites/test_routers.py` |
| F13 | **Il n'existe pas de mode SSG.** `nexy build` prérend en HTML à deux endroits distincts, tous deux consommés **par le serveur Nexy** à la requête : (a) les composants serveur, écrits dans `__nexy__/client/static/**` + `snippets.json` et réinjectés dans les pages `.nexy` (islands) ; (b) les documents client (`useCSR = True` uniquement), écrits en `.document.html` / `.shell.html` / `<path>.html`, puis relus et complétés des assets par `csr_document.py`. Aucun dossier de HTML autonome n'est produit : le serveur reste nécessaire. | `frontend/scripts/ssg.ts:94`, `frontend/document.ts:322-405`, `runtime/csr_document.py:69-88,123-151`, `cli/commands/build.py:105` |
| F14 | Le prérendu des routes dynamiques client s'appuie sur `getStaticPaths` / `generateStaticParams` / `getStaticParams` exportés par la page. Ces trois noms n'apparaissaient **dans aucune page de doc, aucun skill, aucun test** avant DOC-16. | `frontend/document.ts:296-310` |
| F15 | `revalidate(...)` (Action) **n'invalide pas le cache ISR** : il empile des chemins, `header_value()` en fait l'en-tête `x-nexy-revalidate`, et `client/actions.ts:42-49` s'en sert pour recharger la page dans le navigateur. Le cache serveur n'a pas d'API de purge ; seule la fenêtre `revalidate` le vide. | `routers/actions/revalidate.py:7,29`, `frontend/client/actions.ts:40-49` |
| F16 | `client:only` et `client:manual` ne s'hydratent **jamais** automatiquement : `islands.js:40-41` sort avant d'appeler `hydrate()`. `client:only` laisse donc le HTML du build inerte, et `client:manual` n'a aucun déclencheur public. Les pages `views/*/islands.md` ne les listent plus (commit `affe6b2`) ; `rendering/islands.md` et `skills/nexy-file/SKILL.md` les recommandaient encore. | `frontend/islands/islands.js:36-47`, `islands/react.js:145-155` |
| F17 | Une route composant (`.tsx`, `.mdx`, `.vue`, `.svelte`) en mode serveur n'est pas rendue à chaque requête : `__ssr` vaut le HTML du build **en production et sans layout**, `pass` sinon ; en développement il vaut toujours `''`, donc le composant monte côté navigateur. Toute réponse passe par `StreamingResponse`, mais le streaming ne sert que si le composant yield. | `compiler/frontend_route.py:97-111`, `compiler/frontend_templates.py:54-59,108-116`, `routers/fbrouter/handlers.py:86-89` |
| F18 | `.jsx` est déclaré comme extension de route (`ROUTE_FILE_EXTENSIONS`, `FRONTEND_EXTENSIONS`) mais **n'est pas compilable** : `is_framework_route_file()` et `_EXT_TO_FW` l'omettent, donc `Compiler.compile()` l'envoie à `_compile_component()`, qui lève `NexyCompileError` (« is not a nexy component »). Aucun test ne compile une route `.jsx`. À documenter comme non supporté, et à corriger en Chantier 2. | `core/config.py:46-47,101-107`, `compiler/__init__.py:25-27,73-77`, `compiler/frontend_route.py:33-38` |

## Contraintes dures

- **Ne jamais** créer un `.md` dans `docs/` sans l'ajouter à la navigation de `docs/README.md` (F5).
- **Ne jamais** renommer/déplacer une page sans corriger ses liens relatifs (F10) et `llms.txt` (F4).
- **Ne jamais** changer `ROUTERS` sans mettre à jour les tests (F12).
- **Ne jamais** réécrire Getting Started sans relire F11.
- Le dossier `TASKS/` n'est ni lu par les tests, ni publié : il peut évoluer librement.

## Commandes

```bash
# garde-fous de la doc
python -m pytest tests/unit/nexy/docs tests/unit/sites -q

# après tout déplacement ou renommage
python -m pytest tests/unit/nexy/docs/test_links.py -q

# gates complets avant commit
python scripts/verify.py
```

## Règles de rédaction (rappel)

- Pages **conceptuelles** : Definition · How it works · Lifecycle · When to use · Configuration · Example · Limitations · Related.
- Pages de **référence** : tableau strict, aucun paragraphe narratif.
- Trois niveaux de garantie, jamais dans la même phrase : *garanti par Nexy* / *convention* / *à la charge du développeur*.
- Anglais pour tout ce qui entre dans `docs/` ; français accepté dans `TASKS/`.
