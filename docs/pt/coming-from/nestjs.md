# De NestJS para Nexy

O roteador modular da Nexy mantém a forma NestJS - controladores, módulos, serviços injetáveis e guardas - em Python, com Pydantic no lugar das classes DTO e os OpenAPI documentos construídos para você.

Cada seção abaixo mostra um hábito NestJS, então a mesma coisa no Nexy. O que NestJS tem e Nexy não está listado em [Nexy e NestJS](../routing/modular/vs-nestjs.md).

## Ligando o roteador

```ts filename="src/main.ts"
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";

const app = await NestFactory.create(AppModule);
await app.listen(3000);
```

O módulo raiz é um campo de `nexyconfig.py` e `nx dev` o atende:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

## Um controlador

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

O nome do método é o verbo HTTP:

```python filename="src/apps/cats/cats_controller.py"
from nexy.decorators import Controller


@Controller(prefix="/cats")
class CatsController:
    async def get(self) -> list[dict]:
        return [{"name": "Tom"}]
```

Um controlador possui um manipulador por verbo. `GET /cats` e `GET /cats/:id` são dois controladores.

## Parâmetros de rota

```ts filename="src/cats/cat.controller.ts"
@Controller("cats/:id")
export class CatController {
  @Get()
  findOne(@Param("id", ParseIntPipe) id: number) {
    return { id };
  }
}
```

`@Param` e `ParseIntPipe` tornam-se um `{id}` no prefixo e uma anotação `int`:

```python filename="src/apps/cats/cat_controller.py"
from nexy.decorators import Controller


@Controller(prefix="/cats/{id}")
class CatController:
    async def get(self, id: int) -> dict:
        return {"id": id}
```

## Parâmetros de consulta

```ts filename="src/cats/cats.controller.ts"
@Get()
findAll(@Query("limit", new DefaultValuePipe(10), ParseIntPipe) limit: number) {
  return { limit };
}
```

Um parâmetro de consulta é um parâmetro com um padrão:

```python filename="src/apps/search/search_controller.py"
from nexy.decorators import Controller


@Controller(prefix="/search")
class SearchController:
    async def get(self, q: str = "", limit: int = 10) -> dict:
        return {"q": q, "limit": limit}
```

## DTOs e `ValidationPipe`

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

O DTO é um modelo Pydantic. É sempre validado, e um corpo ruim responde `422`:

```python filename="src/apps/cats/cats_dto.py"
from pydantic import BaseModel, Field


class CreateCat(BaseModel):
    name: str
    age: int = Field(ge=0)
```

```python filename="src/apps/cats/new_cat_controller.py"
from nexy.decorators import Controller

from .cats_dto import CreateCat


@Controller(prefix="/cats/new")
class NewCatController:
    async def post(self, body: CreateCat) -> CreateCat:
        return body
```

## Provedores e injeção de construtor

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

Os mesmos dois decoradores; a anotação de tipo de `__init__` informa ao contêiner o que injetar:

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


@Controller(prefix="/cats")
class CatsController:
    def __init__(self, cats: CatsService) -> None:
        self.cats = cats

    async def get(self) -> list[dict]:
        return self.cats.find_all()
```

## Escopos

```ts filename="src/cats/request-context.ts"
@Injectable({ scope: Scope.REQUEST })
export class RequestContext {}
```

```python filename="src/apps/cats/request_context.py"
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class RequestContext: ...
```

`Scope.SINGLETON` é o padrão, como em NestJS, e `Scope.TRANSIENT` fornece uma nova instância por injeção.

## Módulos

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

As quatro matrizes são quatro atributos de classe:

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

`@Module(prefix="/api")` prefixa todos os controladores do módulo, como `RouterModule` ou `setGlobalPrefix("api")`.

## Guardas

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

Um guarda é uma função que surge quando a solicitação não pode continuar:

```python filename="src/apps/admin/admin_controller.py"
from fastapi import Header, HTTPException

