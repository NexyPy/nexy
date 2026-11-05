# CLI

Le binaire est `nx` (également installé sous le nom `nexy`). `uvx nexy new` crée un projet (`uvx` est livré avec uv). Exécutez toutes les autres commandes dans l'environnement virtuel du projet, ou via `uv run`, par exemple `uv run nexy dev` : c'est là que se trouvent vos propres packages.

## Commandes

| Commande | Alias | Ce qu'il fait |
|---|---|---|
| `nx dev` | `nx d` | serveur de développement : compilation lors du changement, Vite, HMR |
| `nx start` | `nx s` | serveur de production sur la sortie compilée |
| `nx build` | `nx b` | version de production |
| `nx new` | `nx n` | échafauder un projet |
| `nx init` | `nx i` | ajouter Nexy à un projet existant |
| `nx add` | - | ajouter un composant d'interface utilisateur du registre ou une URL à `src/components/ui` |
| `nx migrate` | `nx m` | créer ou appliquer des migrations de bases de données avec Alembic ou Aerich |
| `nx check` | `nx c` | vérification du type : mypy sur Python, `tsc` sur TypeScript |
| `nx format` | `nx f` | format Python (ruff), JS/TS (plus joli), `.nexy` fichiers |
| `nx test` | - | exécuter pytest ; `--client` ajoute vitest |
| `nx skills` | - | ajouter ou rafraîchir les compétences, `AGENTS.md` et `CLAUDE.md` pour les agents de codage |

## Drapeaux

| Commande | Indicateur | Par défaut |
|---|---|---|
| `dev`, `start` | `--port` | `usePort`, `3000` |
| `dev`, `start` | `--host` | `useHost`, `0.0.0.0` |
| `build` | `--check` | off - exécute ruff et mypy après la construction |
| `format` | `--check` | désactivé - rapport au lieu de réécrire |
| `test` | `--client` | désactivé - exécutez également Vitest au lieu de pytest seul |
| `test` | `--no-server` | activé - ignorer pytest lorsque vous souhaitez uniquement des tests clients |
| `new` | `--template`, `-t` | aucun - cloner un modèle enregistré sans invite |
| `new` | `--no-agents` | agents activés - ignorer `AGENTS.md` et les compétences d'agent |
| `add` | `--ui`, `--url` | désactivé - force un nom de registre ou une URL lorsqu'il est ambigu |
| `add` | `--all`, `-a` | désactivé - ajoute chaque composant du registre |
| `add` | `--sha256` | aucun - résumé attendu d'un composant distant ; un décalage annule |
| `migrate` | `--init` | désactivé - écriture de la configuration Alembic ou Aerich |
| `migrate` | `--upgrade`, `-u` | off - appliquer les migrations au lieu d'en écrire une nouvelle |
| `migrate` | `--message`, `-m` | vide - nom de la nouvelle révision |

## Sortie

Les étapes longues (installation des packages, compilation, regroupement) affichent une icône avec le temps écoulé, puis laissent une ligne derrière : `✔ uv sync .venv  1.4s`. Un groupe d'étapes (les installations de `nx new`) affiche une barre de progression avec le nombre d'étapes terminées, `━━━━────  2/5` ; une seule étape (`nx add`) affiche une barre qui clignote pendant son exécution. Les journaux de développement lisent `GET » /about 200 in 12ms` pour les requêtes et `vite » ...` pour Vite. Une étape qui échoue imprime les dernières lignes du résultat de la commande au lieu de le masquer. Les terminaux qui ne peuvent pas restituer Unicode obtiennent `+` et `x`.

## Erreurs lors de l'exécution de `nx dev`

L'enregistrement d'un fichier cassé n'arrête jamais le serveur. Un fichier `.py` avec une erreur de syntaxe est signalé avec son fichier et sa ligne, et le serveur continue de servir la dernière version fonctionnelle jusqu'à ce que vous la corrigiez :

```text
  nexy » error  src/routes/users.py:3
  SyntaxError: invalid syntax

    1 | import json
    2 |
  > 3 | def GET(:
                ^
    4 |     x = 1
    5 |     return {"v": 2}

  Fix it and save: the server keeps its last working version.
```

Un fichier qui analyse mais échoue au chargement de l'application (une importation manquante, une erreur au niveau du module) est signalé de la même manière et `nx dev` attend votre prochaine sauvegarde ; rien n'est servi jusqu'à ce que l'application se charge à nouveau. Une sauvegarde valide lit `nexy » update <file>` pendant le rechargement du serveur. Les fichiers Markdown en dehors de `src/routes`, tels que `README.md`, ne sont pas des pages et ne déclenchent rien. `nx start` est plus strict : il se termine avec le code 1 et ne démarre rien si un fichier de route ne peut pas se charger.

