# CONTEXT — faits vérifiés dans le dépôt

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
| F9 | Incohérence : le sélecteur annonce « Custom Router — *Create your own router* », la page dit « Custom routing — *Include an existing FastAPI app* ». | `docs_source.py:122` vs `docs/routing/custom/README.md` |
| F10 | Tout lien relatif de `docs/`, `skills/` et des entrées racine doit résoudre ; test paramétré par fichier. | `tests/unit/nexy/docs/test_links.py` |
| F11 | Getting Started est verrouillé par des tests : pas de `uvx nexy dev`, activation du venv, `uv run nexy dev`, ordre activation → serveur. | `tests/unit/nexy/docs/test_setup_guidance.py` |
| F12 | `ROUTERS` est asserté à l'identique dans les tests : changer un libellé casse `test_routers.py:36-41`. | `tests/unit/sites/test_routers.py` |

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
