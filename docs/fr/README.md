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
| Page | Ce que vous ferez |
|---|---|
| [Installation](getting-started/installation.md) | Installez uv et la CLI Nexy, puis créez votre premier projet |
| [Démarrage rapide](getting-started/quick-start.md) | Créez un projet, exécutez-le avec live reload et construisez-le pour la production |
| [Tutoriel](getting-started/tutorial.md) | Créez une page de notes avec un point de terminaison, des données partagées et une version de production en 10 minutes |

### Comprendre le modèle
| Page | Ce que vous ferez |
|---|---|
| [Concepts de base](getting-started/core-concepts.md) | Obtenez le modèle mental : route, page, vue, composant, gestionnaire, point de terminaison |
| [Comment fonctionne Nexy](getting-started/how-nexy-works.md) | Suivez une requête depuis l'URL jusqu'au fichier qui y répond |
| [Architecture](architecture.md) | Sachez quelle couche fait quoi et ce que Nexy laisse à votre application |
| [Structure du projet](getting-started/project-structure.md) | Savoir à quoi servent chaque dossier et fichier d'un projet |
| [Choisissez un routeur](routing/README.md) | Choisissez le routeur basé sur des fichiers, modulaire ou personnalisé |
| [Choisissez un format d'affichage](views/README.md) | Choisissez `.nexy`, Markdown ou un framework client pour une page |

### Venant d'ailleurs
| Page | Ce que vous ferez |
|---|---|
| [Venant d'un autre framework](getting-started/coming-from-other-frameworks.md) | Traduire FastAPI, Next.js et exprimer ses habitudes en Nexy |

## Routage

### Basé sur un fichier {fbr}
| Page | Ce que vous ferez |
|---|---|
| [Routage basé sur des fichiers](routing/fbr/README.md) | Transformer un chemin de fichier en URL |
| [Pages](routing/fbr/pages/README.md) | Écrire une page |
| [Routes dynamiques](routing/fbr/pages/dynamic-routes.md) | Utiliser `[slug]`, `[...path]` et les groupes de routes |
| [Métadonnées de la page](routing/fbr/pages/metadata.md) | Définir le titre, la description et l'image de partage d'une page {new} |
| [Mises en page](routing/fbr/layouts/README.md) | Partager un cadre entre les pages |
| [Héritage](routing/fbr/inheritance.md) | Lire l'ordre de résolution des mises en page, des dépendances et des pages d'erreur |
| [Mode serveur et mode client](routing/fbr/modes.md) | `useCSR`, et ce que chaque mode permet |
| [Lier et naviguer](routing/fbr/navigation/linking-and-navigating.md) | Lier des pages, naviguer sur le client, préfetch |
| [Hooks](routing/fbr/navigation/hooks.md) | Lire le chemin, la requête, les cookies et la session |

### Gestionnaires et erreurs {fbr}
| Page | Ce que vous ferez |
|---|---|
| [Gestionnaires de routes](routing/fbr/handlers/README.md) | Ajouter un point de terminaison Python |
| [Validation et erreurs](routing/fbr/handlers/validation-and-errors.md) | Répondez à `422` et `404`, et générez un `HTTPException` |
| [WebSocket gestionnaires](routing/fbr/realtime/websocket.md) | Gérer une connexion `SOCKET` |
| [Dépendances et gardes](routing/fbr/dependencies/README.md) | Exécuter `dependencies.py` avant un gestionnaire et en hériter |
| [Fichiers middleware](routing/fbr/middleware/README.md) | Encapsuler les requêtes avec `middleware.py`, hérités du répertoire |
| [Pages d'erreur](routing/fbr/errors/README.md) | Réponse avec `notfound.nexy`, `errors.nexy` et erreurs JSON |
| [Pages d'erreur par dossier](routing/fbr/errors/folder-pages.md) | Cas limite : erreurs des sous-dossiers |

### Routeur modulaire {modular}
Contrôleurs et modules.
| Page | Ce que vous ferez |
|---|---|
| [Routage modulaire](routing/modular/README.md) | Montage de contrôleurs et de modules |
| [Injection de dépendances](routing/modular/dependency-injection.md) | Définir les services, leurs scopes et le conteneur |
| [Gardes et métadonnées](routing/modular/guards-and-metadata.md) | Protéger et documenter les itinéraires |
| [Routeur modulaire vs NestJS](routing/modular/vs-nestjs.md) | Comparaison avec NestJS |

### Intégration de routeur personnalisé {custom}
| Page | Ce que vous ferez |
|---|---|
| [Routage personnalisé](routing/custom/README.md) | Inclure une application FastAPI existante |

## Front-end

### Contrats partagés
| Page | Ce qu'il définit |
|---|---|
| [Pages frontend](views/frontend/pages.md) | Un fichier, une route : accessoires, rendu, métadonnées |
| [Mise en page du frontend](views/frontend/layouts.md) | Le shell du document, l'imbrication et ce qu'une mise en page ne peut pas faire |
| [Actions et navigation](views/frontend/actions-and-navigation.md) | Appeler une action saisie, lier des pages, lire l'URL |

### Vues Nexy
| Page | Ce que vous ferez |
|---|---|
| [fichiers .nexy](views/nexy/README.md) | Écrivez une page avec Python, Jinja2 et les accessoires |
| [Composants](views/nexy/components.md) | Utiliser `Image`, `Link`, `Audio`, `Video` et `Import` |
| [layout.nexy](views/nexy/layouts.md) | Écrire la mise en page en mode serveur |
| [Markdown et MDX](views/nexy/markdown.md) | Écrire des pages de contenu |

### Différences de cadre
| Page | Ce qui change |
|---|---|
| [React différences](views/react/differences.md) | Composants, crochets et `layout.tsx` {new} |
| [Vue différences](views/vue/differences.md) | SFC, références et `layout.vue` {new} |
| [Svelte différences](views/svelte/differences.md) | Runes, magasins et `layout.svelte` {new} |
| [Solid différences](views/solid/differences.md) | Signaux, accesseurs et `layout.tsx` {new} |
| [Preact différences](views/preact/differences.md) | Hameçons, signaux et `layout.tsx` {new} |

## Rendu

### Modes
| Page | Ce que vous déciderez |
|---|---|
| [Rendu](rendering/README.md) | Quel mode de rendu correspond à une page |
| [SSR](rendering/ssr.md) | Rendu du serveur, valeur par défaut |
| [ISR](rendering/isr.md) | Pages de cache avec périmée pendant la revalidation |
| [CSR](rendering/csr.md) | Routage côté client |
| [Îles](rendering/islands.md) | Hydratez-vous en cas de requête inactive, visible ou multimédia |

## Guides

### Formulaires et données
| Page | Ce que vous ferez |
|---|---|
| [Actions](guides/actions.md) | Appeler une fonction Python depuis un formulaire ou une fonction TypeScript saisie |
| [Bases de données](guides/databases.md) | Choisir un ORM et exécuter des migrations |

### Sécurité et déploiement
| Page | Ce que vous ferez |
|---|---|
| [Middleware et sécurité](guides/middleware-and-security.md) | Configurer CORS, GZip, les hôtes et les sessions de confiance |
| [Déployer](deployment/README.md) | Créer, conteneuriser et servir |
| [Performance](deployment/performance.md) | Mesurer et régler les valeurs par défaut |

### Construire et tester
| Page | Ce que vous ferez |
|---|---|
| [Vite et style](guides/frontend.md) | Configurer Vite, style et build client |
| [Testing](guides/testing.md) | Test avec pytest, `TestClient` et vitest |

### Outillage et aide
| Page | Ce que vous ferez |
|---|---|
| [Barre d'outils Dev](guides/devtools.md) | Utilisez la barre d'outils de `nexy dev` et désactivez-la |
| [Agents de codage](guides/ai-agents.md) | Donnez à Claude Code, Codex et OpenCode les règles de votre projet |
| [Dépannage](guides/troubleshooting.md) | Résoudre les premiers problèmes rencontrés |

## Référence

### Commandes et configuration
| Page | Ce qu'elle répertorie |
|---|---|
| [CLI](reference/cli.md) | Commandes, indicateurs, invites et codes de sortie |
| [Config](reference/config.md) | Chaque champ `nexyconfig.py` et son | par défaut

### Python API et erreurs
| Page | Ce qu'elle répertorie |
|---|---|
| [Python API](reference/python-api.md) | Chaque nom exporté par Nexy, par module |
| [Exceptions et erreurs](reference/exceptions.md) | Chaque panne, son statut et le fichier qui y répond |

### Conventions et concepts
| Page | Ce que vous ferez |
|---|---|
| [Conventions sur les fichiers](reference/file-conventions.md) | Fichiers réservés et règles de routage |
| [Glossaire](reference/glossary.md) | Les mots utilisés dans ces documents |
| [Sécurité](reference/security.md) | Étages de version, règles suivies par Nexy, audits |

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

| Page | Ce que vous ferez |
|---|---|
| [Mise à niveau vers 2.2](getting-started/upgrading.md) | Migrer de 2.1 vers 2.2 |
| [Internationalisation (i18n)](guides/i18n.md) | Ajoutez des traductions avec la bibliothèque de votre choix |
| [Recettes](guides/recipes.md) | Exemples et modèles, pas un tutoriel |

*Ces pages ne font pas partie du chemin de lecture par défaut. Un lien "Toute la documentation" permet de tout voir.*
