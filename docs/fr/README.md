# Documentation Nexy

**Un framework Python pour les applications Web fullstack.**

Nexy place vos pages et votre API dans un seul projet Python, servi par un seul serveur. La version 2.2 est construite sur FastAPI : chaque route API est une route FastAPI, répertoriée dans un schéma OpenAPI que Scalar affiche dans `/docs`.

- **Python en premier.** Les pages, les points de terminaison, les formulaires et les actions sont Python, et une page n'a pas besoin de JavaScript.
- **Un frontend quand vous en voulez un.** React, Vue, Svelte, Solid ou Preact, pour un composant ou pour l'ensemble du site.
- **Un fichier, une URL.** Un fichier sous `src/routes/` est une route : `.nexy` est une page, `.py` est un point de terminaison d'API.
- **De la place pour grandir.** Commencez avec un seul fichier ; déplacez-vous vers des modules ou branchez un routeur FastAPI existant, lorsque le projet se développe.

Nouveau ici ? Lisez [Qu'est-ce que Nexy ?](getting-started/what-is-nexy.md), puis le [Démarrage rapide](getting-started/quick-start.md).

## Commencer

### Premiers pas
| Pages | Ce que tu feras |
|---|---|
| [Qu'est-ce que Nexy ?](getting-started/what-is-nexy.md) | Sachez ce qu'est Nexy, sur quoi il est construit et ce que vous obtenez |
| [Installation](getting-started/installation.md) | Installez uv et la CLI Nexy, puis créez votre premier projet |
| [Démarrage rapide](getting-started/quick-start.md) | Créez un projet, exécutez-le avec Live Reload et construisez-le pour la production |
| [Tutoriel](getting-started/tutorial.md) | Créez une page de notes avec un point de terminaison, des données partagées et une version de production en 10 minutes |

### Comprendre le modèle
| Pages | Ce que tu feras |
|---|---|
| [Concepts de base](getting-started/core-concepts.md) | Obtenez le modèle mental : route, page, vue, composant, gestionnaire, point de terminaison |
| [Structure du projet](getting-started/project-structure.md) | Savoir à quoi servent chaque dossier et fichier d'un projet |
| [Choisissez un routeur](routing/README.md) | Choisissez le routeur basé sur des fichiers, modulaire ou personnalisé |
| [Choisissez un format d'affichage](views/README.md) | Choisissez `.nexy`, Markdown ou un framework client pour une page |

## Routage

### Basé sur un fichier {fbr}
| Pages | Ce que tu feras |
|---|---|
| [Routage basé sur des fichiers](routing/fbr/README.md) | Transformer un chemin de fichier en URL |
| [Pages](routing/fbr/pages/README.md) | Écrire une page |
| [Itinéraires dynamiques](routing/fbr/pages/dynamic-routes.md) | Utiliser `[slug]`, `[...path]` et les groupes de routes |
| [Métadonnées de la page](routing/fbr/pages/metadata.md) | Définir le titre, la description et partager l'image d'une page {new} |
| [Mises en page](routing/fbr/layouts/README.md) | Partager un cadre entre les pages |
| [Héritage](routing/fbr/inheritance.md) | Lire l'ordre de résolution des mises en page, des dépendances et des pages d'erreur |
| [Mode serveur et mode client](routing/fbr/modes.md) | `useCSR`, et ce que chaque mode permet |
| [Liens et navigation](routing/fbr/navigation/linking-and-navigating.md) | Lier des pages, naviguer sur le client, pré-extraire |
| [Crochets](routing/fbr/navigation/hooks.md) | Lire le chemin, la requête, les cookies et la session |

### Gestionnaires et erreurs {fbr}
| Pages | Ce que tu feras |
|---|---|
| [Gestionnaires de routes](routing/fbr/handlers/README.md) | Ajouter un point de terminaison Python |
| [Validation et erreurs](routing/fbr/handlers/validation-and-errors.md) | Répondez à `422` et `404` et lancez un `HTTPException` |
| [WebSocket gestionnaires](routing/fbr/realtime/websocket.md) | Gérer une connexion `SOCKET` |
| [Dépendances et gardiens](routing/fbr/dependencies/README.md) | Exécutez `dependencies.py` avant un gestionnaire et héritez-en |
| [Fichiers middleware](routing/fbr/middleware/README.md) | Envelopper les requêtes avec `middleware.py`, hérité par répertoire |
| [Pages d'erreur](routing/fbr/errors/README.md) | Répondez avec les erreurs `notfound.nexy`, `errors.nexy` et JSON |
| [Pages d'erreur par dossier](routing/fbr/errors/folder-pages.md) | Cas limite : erreurs provenant des sous-dossiers |

### Routeur modulaire {modular}
Contrôleurs et modules.
| Pages | Ce que tu feras |
|---|---|
| [Routage modulaire](routing/modular/README.md) | Monter des contrôleurs et des modules |
| [Injection de dépendances](routing/modular/dependency-injection.md) | Définir les services, leurs portées et le conteneur |
| [Gardes et métadonnées](routing/modular/guards-and-metadata.md) | Protéger et documenter les itinéraires |
| [Routeur modulaire vs NestJS](routing/modular/vs-nestjs.md) | Comparaison avec NestJS |

### Intégration de routeur personnalisé {custom}
| Pages | Ce que tu feras |
|---|---|
| [Routage personnalisé](routing/custom/README.md) | Inclure une application FastAPI existante |

## Front-end

### Contrats partagés
| Pages | Ce qu'il définit |
|---|---|
| [Actions et navigation](views/frontend/actions-and-navigation.md) | Appeler une action tapée, lier des pages, lire l'URL |

### Vues Nexy
| Pages | Ce que tu feras |
|---|---|
| [Fichiers .nexy](views/nexy/README.md) | Écrivez une page avec Python, Jinja2 et des accessoires |
| [Composants](views/nexy/components.md) | Utilisez `Image`, `Link`, `Audio`, `Video` et `Import` |

### Pages et mises en page dans des fichiers {fbr,custom}
| Pages | Ce qu'il définit |
|---|---|
| [Pages frontales](views/frontend/pages.md) | Un fichier, une route : accessoires, rendu, métadonnées |
| [Dispositions frontales](views/frontend/layouts.md) | Le shell du document, l'imbrication et ce qu'une mise en page ne peut pas faire |
| [layout.nexy](views/nexy/layouts.md) | Écrire la disposition en mode serveur |
| [Markdown et MDX](views/nexy/markdown.md) | Rédiger des pages de contenu |

### Différences de cadre
| Pages | Quels changements |
|---|---|
| [React différences](views/react/differences.md) | Composants, crochets et `layout.tsx` {new} |
| [Vue différences](views/vue/differences.md) | SFC, références et `layout.vue` {new} |
| [Svelte différences](views/svelte/differences.md) | Runes, magasins et `layout.svelte` {new} |
| [Solid différences](views/solid/differences.md) | Signaux, accesseurs et `layout.tsx` {new} |
| [Preact différences](views/preact/differences.md) | Hameçons, signaux et `layout.tsx` {new} |

## Rendu

### Modes
| Pages | Ce que vous déciderez |
|---|---|
| [Rendu](rendering/README.md) | Quel mode de rendu correspond à une page |
| [RSS](rendering/ssr.md) | Rendu du serveur, la valeur par défaut |
| [Îles](rendering/islands.md) | Hydratez-vous en cas de requête inactive, visible ou multimédia |

### Modes des pages de fichiers {fbr,custom}
| Pages | Ce que vous déciderez |
|---|---|
| [ISR](rendering/isr.md) | Mettre en cache les pages avec une revalidation obsolète |
| [RSE](rendering/csr.md) | Routage côté client |

## Guides

### Formulaires et données
| Pages | Ce que tu feras |
|---|---|
| [Actions](guides/actions.md) | Appeler une fonction Python depuis un formulaire ou une fonction TypeScript tapée |
| [Bases de données](guides/databases.md) | Choisissez un ORM et effectuez des migrations |

### Sécurité et déploiement
| Pages | Ce que tu feras |
|---|---|
| [Middleware et sécurité](guides/middleware-and-security.md) | Configurer CORS, GZip, des hôtes et des sessions de confiance |
| [Déployer](deployment/README.md) | Construire, conteneuriser et servir |
| [Performances](deployment/performance.md) | Mesurer et ajuster les valeurs par défaut |

### Construire et tester
| Pages | Ce que tu feras |
|---|---|
| [Vite et style](guides/frontend.md) | Configurer Vite, le style et la build client |
| [Tests](guides/testing.md) | Testez avec pytest, `TestClient` et vitest |

### Outillage et aide
| Pages | Ce que tu feras |
|---|---|
| [Barre d'outils de développement](guides/devtools.md) | Utilisez la barre d'outils de `nexy dev` et désactivez-la |
| [Agents de codage](guides/ai-agents.md) | Donnez à Claude Code, Codex et OpenCode les règles de votre projet |
| [Dépannage](guides/troubleshooting.md) | Résolvez les premiers problèmes rencontrés par les gens |

## Bases de données

### Bases de données SQL
| Pages | Ce que tu feras |
|---|---|
| [SQLite](databases/sqlite.md) | Utiliser un seul fichier, pas de serveur : moteur, pragmas, migrations et tests |
| [PostgreSQL](databases/postgresql.md) | Connectez-vous avec psycopg, utilisez JSONB, les tableaux, la recherche et les upserts |
| [Néon](databases/neon.md) | Utiliser sans serveur PostgreSQL : hôte poolé, suspension automatique et branches |
| [MySQL et MariaDB](databases/mysql-mariadb.md) | Connectez-vous avec pymysql, utilisez utf8mb4, upserts et recherche en texte intégral |

## Venant de

Les mêmes tâches, écrites dans le framework que vous connaissez puis dans Nexy.

### Aperçu
| Pages | Ce que tu feras |
|---|---|
| [Venant d'un autre cadre](getting-started/coming-from-other-frameworks.md) | Traduire FastAPI, Next.js et exprimer les habitudes dans Nexy |

### Python cadres {fbr}
| Pages | Ce que tu feras |
|---|---|
| [De FastAPI](coming-from/fastapi.md) | Conservez votre code FastAPI : seul `@app.get` devient un fichier |
| [De Flask](coming-from/flask.md) | Transformez les vues, les plans, les modèles et les formulaires en itinéraires Nexy |
| [De Django](coming-from/django.md) | Mapper les vues, modèles, modèles, formulaires et paramètres vers Nexy |

### JavaScript backends {fbr}
| Pages | Ce que tu feras |
|---|---|
| [Depuis Express](coming-from/express.md) | Traduire les routes, les middlewares et les `req`/`res` en gestionnaires Python |
| [De Fastify](coming-from/fastify.md) | Transformez les schémas, plugins et hooks en modèles, dossiers et fichiers |
| [D'Élysée](coming-from/elysia.md) | Mapper les schémas `t`, les gardes et l'Eden aux Pydantic et aux actions typées |
| [De Hono](coming-from/hono.md) | Mapper les routes, le middleware et le client `hc` vers Nexy |

### Cadres Fullstack {fbr}
| Pages | Ce que tu feras |
|---|---|
| [De Next.js](coming-from/nextjs.md) | Conservez vos pages React et déplacez le code du serveur vers Python |
| [De Remix](coming-from/remix.md) | Transformez les chargeurs et les actions en Python gestionnaires et actions |
| [Depuis Nuxt](coming-from/nuxt.md) | Conservez vos pages Vue et déplacez `server/` vers Python |
| [De SvelteKit](coming-from/sveltekit.md) | Conservez vos Svelte pages et déplacez les charges, actions et hooks vers Python |
| [De Astro](coming-from/astro.md) | Écrivez Astro pages sous forme de `.nexy` pages, avec les mêmes îlots |
| [Depuis Laravel](coming-from/laravel.md) | Cartographier les itinéraires, les contrôleurs, Blade, Eloquent et les files d'attente vers Nexy |
| [De Ruby sur Rails](coming-from/rails.md) | Cartographier les itinéraires, les contrôleurs, l'ERB, l'Active Record et les tâches vers Nexy |

### Cadres de contrôleurs {modular}
| Pages | Ce que tu feras |
|---|---|
| [De NestJS](coming-from/nestjs.md) | Déplacez les contrôleurs, les modules, les fournisseurs et les gardes vers le routeur modulaire |
| [À partir de Spring Boot](coming-from/spring-boot.md) | Déplacez les contrôleurs, les services et les filtres vers le routeur modulaire |

## Référence

### Commandes et configuration
| Pages | Ce qu'il répertorie |
|---|---|
| [CLI](reference/cli.md) | Commandes, indicateurs, invites et codes de sortie |
| [Configuration](reference/config.md) | Chaque champ `nexyconfig.py` et sa valeur par défaut |

### Python API et erreurs
| Pages | Ce qu'il répertorie |
|---|---|
| [API Python](reference/python-api.md) | Tous les noms que Nexy exporte, par module |
| [Exceptions et erreurs](reference/exceptions.md) | Chaque panne, son statut et le fichier qui y répond |

### Conventions de fichiers {fbr,custom}
| Pages | Ce que tu feras |
|---|---|
| [Conventions de fichiers](reference/file-conventions.md) | Fichiers réservés et règles de routage |

### Conventions et concepts
| Pages | Ce que tu feras |
|---|---|
| [Glossaire](reference/glossary.md) | Les mots utilisés par ces documents |
| [Sécurité](reference/security.md) | Planchers de versions, règles suivies par Nexy, audits |

## Disposition
```text
docs/
├─ README.md
├─ getting-started/     what is Nexy, installation, quick start, tutorial, core concepts,
│                       project structure, how Nexy works, migration
├─ coming-from/         one page per framework: FastAPI, Django, Express, Next.js...
├─ databases/           one page per database: SQLite, PostgreSQL, Neon, MySQL
├─ routing/             FBR Router, Modular Router, Custom Router
│  ├─ fbr/              file-based routing
│  │  ├─ modes.md       server mode and client mode
│  │  ├─ inheritance.md layouts, dependencies, error pages
│  │  ├─ pages/         pages, dynamic routes, route groups, metadata
│  │  ├─ layouts/       layout resolution, layout.tsx, layout.vue, layout.svelte
│  │  ├─ handlers/      .py route handlers, validation and errors
│  │  ├─ dependencies/  dependencies.py, guards
│  │  ├─ middleware/    middleware.py
│  │  ├─ errors/        not-found and error pages
│  │  ├─ navigation/    links, hooks
│  │  └─ realtime/    WebSocket
│  ├─ modular/          controllers, injection, guards, NestJS comparison
│  └─ custom/           include an existing FastAPI router
├─ rendering/           SSR, ISR, CSR, islands
├─ views/               choose a format, one page per client framework
│  ├─ frontend/         the four contracts every framework shares
│  └─ nexy/             .nexy files, components, layouts, Markdown and MDX
├─ guides/              actions, i18n, databases, middleware, frontend, testing
├─ deployment/          deploy, performance
└─ reference/           CLI, config, Python API, exceptions, file conventions, glossary,
                        security, agents
```

## Avancé

### Avancé {advanced}

| Pages | Ce que tu feras |
|---|---|
| [Comment fonctionne Nexy](getting-started/how-nexy-works.md) | Voyez ce qui se passe entre un fichier et une page, et ce que Nexy vous laisse |
| [Mise à niveau vers 2.2](getting-started/upgrading.md) | Migrer de 2.1 vers 2.2 |
| [Internationalisation (i18n)](guides/i18n.md) | Ajoutez des traductions avec votre choix de bibliothèque |
| [Recettes](guides/recipes.md) | Exemples et modèles, pas un tutoriel |

*Ces pages ne font pas partie du chemin de lecture par défaut. Un lien "Toute la documentation" permet de tout voir.*
