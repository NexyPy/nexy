# Agents de codage

Un projet réalisé avec `nx new` comporte les règles dont un agent de codage a besoin pour écrire du code Nexy à votre manière :
l'ordre des travaux, les règles de code et d'écriture, et une compétence par sujet. Cette page dit ce que vous obtenez,
où il va et comment le tenir à jour. Travailler sur Nexy en lui-même est un travail différent : lisez le
racine du référentiel `AGENTS.md`.

## Ce que `nx new` ajoute

| Fichier | Lu par | Contient |
|---|---|---|
| `AGENTS.md` | Codex, OpenCode | la stack du projet, l'ordre de travail, les règles, la liste des compétences |
| `CLAUDE.md` | Claude Code | une ligne, `@AGENTS.md`, donc tous les deux lisent le même texte |
| `.agents/skills/` | Codex, OpenCode | les compétences |
| `.claude/skills/` | Claude Code, OpenCode | les mêmes compétences |

`AGENTS.md` est court et adapté. Un projet Vue acheminé par le client indique « routé par le client, Vue, style
avec vent arrière" ; un projet API est informé qu'il n'y a pas de vues. Seules les compétences qui correspondent sont copiées : a
Le projet React obtient `nexy-react` et aucune compétence Vue, un projet serveur obtient le `.nexy` et Markdown
compétences, un projet API n'obtient aucune compétence sur les vues.

Pour tout ignorer, créez le projet avec `nx new --no-agents`.

## Les compétences

| Compétence | Couvre |
|---|---|
| `nexy-principles` | ordre de travail, règles de code, règles d'écriture |
| `nexy-ux-audit` | l'audit d'expérience et d'architecture de l'information à exécuter avant toute vue |
| `nexy-project` | modes, dossiers, conventions de fichiers, configuration, commandes |
| `nexy-file` | `.nexy` pages, accessoires, crochets, îlots |
| `nexy-markdown` | `.md` et `.mdx` contenu |
| `nexy-react`, `nexy-preact`, `nexy-solid`, `nexy-vue`, `nexy-svelte` | code idiomatique pour le framework client |
| `nexy-styling` | Tailwind, UnoCSS ou CSS simple, et les jetons de conception |
| `nexy-backend` | Gestionnaires d'API, actions, WebSocket, ISR, middleware |
| `nexy-modular` | contrôleurs, modules, injection et gardes du routeur modulaire |
| `nexy-security` | dépendances, entrées, sessions, autorisations, secrets |
| `nexy-testing` | la première boucle de test et les portes |
| `nexy-framework-dev` | changer Nexy lui-même, plutôt qu'un projet construit avec Nexy |

Les règles qu'ils appliquent : auditer l'expérience avant de créer une vue, écrire d'abord le test qui a échoué,
une fonction effectue un traitement, une classe porte une intention, un dossier contient un ensemble de
intentions associées, pas d'emoji, de vraies icônes SVG, du texte brut écrit pour les personnes et pas d'écriture manuscrite
Scripts DOM dans React, Vue, Svelte, Solid ou Preact.

## Ajoutez-les à un projet existant

```bash
nx skills
```

Exécutez-le à la racine du projet. Il lit `nexyconfig.py` et `package.json` pour trouver la pile,
copie les compétences correspondantes et écrit `AGENTS.md` et `CLAUDE.md` lorsqu'elles sont manquantes.

Il n'écrase jamais un fichier que vous avez écrit : un `AGENTS.md` ou un `CLAUDE.md` existant est conservé et le
la commande vous le dit. Ajoutez manuellement la liste de compétences à votre propre fichier si vous le souhaitez. Une compétence de
le vôtre dans `.claude/skills/` ou `.agents/skills/` est laissé seul ; seules les compétences `nexy-*` sont
rafraîchi.

Exécutez à nouveau `nx skills` après avoir mis à niveau Nexy pour actualiser les copies et validez le résultat afin que le
toute l’équipe le partage.

## Comment un agent les trouve

