# Routage modulaire

Le routage modulaire utilise des classes avec des décorateurs au lieu de fichiers sous `src/routes/` : les contrôleurs gèrent les requêtes, les modules les regroupent et les fournisseurs sont injectés. Montez le `APIRouter` résultant avec `useRouter` dans `nexyconfig.py`.

**Avant de commencer :** un projet Nexy et une page de travail. Le routeur modulaire remplace celui basé sur des fichiers, alors lisez d'abord [Routage](../README.md) si vous n'avez pas encore choisi de routeur.

| Page | Ce qu'il couvre |
|---|---|
| Cette page | Monter un module, écrire un contrôleur, regrouper des contrôleurs |
| [Injection de dépendances](dependency-injection.md) | `@Injectable`, les scopes, le conteneur |
| [Gardes et métadonnées](guards-and-metadata.md) | `@UseGuard`, `@Middleware`, `@UseRoute`, `@UseResponse` |
| [Nexy et NestJS](vs-nestjs.md) | Ce qui correspond à NestJS et ce qui ne correspond pas |

## Configurer le routeur

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

> [!NOTE]
> Le routage basé sur des fichiers continue de fonctionner. Si `src/routes/` existe, il est numérisé même lorsque `useRouter` est défini.

## Écrire un contrôleur

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
```

Les méthodes sont mises en correspondance par nom, sans tenir compte de la casse : `get`, `post`, `put`, `patch`, `delete`, `options`, `head`, `trace`.

Un contrôleur déclare un gestionnaire par méthode HTTP ; un doublon apparaît au démarrage. Ajoutez un préfixe avec `@Controller(prefix="/users")` - chaque gestionnaire est monté sur `prefix/`. `async def SOCKET(...)` sur un contrôleur enregistre un WebSocket sur le même chemin.

## Regrouper les contrôleurs dans un module

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

`@Module(prefix="/api")` renvoie un `APIRouter`. `controllers` est requis ; `providers`, `imports` et `exports` sont facultatifs. Les modules importés sont montés en tant que sous-routeurs et leurs fournisseurs exportés sont résolus au démarrage.

## Vues depuis un contrôleur

Un contrôleur peut renvoyer une page. `useViews` restitue une vue `.nexy` ; imbriquez-les les uns dans les autres pour les envelopper dans une mise en page :

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller()
class AppController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/app_view.nexy"),
        })
```

Voir [Mise en page](../fbr/layouts/README.md).

## Exemple

Voir `examples/Modular/api/minimal/`.

## Prochaines étapes

- [Injection de dépendances](dependency-injection.md) : services et scopes
- [Gardes et métadonnées](guards-and-metadata.md) : protéger et documenter les itinéraires
- [Routage](../README.md) : le routeur basé sur les fichiers
- [Configuration](../../reference/config.md) : toutes les options, y compris `useRouter`
