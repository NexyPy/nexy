# Plan qualité Nexy - Audit & feuille de route

> **Mise à jour du 2026-10-27.** Les chiffres des sections 1 à 3 datent du 2026-10-18 et ne sont plus
> exacts. État mesuré le 2026-10-27, branche `feature/csr-layout-conventions`, Python 3.13 :
>
> | Garde-fou | Résultat |
> |---|---|
> | `ruff check nexy/ tests/` | 0 erreur |
> | `ruff format --check nexy/ tests/` | 378 fichiers formatés |
> | `mypy nexy --strict` | 0 erreur, 203 fichiers |
> | `bandit -r nexy/ -c .bandit` | 0 finding |
> | `audit_structure.py --check` | passe |
> | `pip-audit` (`audit_dependencies.py`) | aucune vulnérabilité connue, 1 ignorée (voir `SECURITY.md`) |
> | Couverture (branches) | 86,3 %, seuil `fail_under` = 84 |
> | Tests | voir `CHANGELOG.md` et la CI; les tests e2e (`-m e2e`) tournent dans `e2e.yml` |
>
> Le reste de ce document est conservé comme historique de la feuille de route.

> **Statut initial : DRAFT, en attente de validation. Aucun fichier source n'a été modifié.**
> Date des mesures initiales : 2026-10-18 · Branche `V2` · Python 3.13 / 3.14

---

## 0. Comment ces chiffres ont été obtenus

```bash
# Install (après ajout de pytest-cov, voir P0-1)
uv pip install -e . && uv pip install pytest-cov

# Couverture
./.venv/Scripts/python.exe -m pytest tests/ -q --cov=nexy --cov-report=term:skip-covered

# Lint / Format / Typecheck
./.venv/Scripts/ruff.exe check nexy/
./.venv/Scripts/ruff.exe format nexy/ --check
./.venv/Scripts/python.exe -m mypy nexy --strict

# Statistiques docstrings (AST, pas de regex)
python - <<'EOF'
import ast, pathlib
# compte les defs/classes publics, leur docstring, et la présence
# des sections Google (Args: / Returns: / Raises: ...)
EOF
```

Tous les nombres ci-dessous sont mesurés, pas estimés.

---

## 1. Réponse aux quatre questions

### 1.1 - « Tout le code de `nexy/` est-il testé ? » → **NON**

| Indicateur | Valeur |
|---|---|
| Tests qui passent | **304** (46 fichiers unitaires, 274 fonctions de test) |
| Instructions (statements) dans `nexy/` (coverage.py `num_statements`) | **5 930** |
| Lignes couvertes | **3 214** |
| **Lignes non couvertes** | **2 716** |
| **Couverture globale** | **54 %** |
| Fichiers à **100 %** | 31 / 125 |
| Fichiers **≥ 95 %** (cible annoncée) | **38 / 125** |
| Fichiers **< 95 %** | **87 / 125** |
| Fichiers à **0 %** | **11 / 125** |

**La cible documentée de 95 % par module n'est atteinte que par 30 % des fichiers.**

> *38 fichiers et non 40 : le rapport textuel de coverage.py arrondit `percent_covered` à la dizaine, la mesure JSON ci-dessus est exacte (0 fichier de plus, 2 fichiers redescendus sous 95 %).*

### 1.2 - « Rigueur type Google, strict, zéro tolérance aux erreurs ? » → **NON**

| Garde-fou | État réel |
|---|---|
| `ruff check nexy/` | **114 erreurs** (échec) |
| `ruff format nexy/ --check` | ✅ 126 fichiers formatés |
| `mypy nexy --strict` | **144 erreurs / 40 fichiers** (échec) |
| `pytest` | ✅ 304 passed |
| **Score : 2 gates sur 4 au vert** | |

Détail des règles ruff en échec :

| Règle | Nb | Signification |
|---|---|---|
| `N815` | 49 | variable `mixedCase` en scope de classe (ex. `useFF`, `useRouter`) |
| `E501` | 26 | ligne > 100 caractères |
| `N802` | 22 | nom de fonction non lowercase (ex. `Controller`, `UseGuard`) |
| `N812` | 4 | `audio` importé en `Audio` |
| `W291` | 3 | espace final (`utils/init/registry.py`) |
| `SIM108` | 3 | `if/else` → opérateur ternaire |
| `B008` | 2 | appel de fonction en valeur par défaut (`typer.Option`) |
| `UP035` / `SIM102` / `N807` / `F841` / `ARG001` | 1+1+1+1+1 | dont **1 variable morte** |

Détail mypy `--strict` (top codes) :

| Code | Nb | Interprétation |
|---|---|---|
| `attr-defined` | 44 | attribut déclaré nowhere - cause principale : 7 champs `Config` absents (`type[Config] has no attribute "useTocDepth"` à `core/config.py:225`) ; réparti sur **11 fichiers**, pas une seule cause |
| `arg-type` | 29 | arguments incompatibles |
| `no-untyped-def` | 16 | fonctions sans annotation de retour |
| `type-arg` | 15 | generics non paramétrés |
| `no-untyped-call` | 13 | appel à une fonction non typée |
| `union-attr` / `assignment` | 4 + 4 | |
| `import-not-found` | **3** | dépendances manquantes réelles |
| `override` | 1 | signature incompatible avec la `supertype` |

### 1.3 - « Docstrings pydoc Google style uniquement, rien d'autre ? » → **NON**