## Questions de `nx new`

`nx new` demande, dans cet ordre : le routeur basé sur les fichiers, le type de projet (web ou API), le routage côté client, le framework client, comment styliser l'application, l'alias d'importation, l'ORM, la base de données et l'URL de la base de données. Chaque option a une brève description et celle actuelle est mise en surbrillance. Les questions qui ne s'appliquent pas sont ignorées (un projet API n'a ni cadre ni style ; en choisissant **Aucune base de données** car l'ORM ignore la base de données et l'URL). Déplacez-vous avec les touches fléchées (ou `j`/`k`, ou un chiffre), confirmez avec `enter`, revenez à la question précédente avec `←` ou `esc`, quittez avec `ctrl+c`.

| Question | Choix |
|---|---|
| Alias d'importation | `@` (`@/components/...` pointe vers `src/`), ou un autre préfixe tel que `~` ou `#app` |
| Style | Tailwind CSS, UnoCSS, Vanilla CSS, Autre (pas d'outil CSS, même feuille de style simple que Vanilla) |
| ORM | SQLModel, SQLAlchemy, Tortue-ORM, Aucune base de données |
| Base de données (avec un ORM) | SQLite, PostgreSQL, Neon, MySQL / MariaDB, Autre (vous tapez l'URL) |

Le pilote de base de données de l'ORM choisi est installé avec celui-ci (`psycopg`, `pymysql`, `asyncpg` ou `aiomysql`), et l'URL est écrite dans `.env`.

Avant d'installer les packages, `nx new` vérifie la connexion. Sans cela, il ignore les installations et vous demande d'exécuter `uv sync` et l'installation de votre gestionnaire de packages plus tard. Avec un, il imprime la latence et la vitesse de téléchargement, et avertit lorsque la connexion est lente (plus de 400 ms ou moins de 100 Ko/s). Chaque ligne d'installation nomme l'outil et le dossier qu'il remplit, par exemple `pnpm install node_modules` ou `uv sync .venv`.

## Ce que `dev`, `build` et `start` créent

Avant de s'exécuter, les trois commandes créent un `__init__.py` vide dans `src/` et dans chaque dossier situé en dessous contenant un fichier `.py` ou `.nexy`, donc une route telle que `src/routes/users.py` est importée de la même manière dans chacun d'eux. Les fichiers existants ne sont jamais modifiés et `nx dev` fait de même lorsque vous ajoutez un dossier. Le bytecode Python va à `__nexy__/__pycache__`, donc aucun dossier `__pycache__` n'apparaît à côté de vos sources.

## Langue

La ligne de commande parle anglais, chinois, hindi, espagnol, portugais, français, allemand, japonais, russe, coréen, indonésien et arabe. Il utilise le premier d’entre eux qu’il prend en charge :

1. la variable d'environnement `NEXY_LANG` (`NEXY_LANG=ja nx dev`) ;
2. les variables locales de votre shell (`LC_ALL`, `LC_MESSAGES`, `LANG`, puis `LANGUAGE`) ;
3. la langue de votre système d'exploitation.

Tout le reste est en anglais, tout comme tout message qu'une langue n'a pas encore. Seul ce que `nx` imprime est traduit : les erreurs du compilateur, les traces et les résultats des outils qu'il exécute restent tels quels. Les traductions n'ont pas encore été révisées par des locuteurs natifs : les corrections sont les bienvenues sous forme de pull request à `nexy/modules/i18n/<language>.json`.

## Construire un comportement

`nx build` compile les routes, puis regroupe le client lorsque `useVite` est activé.

> [!REMARQUE]
> il n'y a pas de drapeau `--static`. L'hébergement statique est un choix de déploiement, pas un mode de construction - voir [Deploy](../deployment/README.md).

## Travailler sur Nexy lui-même

À l'intérieur de ce référentiel, les portes sont :

```bash
python scripts/verify.py             # lint, format, typecheck, tests
python scripts/audit_dependencies.py # supply-chain audit against the lock
```

## Prochaines étapes

- [Mise en route](../getting-started/quick-start.md) : premier projet
- [Tests](../guides/testing.md) : ce que `nx test` exécute
- [Déployer](../deployment/README.md) : `build` et `start` en production
