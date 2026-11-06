# Concepts de base

Les mots utilisés par le reste de la documentation - route, page, vue, composant, gestionnaire, point de terminaison - chacun sur une seule ligne, avec un lien vers la page qui va plus loin. Nouveau sur Nexy ? Commencez par [Qu'est-ce que Nexy ?](what-is-nexy.md).

## Comment lire ces documents

| Niveau | La question à laquelle il répond | Commencez par |
|---|---|---|
| Architecture des applications | quelle couche répond à une demande et ce qu'elle refuse de faire | [Comment fonctionne Nexy](how-nexy-works.md) |
| Structure de la candidature | où se trouve le code et ce que devient un fichier | [Structure du projet](project-structure.md) |
| Présentation et rendu | ce que le lecteur voit et qui produit le HTML | [Vues](../views/README.md), [Rendu](../rendering/README.md) |
| Interaction avec les applications | ce que fait le lecteur et ce qui s'exécute en réponse | [Actions](../guides/actions.md) |

Les niveaux sont lus une fois dans cet ordre. Après cela, une page dont vous avez besoin est une recherche, pas un cours.

## Architecture des applications

Trois façons de décider quel code répond à une URL. Ce sont des alternatives, pas des couches :

- **Routage basé sur des fichiers (FBR)** : un fichier sous `src/routes/` est une route. La valeur par défaut.
- **Routeur modulaire** : contrôleurs et modules sous `src/apps/`, déclarés auprès des décorateurs, pour une base de code de style NestJS.
- **Routeur personnalisé** : un FastAPI `APIRouter` existant inclus dans l'application.

Le choix est une ligne de la classe `NexyConfig` dans `nexyconfig.py`.

<!-- router:fbr -->
Le routage basé sur des fichiers ne nécessite aucune ligne : sans `useRouter`, Nexy lit `src/routes/`.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    pass  # file-based: no useRouter, the files of src/routes/ are the routes
```
<!-- /router -->

<!-- router:modular -->
Le routeur modulaire est le module racine de `src/apps/` :

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule  # modular: the root module of src/apps/
```
<!-- /router -->

<!-- router:custom -->
Un routeur personnalisé est un `APIRouter` que vous possédez déjà :

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import api  # an APIRouter you already have


class NexyConfig(NexyConfigModel):
    useRouter = api  # custom: your router, included as it is
```
<!-- /router -->

Choisir l’un des trois est une décision. Le choix d'un framework frontend en est un autre, distinct : voir [Choisir un routeur](../routing/README.md) et [Vues](../views/README.md).

## Structure de la candidature

Cinq notions qu'un lecteur venant de Next.js fusionne habituellement en une seule. Ce n'est pas la même chose, et la différence explique la plupart des questions « pourquoi ma page ne s'affiche-t-elle pas ».

| Notion | Qu'est-ce que c'est | Ce que ce n'est pas |
|---|---|---|
| **Itinéraire** | un modèle d'URL, produit par le chemin d'un fichier | un fichier : un fichier peut répondre à plusieurs URL (`[slug]`) |
| **Page** | un fichier de route qui restitue une vue : `.nexy`, `.md`, `.mdx`, `.tsx`, `.vue`, `.svelte` | un endpoint : il répond à un document, pas à des données |
| **Voir** | ce qui produit le corps d'une page : Jinja2 et Python, Markdown, ou un composant client | un itinéraire : une même vue peut servir plusieurs pages |
| **Composant** | une pièce réutilisable qu'une page importe | une route : en mode serveur un composant n'est jamais servi seul |
| **Gestionnaire de route** | la fonction d'un fichier de route `.py`, nommé d'après la méthode HTTP (`GET`, `POST`, …) | une page : elle renvoie du JSON, un fichier ou un `Response` |
| **Point de terminaison** | la paire (URL, méthode) à laquelle un gestionnaire répond | un gestionnaire : un fichier peut répondre à plusieurs points de terminaison |

En une phrase : **une page est un fichier de route, une vue est ce qui le restitue, un composant est ce qu'une page réutilise, un gestionnaire répond à un point de terminaison.**

<!-- router:fbr -->
Les cinq dans un petit projet :

```text
src/
├─ routes/
│  ├─ blog/[slug].nexy    a route (/blog/{slug}) whose file is a page
│  └─ api/posts.py        a route whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```nexy filename="src/routes/blog/[slug].nexy"
---
from "@/components/Like.tsx" import Like

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Like post="{{ slug }}" />
```

Le frontmatter et le modèle en dessous sont la vue de la page ; `Like` est le composant qu'il réutilise.

```python filename="src/routes/api/posts.py"
async def GET():  # the endpoint GET /api/posts
    return {"posts": []}


async def POST():  # the endpoint POST /api/posts
    return {"created": True}
```

<!-- /router -->

<!-- router:modular -->
Avec le routeur modulaire, une route est le chemin d'un contrôleur, et un gestionnaire est l'une de ses méthodes, nommée d'après le verbe HTTP :

```text
src/
├─ apps/
│  ├─ app_module.py       the root module: lists the controllers
│  └─ posts_controller.py a route (/api/posts) whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```python filename="src/apps/posts_controller.py"
from nexy.decorators import Controller


@Controller("/api/posts")
class PostsController:
    async def get(self) -> dict:  # the endpoint GET /api/posts
        return {"posts": []}

    async def post(self) -> dict:  # the endpoint POST /api/posts
        return {"created": True}
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .posts_controller import PostsController


@Module()
class AppModule:
    controllers = [PostsController]
```

Une page est toujours un fichier de `src/routes/`, ou une vue qu'un contrôleur renvoie avec `useViews`.
<!-- /router -->

<!-- router:custom -->
Avec un routeur personnalisé, une route est un chemin de votre `APIRouter`, et un gestionnaire est la fonction enregistrée par son décorateur :

```python filename="src/legacy.py"
from fastapi import APIRouter

api = APIRouter()


@api.get("/api/posts")  # the endpoint GET /api/posts
async def list_posts():
    return {"posts": []}


@api.post("/api/posts")  # the endpoint POST /api/posts
async def create_post():
    return {"created": True}
```

Les pages sont toujours des fichiers de `src/routes/` : une page de `.nexy` répond à côté des itinéraires inclus.
<!-- /router -->

Encore deux mots qui reviennent partout :

- **Layout** : un fichier `layout.*` qui enveloppe les pages sous son dossier ; la racine est propriétaire du document HTML. Voir [Mise en page](../routing/fbr/layouts/README.md).
- **Dépendance** : une fonction qui s'exécute avant un gestionnaire, appliquée par route ou par dossier. Voir [Dépendances](../routing/fbr/dependencies/README.md).

## Présentation et rendu

Deux décisions indépendantes, souvent confondues :

- **Le format** décide quel fichier restitue la page : [Vues](../views/README.md).
- **Le mode** décide qui produit le HTML et quand : [Rendu](../rendering/README.md).

| Notion | Une ligne |
|---|---|
| Mode serveur | le serveur restitue les pages `.nexy` et `.md` ; les composants sont des îlots ([modes](../routing/fbr/modes.md)) |
| Mode client | `useCSR = True` : les fichiers framework sont les itinéraires et la navigation se fait dans le navigateur |
| SSR, ISR, CSR, îles | quatre modes de rendu, décidés par page sauf CSR, qui est par projet ([rendu](../rendering/README.md)) |
| Hydratation | le navigateur attachant un framework au HTML que le serveur a déjà envoyé ([îlots](../rendering/islands.md)) |
| Accessoires | les valeurs qu'un parent transmet à un composant, déclarées `name: prop[type]` dans un fichier `.nexy` ([fichiers .nexy](../views/nexy/README.md)) |

Une page en mode serveur avec un îlot : le serveur restitue la page, le navigateur hydrate le graphique uniquement lorsqu'il défile.

```nexy filename="src/routes/sales.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Sales</h1>
<Chart directive="client:visible" />
```

## Interaction avec les applications

| Notion | Une ligne |
|---|---|
| Action | une fonction Python marquée `@Action`, servant de `POST`, appelable depuis un formulaire ou comme fonction typée ([actions](../guides/actions.md)) |
| Formulaire | un formulaire HTML qui publie dans une action, avec des erreurs de validation revenant sur la page ([actions](../guides/actions.md)) |
| Navigation | des liens qui prélevent et des hooks qui lisent le chemin, la requête, les cookies et la session ([hooks](../routing/fbr/navigation/hooks.md)) |
| Récupération de données | effectué par la page ou le gestionnaire qui en a besoin ; Nexy ne fournit aucune couche de données client ([gestionnaires](../routing/fbr/handlers/README.md)) |

Une action et le formulaire qui y est publié, qui fonctionne avant le chargement de tout script :

```python filename="src/actions/newsletter.py"
from nexy.decorators import Action


@Action
async def subscribe(email: str) -> bool:
    return True
```

```html filename="src/routes/index.nexy"
<form method="post" action="{{ __actions_path['subscribe'] }}">
  <input name="email" type="email">
  <button type="submit">Subscribe</button>
</form>
```

## Ce que Nexy ne fait pas

L'authentification, l'autorisation, la base de données, l'internationalisation, les tâches en arrière-plan, le courrier électronique, les paiements et la recherche sont **la responsabilité de votre application**, et non celle du framework. Nexy donne les points d'extension et indique où brancher chacun d'eux : voir [Ce que Nexy vous laisse](how-nexy-works.md#what-nexy-leaves-to-you).

<!-- router:fbr -->
L'authentification, par exemple, se connecte à une dépendance du dossier qu'elle protège. Nexy l'exécute avant chaque itinéraire ci-dessous ; qui est l'utilisateur reste votre décision :

```python filename="src/routes/compte/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```
<!-- /router -->

<!-- router:modular -->
L'authentification, par exemple, se connecte à un garde sur le contrôleur qu'elle protège. Nexy l'exécute avant chaque gestionnaire de la classe ; qui est l'utilisateur reste votre décision :

```python filename="src/apps/account_controller.py"
from nexy import unauthorized
from nexy.decorators import Controller, UseGuard
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


@Controller("/account")
@UseGuard(require_login)
class AccountController:
    async def get(self) -> dict:
        return {"ok": True}
```
<!-- /router -->

<!-- router:custom -->
L'authentification, par exemple, se connecte à une dépendance du routeur qu'elle protège, comme dans FastAPI ; qui est l'utilisateur reste votre décision :

```python filename="src/compte.py"
from fastapi import APIRouter, Depends

from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


api = APIRouter(prefix="/account", dependencies=[Depends(require_login)])
```
<!-- /router -->

La raison n'est pas le minimalisme en soi : un framework qui sélectionne votre ORM ou votre bibliothèque d'authentification a décidé quelque chose que seule votre application peut décider.

## Prochaines étapes

- [Structure du projet](project-structure.md) : chaque dossier et fichier d'un projet
- [Glossaire](../reference/glossary.md) : les mêmes mots, dans un index alphabétique
- [Comment fonctionne Nexy](how-nexy-works.md) : les couches, qui construit quoi et ce que Nexy vous laisse