- `AGENTS.md` (ou `CLAUDE.md`, qui l'importe) est lu au début de chaque session. Il nomme
  les compétences.
- Chaque compétence commence par un nom et une description indiquant ce qu'elle couvre et quand la charger. Le
  l'agent les lit en premier et ouvre une compétence uniquement lorsque la tâche correspond.

Les compétences suivent le [format Compétences d'agent](https://agentskills.io/specification) ouvert, donc les autres
les agents qui lisent les dossiers `SKILL.md` peuvent également les utiliser.

## Ce qu'ils ne font pas

Les compétences indiquent à un agent comment travailler ; ils ne rendent pas sa sortie correcte. Conservez vos propres chèques :

- Lisez ce que l'agent a modifié.
- Exécutez `nx check`, `nx test` et `nx build`. Les compétences le demandent et le résultat doit être
  rapporté, non résumé.
- Audit les dépendances ajoutées par l'agent (`nexy-security` explique comment).

Les exemples dans les compétences sont vérifiés par les tests propres à Nexy : les importations existent, la configuration
les champs existent, les commandes existent, le Python analyse. Cela reflète une dérive, pas une erreur de jugement.

## Carte

Un agent répond plus rapidement lorsqu’il sait quelle page contient la réponse.

| Vous avez besoin de | Lire |
|---|---|
| le produit, sur une seule page | [README](../README.md) |
| pour exécuter un projet | [démarrage](../getting-started/quick-start.md) |
| l'URL d'un fichier | [routage](../routing/README.md) |
| segments dynamiques, mises en page, pages d'erreur | [pages](../routing/fbr/pages/README.md) |
| le chemin actuel, la requête, les cookies, la session | [hooks](../routing/fbr/navigation/hooks.md) |
| pour éditer une page | [fichiers .nexy](../views/nexy/README.md) ou [views](../views/README.md) |
| Markdown ou MDX | [markdown](../views/nexy/markdown.md) |
| assistants HTML intégrés | [composants](../views/nexy/components.md) |
| mode de rendu | [SSR](../rendering/ssr.md), [CSR](../rendering/csr.md), [ISR](../rendering/isr.md) |
| un WebSocket | [websocket](../routing/fbr/realtime/websocket.md) |
| contrôleurs et modules | [modulaire](../routing/modular/README.md) |
| pour ajouter un point de terminaison | [API](../routing/fbr/handlers/README.md) |
| un formulaire posté à partir d'une page | [actions](actions.md) |
| pourquoi une requête a échoué et quelle page y répond | [exceptions](../reference/exceptions.md) |
| traductions | [i18n](i18n.md) |
| un champ de configuration | [config](../reference/config.md) |
| pour tester l'application | [testing](testing.md) |
| la version client | [frontend](frontend.md) |

## Invariants du projet

1. `__nexy__/` est généré. Ne le modifiez jamais, ne le validez jamais. Supprimez-le pour forcer une nouvelle version.
2. Un fichier par URL. `index.nexy` et `index.py` pour le même chemin est un bug, pas une règle de priorité.
3. Noms réservés à l'intérieur de `src/routes/` : `layout.nexy`, `loading.nexy`, `errors.nexy`,
   `notfound.nexy`, `dependencies.py`, `__init__.py`. Ne les utilisez pas pour le contenu.
4. `.nexy` le sujet principal est Python qui s'exécute par requête. Aucun effet secondaire au niveau du module : pas de fichier
   handles, pas de connexions à la base de données, pas d’appels réseau lors de l’importation.
5. `.py` dans `src/routes/` est un gestionnaire d'API. Les méthodes sont des noms de fonctions (`GET`, `POST`, ...).
6. La configuration réside dans `nexyconfig.py`, pas dans des variables d'environnement ni dans des fichiers dispersés
   constantes.
7. L'échappement automatique est désactivé dans les modèles `.nexy` : échappez aux valeurs non fiables avec `| e`.

```bash
nx dev      # development
nx build    # production build
nx start    # production server
nx test     # pytest, --client adds vitest
```

Lorsque la documentation et le code ne sont pas d'accord, faites confiance au code et dites-le : `nexy/core/config.py` détient chaque
option, `nexy/modules/routers/fbrouter/` les règles de routage, `nexy/modules/compiler/` comment `.nexy`
les fichiers deviennent des modules.

## Étapes suivantes

- [CLI](../reference/cli.md) : `nx new` et `nx skills`
- [Conventions sur les fichiers](../reference/file-conventions.md) : noms réservés et règles de routage
- [Glossaire](../reference/glossary.md) : les mots sur lesquels s'appuient ces règles
- [Sécurité](../reference/security.md) : la version indique la compétence de sécurité vers laquelle pointe