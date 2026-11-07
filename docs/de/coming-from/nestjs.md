# Von NestJS zu Nexy

Der modulare Router von Nexy behält die NestJS-Form – Controller, Module, injizierbare Dienste und Wachen – in Python bei, mit Pydantic anstelle von DTO-Klassen und den für Sie erstellten OpenAPI-Dokumenten.

Jeder Abschnitt unten zeigt eine NestJS-Gewohnheit, dann dasselbe in Nexy. Was NestJS hat und Nexy nicht, ist in [Nexy und NestJS](../routing/modular/vs-nestjs.md) aufgeführt.

## Einschalten des Routers

```ts filename="src/main.ts"
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";

const app = await NestFactory.create(AppModule);
await app.listen(3000);
```

Das Root-Modul ist ein Feld von `nexyconfig.py` und `nx dev` bedient es:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

## Ein Controller

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

Der Methodenname ist das HTTP-Verb:

```python filename="src/apps/cats/cats_controller.py"
from nexy.decorators import Controller


@Controller("/cats")
class CatsController:
    async def get(self) -> list[dict]:
        return [{"name": "Tom"}]
```

Ein Controller verfügt über einen Handler pro Verb. `GET /cats` und `GET /cats/:id` sind zwei Controller.

## Routenparameter

```ts filename="src/cats/cat.controller.ts"
@Controller("cats/:id")
export class CatController {
  @Get()
  findOne(@Param("id", ParseIntPipe) id: number) {
    return { id };
  }
}
```

`@Param` und `ParseIntPipe` werden zu einem `{id}` im Pfad und einer `int`-Anmerkung:

```python filename="src/apps/cats/cat_controller.py"
from nexy.decorators import Controller


@Controller("/cats/{id}")
class CatController:
    async def get(self, id: int) -> dict:
        return {"id": id}
```

## Abfrageparameter

```ts filename="src/cats/cats.controller.ts"
@Get()
findAll(@Query("limit", new DefaultValuePipe(10), ParseIntPipe) limit: number) {
  return { limit };
}
```

Ein Abfrageparameter ist ein Parameter mit einem Standardwert:

```python filename="src/apps/search/search_controller.py"
from nexy.decorators import Controller


@Controller("/search")
class SearchController:
    async def get(self, q: str = "", limit: int = 10) -> dict:
        return {"q": q, "limit": limit}
```

## DTOs und `ValidationPipe`

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

Das DTO ist ein Pydantic Modell. Es wird immer bestätigt und ein schlechter Körper antwortet `422`:

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

## Anbieter und Konstruktorinjektion

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

Die gleichen zwei Dekorateure; Die Typanmerkung von `__init__` teilt dem Container mit, was injiziert werden soll:

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

## Bereiche

```ts filename="src/cats/request-context.ts"
@Injectable({ scope: Scope.REQUEST })
export class RequestContext {}
```

```python filename="src/apps/cats/request_context.py"
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class RequestContext: ...
```

`Scope.SINGLETON` ist die Standardeinstellung, wie in NestJS, und `Scope.TRANSIENT` gibt eine neue Instanz pro Injektion an.

## Module

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

Die vier Arrays sind vier Klassenattribute:

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

`@Module(prefix="/api")` stellt jedem Controller des Moduls ein Präfix voran, wie `RouterModule` oder `setGlobalPrefix("api")`.

## Wachen

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

Ein Guard ist eine Funktion, die ausgelöst wird, wenn die Anfrage möglicherweise nicht ausgeführt wird:

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

## Ausnahmen

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

Beide antworten `{"detail": ...}` mit dem Statuscode, während NestJS auf `{"message": ...}` antwortet.

## Middleware und Abfangjäger

```ts filename="src/logger.middleware.ts"
@Injectable()
export class AppHeaderMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    res.setHeader("X-App", "demo");
    next();
  }
}
```

Eine ASGI-Middleware-Klasse, aufgeführt in `nexyconfig.py`, umschließt jede Anfrage:

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

Ein Interceptor, der die Antwort abbildet, ist dieselbe Middleware, mit Code nach `call_next`.

## Prahlerei

```ts
@ApiOperation({ summary: "List cats" })
@ApiResponse({ status: 200 })
@Get()
findAll() {}
```

Es gibt kein `SwaggerModule.setup`: Jeder Controller befindet sich im Schema, das unter `/docs` bereitgestellt wird. Die Dekorateure fügen nur das hinzu, was in der Signatur nicht steht:

```python filename="src/apps/docs/documented_controller.py"
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller("/documented")
class DocumentedController:
    @UseRoute(summary="List cats", tags=["cats"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

## WebSocket Gateways

```ts filename="src/events.gateway.ts"
@WebSocketGateway()
export class EventsGateway {
  @SubscribeMessage("echo")
  echo(@MessageBody() data: string) {
    return data;
  }
}
```

Eine `SOCKET`-Methode öffnet eine WebSocket auf dem Pfad ihres Controllers:

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller("/ws/echo")
class EchoController:
    async def SOCKET(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

Wie jeder Controller antwortet er, sobald ein Modul ihn in `controllers` auflistet. Die Route eines Controllers endet mit einem Schrägstrich: connect zu `/ws/echo/`, da ein WebSocket nicht wie eine HTTP-Anfrage umgeleitet wird.

## `ConfigModule`

```ts
@Module({ imports: [ConfigModule.forRoot()] })
export class AppModule {}

constructor(private config: ConfigService) {}
this.config.get("DATABASE_URL");
```

Einstellungen sind ein Pydantic-Modell oder einfache Umgebungsvariablen, die wie bei jedem Anbieter eingefügt werden:

```python filename="src/apps/settings.py"
import os

from nexy.decorators import Injectable


@Injectable()
class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## Tests

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

Um einen Dienst in einem Test zu ersetzen, verlassen Sie sich über `Depends` auf ihn und verwenden Sie `app.dependency_overrides` von FastAPI: siehe [Nexy und NestJS](../routing/modular/vs-nestjs.md#what-is-missing).

## Laufen

| NestJS | Nexy |
|---|---|
| `nest new` | `nx new` und wählen Sie dann den modularen Router aus |
| `npm run start:dev` | `nx dev` |
| `npm run build && npm run start:prod` | `nx build`, dann `nx start` |
| `npm test` | `nx test` |
| `nest generate controller` | ein neues `*_controller.py`, das zu seinem Modul hinzugefügt wurde |

<!-- router:fbr,custom -->
## Oder Dateien statt Klassen

Eine NestJS App, die größtenteils CRUD ist, kann auch auf den dateibasierten Router verschoben werden, wo der Ordner der Pfad ist und es keine Module gibt, die synchronisiert werden müssen:

```python filename="src/routes/cats/[id].py"
async def GET(id: int):
    return {"id": id}
```

<!-- /router -->

Siehe [Wählen Sie einen Router](../routing/README.md).

## Nächste Schritte

- [Modulares Routing](../routing/modular/README.md)
- [Abhängigkeitsinjektion](../routing/modular/dependency-injection.md)
- [Nexy und NestJS](../routing/modular/vs-nestjs.md)
- [Von Express zu Nexy](../getting-started/coming-from-other-frameworks.md#from-express-or-node-backends)
