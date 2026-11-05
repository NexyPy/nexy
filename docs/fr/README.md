# Documentation Nexy

**Un framework Python pour les applications Web fullstack.**

Nexy est à la frontière entre un backend Python et une interface de navigateur. Au lieu de deux serveurs, deux systèmes de build et deux tables de routage, vous obtenez une origine : FastAPI et Starlette servent l'application, Vite construit le client et un fichier sous `src/routes/` est une route - `.nexy` est une page, `.py` est un gestionnaire d'API.

- **Python en premier.** Les pages, les points de terminaison, les formulaires et les actions sont Python, et une page rendue par le serveur n'a besoin d'aucun framework frontend.
- **Trois routeurs, une intégration.** Basé sur des fichiers, modulaire ou existant FastAPI `APIRouter`.
- **Un frontend quand vous en voulez un.** React, Vue, Svelte, Solid ou Preact, par page en îlots, ou pour l'ensemble du projet en mode client.
- **Rendu, un modèle.** Le rendu du serveur, les pages mises en cache et les îlots sont décidés par page ; Le routage client est un changement de projet.
- **Actions typées.** Une publication de formulaire et un appel client tapé atteignent la même fonction Python.

Commencez avec un fichier sous `src/routes/` et ajoutez une structure lorsque le projet se développe.

## Commencer

### Premiers pas
| Pages | Ce que tu feras |
|---|---|
| [Installation](getting-started/installation.md) | Installez uv et la CLI Nexy, puis créez votre premier projet |
| [Démarrage rapide](getting-started/quick-start.md) | Créez un projet, exécutez-le avec Live Reload et construisez-le pour la production |
| [Tutoriel](getting-started/tutorial.md) | Créez une page de notes avec un point de terminaison, des données partagées et une version de production en 10 minutes |

### Comprendre le modèle
| Pages | Ce que tu feras |
|---|---|
| [Concepts de base](getting-started/core-concepts.md) | Obtenez le modèle mental : route, page, vue, composant, gestionnaire, point de terminaison |
| [Comment fonctionne Nexy](getting-started/how-nexy-works.md) | Suivez une requête depuis l'URL jusqu'au fichier qui y répond |
| [Architecture](architecture.md) | Sachez quelle couche fait quoi et ce que Nexy laisse à votre application |
| [Structure du projet](getting-started/project-structure.md) | Savoir à quoi servent chaque dossier et fichier d'un projet |
| [Choisissez un routeur](routing/README.md) | Choisissez le routeur basé sur des fichiers, modulaire ou personnalisé |
| [Choisissez un format d'affichage](views/README.md) | Choisissez `.nexy`, Markdown ou un framework client pour une page |

### Venant d'ailleurs
| Pages | Ce que tu feras |
|---|---|
| [Venant d'un autre cadre](getting-started/coming-from-other-frameworks.md) | Traduire FastAPI, Next.js et exprimer les habitudes dans Nexy |

## Routage

### Basé sur un fichier {fbr}
| Pages | Ce que tu feras |
|---|---|
| [Routage basé sur des fichiers](routing/fbr/README.md) | Transformer un chemin de fichier en URL |
| [Pages](routing/fbr/pages/README.md) | Écrire une page |
| [Itinéraires dynamiques](routing/fbr/pages/dynamic-routes.md) | Utiliser `[slug]`, `[...path]` et les groupes de routes |
| [Métadonnées de la page](routing/fbr/pages/metadata.md) | Définir le titre, la description et partager l'image d'une page {new} |
| [Mise en page](routing/fbr/layouts/README.md) | Partager un cadre entre les pages |
| [Héritage](routing/fbr/inheritance.md) | Lire l'ordre de résolution des mises en page, des dépendances et des pages d'erreur |
| [Mode serveur et mode client](routing/fbr/modes.md) | `useCSR`, et ce que chaque mode permet |
| [Lien et navigation](routing/fbr/navigation/linking-and-navigating.md) | Lier des pages, naviguer sur le client, pré-extraire |
| [Crochets](routing/fbr/navigation/hooks.md) | Lire le chemin, la requête, les cookies et la session |

### Gestionnaires et erreurs {fbr}
| Pages | Ce que tu feras |
|---|---|
| [Gestionnaires d'itinéraires](routing/fbr/handlers/README.md) | Ajouter un point de terminaison Python |
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
| [Pages frontales](views/frontend/pages.md) | Un fichier, une route : accessoires, rendu, métadonnées |
| [Dispositions du frontend](views/frontend/layouts.md) | Le shell du document, l'imbrication et ce qu'une mise en page ne peut pas faire |
| [Actions et navigation](views/frontend/actions-and-navigation.md) | Appeler une action tapée, lier des pages, lire l'URL |

### Vues Nexy
| Pages | Ce que tu feras |
|---|---|
| [fichiers .nexy](views/nexy/README.md) | Écrivez une page avec Python, Jinja2 et des accessoires |
| [Composants](views/nexy/components.md) | Utilisez `Image`, `Link`, `Audio`, `Video` et `Import` |
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
| [ISR](rendering/isr.md) | Mettre en cache les pages avec une revalidation obsolète |
| [RSE](rendering/csr.md) | Routage côté client |
| [Îles](rendering/islands.md) | Hydratez-vous en cas de requête inactive, visible ou multimédia |

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
| [Vite et style](guides/frontend.md) | Configurer Vite, le style et la construction du client |
| [Tests](guides/testing.md) | Testez avec pytest, `TestClient` et vitest |

### Outillage et aide
| Pages | Ce que tu feras |
|---|---|
| [Barre d'outils de développement](guides/devtools.md) | Utilisez la barre d'outils de `nexy dev` et désactivez-la |
| [Agents de codage](guides/ai-agents.md) | Donnez à Claude Code, Codex et OpenCode les règles de votre projet |
| [Dépannage](guides/troubleshooting.md) | Résolvez les premiers problèmes rencontrés par les gens |

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

### Conventions et concepts
| Pages | Ce que tu feras |
|---|---|
| [Conventions de fichiers](reference/file-conventions.md) | Fichiers réservés et règles de routage |
| [Glossaire](reference/glossary.md) | Les mots utilisés par ces documents |
| [Sécurité](reference/security.md) | Planchers de versions, règles suivies par Nexy, audits |

## Disposition
```text
docs/
├─ README.md
├─ architecture.md       the layers, and what Nexy leaves to the application
├─ getting-started/     installation, quick start, tutorial, core concepts, project structure,
│                       migration
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
| [Mise à niveau vers 2.2](getting-started/upgrading.md) | Migrer de 2.1 vers 2.2 |
| [Internationalisation (i18n)](guides/i18n.md) | Ajoutez des traductions avec votre choix de bibliothèque |
| [Recettes](guides/recipes.md) | Exemples et modèles, pas un tutoriel |

*Ces pages ne font pas partie du chemin de lecture par défaut. Un lien "Toute la documentation" permet de tout voir.*