Mesure AST sur toutes les fonctions et classes **publiques** de `nexy/` :

| | |
|---|---|
| API publiques (defs + classes non `_`) | **365** |
| …qui **ont** une docstring | **145** (40 %) → **220 en manquent** |
| …qui ont une section **Google** (`Args:` / `Returns:` / `Raises:`) | **0** |
| **À convertir/écrire en Google style** | **365** |

`CONTRIBUTING.md` (rubrique *Coding standards → Python*) l'exige déjà :

> **Docstrings**: Google style (public APIs)

Autres écarts par rapport à « que dans du pydoc » :

- **298 commentaires `#`** hors docstrings (`nexy/audio.py:12 # Build attributes`, …).
- **Commentaires en français**, contre la règle « All code in English » :
  - `nexy/builder/discovery.py:59` → `# # 2. Lance le scan`
- **Code mort commenté** :
  - `nexy/builder/discovery.py:57-62`
  - `nexy/cli/__init__.py:123-124`
- **11 suppressions** `noqa` / `type: ignore` (tolérance explicite aux erreurs), dont **4 mortes** :
  - `# noqa: A002` ×4 (`compiler/frontend_route.py:275`, `compiler/markdown_route.py:36`, `compiler/__init__.py:110`, `compiler/__init__.py:154`) - la règle `A` **n'est pas dans** `select`, ces suppressions ne servent à rien.
  - Les 7 autres (`F401`×3, `B008`, `F403`, `ARG001`, `type: ignore[import-untyped]`) sont valides mais **aucune n'est justifiée** en clair.
- **Aucun `conftest.py`** dans le projet → les fixtures sont recopiées.

### 1.4 - « Tests unitaires et d'intégration ? »

| Type | État réel |
|---|---|
| **Unitaires** | ✅ **304 tests verts** (7,6 s) |
| **Intégration** | ❌ **0 test** - les 2 fichiers sont **vides (0 octet)** |

- `tests/integration/test_runtime.py` → 0 octet
- `tests/integration/nexy/builder/test_builder.py` → 0 octet
- `pytest tests/integration` → `no tests ran in 0.02s`

### 1.5 - Qualité des assertions (règle « one assertion per test »)

| | |
|---|---|
| Nommage `test_<thing>_<scenario>` | **98 %** (271 / 274) ✅ |
| Assertions moyennes par test | **1,4** |
| Tests avec **plusieurs assertions** | **77 (28 %)** ⚠️ |
| Total de `pytest.raises` | **13**, répartis sur **8 fichiers** → **38 fichiers de test n'ont aucun cas d'erreur** |

---

## 2. Écarts entre les règles écrites et la réalité

| Règle | Source | Constat |
|---|---|---|
| Coverage target 95 %/module | `CONTRIBUTING.md:213`, `AGENTS.md` | **54 %** réel, **aucune fenêtre CI ne l'applique** |
| Docstrings Google style (public API) | `CONTRIBUTING.md` | **0 %** appliqué |
| `mypy --strict` | `pyproject.toml [tool.mypy]` | **144 erreurs** |
| One assertion per test | `CONTRIBUTING.md` | **28 %** des tests le violent |
| All code in English | `AGENTS.md` | commentaires FR résiduels |
| `uv pip install -e ".[dev]"` | `AGENTS.md`, `CONTRIBUTING.md`, **`.github/workflows/ci.yml:24`** | **échec** : `pyproject.toml` n'a **pas** d'extra `dev`, c'est un `[dependency-groups]` → réel message : *"does not have an extra named `dev`"* |
| `pytest-cov` requis par l'étape *Test coverage* de la CI | `.github/workflows/ci.yml:39` | **absent** du groupe `dev` |
| Portée des tests d'intégration | `tests/integration/` | **0 test** |

**Conséquence : la CI `.github/workflows/ci.yml` ne peut pas passer aujourd'hui** - l'install (`:24`) laisse tomber pytest/mypy/ruff, et même corrigée, `ruff` (114) et `mypy` (144) échoueraient.

Il n'existe **aucun** seuil de couverture (`fail_under`), **aucune** couverture de branches, **aucune** omission dans `pyproject.toml`.

---

## 3. Plan priorisé

L'ordre n'est pas arbitraire : P0 est bloquant pour **mesurer**, P1/P2 pour **protéger**, P3 pour **verrouiller**, P4 pour **documenter** (après P3, sinon `E501` casse les nouvelles docstrings), P5 pour **durcir**.

### P0 - Réparer la mesure et la CI *(bloquant, ~0,5 jour)*

| # | Fichier | Action |
|---|---|---|
| 0.1 | `pyproject.toml` | Ajouter `pytest-cov>=6` au groupe `[dependency-groups].dev` |
| 0.2 | `pyproject.toml` | Ajouter `[tool.coverage.run] branch = true`, `source = ["nexy"]`, `omit = ["nexy/templates/*", "nexy/__version__.py"]` |
| 0.3 | `pyproject.toml` | Ajouter `[tool.coverage.report] fail_under = 54, show_missing = true, exclude_altogether = ["if TYPE_CHECKING:"]` - **`fail_under` sert d'anti-régression : il ne peut que monter** |
| 0.4 | `pyproject.toml` | Ajouter `RUF` à `lint.select` (détecte les `noqa` morts, ex. les 4 `A002`) |
| 0.5 | `.github/workflows/ci.yml:24` | `uv pip install -e ".[dev]"` → `uv pip install -e . --group dev` (ou `uv sync --group dev`) |
| 0.6 | `CONTRIBUTING.md` (*Quick start*, *Development setup*) + `AGENTS.md` (*Commands*) | Remplacer `uv pip install -e ".[dev]"` par la commande réelle |
| 0.7 | `.github/workflows/ci.yml:39` | Passer `--cov-fail-under=54` explicitement, puis le relever phase par phase |
| 0.8 | `tests/conftest.py` | **Créer** : fixtures partagées (`tmp_project`, `vfs`, `client`) - n'existe pas aujourd'hui |

