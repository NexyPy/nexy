# Conventions de fichiers

Noms et règles réservés sous `src/routes/`.

## Fichiers d'itinéraire

| Le fichier | devient |
|---|---|
| `index.nexy`, `index.md`, `index.mdx`, `index.py` | l'itinéraire de son répertoire |
| `about.nexy` | `/about` |
| `[slug].nexy` | segment dynamique `{slug}` |
| `[...path].nexy` | fourre-tout `{path:path}` |
| `(group)/page.nexy` | `/page` : le groupe n'apparaît pas dans l'URL |
| `name.py` | Gestionnaire d'API ; les noms de fonctions `GET`, `POST`, ... sont les méthodes |
| `name.tsx`, `.jsx`, `.vue`, `.svelte` | route client lorsque le framework est activé avec `useFF` |

## Fichiers réservés

| Fichier | Rôle | Détails |
|---|---|---|
| `layout.nexy` | mode serveur : encapsule chaque page en dessous ; le root possède le document HTML | [layout.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | mode client (React) : la racine est propriétaire du document HTML, les imbriquées enveloppent les pages | [layout.tsx](../views/react/differences.md) |
| `layout.vue`, `layout.svelte` | mode client : mises en page imbriquées | [layout.vue](../views/vue/differences.md), [layout.svelte](../views/svelte/differences.md) |
| `notfound.nexy` | Page 404 pour son répertoire | [Pages d'erreur](../routing/fbr/errors/README.md) |
| `errors.nexy` | 500 pages pour son répertoire | [Pages d'erreur](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | 403 pages pour son répertoire | [Pages d'erreur par dossier](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | 401 pages pour son répertoire | [Pages d'erreur par dossier](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | réservé ; aucun effet d'exécution pour l'instant | [Pages d'erreur](../routing/fbr/errors/README.md) |
| `middleware.py` | et `async def middleware(request, call_next)` encapsulant les requêtes du répertoire et ci-dessous | [Fichiers Middleware](../routing/fbr/middleware/README.md) |
| `dependencies.py` | une `dependencies = [fn, ...]` liste appliquée au répertoire et à ses enfants | [Dépendances](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Python marqueur de paquet | |
| `favicon.ico` | servi à `/favicon.ico` | |

`useLayoutExtensions`, `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions`, `useUnauthorizedExtensions` et `useLoadingExtensions` réservent davantage d'extensions pour ces noms. Voir [Configuration](config.md).

## Fichiers ignorés

- Un fichier ou un dossier commençant par `_` ou `.` : utilisez-le pour les partiels, les brouillons et les aides.
- Un fichier dont l'extension n'est pas active pour le projet : il est ignoré avec un avertissement.

## Un fichier par URL

Deux fichiers qui renvoient à la même URL sont tous deux enregistrés. Ne mettez pas `blog.nexy` à côté de `blog/index.nexy`.

## À l'extérieur `src/routes/`

| Dossier | Objectif |
|---|---|
| `src/components/` | composants importés par pages ; jamais de routes |
| `src/apps/` | contrôleurs et modules du [routeur modulaire](../routing/modular/README.md) |
| `public/` | fichiers statiques, servis à la racine : `public/logo.svg` est `/logo.svg` (également sous `/public/`) |
| `__nexy__/` | sortie générée ; ne commettez pas |

## Prochaines étapes

- [Routage](../routing/README.md)
- [Structure du projet](../getting-started/project-structure.md)
