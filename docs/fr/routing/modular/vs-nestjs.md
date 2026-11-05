# Nexy et NestJS

Le routeur modulaire s'inspire de NestJS : contrôleurs, modules et injection de constructeur. Il s'agit d'une fine couche sur FastAPI, il n'essaie donc pas de reproduire la totalité de NestJS. Cette page répertorie les deux côtés.

## Ce qui correspond

| NestJS | Nexy |
|---|---|
| `@Controller('users')` | `@Controller(prefix="/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` avec les quatre mêmes attributs de classe |
| `@Injectable()` | `@Injectable()` |
| Injection de constructeur | `__init__` paramètres résolus à partir des annotations de type |
| Portées singleton, requêtes et transitoires | `Scope.SINGLETON`, `Scope.REQUEST`, `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (une dépendance FastAPI) |
| `@ApiOperation`, `@ApiResponse` (Swagger) | `@UseRoute`, `@UseResponse` (OpenAPI, servi à `/docs`) |
| WebSocket passerelles | `async def SOCKET(...)` sur un contrôleur |
| Validation DTO (`class-validator`) | Modèles Pydantic, natifs de FastAPI |
| Détection de dépendance circulaire | `RecursionError` nommer la classe |

Le même contrôleur et son service injecté, NestJS d'abord :

```ts filename="utilisateurs.controller.ts"
@Injectable()
export class UsersService {
  findAll() {
    return [{ id: 1, name: "Ada" }];
  }
}

@Controller("users")
export class UsersController {
  constructor(private readonly users: UsersService) {}

  @Get()
  findAll() {
    return this.users.findAll();
  }
}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller, Injectable


@Injectable()
class UserService:
    def find_all(self) -> list[dict]:
        return [{"id": 1, "name": "Ada"}]


@Controller(prefix="/users")
class UserController:
    def __init__(self, users: UserService) -> None:
        self.users = users

    async def get(self) -> list[dict]:
        return self.users.find_all()
```

## Ce qui diffère

- Les gestionnaires sont des méthodes nommées d'après le verbe HTTP (`get`, `post`...), une par contrôleur.
- Les gardes et les décorateurs middleware sont des FastAPI `Depends`, et non des classes avec `canActivate`.
- Les paramètres (`@Body`, `@Param`, `@Query`) sont des paramètres FastAPI : annotations de type, `Query`, `Path`, `Body`.
- Les tuyaux sont des Pydantic validations et des FastAPI dépendances.

`@Query()`, un DTO et une classe de garde deviennent une annotation, un modèle Pydantic et une fonction :

```python filename="src/apps/posts/post_controller.py"
from fastapi import Header, HTTPException, Query
from pydantic import BaseModel
from nexy.decorators import Controller, UseGuard


class NewPost(BaseModel):
    title: str


def require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller(prefix="/posts")
@UseGuard(require_token)
class PostController:
    async def get(self, limit: int = Query(10)) -> list[dict]:
        return []

    async def post(self, body: NewPost) -> dict:
        return {"title": body.title}
```

## Ce qui manque

| NestJS fonctionnalité | Statut à Nexy |
|---|---|
| Fournisseurs personnalisés (`useValue`, `useFactory`, `useClass`, jetons de chaîne) | non disponible : uniquement `@Injectable()` classes |
| Injection par interface ou classe abstraite | non disponible |
| Encapsulation de modules | non appliqué : le conteneur s'applique à l'ensemble du processus, `exports` contrôle uniquement la résolution rapide |
| Modules dynamiques et globaux (`forRoot`, `@Global`) | non disponible |
| Crochets de cycle de vie (`onModuleInit`, `onApplicationShutdown`) | non disponible |
| Intercepteurs | utiliser le middleware ASGI (`useMiddlewares`) ou des dépendances |
| Filtres d'exceptions | utiliser FastAPI gestionnaires d'exceptions |
| Module de test avec remplacements de fournisseur | pas d'API publique ; utilisez FastAPI `dependency_overrides` et `TestClient` |
| Module de configuration, planification, files d'attente, CQRS, microservices, mise en cache | ne fait pas partie de Nexy ; utiliser l'écosystème Python |

À la place d'un fournisseur `useFactory`, une simple fonction derrière `Depends`, qu'un test remplace par `dependency_overrides` :

```python filename="src/apps/reports/report_controller.py"
from fastapi import Depends
from nexy.decorators import Controller


def get_settings() -> dict:
    return {"currency": "EUR"}


@Controller(prefix="/reports")
class ReportController:
    async def get(self, settings: dict = Depends(get_settings)) -> dict:
        return {"currency": settings["currency"]}
```

## Quand le choisir

Choisissez le routeur modulaire lorsque vous souhaitez une structure basée sur les classes avec injection pour une API plus grande. Choisissez le routeur basé sur des fichiers lorsque la structure de l'URL est le principe d'organisation. Les deux sont échafaudés par `nx new`, exécutés sur la même application FastAPI et peuvent coexister.

> [!NOTE]
> les éléments manquants ci-dessus constituent l'écart honnête. Si vous avez besoin de fournisseurs `useFactory` ou de fournisseurs remplaçables dans les tests aujourd'hui, conservez la logique dans les fonctions simples et FastAPI `Depends`, qui composent et remplacent naturellement.

## Prochaines étapes

- [Injection de dépendances](dependency-injection.md)
- [Gardes et métadonnées](guards-and-metadata.md)
- [Tests](../../guides/testing.md)
