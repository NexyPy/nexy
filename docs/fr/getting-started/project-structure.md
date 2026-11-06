# Structure du projet

Chaque fichier d'un projet Nexy a une tâche, et sa destination dépend du routeur : `src/routes/` pour le routage basé sur les fichiers, `src/apps/` pour le routeur modulaire.

## Niveau supérieur

<!-- router:fbr -->
```text
my-app/
├─ src/
│  ├─ routes/            every file is a route
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
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
- **Une pièce utilisée par plusieurs voies** - un composant ou un module : `src/components/`, `src/`.
- **Un dossier servi tel quel** - `public/`.
- **Généré** - `__nexy__/` ; ne le modifiez jamais.

> [!WARNING]
> `src/routes/` est scanné : un assistant placé là devient un itinéraire. Placez un assistant qui n'est pas une route en dehors de `src/routes/`, ou commencez son nom par `_`.
<!-- /router -->

<!-- router:modular -->
```text
my-app/
├─ src/
│  ├─ apps/              controllers, modules and their views
│  │  ├─ app_module.py   the root module, given to useRouter
│  │  ├─ app_controller.py
│  │  ├─ app_view.nexy   a view a controller returns
│  │  ├─ layout.nexy     the frame the controllers pass their view to
│  │  └─ users/          one folder per feature: controller, module, service, model
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = AppModule
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Pour choisir un dossier, demandez quel est le fichier :

- **Une URL** - une méthode d'un contrôleur dans `src/apps/`, enregistrée par son module.
- **Une page** - une vue `.nexy` à côté de son contrôleur, renvoyée avec `useViews`.
- **Une pièce utilisée par plusieurs vues** - `src/components/`.
- **Un dossier servi tel quel** - `public/`.
- **Généré** - `__nexy__/` ; ne le modifiez jamais.
<!-- /router -->

<!-- router:custom -->
```text
my-app/
├─ src/
│  ├─ legacy/            the FastAPI router you include
│  │  └─ api.py          router = APIRouter(prefix="/api")
│  ├─ routes/            pages and route files, served next to it
│  │  └─ index.nexy      → /
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = router
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Pour choisir un dossier, demandez quel est le fichier :

- **Un itinéraire de l'application incluse** - là où elle se trouve déjà, ici `src/legacy/`.
- **Une nouvelle page ou route** - `src/routes/`, à côté du routeur inclus.
- **Un dossier servi tel quel** - `public/`.
- **Généré** - `__nexy__/` ; ne le modifiez jamais.
<!-- /router -->

<!-- router:fbr,custom -->
## `src/routes/`

Chaque fichier devient une route, à l'exception des noms réservés ci-dessous. Le chemin du fichier moins l'extension est l'URL - voir [routage basé sur les fichiers](../routing/fbr/README.md).

| Fichier | Rôle |
|---|---|
| `layout.nexy` | enveloppe les pages frères et sœurs et enfants |
| `errors.nexy` | 500 pages pour l'annuaire |
| `notfound.nexy` | Page 404 pour l'annuaire |
| `dependencies.py` | dépendances FastAPI partagées pour le répertoire |
| `__init__.py` | Python marqueur de paquet |
| `loading.nexy` | réservé - exclu des routes, mais cela n'a pas encore d'effet d'exécution |

Chaque nom de page existe également par framework. Avec `react()` configuré, `layout.jsx` et `layout.tsx` sont réservés exactement comme `layout.nexy`. Les listes sont construites en `nexy/core/config.py` (`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`).

> [!NOTE]
> `notfound.nexy` et `errors.nexy` ne sont installés que lorsqu'une copie existe à la racine des routes. Une copie dans un sous-répertoire affine ensuite la page pour ce préfixe.
<!-- /router -->

<!-- router:modular -->
## `src/apps/`

Un contrôleur répond aux URL, un module regroupe les contrôleurs et les fournisseurs, et le module racine est monté avec `useRouter` dans `nexyconfig.py` :

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller()
class AppController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/app_view.nexy")})
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    useAliases = {"@": "src"}  # the views import @/components/...
```

Aucun fichier dans `src/apps/` n'est une route par son nom : seuls les contrôleurs répertoriés par un module répondent. Voir [routage modulaire](../routing/modular/README.md).
<!-- /router -->

## `public/`

Les fichiers ici sont servis depuis la racine du site : `/favicon.ico`, `/robots.txt`, images, polices.

## `__nexy__/`

Généré par `nx build` (et par `nx dev` pour les pièces dont il a besoin). Il contient :

- les fichiers `.nexy` compilés, sous la forme d'un package Python (`__nexy__/src/...`) ;
- les points d'entrée client générés (`main.ts`, `vite.ts`, `*.auto.ts`) ;
- `client/` après une Vite build - actifs, manifeste, HTML pré-rendu ;
- `build-cache.json`.

Traitez l'ensemble du répertoire comme jetable : supprimez-le, reconstruisez-le. Le modifier à la main perd la modification lors de la prochaine version. Ajoutez-le à `.gitignore`.

## Prochaines étapes

<!-- router:fbr -->
- [Routage basé sur des fichiers](../routing/fbr/README.md) : comment un chemin devient une URL
<!-- /router -->
<!-- router:modular -->
- [Routage modulaire](../routing/modular/README.md) : contrôleurs, modules et fournisseurs
<!-- /router -->
<!-- router:custom -->
- [Routage personnalisé](../routing/custom/README.md) : inclure un routeur FastAPI existant
<!-- /router -->
- [Configuration](../reference/config.md) : toutes les options du projet
- [Frontend](../guides/frontend.md) : Vite, style et build client