**Critère d'acceptation P0** : les 4 commandes sortent 0 ; `pytest --cov=nexy` refuse de passer si la couverture descend ; `AGENTS.md` et `CONTRIBUTING.md` ne référencent plus `".[dev]"`.

---

### P1 - Tests d'intégration *(0 → réel, ~1,5 jour)*

Les deux fichiers existants sont des zéros : les remplir plutôt que d'en créer de nouveaux.

**`tests/conftest.py`** (pagaille du P0) : fixtures `tmp_project` (scaffold `.nexy` minimal dans `tmp_path`), `vfs` (instance VFS isolée), `client` (`fastapi.testclient.TestClient`).

**`tests/integration/test_runtime.py`** *(actuellement vide)* - à remplir de :

| # | Test | Cible réelle |
|---|---|---|
| 1 | `test_runtime_compile_and_serve_returns_html` | `nexy/compiler` → `nexy/template.py` → `nexy/modules/routers/app.py` |
| 2 | `test_runtime_unknown_route_returns_404` | `nexy/modules/routers/error_handlers.py` (couverture actuelle **0 %**) |
| 3 | `test_runtime_layout_chain_renders_nested` | `nexy/builder/__init__.py` + `routers/fbrouter/layout.py` |
| 4 | `test_runtime_markdown_page_renders_toc` | `nexy/modules/runtime/markdown.py` (39 %) |
| 5 | `test_runtime_second_request_uses_cache` | `nexy/modules/runtime/cache.py` (98 %) - non régression HIT/MISS |
| 6 | `test_runtime_hmr_message_reaches_client` | `nexy/modules/routers/hmr.py` (**0 %**) |
| 7 | `test_runtime_locale_prefix_rewrites_path` | `nexy/modules/i18n/middleware.py` (97 %) en condition réelle |
| 8 | `test_runtime_static_asset_served_from_disk` | `nexy/modules/routers/static_assets.py` (**0 %**) |

**`tests/integration/nexy/builder/test_builder.py`** *(actuellement vide)* - à remplir de :

| # | Test | Cible réelle |
|---|---|---|
| 1 | `test_builder_scan_discovers_route_files` | `nexy/builder/discovery.py` |
| 2 | `test_builder_full_build_writes_html` | `nexy/builder/__init__.py` |
| 3 | `test_builder_layout_edit_invalidates_children` | complément aux tests unitaires `test_layout_chain_cache.py` |
| 4 | `test_builder_parallel_build_is_deterministic` | contract *byte determinism* déjà instauré par `test_frontend_route_matrix.py` |
| 5 | `test_builder_missing_template_raises_compile_error` | **cas d'erreur** (P5) |

**Optionnel mais recommandé** : `tests/integration/nexy/cli/test_cli_e2e.py` - `nx build` / `nx check` sur un scaffold de `tmp_path`, via `typer.testing.CliRunner`. Couvre `cli/commands/build.py` (28 %), `check.py` (28 %), `new.py` (30 %).

**Critère d'acceptation P1** : `pytest tests/integration` exécute **≥ 13 tests** ; aucun fichier 0 octet ; le `coverage.report` des modules touchés progresse.

---

### P2 - Couverture : 54 % → 95 % *(`fail_under` relevé à chaque lot, ~4 à 6 jours)*

33 fichiers représentent **60 % du code non couvert** (1 628 / 2 716 lignes). On commence là.

#### Tier A - 10 fichiers à **0 %** (141 lignes) ⬅️ priorité 1

| Fichier | % | Statements | Test cible à créer |
|---|---|---|---|
| `nexy/modules/routers/app.py` | 0 | 57 | `tests/unit/nexy/modules/routers/test_app_server.py` |
| `nexy/modules/routers/static_assets.py` | 0 | 23 | `tests/unit/nexy/modules/routers/test_static_assets.py` |
| `nexy/modules/routers/router_resolver.py` | 0 | 19 | `tests/unit/nexy/modules/routers/test_router_resolver.py` |
| `nexy/modules/routers/error_handlers.py` | 0 | 17 | `tests/unit/nexy/modules/routers/test_error_handlers.py` |
| `nexy/modules/routers/hmr.py` | 0 | 11 | `tests/unit/nexy/modules/routers/test_hmr.py` |
| `nexy/cli/__main__.py` | 0 | 5 | `tests/unit/nexy/cli/test_main.py` |
| `nexy/app.py` | 0 | 3 | `tests/unit/nexy/test_app.py` |
| `nexy/core/types.py` | 0 | 2 | `tests/unit/nexy/core/test_types.py` |
| `nexy/router.py` | 0 | 2 | `tests/unit/nexy/test_router.py` |
| `nexy/script.py` | 0 | 2 | `tests/unit/nexy/test_script.py` |

#### Tier B - 22 fichiers **< 30 %** (1 464 lignes manquantes) ⬅️ priorité 2

