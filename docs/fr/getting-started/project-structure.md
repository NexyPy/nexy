# Structure du projet

Chaque fichier d'un projet Nexy a une tâche. Cette page dit lequel.

## Niveau supérieur

```text
my-app/
├─ src/
│  ├─ routes/            file-based routes (FBR)
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ apps/              modular router, decorators (optional, next to routes/)
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Pour choisir un dossier, demandez quel est le fichier :

- **Quelque chose que le navigateur peut ouvrir** - un itinéraire : `src/routes/`.
- **Une pièce utilisée par plusieurs itinéraires** - un composant ou un module : `src/components/`, `src/`.
- **Un dossier servi tel quel** - `public/`.
- **Un contrôleur du routeur modulaire** - `src/apps/`.
- **Généré** - `__nexy__/` ; ne le modifiez jamais.

> [!WARNING]
> `src/routes/` est scanné : un assistant placé là devient un itinéraire. Placez un assistant qui n'est pas une route en dehors de `src/routes/`, ou commencez son nom par `_`.

## `src/routes/`

Chaque fichier devient une route, à l'exception des noms réservés ci-dessous. Le chemin du fichier moins l'extension est l'URL - voir [routage](../routing/README.md).

| Fichier | Rôle |
|---|---|
| `layout.nexy` | enveloppe les pages frères et sœurs et enfants |
| `errors.nexy` | 500 pages pour le répertoire |
| `notfound.nexy` | Page 404 pour le répertoire |
| `dependencies.py` | dépendances partagées FastAPI pour le répertoire |
| `__init__.py` | Python marqueur de paquet |
| `loading.nexy` | réservé - exclu des routes, mais n'a pas encore d'effet d'exécution |

Chaque nom de page existe également par framework. Avec `react()` configuré, `layout.jsx` et `layout.tsx` sont réservés exactement comme `layout.nexy`. Les listes sont construites en `nexy/core/config.py` (`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`).

> [!NOTE]
> `notfound.nexy` et `errors.nexy` ne sont installés que lorsqu'une copie existe à la racine des routes. Une copie dans un sous-répertoire affine ensuite la page pour ce préfixe.

## `src/apps/`

Le répertoire que `nexy new` utilise pour le routeur modulaire : les contrôleurs, les modules et les fournisseurs enregistrent leurs routes via les décorateurs de `nexy.decorators`, puis l'agrégat `APIRouter` est monté avec `useRouter` dans `nexyconfig.py`.

Un projet peut avoir les deux routeurs : `useRouter` monte le routeur modulaire et `src/routes/` est analysé chaque fois que ce répertoire existe. Voir [routage modulaire](../routing/modular/README.md).

## `public/`

Les fichiers ici sont servis depuis la racine du site : `/favicon.ico`, `/robots.txt`, images, polices.

## `__nexy__/`

Généré par `nx build` (et par `nx dev` pour les pièces dont il a besoin). Il contient :

- les modules de route compilés, sous forme de package Python (`__nexy__/src/routes/...`) ;
- les points d'entrée clients générés (`main.ts`, `vite.ts`, `*.auto.ts`) ;
- `client/` après une Vite build - actifs, manifeste, HTML pré-rendu ;
- `build-cache.json`.

Traitez l'ensemble du répertoire comme jetable : supprimez-le, reconstruisez-le. Le modifier à la main perd la modification lors de la prochaine version. Ajoutez-le à `.gitignore`.

## Prochaines étapes

- [Routage](../routing/README.md) : comment un chemin devient une URL
- [Configuration](../reference/config.md) : chaque option du projet
- [Frontend](../guides/frontend.md) : Vite, style et build client