from nexy.decorators import Controller, UseGuard


def require_token(x_token: str = Header("")) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller(prefix="/admin")
@UseGuard(require_token)
class AdminController:
    async def get(self) -> dict:
        return {"ok": True}
```

## Exceções

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

Ambos respondem `{"detail": ...}` com o código de status, assim como NestJS responde `{"message": ...}`.

## Middleware e interceptadores

```ts filename="src/logger.middleware.ts"
@Injectable()
export class AppHeaderMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    res.setHeader("X-App", "demo");
    next();
  }
}
```

Uma classe de middleware ASGI, listada em `nexyconfig.py`, agrupa todas as solicitações:

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

Um interceptor que mapeia a resposta é o mesmo middleware, com código após `call_next`.

## Arrogância

```ts
@ApiOperation({ summary: "List cats" })
@ApiResponse({ status: 200 })
@Get()
findAll() {}
```

Não há `SwaggerModule.setup`: todo controlador está no esquema servido em `/docs`. Os decoradores apenas acrescentam o que a assinatura não diz:

```python filename="src/apps/docs/documented_controller.py"
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller(prefix="/documented")
class DocumentedController:
    @UseRoute(summary="List cats", tags=["cats"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

## WebSocket portais

```ts filename="src/events.gateway.ts"
@WebSocketGateway()
export class EventsGateway {
  @SubscribeMessage("echo")
  echo(@MessageBody() data: string) {
    return data;
  }
}
```

Um método `SOCKET` abre um WebSocket no caminho de seu controlador:

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller(prefix="/ws/echo")
class EchoController:
    async def SOCKET(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

Como todo controlador, ele responde quando um módulo o lista em `controllers`. A rota de um controlador termina com uma barra: conecte-se a `/ws/echo/`, já que um WebSocket não é redirecionado da mesma forma que uma solicitação HTTP.

## `ConfigModule`

```ts
@Module({ imports: [ConfigModule.forRoot()] })
export class AppModule {}

constructor(private config: ConfigService) {}
this.config.get("DATABASE_URL");
```

As configurações são um modelo Pydantic ou variáveis de ambiente simples, injetadas como qualquer provedor:

```python filename="src/apps/settings.py"
import os

from nexy.decorators import Injectable


@Injectable()
class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## Testes

```ts filename="src/cats/cats.controller.spec.ts"
const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
const app = moduleRef.createNestApplication();
await app.init();
await request(app.getHttpServer()).get("/cats").expect(200);
```

```python filename="testes/test_cats.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_cats():
    assert TestClient(app).get("/cats").json() == [{"name": "Tom"}]
```

Para substituir um serviço em um teste, dependa dele através de `Depends` e use FastAPI de `app.dependency_overrides`: veja [Nexy e NestJS](../routing/modular/vs-nestjs.md#what-is-missing).

## Correndo

| NestJS | Nexy |
|---|---|
| `nest new` | `nx new`, então escolha o roteador modular |
| `npm run start:dev` | `nx dev` |
| `npm run build && npm run start:prod` | `nx build`, então `nx start` |
| `npm test` | `nx test` |
| `nest generate controller` | um novo `*_controller.py`, adicionado ao seu módulo |

## Ou arquivos em vez de classes

Um aplicativo NestJS que é principalmente CRUD também pode ser movido para o roteador baseado em arquivo, onde a pasta é o prefixo e não há módulos para manter sincronizados:

```python filename="src/rotas/cats/[id].py"
async def GET(id: int):
    return {"id": id}
```

Consulte [Escolha um roteador](../routing/README.md).

## Próximas etapas

- [Roteamento modular](../routing/modular/README.md)
- [Injeção de dependência](../routing/modular/dependency-injection.md)
- [Nexy e NestJS](../routing/modular/vs-nestjs.md)
- [Do Expresso ao Nexy](../getting-started/coming-from-other-frameworks.md#from-express-or-node-backends)
