# Conventions de fichiers

Noms et règles réservés sous `src/routes/`.

## Fichiers d'itinéraire

| Fichier | Devient |
|---|---|
| `index.nexy`, `index.md`, `index.mdx`, `index.py` | le parcours de son répertoire |
| `about.nexy` | `/about` |
| `[slug].nexy` | segment dynamique `{slug}` |
| `[...path].nexy` | fourre-tout `{path:path}` |
| `(group)/page.nexy` | `/page` : le groupe n'apparaît pas dans l'URL |
| `name.py` | Gestionnaire d'API ; les noms de fonctions `GET`, `POST`, ... sont les méthodes |
| `name.tsx`, `.jsx`, `.vue`, `.svelte` | route client lorsque le framework est activé avec `useFF` |

```text
src/routes/
├─ index.nexy           /
├─ about.nexy           /about
├─ (marketing)/
│  └─ pricing.nexy      /pricing
├─ blog/
│  ├─ index.md          /blog
│  └─ [slug].nexy       /blog/{slug}
├─ docs/
│  └─ [...path].nexy    /docs/{path:path}
└─ api/
   └─ users.py          GET /api/users, POST /api/users
```

```python filename="src/routes/api/users.py"
async def GET():
    return {"users": []}


async def POST():
    return {"created": True}
```

## Fichiers réservés

| Fichier | Rôle | Détails |
|---|---|---|
| `layout.nexy` | mode serveur : encapsule chaque page en dessous ; la racine est propriétaire du document HTML | [layout.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | mode client (React) : la racine est propriétaire du document HTML, les pages imbriquées enveloppent les pages | [layout.tsx](../views/react/differences.md) |
| `layout.vue`, `layout.svelte` | mode client : mises en page imbriquées | [layout.vue](../views/vue/differences.md), [layout.svelte](../views/svelte/differences.md) |
| `notfound.nexy` | Page 404 pour son annuaire | [Pages d'erreur](../routing/fbr/errors/README.md) |
| `errors.nexy` | 500 pages pour son annuaire | [Pages d'erreur](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | Page 403 pour son annuaire | [Pages d'erreur par dossier](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | 401 page pour son annuaire | [Pages d'erreur par dossier](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | réservé; pas encore d'effet d'exécution | [Pages d'erreur](../routing/fbr/errors/README.md) |
| `middleware.py` | un `async def middleware(request, call_next)` encapsulant les requêtes du répertoire et ci-dessous | [Fichiers middleware](../routing/fbr/middleware/README.md) |
| `dependencies.py` | une liste `dependencies = [fn, ...]` appliquée au répertoire et à ses enfants | [Dépendances](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Python marqueur de paquet | |
| `favicon.ico` | servi à `/favicon.ico` | |

`useLayoutExtensions`, `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions`, `useUnauthorizedExtensions` et `useLoadingExtensions` réservent davantage d'extensions pour ces noms. Voir [Configuration](config.md).

Les deux fichiers Python du tableau, côte à côte dans un même dossier :

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

Et une page qui répond à la 404 de son dossier :

```nexy filename="src/routes/notfound.nexy"
<h1>Page not found</h1>
<p><a href="/">Back home</a></p>
```

## Fichiers ignorés

- Un fichier ou un dossier commençant par `_` ou `.` : utilisez-le pour les partiels, les brouillons et les aides.
- Un fichier dont l'extension n'est pas active pour le projet : il est ignoré avec un avertissement.

```text
src/routes/
├─ index.nexy           /
├─ _card.nexy           ignored: a partial the pages include
├─ _helpers/            ignored, with everything inside
│  └─ format.py
└─ .draft.nexy          ignored: a draft
```

## Un fichier par URL

Deux fichiers qui renvoient à la même URL sont tous deux enregistrés. Ne mettez pas `blog.nexy` à côté de `blog/index.nexy`.

```text
src/routes/
├─ blog.nexy            /blog
└─ blog/
   └─ index.nexy        /blog as well: keep only one of the two
```

## À l'extérieur `src/routes/`

| Dossier | Objectif |
|---|---|
| `src/components/` | composants importés par pages ; jamais de routes |
| `src/apps/` | contrôleurs et modules du [routeur modulaire](../routing/modular/README.md) |
| `public/` | fichiers statiques, servis à la racine : `public/logo.svg` est `/logo.svg` (également sous `/public/`) |
| `__nexy__/` | sortie générée ; ne vous engagez pas |

```text
my-app/
├─ nexyconfig.py
├─ public/
│  └─ logo.svg          /logo.svg
├─ src/
│  ├─ routes/           the routes
│  ├─ components/
│  │  └─ Counter.tsx    imported by pages, never served on its own
│  └─ apps/             the modular router, when you use it
└─ __nexy__/            generated: add it to .gitignore
```

## Prochaines étapes

- [Routage](../routing/README.md)
- [Structure du projet](../getting-started/project-structure.md)
