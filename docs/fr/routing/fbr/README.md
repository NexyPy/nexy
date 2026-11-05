# Routage basé sur des fichiers

Un itinéraire est un fichier. L'URL est le chemin du fichier relatif à `src/routes/`, moins l'extension.

## Fichier vers URL

| Fichier | URL |
|---|---|
| `index.nexy` | `/` |
| `about.nexy` | `/about` |
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/{slug}` |
| `docs/[...path].nexy` | `/docs/{path:path}` |
| `(marketing)/pricing.nexy` | `/pricing` |
| `api/users.py` | `/api/users` |

`index` correspond à son répertoire, pas à `/index`. Un répertoire entre parenthèses est un **groupe** : il organise les fichiers sans apparaître dans l'URL.

En mode client, les fichiers d'échange sont `.tsx`, `.vue` ou `.svelte` au lieu de `.nexy` ; les règles d'URL sont les mêmes.

## Deux modes

`useCSR` décide quelles sont les pages. Les deux ne peuvent pas être mélangés dans un seul projet : Nexy refuse de démarrer lorsqu'une page serveur se trouve à côté d'une route client.

| Mode | Pages | Disposition racine | Voir |
|---|---|---|---|
| Serveur (`useCSR = False`) | `.nexy`, `.md`, `.mdx` | `layout.nexy` | [Mode serveur et mode client](modes.md) |
| Client (`useCSR = True`) | fichiers de structure | `layout.tsx` | [layout.tsx](../../views/react/differences.md) |

Les fichiers `.py` sont des gestionnaires d'API dans les deux modes.

## Ce qui n'est pas un itinéraire

- Noms de fichiers réservés : `layout.*`, `loading.nexy`, `errors.nexy`, `notfound.nexy`, `dependencies.py`, `middleware.py`, `__init__.py`.
- Fichiers et dossiers commençant par `_` ou `.` : utilisez-les pour les partiels et les brouillons.
- Extensions qui ne sont pas actives pour votre projet. Un fichier dont l'extension est inactive est ignoré avec un avertissement.

## Un fichier par URL

Deux fichiers qui renvoient à la même URL sont tous deux enregistrés. Ne créez pas `blog.nexy` à côté de `blog/index.nexy` et ne mélangez pas `index.nexy` et `index.py` pour le même chemin. Choisissez-en un.

## Dans cette rubrique

| Dossier | Ce qu'il couvre |
|---|---|
| [pages/](pages/README.md) | pages, [routes dynamiques](pages/dynamic-routes.md), groupes de routes |
| [layouts/](layouts/README.md) | une page par type de fichier de mise en page |
| [gestionnaires/](handlers/README.md) | `.py` gestionnaires, validation et erreurs |
| [dépendances/](dependencies/README.md) | `dependencies.py`, gardiens |
| [middleware/](middleware/README.md) | `middleware.py` |
| [erreurs/](errors/README.md) | pages introuvables et pages d'erreur |
| [navigation/](navigation/linking-and-navigating.md) | liens, crochets |
| [temps réel/](realtime/websocket.md) | WebSocket |
| [héritage](inheritance.md) | les règles d'héritage dans une seule table |

## Prochaines étapes

- [Mode serveur et mode client](modes.md)
- [Mises en page](layouts/README.md)
- [Routage modulaire](../modular/README.md)