| Fichier | % | Manquant | Focus principal |
|---|---|---|---|
| `nexy/video.py` | 4 | 23 | branches `Video()` |
| `nexy/audio.py` | 5 | 19 | branches `Audio()` |
| `nexy/image.py` | 9 | 10 | branches `Image()` |
| `nexy/cli/commands/migrate.py` | 9 | 108 | 3 ORM (sqlmodel/tortoise/sqlalchemy) - mocker |
| `nexy/link.py` | 10 | 9 | branches `Link()` |
| `nexy/modules/cli/init/clone.py` | 13 | 115 | clone de template + erreurs réseau |
| `nexy/cli/commands/dev.py` | 13 | 94 | supervision du processus |
| `nexy/helpers/server/uvicorn_config.py` | 14 | 92 | config uvicorn |
| `nexy/helpers/common/report.py` | 17 | 35 | rendu console |
| `nexy/cli/commands/translate.py` | 17 | 163 | batch translate - mocker `deep_translator` |
| `nexy/modules/i18n/_cli.py` | 18 | 62 | CLI i18n |
| `nexy/cli/commands/format.py` | 19 | 83 | formatage |
| `nexy/modules/i18n/i18n_decorator.py` | 19 | 17 | **+ erreur mypy `method-assign`** |
| `nexy/helpers/common/formatting.py` | 20 | 12 | |
| **`nexy/decorators.py`** | 20 | **184** | **2e plus gros trou**, 0 docstring |
| `nexy/modules/cli/init/dependencies.py` | 20 | 87 | |
| `nexy/modules/routers/fbrouter/dependencies.py` | 21 | 31 | injection |
| `nexy/cli/commands/start.py` | 22 | 25 | |
| `nexy/modules/cli/init/template_setup.py` | 25 | 126 | |
| `nexy/cli/commands/add.py` | 26 | 63 | |
| `nexy/cli/commands/check.py` | 28 | 44 | |
| `nexy/cli/commands/build.py` | 28 | 62 | couvert plus largement par P1 e2e |

> **Gains rapides micro-modules** : `nexy/video.py` + `nexy/audio.py` + `nexy/image.py` + `nexy/link.py` totalisent **61 lignes manquantes sur 4 fichiers** - à faire en premier, ce sont des composants présentationnels quasi sans dépendance. (`vite.py` ajoute 25 autres lignes, au total **86** pour 5 fichiers.)

#### Tier C - 92 fichiers **30–95 %** (1 088 lignes manquantes) ⬅️ priorité 3

Ordre : `decorators.py` (184) → `utils/server/server.py` (112) → `routers/fbrouter/__init__.py` (158) → `core/config.py` (31) → `utils/fs/path.py` / `vfs.py` → `compiler/parser/validator.py` (51 %) → `compiler/parser/sanitizer.py` (77 %) → `hooks.py` → `i18n/core.py` (57 %) → reste.

**Critère d'acceptation P2** : `fail_under` passé à **95**, cible `CONTRIBUTING.md` respectée, aucun fichier < 95 %.

---

### P3 - Les 4 quality gates au vert *(~2 jours)*

| Fichier | Ruff | Mypy | Stratégie |
|---|---|---|---|
| `nexy/core/models.py` | **38** | 5 | `N815` → décision de convention (voir §3.1) |
| `nexy/helpers/server/server.py` | 1 | **34** | annotations & `Protocol` : c'est **24 % de tout mypy** |
| `nexy/modules/cli/init/registry.py` | 13 | 0 | `W291`×3 = auto-fix ; reste = `N815` |
| `nexy/decorators.py` | 11 | **9** | `N802` sur `Controller`/`UseGuard`/… (API publique) |
| `nexy/core/config.py` | 11 | **6** | déclarer les 7 champs manquants de `Config` (`useTocDepth`, `useTocTitle`, `useTocAuto`, `useDocsUrl`, `useRedocsUrl`, `useDefaultLocale`, `useLocalesDir`) → **10 des 44 `attr-defined`** tombent (ses 6 + les 4 de `routers/app.py` qui lisent ces mêmes attributs) |
| `nexy/modules/routers/middlewares.py` | 0 | **12** | **plus gros contributeur** : annoter les types du pipeline de middlewares |
| `nexy/modules/routers/app.py` | 0 | 6 | lit `Config.useDocsUrl/useRedocsUrl/useDefaultLocale/useLocalesDir` → résolu par la ligne au-dessus ; **0 % de couverture** (Tier A) |
| `nexy/cli/commands/add.py` | 9 | 2 | `E501` + `ARG001 ui` (paramètre mort) |
| `nexy/cli/commands/translate.py` | 4 | 7 | **+ `F841 status` - valeur écrasée jamais lue = bug probable** |
| `nexy/hooks.py` | 8 | 5 | 0 docstring, 38 % de couverture |
| `nexy/__init__.py` | 4 | 0 | `N812` ×4 (ré-exports `Audio`…) → `__all__` |
| `nexy/modules/i18n/i18n_decorator.py` | 1 | 6 | **+ `method-assign`**, 19 % de couverture |
| `nexy/cli/commands/migrate.py` | 0 | 3 | `import-not-found` ×3 → ajouter types extras **ou** import local + `# type: ignore[import-not-found]` **justifié** |
| `nexy/vite.py` | 4 | 2 | |
| `nexy/modules/cli/devtools/watcher.py` | 0 | 4 | couverture 81 % |
| `nexy/modules/runtime/importer.py` | 0 | 4 | **+ `override` : signature `find_spec` incompatible avec la `supertype` `MetaPathFinder` → comportement à risque** |
| + 24 fichiers à 1–3 erreurs chacun | 3 | 24 | passage en revue unitaire |

