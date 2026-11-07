# De NestJS a Nexy

El enrutador modular de Nexy mantiene la forma NestJS (controladores, módulos, servicios inyectables y protectores) en Python, con Pydantic en lugar de las clases DTO y los documentos OpenAPI creados para usted.

Cada sección a continuación muestra un hábito NestJS, luego lo mismo en Nexy. Lo que NestJS tiene y Nexy no aparece en [Nexy y NestJS](../routing/modular/vs-nestjs.md).

## Encendido del enrutador

```ts filename="src/main.ts"
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";

const app = await NestFactory.create(AppModule);
await app.listen(3000);
```

El módulo raíz es un campo de `nexyconfig.py` y `nx dev` le sirve:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

## un controlador

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

El nombre del método es el verbo HTTP:

```python filename="src/apps/cats/cats_controller.py"
from nexy.decorators import Controller


@Controller("/cats")
class CatsController:
    async def get(self) -> list[dict]:
        return [{"name": "Tom"}]
```

Un controlador tiene un controlador por verbo. `GET /cats` y `GET /cats/:id` son ​​dos controladores.

## Parámetros de ruta

```ts filename="src/cats/cat.controller.ts"
@Controller("cats/:id")
export class CatController {
  @Get()
  findOne(@Param("id", ParseIntPipe) id: number) {
    return { id };
  }
}
```

`@Param` y `ParseIntPipe` se convierten en un `{id}` en la ruta y una `int` anotación:

```python filename="src/apps/cats/cat_controller.py"
from nexy.decorators import Controller


@Controller("/cats/{id}")
class CatController:
    async def get(self, id: int) -> dict:
        return {"id": id}
```

## Parámetros de consulta

```ts filename="src/cats/cats.controller.ts"
@Get()
findAll(@Query("limit", new DefaultValuePipe(10), ParseIntPipe) limit: number) {
  return { limit };
}
```

Un parámetro de consulta es un parámetro con un valor predeterminado:

```python filename="src/apps/search/search_controller.py"
from nexy.decorators import Controller


@Controller("/search")
class SearchController:
    async def get(self, q: str = "", limit: int = 10) -> dict:
        return {"q": q, "limit": limit}
```

## DTO y `ValidationPipe`

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

El DTO es un modelo Pydantic. Siempre se valida, y un mal cuerpo responde `422`:

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

## Inyección de proveedores y constructores.

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

Los mismos dos decoradores; la anotación de tipo de `__init__` le dice al contenedor qué inyectar:

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

## Alcances

```ts filename="src/cats/request-context.ts"
@Injectable({ scope: Scope.REQUEST })
export class RequestContext {}
```

```python filename="src/apps/cats/request_context.py"
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class RequestContext: ...
```

`Scope.SINGLETON` es el valor predeterminado, como en NestJS, y `Scope.TRANSIENT` proporciona una nueva instancia por inyección.

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

Las cuatro matrices son cuatro atributos de clase:

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

`@Module(prefix="/api")` antepone cada controlador del módulo, como `RouterModule` o `setGlobalPrefix("api")`.

## guardias

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

Una guardia es una función que se activa cuando la solicitud no puede continuar:

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

## Excepciones

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

Ambos responden `{"detail": ...}` con el código de estado, mientras que NestJS responde `{"message": ...}`.

## Middleware e interceptores

```ts filename="src/logger.middleware.ts"
@Injectable()
export class AppHeaderMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    res.setHeader("X-App", "demo");
    next();
  }
}
```

Una clase de middleware ASGI, enumerada en `nexyconfig.py`, envuelve cada solicitud:

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

Un interceptor que mapea la respuesta es el mismo middleware, con código después de `call_next`.

## arrogancia

```ts
@ApiOperation({ summary: "List cats" })
@ApiResponse({ status: 200 })
@Get()
findAll() {}
```

No hay `SwaggerModule.setup`: cada controlador está en el esquema servido en `/docs`. Los decoradores sólo añaden lo que no dice la firma:

```python filename="src/apps/docs/documented_controller.py"
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller("/documented")
class DocumentedController:
    @UseRoute(summary="List cats", tags=["cats"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

## WebSocket puertas de enlace

```ts filename="src/eventos.gateway.ts"
@WebSocketGateway()
export class EventsGateway {
  @SubscribeMessage("echo")
  echo(@MessageBody() data: string) {
    return data;
  }
}
```

Un método `SOCKET` abre un WebSocket en la ruta de su controlador:

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller("/ws/echo")
class EchoController:
    async def SOCKET(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

Como todo controlador, responde una vez que un módulo lo incluye en `controllers`. La ruta de un controlador termina con una barra diagonal: conectarse a `/ws/echo/`, ya que un WebSocket no se redirige como lo es una solicitud HTTP.

## `ConfigModule`

```ts
@Module({ imports: [ConfigModule.forRoot()] })
export class AppModule {}

constructor(private config: ConfigService) {}
this.config.get("DATABASE_URL");
```

Las configuraciones son un modelo Pydantic o variables de entorno simples, inyectadas como cualquier proveedor:

```python filename="src/aplicaciones/settings.py"
import os

from nexy.decorators import Injectable


@Injectable()
class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## Pruebas

```ts filename="src/cats/cats.controller.spec.ts"
const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
const app = moduleRef.createNestApplication();
await app.init();
await request(app.getHttpServer()).get("/cats").expect(200);
```

```python filename="pruebas/test_cats.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_cats():
    assert TestClient(app).get("/cats").json() == [{"name": "Tom"}]
```

Para reemplazar un servicio en una prueba, dependa de él a través de `Depends` y use el `app.dependency_overrides` de FastAPI: vea [Nexy y NestJS](../routing/modular/vs-nestjs.md#what-is-missing).

## corriendo

| NestJS | nexy |
|---|---|
| `nest new` | `nx new`, luego elija el enrutador modular |
| `npm run start:dev` | `nx dev` |
| `npm run build && npm run start:prod` | `nx build`, luego `nx start` |
| `npm test` | `nx test` |
| `nest generate controller` | un nuevo `*_controller.py`, agregado a su módulo |

<!-- router:fbr,custom -->
## O archivos en lugar de clases.

Una aplicación NestJS que es principalmente CRUD también puede moverse al enrutador basado en archivos, donde la carpeta es la ruta y no hay módulos que mantener sincronizados:

```python filename="src/rutas/cats/[id].py"
async def GET(id: int):
    return {"id": id}
```

<!-- /router -->

Consulte [Elija un enrutador](../routing/README.md).

## Próximos pasos

- [Enrutamiento modular](../routing/modular/README.md)
- [Inyección de dependencia](../routing/modular/dependency-injection.md)
- [Nexy y NestJS](../routing/modular/vs-nestjs.md)
- [De Express a Nexy](../getting-started/coming-from-other-frameworks.md#from-express-or-node-backends)
