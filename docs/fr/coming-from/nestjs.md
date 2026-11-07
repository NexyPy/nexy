# De NestJS à Nexy

Le routeur modulaire de Nexy conserve la forme NestJS - contrôleurs, modules, services injectables et gardes - dans Python, avec Pydantic à la place des classes DTO et les documents OpenAPI construits pour vous.

Chaque section ci-dessous montre une habitude NestJS, puis la même chose dans Nexy. Ce que NestJS a et ce que Nexy n'a pas est répertorié dans [Nexy et NestJS](../routing/modular/vs-nestjs.md).

## Allumer le routeur

```ts filename="src/main.ts"
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";

const app = await NestFactory.create(AppModule);
await app.listen(3000);
```

Le module racine est un champ de `nexyconfig.py`, et `nx dev` le sert :

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

## Un contrôleur

```ts filename="src/cats/cats.controller.ts"
import { Controller, Get } from "@nestjs/common";

@Controller("cats")
export class CatsController {
  @Get()
  findAll() {
    return [{ name: "Tom" }];
  }
}
```

Le nom de la méthode est le verbe HTTP :

```python filename="src/apps/cats/cats_controller.py"
from nexy.decorators import Controller


@Controller("/cats")
class CatsController:
    async def get(self) -> list[dict]:
        return [{"name": "Tom"}]
```

Un contrôleur a un gestionnaire par verbe. `GET /cats` et `GET /cats/:id` sont deux contrôleurs.

## Paramètres d'itinéraire

```ts filename="src/cats/cat.controller.ts"
@Controller("cats/:id")
export class CatController {
  @Get()
  findOne(@Param("id", ParseIntPipe) id: number) {
    return { id };
  }
}
```

`@Param` et `ParseIntPipe` deviennent un `{id}` dans le chemin et une annotation `int` :

```python filename="src/apps/cats/cat_controller.py"
from nexy.decorators import Controller


@Controller("/cats/{id}")
class CatController:
    async def get(self, id: int) -> dict:
        return {"id": id}
```

## Paramètres de requête

```ts filename="src/cats/cats.controller.ts"
@Get()
findAll(@Query("limit", new DefaultValuePipe(10), ParseIntPipe) limit: number) {
  return { limit };
}
```

Un paramètre de requête est un paramètre avec une valeur par défaut :

```python filename="src/apps/search/search_controller.py"
from nexy.decorators import Controller


@Controller("/search")
class SearchController:
    async def get(self, q: str = "", limit: int = 10) -> dict:
        return {"q": q, "limit": limit}
```

## DTO et `ValidationPipe`

```ts filename="src/cats/create-cat.dto.ts"
import { IsInt, IsString, Min } from "class-validator";

export class CreateCatDto {
  @IsString()
  name: string;

  @IsInt()
  @Min(0)
  age: number;
}
```

```ts filename="src/cats/cats.controller.ts"
@Post()
create(@Body() dto: CreateCatDto) {
  return dto;
}
```

Le DTO est un modèle Pydantic. C'est toujours validé, et un mauvais corps répond `422` :

```python filename="src/apps/cats/cats_dto.py"
from pydantic import BaseModel, Field


class CreateCat(BaseModel):
    name: str
    age: int = Field(ge=0)
```

```python filename="src/apps/cats/new_cat_controller.py"
from nexy.decorators import Controller

from .cats_dto import CreateCat


@Controller("/cats/new")
class NewCatController:
    async def post(self, body: CreateCat) -> CreateCat:
        return body
```

## Fournisseurs et injection constructeur

```ts filename="src/cats/cats.service.ts"
@Injectable()
export class CatsService {
  findAll() {
    return [{ name: "Tom" }];
  }
}

@Controller("cats")
export class CatsController {
  constructor(private readonly cats: CatsService) {}

  @Get()
  findAll() {
    return this.cats.findAll();
  }
}
```

Les deux mêmes décorateurs ; l'annotation de type de `__init__` indique au conteneur ce qu'il faut injecter :

```python filename="src/apps/cats/cats_service.py"
from nexy.decorators import Injectable


@Injectable()
class CatsService:
    def find_all(self) -> list[dict]:
        return [{"name": "Tom"}]
```

```python filename="src/apps/cats/cats_controller.py"
from nexy.decorators import Controller

from .cats_service import CatsService


@Controller("/cats")
class CatsController:
    def __init__(self, cats: CatsService) -> None:
        self.cats = cats

    async def get(self) -> list[dict]:
        return self.cats.find_all()
```

## Portées

```ts filename="src/cats/request-context.ts"
@Injectable({ scope: Scope.REQUEST })
export class RequestContext {}
```

```python filename="src/apps/cats/request_context.py"
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class RequestContext: ...
```

`Scope.SINGLETON` est la valeur par défaut, comme dans NestJS, et `Scope.TRANSIENT` donne une nouvelle instance par injection.

## Modules

```ts filename="src/cats/cats.module.ts"
@Module({
  controllers: [CatsController, CatController],
  providers: [CatsService],
  exports: [CatsService],
})
export class CatsModule {}

@Module({ imports: [CatsModule] })
export class AppModule {}
```

Les quatre tableaux sont quatre attributs de classe :