> **Les 44 `attr-defined` sont répartis sur 11 fichiers** (middlewares 12, server 7, config 6, app 4, translate 4, decorators 3, vite 2, watcher 2, i18n.middleware 2, error_handlers 1, i18n_decorator 1) - **il n'y a donc pas une cause unique**. Le lot `Config` (10 erreurs) s'efface d'un trait, mais `middlewares.py` (12) et `server.py` (7) exigent leur propre passe d'annotations.

**Ordre recommandé dans P3** :
0. **Décider les conventions de nom (§3.1) - bloquant, avant toute modification** : `N815` + `N802` = 71 des 114 erreurs.
1. auto-fix sûrs : `ruff check nexy/ --fix` puis `ruff format nexy/` (`W291`, `SIM108`, `UP035`, `F841`).
2. `E501` (26) : reformatage manuel - **à faire avant P4**.
3. `core/config.py` : déclarer les 7 champs manquants de `Config` → **10 des 44** `attr-defined` tombent (6 dans `config.py` + 4 dans `routers/app.py`).
4. `middlewares.py` (12) puis `utils/server/server.py` (34) : extraction d'`Protocol` + annotations de types.
5. Les 3 `import-not-found` de `migrate.py` (vrais modules absents).

**Critère d'acceptation P3** : les 4 gates retournent 0 **sans aucun `noqa` ajouté** ; RUF signale zéro `noqa` mort.

#### §3.1 - Décision requise avant P3 (bloquant, 71 des 114 erreurs ruff)

`N815` (49) + `N802` (22) portent sur des noms qui ressemblent à une **API publique délibérée** (la config `nexyconfig.py` en camelCase, découpée `useFF` / `useRouter` / `useTitle`, et les décorateurs `Controller` / `UseGuard` / `UseRoute` qui imitent la surface NestJS/Angular).

Deux issues réalistes :

- **A - Conserver le contrat public** : ajouter `per-file-ignores` **déclaratifs** dans `pyproject.toml` (`"nexy/decorators.py" = ["N802"]`, `"nexy/core/config.py" = ["N815"]`). Documenté dans `CONTRIBUTING.md`, auditable en un fichier, **0 suppression inline**.
- **B - Renommer** vers `snake_case` + compat shim de dépréciation : rupture d'API pour tout utilisateur de `nexyconfig.py`.

Le choix **impacte 71 des 114 erreurs** et doit être tranché avant d'implémenter P3.

---

### P4 - Docstrings Google style sur **tout** `nexy/` *(~2 à 3 jours, après P3)*

Le périmètre est **365 API publiques** : 145 docstrings en prose à convertir, 220 à écrire.

| Priorité | Bloc | API | État |
|---|---|---|---|
| 1 | `nexy/__init__.py`, `nexy/template.py`, `nexy/hooks.py`, `nexy/decorators.py`, `nexy/errors.py`, `nexy/vite.py`, `nexy/core/*` | surface exportée | **ignorée : 0 docstring sur `decorators.py` (23), `models.py` (14), `hooks.py` (8), `core/types.py`** |
| 2 | `nexy/modules/compiler/**` | parser/generator | 20 docstrings sans section |
| 3 | `nexy/modules/routers/**` | routing | `fbrouter/validator.py`, `middlewares.py` vides |
| 4 | `nexy/modules/frontend/**` | frameworks | `vite_entry.py` : 9 docstrings, **0 Google** |
| 5 | `nexy/helpers/**` | utilitaires | `fs/path.py` 8/8 non-Google, `server/*`, `init/*` |
| 6 | `nexy/cli/**` | commandes Typer | la docstring devient l'aide `--help` |

**Format imposé** (CONTRIBUTING.md) :

```python
def compile_routes(*, source: Path, target: Path) -> list[CompiledRoute]:
    """Compile every frontend route of the project.

    Args:
        source: Directory containing route files (.tsx, .vue, .md).
        target: Output directory for the generated wrapper modules.

    Returns:
        One entry per compiled route, in deterministic order.

    Raises:
        NexyCompileError: If a route file has no default export.
    """
```

**« Tout dans du pydoc, rien d'autre » - nettoyage associé :**

| Nb | Action |
|---|---|
| 298 | commentaires `#` → déplacer l'information dans la docstring, supprimer le reste |
| 11 | suppressions → supprimer les **4** `# noqa: A002` **mortes**, justifier les **7** autres en une ligne |
| 6 lignées | code mort commenté → supprimer (`discovery.py:57-62`, `cli/__init__.py:123-124`) |
| 1 | `discovery.py:59` commentaire français → anglais |

**Vérrou anti-régression :** ajouter `tests/unit/nexy/test_docstrings_google.py` qui parcourt `nexy/**.py` en AST et échoue si une API publique n'a pas `Args:`/`Returns:`/`Raises:`. Sans ce test, la cible retombe.

**Critère d'acceptation P4** : script AST vert (365/365), 0 `#` explicatif hors pydoc, 0 commentaire FR, `ruff format` toujours vert.

---

### P5 - Zéro tolérance aux erreurs *(continu, ~1 à 2 jours +)*

