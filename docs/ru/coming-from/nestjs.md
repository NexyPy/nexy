# От NestJS до Некси

Модульный маршрутизатор Nexy сохраняет форму NestJS - контроллеры, модули, внедряемые сервисы и средства защиты - в Python, с Pydantic вместо классов DTO и документацией OpenAPI, созданной для вас.

В каждом разделе ниже показана привычка NestJS, затем то же самое в Nexy. То, что есть в NestJS и чего нет в Nexy, перечислено в [Nexy и NestJS](../routing/modular/vs-nestjs.md).

## Включение маршрутизатора

```ts filename="источник/main.ts"
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";

const app = await NestFactory.create(AppModule);
await app.listen(3000);
```

Корневой модуль - это поле `nexyconfig.py`, а `nx dev` обслуживает его:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

## Контроллер

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

Имя метода - это HTTP-глагол:

```python filename="src/apps/cats/cats_controller.py"
from nexy.decorators import Controller


@Controller("/cats")
class CatsController:
    async def get(self) -> list[dict]:
        return [{"name": "Tom"}]
```

Контроллер имеет один обработчик для каждого глагола. `GET /cats` и `GET /cats/:id` - два контроллера.

## Параметры маршрута

```ts filename="src/cats/cat.controller.ts"
@Controller("cats/:id")
export class CatController {
  @Get()
  findOne(@Param("id", ParseIntPipe) id: number) {
    return { id };
  }
}
```

`@Param` и `ParseIntPipe` становятся `{id}` в пути и аннотацией `int`:

```python filename="src/apps/cats/cat_controller.py"
from nexy.decorators import Controller


@Controller("/cats/{id}")
class CatController:
    async def get(self, id: int) -> dict:
        return {"id": id}
```

## Параметры запроса

```ts filename="src/cats/cats.controller.ts"
@Get()
findAll(@Query("limit", new DefaultValuePipe(10), ParseIntPipe) limit: number) {
  return { limit };
}
```

Параметр запроса - это параметр со значением по умолчанию:

```python filename="src/apps/search/search_controller.py"
from nexy.decorators import Controller


@Controller("/search")
class SearchController:
    async def get(self, q: str = "", limit: int = 10) -> dict:
        return {"q": q, "limit": limit}
```

## DTO и `ValidationPipe`

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

DTO - это модель Pydantic. Оно всегда проверяется, и плохое тело отвечает `422`:

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

## Провайдеры и внедрение конструктора

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

Те же два декоратора; аннотация типа `__init__` сообщает контейнеру, что нужно внедрить:

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

## Области применения

```ts filename="src/cats/request-context.ts"
@Injectable({ scope: Scope.REQUEST })
export class RequestContext {}
```

```python filename="src/apps/cats/request_context.py"
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class RequestContext: ...
```

`Scope.SINGLETON` используется по умолчанию, как и в NestJS, а `Scope.TRANSIENT` создает новый экземпляр для каждой инъекции.

## Модули

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

Четыре массива представляют собой четыре атрибута класса:

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

`@Module(prefix="/api")` ставится перед каждым контроллером модуля, например `RouterModule` или `setGlobalPrefix("api")`.

## Охранники

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

Guard - это функция, которая вызывается, когда запрос не может быть выполнен:

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

## Исключения

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

Оба отвечают `{"detail": ...}` кодом состояния, а NestJS отвечает `{"message": ...}`.

## Промежуточное программное обеспечение и перехватчики

```ts filename="src/logger.middleware.ts"
@Injectable()
export class AppHeaderMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    res.setHeader("X-App", "demo");
    next();
  }
}
```

Класс промежуточного программного обеспечения ASGI, указанный в `nexyconfig.py`, оборачивает каждый запрос:

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

Перехватчик, отображающий ответ, представляет собой то же промежуточное программное обеспечение с кодом после `call_next`.

## Сваггер

```ts
@ApiOperation({ summary: "List cats" })
@ApiResponse({ status: 200 })
@Get()
findAll() {}
```

`SwaggerModule.setup` нет: каждый контроллер находится в схеме, обслуживаемой в `/docs`. Декораторы лишь добавляют то, о чем не сказано в подписи:

```python filename="src/apps/docs/documented_controller.py"
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller("/documented")
class DocumentedController:
    @UseRoute(summary="List cats", tags=["cats"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

## WebSocket шлюзы

```ts filename="src/events.gateway.ts"
@WebSocketGateway()
export class EventsGateway {
  @SubscribeMessage("echo")
  echo(@MessageBody() data: string) {
    return data;
  }
}
```

Метод `SOCKET` открывает WebSocket на пути своего контроллера:

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller("/ws/echo")
class EchoController:
    async def SOCKET(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

Как и любой контроллер, он отвечает, как только модуль указывает его в `controllers`. Маршрут контроллера заканчивается косой чертой: подключиться к `/ws/echo/`, поскольку WebSocket не перенаправляется так, как HTTP-запрос.

## `ConfigModule`

```ts
@Module({ imports: [ConfigModule.forRoot()] })
export class AppModule {}

constructor(private config: ConfigService) {}
this.config.get("DATABASE_URL");
```

Настройки - это модель Pydantic или простые переменные среды, внедряемые как любой провайдер:

```python filename="src/apps/settings.py"
import os

from nexy.decorators import Injectable


@Injectable()
class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## Тесты

```ts filename="src/cats/cats.controller.spec.ts"
const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
const app = moduleRef.createNestApplication();
await app.init();
await request(app.getHttpServer()).get("/cats").expect(200);
```

```python filename="тесты/test_cats.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_cats():
    assert TestClient(app).get("/cats").json() == [{"name": "Tom"}]
```

Чтобы заменить сервис в тесте, положитесь на него через `Depends` и используйте FastAPI из `app.dependency_overrides`: см. [Nexy и NestJS](../routing/modular/vs-nestjs.md#what-is-missing).

## Бег

| NestJS | Некси |
|---|---|
| `nest new` | `nx new`, затем выберите модульный маршрутизатор |
| `npm run start:dev` | `nx dev` |
| `npm run build && npm run start:prod` | `nx build`, затем `nx start` |
| `npm test` | `nx test` |
| `nest generate controller` | новый `*_controller.py`, добавленный в его модуль |

<!-- router:fbr,custom -->
## Или файлы вместо классов

Приложение NestJS, которое в основном представляет собой CRUD, также может перейти на файловый маршрутизатор, где папка является путем и нет модулей для синхронизации:

```python filename="src/routes/cats/[id].py"
async def GET(id: int):
    return {"id": id}
```

<!-- /router -->

См. [Выбор маршрутизатора](../routing/README.md).

## Следующие шаги

- [Модульная маршрутизация](../routing/modular/README.md)
- [Внедрение зависимостей](../routing/modular/dependency-injection.md)
- [Некси и NestJS](../routing/modular/vs-nestjs.md)
- [От Экспресса до Некси](../getting-started/coming-from-other-frameworks.md#from-express-or-node-backends)