```python filename="src/apps/cats/cats_module.py"
from nexy.decorators import Module

from .cat_controller import CatController
from .cats_controller import CatsController
from .cats_service import CatsService
from .new_cat_controller import NewCatController


@Module()
class CatsModule:
    controllers = [CatsController, CatController, NewCatController]
    providers = [CatsService]
    exports = [CatsService]
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .admin.admin_controller import AdminController
from .cats.cats_module import CatsModule
from .search.search_controller import SearchController


@Module()
class AppModule:
    controllers = [SearchController, AdminController]
    imports = [CatsModule]
```

`@Module(prefix="/api")` préfixe chaque contrôleur du module, comme `RouterModule` ou `setGlobalPrefix("api")`.

## Gardes

```ts filename="src/auth/token.guard.ts"
@Injectable()
export class TokenGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    return request.headers["x-token"] === "secret";
  }
}

@Controller("admin")
@UseGuards(TokenGuard)
export class AdminController {}
```

Une garde est une fonction qui se déclenche lorsque la requête ne peut pas continuer :

```python filename="src/apps/admin/admin_controller.py"
from fastapi import Header, HTTPException

from nexy.decorators import Controller, UseGuard


def require_token(x_token: str = Header("")) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller("/admin")
@UseGuard(require_token)
class AdminController:
    async def get(self) -> dict:
        return {"ok": True}
```

## Exceptions

```ts
throw new NotFoundException("No such cat");
throw new ForbiddenException();
```

```python
from fastapi import HTTPException

from nexy import forbidden

raise HTTPException(status_code=404, detail="No such cat")
forbidden()
```

Les deux répondent à `{"detail": ...}` avec le code d'état, tandis que NestJS répond à `{"message": ...}`.

## Middleware et intercepteurs

```ts filename="src/logger.middleware.ts"
@Injectable()
export class AppHeaderMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    res.setHeader("X-App", "demo");
    next();
  }
}
```

Une classe middleware ASGI, répertoriée dans `nexyconfig.py`, encapsule chaque requête :

```python filename="src/app_header.py"
from starlette.middleware.base import BaseHTTPMiddleware


class AppHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["x-app"] = "demo"
        return response
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.app_header import AppHeaderMiddleware
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    useMiddlewares = [AppHeaderMiddleware]
```

Un intercepteur qui mappe la réponse est le même middleware, avec le code après `call_next`.

## Fanfaronnade

```ts
@ApiOperation({ summary: "List cats" })
@ApiResponse({ status: 200 })
@Get()
findAll() {}
```

Il n'y a pas de `SwaggerModule.setup` : chaque contrôleur est dans le schéma servi dans `/docs`. Les décorateurs ajoutent seulement ce que la signature ne dit pas :

```python filename="src/apps/docs/documented_controller.py"
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller("/documented")
class DocumentedController:
    @UseRoute(summary="List cats", tags=["cats"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

## WebSocket passerelles

```ts filename="src/events.gateway.ts"
@WebSocketGateway()
export class EventsGateway {
  @SubscribeMessage("echo")
  echo(@MessageBody() data: string) {
    return data;
  }
}
```

Une méthode `SOCKET` ouvre un WebSocket sur le chemin de son contrôleur :

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller("/ws/echo")
class EchoController:
    async def SOCKET(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

Comme tout contrôleur, il répond une fois qu'un module le répertorie dans `controllers`. La route d'un contrôleur se termine par un slash : connectez-vous à `/ws/echo/`, puisqu'un WebSocket n'est pas redirigé comme l'est une requête HTTP.

## `ConfigModule`

```ts
@Module({ imports: [ConfigModule.forRoot()] })
export class AppModule {}

constructor(private config: ConfigService) {}
this.config.get("DATABASE_URL");
```

Les paramètres sont un modèle Pydantic ou des variables d'environnement simples, injectées comme n'importe quel fournisseur :

```python filename="src/apps/settings.py"
import os

from nexy.decorators import Injectable


@Injectable()
class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## Essais

```ts filename="src/cats/cats.controller.spec.ts"
const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
const app = moduleRef.createNestApplication();
await app.init();
await request(app.getHttpServer()).get("/cats").expect(200);
```

```python filename="tests/test_cats.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_cats():
    assert TestClient(app).get("/cats").json() == [{"name": "Tom"}]
```

Pour remplacer un service dans un test, dépendez-en via `Depends` et utilisez le `app.dependency_overrides` de FastAPI : voir [Nexy et NestJS](../routing/modular/vs-nestjs.md#what-is-missing).

## Courir

| NestJS | Nexy |
|---|---|
| `nest new` | `nx new`, puis choisissez le routeur modulaire |
| `npm run start:dev` | `nx dev` |
| `npm run build && npm run start:prod` | `nx build`, puis `nx start` |
| `npm test` | `nx test` |
| `nest generate controller` | un nouveau `*_controller.py`, ajouté à son module |

<!-- router:fbr,custom -->
## Ou des fichiers au lieu de classes

Une application NestJS qui est principalement CRUD peut également être déplacée vers le routeur basé sur des fichiers, où le dossier est le chemin et où il n'y a aucun module à synchroniser :

```python filename="src/routes/cats/[id].py"
async def GET(id: int):
    return {"id": id}
```

<!-- /router -->

Voir [Choisir un routeur](../routing/README.md).

## Prochaines étapes

- [Routage modulaire](../routing/modular/README.md)
- [Injection de dépendances](../routing/modular/dependency-injection.md)
- [Nexy et NestJS](../routing/modular/vs-nestjs.md)
- [De l’Express à Nexy](../getting-started/coming-from-other-frameworks.md#from-express-or-node-backends)
