# Injection de dépendances

Nexy résout les dépendances du constructeur pour les contrôleurs et les services. Une classe s'inscrit avec `@Injectable()`.

## Injecter un service

```python filename="src/apps/users/user_service.py"
from nexy.decorators import Injectable


@Injectable()
class UserService:
    def get_all(self) -> list[dict]:
        return [{"id": 1, "name": "Ada"}]
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller
from .user_service import UserService


@Controller(prefix="/users")
class UserController:
    def __init__(self, svc: UserService) -> None:
        self.svc = svc

    def get(self) -> list[dict]:
        return self.svc.get_all()
```

Enregistrez le contrôleur dans un module. La liste du service dans `providers` le résout également rapidement au démarrage :

```python filename="src/apps/users/users_module.py"
from nexy.decorators import Module
from .user_controller import UserController
from .user_service import UserService


@Module()
class UsersModule:
    controllers = [UserController]
    providers = [UserService]
```

## Comment fonctionne la résolution

- Chaque paramètre `__init__` est résolu à partir de son **annotation de type**. L'annotation doit être une classe `@Injectable()`, ou le paramètre doit avoir une valeur par défaut ; sinon la résolution augmente `ValueError`.
- Les contrôleurs sont instanciés avec `Container.resolve()` au démarrage.
- Un cycle de dépendance génère `RecursionError` en nommant la classe.
- Les services peuvent injecter d’autres services, à n’importe quelle profondeur.

## Portées

```python
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class CurrentUser: ...
```

| Portée | Durée de vie |
|---|---|
| `Scope.SINGLETON` (par défaut) | une instance pour l'ensemble du processus |
| `Scope.REQUEST` | une instance par contexte de requête |
| `Scope.TRANSIENT` | une nouvelle instance à chaque résolution |

## Le conteneur

```python
from nexy.decorators import Container

service = Container.resolve(UserService)
```

Construire soi-même une classe `@Injectable()` génère `TypeError` : le conteneur est propriétaire de son cycle de vie. Utilisez `Container.resolve(...)` ou recevez la classe via un autre constructeur.

`Container.clear_request_scope()` supprime les instances de la requête actuelle.

## Paramètres d'itinéraire

FastAPI `Depends` fonctionne comme d'habitude pour les paramètres du gestionnaire, à côté de l'injection du constructeur :

```python
from fastapi import Depends


def get(self, limit: int = Depends(pagination)) -> list[dict]: ...
```

## Limites

Le conteneur s'étend à l'ensemble du processus. Les fournisseurs ne sont pas isolés par module, `exports` décide uniquement quels fournisseurs un module d'importation résout avec impatience, et il n'y a pas d'API publique pour échanger un fournisseur dans les tests. Voir [Nexy et NestJS](vs-nestjs.md) pour la comparaison complète.

## Prochaines étapes

- [Gardes et métadonnées](guards-and-metadata.md)
- [Tests](../../guides/testing.md)