| Action | État actuel | Cible |
|---|---|---|
| Un `pytest.raises` par chemin d'erreur public | **13** | ≥ 1 test d'échec par bloc qui **peut** lever |
| Fichiers de test sans aucun cas d'erreur | **38 / 46** | 0 |
| `errors.py` | 62 % | 95 % - chaque erreur métier testée + `__str__`/code |
| `raise` sans test associé | à inventorier | zéro |
| Suppressions de type | 11 | 0 ou justifiées et révisées |
| F841 `translate.py:279` | valeur ignorée | corrigé + test de non-régression |

TDD imposé par `AGENTS.md` : **test rouge → vert → refactor**, un test = une assertion.

---

## 4. Définition de « fait »

```bash
ruff check nexy/                             # 0 (114 → 0)
ruff format nexy/ --check                    # 0 (déjà vert)
python -m mypy nexy --strict                 # 0 (144 → 0)
python -m pytest tests/ -v                   # 304 → N tests, 0 échec
python -m pytest tests/ --cov=nexy --cov-fail-under=95
python -m pytest tests/integration/ -v       # 0 → ≥ 13 tests
```

- [ ] `fail_under = 95` et couverture de **branches** activée
- [ ] 0 fichier < 95 % (aujourd'hui : **87**)
- [ ] 0 fichier de test vide (aujourd'hui : **2**)
- [ ] 365/365 docstrings Google style (aujourd'hui : **0**)
- [ ] 0 `#` explicatif hors pydoc, 0 commentaires FR
- [ ] 0 suppression non justifiée (aujourd'hui : **4 mortes**, 7 non justifiées)
- [ ] CI `.github/workflows/ci.yml` verte de bout en bout (aujourd'hui : **install cassée**)
- [ ] `CONTRIBUTING.md` / `AGENTS.md` alignés sur les commandes réelles

---

## 5. Séquence

```
P0 mesure ─▶ P1 intégration ─▶ P2 couverture ─▶ P3 gates ─▶ P4 docstrings ─▶ P5 durcissement
 (0,5 j)      (1,5 j)           (4-6 j)          (2 j)        (2-3 j)          (continu)
                 │                    │              │             │
                 └──── `fail_under` relevé à chaque lot ───────────┘
```

**Décisions requises avant de commencer :**
1. **§3.1** - camelCase public conservé (`per-file-ignores`) ou renommé ? → **71 des 114 erreurs ruff**
2. Confirmer l'ordre P0 → P5
3. Confirmer la cible : 95 % de couverture **avec branches**, ou 95 % sans branches (moins coûteux)

---

## 6. Audit post-suppressions (état du dépôt)

> Mesuré après exécution des suppressions demandées. `src/`, les configs racine et `node_modules/` ont disparu de l'arbre de travail.

### 6.1 Ce qui a été supprimé (55 fichiers trackés en ` D` + hors track)

| Groupe | Détail | Décision validée |
|---|---|---|
| `src/` | 38 fichiers (app de démo) | ✅ Q1 - « supprimer src/ » |
| `scripts/` | 5 fichiers `_diag_*` / `_smoke_*` | ✅ Q2 |
| `nexyconfig.py` + `.example.py` | 2 fichiers | ✅ Q2 (« nexyconfig.py ») |
| Configs racine (8 fichiers) | `package.json`, `pnpm-lock.yaml`, `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`, `vite.config.ts`, `eslint.config.js`, `uv.lock` | ✅ Q2 (« tous les configs sauf pyproject.toml ») |
| Divers | `snapshot_frontend.py`, `public/vite.svg` | ✅ Q2 |
| Hors track | **`node_modules/`** (23 086 fichiers), `session.ai`, `__pycache__/` | ✅ Q2 |

**Restés sur place alors que la consigne « tout config racine sauf pyproject.toml » les couvre :** `cliff.toml`, `.gitignore`, `.python-version`, `.github/workflows/ci.yml`. (`tasks/` (27 fichiers) et `packages/docs/` aussi.)

### 6.2 Régression bloquante - la CI locale est rouge

```bash
python -m pytest tests/ -q
# 4 failed, 300 passed   ← baseline avant suppressions : 304 passed, 0 failed
# EXIT=1
```

Cause racine de chaque échec, tracée dans le code, **pas supposée** :

| Test | Echec | Cause racine |
|---|---|---|
| `test_vite_overlay.py::...test_hmr_script_handles_nexy_error` | `assert "nexy:error" in ''` | `nexy/vite.py:11` - `if not os.path.exists("vite.config.ts"): return ""` → la suppression de `vite.config.ts` fait que **`Vite()` renvoie `""`** (vérifié : longueur 0) |
| `test_vite_overlay.py::...test_overlay_renders_error_file_and_message` | idem | idem |
| `test_vite_overlay.py::...test_overlay_has_styled_container` | `assert 'nexy-error-overlay' in ''` | idem |
| `frontend/test_ssg_benchmark.py::test_ssg_completes_under_sanity_ceiling` | `node --import tsx …` → **ERR_MODULE_NOT_FOUND** | `package.json` + `node_modules/` supprimés → **`tsx`/`vite`/`react` ne résolvent plus** |

> Aucune de ces 4 régressions n'est un défaut du test : le test est juste, c'est l'environnement qui a bougé. Les « réparer » en assouplissant l'assertion serait exactement ce qu'il ne faut pas faire.

**Régression `mypy` : 144 → 145 erreurs** (rejoué, `exit=1`) : `nexy/core/config.py:176: Cannot find implementation or library stub for module named "nexyconfig" [import-not-found]` - conséquence directe de la suppression de `nexyconfig.py` à la racine (le runtime tolère l'absence par `try/except`, mypy non). `ruff check` : toujours **114 errors**. `ruff format --check` : vert (126 fichiers).

**Vérifications non rejouées** (entrées inchangées) : rien - `ruff`, `mypy` et `pytest` ont tous été rejoués ci-dessus.

### 6.3 Références pendantes (documentations qui pointent vers du fantôme)

| Fichier | Ligne | Contenu mort |
|---|---|---|
| `AGENTS.md` | 62 | « `nexyconfig.py` at root is the user-facing config » |
| `SECURITY.md` | 49-50 | « configure via `nexyconfig.py` » |
| `.github/ISSUE_TEMPLATE/01_bug_report.yml` | 70 | « paste your `nexyconfig.py` file » |
| `AGENTS.md` | 123 | « Top-level `src/routes/docs/` now clean » |
| `ARCHITECTURE.md` | 163-164 | « `src/routes/index.nexy` → `/`, `src/routes/blog/[slug].nexy` → `/blog/{slug}` » |
| `CONTRIBUTING.md` | *Development setup* | `uv pip install -e ".[dev]"` **et** `pnpm install --frozen-lockfile` - lock racine supprimé |
| `AGENTS.md` | *Toolchain* | gate **`tsc -b`** - `tsconfig*.json` supprimés |
| `.github/workflows/ci.yml` | 24 | `uv pip install -e ".[dev]"` (cassée **avant** suppressions, toujours cassée) |

### 6.4 Impact outillage

| Gate documentée | État |
|---|---|
| `ruff check` / `ruff format` / `mypy --strict` / `pytest` | Python : fonctionne (mais `pytest` sort en **1**) |
| `tsc -b` (AGENTS.md) | ❌ **impossible** - plus de `tsconfig*.json` |
| `pnpm install --frozen-lockfile` (CONTRIBUTING) | ❌ **impossible** en racine - plus de `package.json` ni de lock |
| `npx git-cliff -o CHANGELOG.md` | ✅ `cliff.toml` toujours présent |
| Extension VS Code (`extensions/vscode/`) | ✅ autonome (son `package.json`, son `pnpm-lock.yaml`, son `node_modules/`) |
| `packages/` | ne contient que `docs/`, sans `package.json` → inert (candidat) |

### 6.5 Décisions en attente

1. **Corriger les 4 tests cassés** - trois voies, je ne choisis pas à votre place :
   - (a) locale **minimale** : régénérer un `vite.config.ts` + `package.json`/lock au dépôt (contre la consigne « supprimés ») ;
   - (b) **isoler les tests** : commenter `test_vite_overlay` pour créer un `vite.config.ts` dans `tmp_path` (`monkeypatch.chdir`) - tests plus propres, aucun assouplissement d'assertion ;
   - (c) marquer les 4 tests en `pytest.mark.skipif` si la toolchain est absente (**le moins souhaitable, dernier recours** - cela masque la régression au lieu de la corriger).
2. ~~**`examples/` n'existe pas encore**~~ - **fait** : `examples/README.md` + `examples/FBR/web/basics/minimal/` (`nexyconfig.py`, `src/routes/{layout,index}.nexy`), constat `ROUTER_PATH = "src/routes"` (`nexy/core/config.py:38`) vérifié.
3. ~~**Code mort + commentaires `#` dans `nexy/`**~~ - **fait** : 312 commentaires `#` hors docstring supprimés (53 fichiers), 7 conservés (6 `noqa` vivants + 1 `type: ignore`), 4 `noqa: A002` morts retirés, 2 `F841` de `translate.py` corrigés (`:227` et `:278`, le second masquant le premier), blocs de code mort `discovery.py`/`cli/__init__.py` supprimés, espaces de fin de ligne nettoyés (3 × `W291`). **ruff : 114 → 109**.
4. `cliff.toml` / `.gitignore` / `.python-version` / `.github/` : les garder ou les supprimer aussi ?

---

### 6.6 État des gates après nettoyage (session du 2026-10-18)

| Gate | Avant nettoyage | Après | Exit |
|---|---|---|---|
| `ruff check nexy/` | 114 | **109** (restants : N815/N802/E501/B008/SIM - planifiés P0-P3) | 1 |
| `ruff format nexy/ --check` | vert | **vert** (126 fichiers) | 0 |
| `mypy nexy --strict` | 144 (+1 après suppressions = 145) | **144** - retour au baseline : override `[[tool.mypy.overrides]] module = "nexyconfig"` dans `pyproject.toml`, l'import `config.py:172` étant volontairement optionnel (`try/except ModuleNotFoundError`) | 1 |
| `pytest tests/` | 4 failed / 300 passed | **inchangé : 4 failed / 300 passed** - les 4 mêmes tests (cf. §6.5.1, en attente de votre arbitrage) | 1 |

Aucune suppression de lint n'a été ajoutée pour faire passer un gate ; les 2 `F841` ont été corrigés en variable réellement valide, pas en noqa.

---

### 6.7 État des gates - session du 2026-10-21 (P3 terminé)

Les 4 quality gates retournent **0**. Aucun `noqa`, `type: ignore` ou `per-file-ignores` ajouté pour y parvenir dans cette session.

| Gate | §6.6 (2026-10-18) | Mesuré le 2026-10-21 | Exit |
|---|---|---|---|
| `ruff check nexy/` | 109 | **0** - «All checks passed!» | 0 |
| `ruff format nexy/ --check` | vert | **0** - 126 fichiers déjà formatés | 0 |
| `mypy nexy --strict` | 144 | **0** - «Success: no issues found in 126 source files» | 0 |
| `pytest tests/` | 4 failed / 300 passed | **378 passed, 1 skipped** (10,6 s), 0 échec | 0 |
| `pytest --cov=nexy` (`fail_under`) | 52,79 % (échec temporaire, seuil 52,8) | **54,15 % ≥ 54** | 0 |

#### Ce qui a été fait dans cette session

**1. `mypy --strict` : 144 → 0.**

Dès la première mesure, les 29 dernières erreurs projectives étaient **toutes dans un seul fichier**, `nexy/helpers/server/server.py` ; les 125 autres fichiers étaient déjà verts. Corrections, sans aucune suppression :

| Erreur mypy | Nb | Correction |
|---|---|---|
| `attr-defined` sur `_ProactorBasePipeTransport._call_connection_lost` et `_patch_win_asyncio._applied` | 4 | flag d'application promu en variable de module `_WIN_ASYNCIO_PATCHED` (au lieu d'un attribut de fonction) ; l'objet transport est saisi via une annotation `transport_cls: Any`, pas via `getattr`/`setattr` (interdits par `B009`/`B010`) |
| `no-untyped-def` sur `_safe_call_connection_lost` | 1 | annotations `self: Any, exc: BaseException \| None = None` + retour `-> None` |
| `no-any-return` sur `s.getsockname()[0]` | 1 | enveloppé dans `str(...)` |
| `type-arg` sur `proc: Popen \| None` | 1 | `Popen[Any] \| None` |
| `arg-type` : `host=host` passé à `uvicorn.run` alors que `host: str \| None` | 1 | **bug réel corrigé** : passage de `run_host` (`host or "127.0.0.1"`) - avant, un `host=None` partait vers uvicorn |
| `arg-type` ×19 sur `**ssl_args` / `**workers_kwargs` dépliés dans `uvicorn.run` | 19 | dicts typés `dict[str, Any]` explicites |
| `return-value` : `return True` hors signature `Popen[Any] \| None` | 1 | signature élargie en `Popen[Any] \| bool \| None` + docstring *Returns* décrivant les 3 cas |

**2. `pyproject.toml` : option mypy invalide supprimée.**

`ignore_untyped_imports = true` dans l'override `deep_translator.*` fait remonter *«Unrecognized option»* - option **non reconnue par mypy**. Elle n'était d'aucune utilité : `ignore_missing_imports = true` suffit à gérer le fait que `deep-translator` n'exporte pas de `py.typed`. Supprimée ; l'override reste en place.

**3. `ruff format` : `cli/commands/add.py` reformatté** (ligne blanche surnuméraire, le seul fichier à sortir du format).

**4. Couverture : `fail_under` 52,8 → 54.**

`nexy/helpers/server/server.py` était à **24 %** ; les 29 lignes ajoutées par le travail de typage l'ont fait retomber à 52,79 %, sous le seuil. Plutôt que de baisser le seuil, `tests/unit/nexy/helpers/test_server.py` a été créé : **18 tests, 1 assertion chacun, tous verts**, portant le module à **67 %** et la couverture globale à **54,15 %**.

Cas couverts : écriture de port, marqueur `nexy.prod` (création **et** suppression), IP réseau, `get_ssl_config` (complet / certfile manquant), `stop_process` (None / process fini / enfant vivant), `_detect_pm`, les 3 sorties de `wait_for_vite_ready` (succès immédiat, échec jusqu'au timeout, `ssl=True` → `https://`), les 3 sorties de `uvicorn()` (`as_process` → `Popen`, premier plan → `True`, exception → `None`), propagation de `workers`, et `resolve_ports(with_client=False)` → `0`.

> Le garde de schéma CAT III de `wait_for_vite_ready` a été **déplacé hors de la boucle** : placé dans le `try`, il était avalé par son propre `except Exception` et ne pouvait jamais se propager. Levé avant la boucle, il échoue effectivement.

**5. Deux commentaires/Docstrings français → anglais** (`stop_process`, `wait_for_vite_ready`), conformément à « All code in English ».

#### Restant ouvert (hors périmètre de cette session)

| Point | État |
|---|---|
| `ruff check tests/` | **57 erreurs préexistantes** dans `tests/` (F401, I001, ARG002…). Le gate documenté ne couvre que `nexy/` ; le nouveau `test_server.py` est propre (0 erreur). |
| `pytest tests/integration/` | **13 passed** - critère P1 « ≥ 13 tests » atteint |
| Docstrings Google style (P4) | non commencé - `test_docstrings_google.py` existe déjà comme verrou |
| Bandit | `bandit -r nexy/ -c .bandit` sort en 1 : LOW ×22 + le MEDIUM B310 du probe `urlopen` documenté comme risque accepté dans `SECURITY.md` |
| Artefacts de session non trackés | `server_orig.py`, `bandit*.json`, `bf*.json`, `ai` - à supprimer avant commit |

---

*Généré par audit automatisé le 2026-10-18, complété par l'audit post-suppressions (§6) et le nettoyage code mort/commentaires (§6.5-2, §6.5-3, §6.6). Toutes les commandes de la §0 reproductibles depuis la racine du dépôt.*