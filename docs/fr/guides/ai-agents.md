# Agents de codage

Un projet réalisé avec `nx new` comporte les règles dont un agent de codage a besoin pour écrire du code Nexy à votre manière : l'ordre de travail, les règles de code et d'écriture, et une compétence par sujet. Cette page indique ce que vous obtenez, où cela va et comment le maintenir à jour. Travailler sur Nexy lui-même est un travail différent : lire la racine du référentiel `AGENTS.md`.

## Ce que `nx new` ajoute

| Fichier | Lu par | Contient |
|---|---|---|
| `AGENTS.md` | Codex, OpenCode | la pile du projet, l'ordre des travaux, les règles, la liste des compétences |
| `CLAUDE.md` | Claude Code | une ligne, `@AGENTS.md`, donc les deux lisent le même texte |
| `.agents/skills/` | Codex, OpenCode | les compétences |
| `.claude/skills/` | Claude Code, OpenCode | les mêmes compétences |

`AGENTS.md` est court et adapté. Un projet Vue acheminé par le client indique « acheminé par le client, Vue, stylisé avec Tailwind » ; un projet API est informé qu'il n'y a pas de vues. Seules les compétences qui correspondent sont copiées : un projet React obtient `nexy-react` et aucune compétence Vue, un projet serveur obtient les compétences `.nexy` et Markdown, un projet API n'obtient aucune compétence sur les vues.

Pour tout ignorer, créez le projet avec `nx new --no-agents`.

## Les compétences

| Compétence | Couvre |
|---|---|
| `nexy-principles` | ordre de travail, règles de code, règles d'écriture |
| `nexy-ux-audit` | l'audit d'expérience et d'architecture d'information à exécuter avant toute vue |
| `nexy-project` | modes, dossiers, conventions de fichiers, configuration, commandes |
| `nexy-file` | `.nexy` pages, accessoires, crochets, îles |
| `nexy-markdown` | `.md` et `.mdx` contenu |
| `nexy-react`, `nexy-preact`, `nexy-solid`, `nexy-vue`, `nexy-svelte` | code idiomatique pour le framework client |
| `nexy-styling` | Tailwind, UnoCSS ou CSS simple, et les jetons de conception |
| `nexy-backend` | Gestionnaires d'API, actions, WebSocket, ISR, middleware |
| `nexy-modular` | contrôleurs, modules, injection et gardes du routeur modulaire |
| `nexy-security` | dépendances, entrées, sessions, autorisations, secrets |
| `nexy-testing` | la boucle de test en premier et les portes |
| `nexy-framework-dev` | changer Nexy lui-même, plutôt qu'un projet construit avec Nexy |

Les règles qu'ils appliquent : auditer l'expérience avant de créer une vue, écrire d'abord le test qui a échoué, une fonction effectue un traitement, une classe porte une intention, un dossier contient un ensemble d'intentions associées, pas d'emoji, de véritables icônes SVG, du texte brut écrit pour les personnes et aucun script DOM écrit à la main dans React, Vue, Svelte, Solid ou Preact.

## Ajoutez-les à un projet existant

```bash
nx skills
```

Exécutez-le à la racine du projet. Il lit `nexyconfig.py` et `package.json` pour trouver la pile, copie les compétences correspondantes et écrit `AGENTS.md` et `CLAUDE.md` lorsqu'elles sont manquantes.

Il n'écrase jamais un fichier que vous avez écrit : un `AGENTS.md` ou un `CLAUDE.md` existant est conservé, et la commande vous l'indique. Ajoutez manuellement la liste de compétences à votre propre fichier si vous le souhaitez. Une compétence qui vous est propre dans `.claude/skills/` ou `.agents/skills/` est laissée seule ; seules les compétences `nexy-*` sont rafraîchies.

Exécutez à nouveau `nx skills` après avoir mis à niveau Nexy pour actualiser les copies et validez le résultat afin que toute l'équipe le partage.

## Comment un agent les trouve

- `AGENTS.md` (ou `CLAUDE.md`, qui l'importe) est lu au début de chaque session. Il nomme les compétences.
- Chaque compétence commence par un nom et une description indiquant ce qu'elle couvre et quand la charger. L'agent les lit en premier et ouvre une compétence uniquement lorsque la tâche correspond.

Les compétences suivent le [format Compétences d'agent](https://agentskills.io/specification) ouvert, de sorte que les autres agents qui lisent les dossiers `SKILL.md` peuvent également les utiliser.

## Ce qu'ils ne font pas

Les compétences indiquent à un agent comment travailler ; ils ne rendent pas sa sortie correcte. Conservez vos propres chèques :

- Lisez ce que l'agent a changé.
- Exécutez `nx check`, `nx test` et `nx build`. Les compétences demandent cela et que les résultats soient rapportés et non résumés.
- Auditez les dépendances ajoutées par l'agent (`nexy-security` explique comment).

Les exemples dans les compétences sont vérifiés par les propres tests de Nexy : les importations existent, les champs de configuration existent, les commandes existent, les Python analyses. Cela reflète une dérive, pas une erreur de jugement.

## Carte

Un agent répond plus rapidement lorsqu’il sait quelle page contient la réponse.

| Vous avez besoin de | Lire |
|---|---|
| le produit, sur une seule page | [README](../README.md) |
| exécuter un projet | [démarrage](../getting-started/quick-start.md) |
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
| la build du client | [frontend](frontend.md) |

## Invariants du projet

1. `__nexy__/` est généré. Ne le modifiez jamais, ne le validez jamais. Supprimez-le pour forcer une nouvelle version.
2. Un fichier par URL. `index.nexy` et `index.py` pour le même chemin est un bug, pas une règle de priorité.
3. Noms réservés à l'intérieur de `src/routes/` : `layout.nexy`, `loading.nexy`, `errors.nexy`, `notfound.nexy`, `dependencies.py`, `__init__.py`. Ne les utilisez pas pour le contenu.
4. `.nexy` le sujet principal est Python qui s'exécute par requête. Aucun effet secondaire au niveau du module : aucun descripteur de fichier, aucune connexion à une base de données, aucun appel réseau lors de l'importation.
5. `.py` dans `src/routes/` est un gestionnaire d'API. Les méthodes sont des noms de fonctions (`GET`, `POST`, ...).
6. La configuration réside dans `nexyconfig.py`, pas dans des variables d'environnement ni dans des constantes dispersées.
7. L'échappement automatique est désactivé dans les modèles `.nexy` : échappez aux valeurs non fiables avec `| e`.

```bash
nx dev      # development
nx build    # production build
nx start    # production server
nx test     # pytest, --client adds vitest
```

Lorsque la documentation et le code ne sont pas d'accord, faites confiance au code et dites-le : `nexy/core/config.py` contient toutes les options, `nexy/modules/routers/fbrouter/` les règles de routage, `nexy/modules/compiler/` comment `.nexy` les fichiers deviennent des modules.

## Prochaines étapes

- [CLI](../reference/cli.md) : `nx new` et `nx skills`
- [Conventions de fichiers](../reference/file-conventions.md) : noms réservés et règles de routage
- [Glossaire](../reference/glossary.md) : les mots sur lesquels s'appuient ces règles
- [Sécurité](../reference/security.md) : la version planchers sur laquelle pointe la compétence de sécurité
