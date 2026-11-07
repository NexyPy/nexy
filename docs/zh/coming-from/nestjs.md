# 从 NestJS 到 Nexy

Nexy 的模块化路由器在 Python 中保留 NestJS 形状 - 控制器、模块、可注入服务和防护，用 Pydantic 代替 DTO 类，并为您构建 OpenAPI 文档。

下面的每个部分都显示了一个 NestJS 习惯，然后 Nexy 中也显示了相同的内容。 NestJS 有而 Nexy 没有的内容列在 [Nexy 和 NestJS](../routing/modular/vs-nestjs.md) 中。

## 打开路由器

```ts filename="src/main.ts"
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";

const app = await NestFactory.create(AppModule);
await app.listen(3000);
```

根模块是 `nexyconfig.py` 的一个字段，`nx dev` 为它服务：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

## 控制器一个

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

方法名称是 HTTP 动词：

```python filename="src/apps/cats/cats_controller.py"
from nexy.decorators import Controller


@Controller("/cats")
class CatsController:
    async def get(self) -> list[dict]:
        return [{"name": "Tom"}]
```

控制器的每个动词都有一个处理程序。 `GET /cats` 和 `GET /cats/:id` 是两个控制器。

## 路由参数

```ts filename="src/cats/cat.controller.ts"
@Controller("cats/:id")
export class CatController {
  @Get()
  findOne(@Param("id", ParseIntPipe) id: number) {
    return { id };
  }
}
```

`@Param` 和 `ParseIntPipe` 成为路径中的 `{id}` 和 `int` 注释：

```python filename="src/apps/cats/cat_controller.py"
from nexy.decorators import Controller


@Controller("/cats/{id}")
class CatController:
    async def get(self, id: int) -> dict:
        return {"id": id}
```

## 查询参数

```ts filename="src/cats/cats.controller.ts"
@Get()
findAll(@Query("limit", new DefaultValuePipe(10), ParseIntPipe) limit: number) {
  return { limit };
}
```

查询参数是具有默认值的参数：

```python filename="src/apps/search/search_controller.py"
from nexy.decorators import Controller


@Controller("/search")
class SearchController:
    async def get(self, q: str = "", limit: int = 10) -> dict:
        return {"q": q, "limit": limit}
```

## DTO 和 `ValidationPipe`

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

DTO 是一个 Pydantic 模型。它总是经过验证的，并且一个坏的身体会回答 `422`：

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

## 提供者和构造函数注入

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

相同的两个装饰器； `__init__` 的类型注释告诉容器要注入什么：

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

## 范围

```ts filename="src/cats/request-context.ts"
@Injectable({ scope: Scope.REQUEST })
export class RequestContext {}
```

```python filename="src/apps/cats/request_context.py"
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class RequestContext: ...
```

`Scope.SINGLETON` 是默认值，如 NestJS 中一样，`Scope.TRANSIENT` 每次注入都会给出一个新实例。

## 模块

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

这四个数组是四个类属性：

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

`@Module(prefix="/api")` 为模块的每个控制器添加前缀，如 `RouterModule` 或 `setGlobalPrefix("api")`。

## 卫兵

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

守卫是一个在请求无法继续时引发的函数：

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

## 例外情况

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

两者都使用状态代码回答 `{"detail": ...}`，正如 NestJS 回答 `{"message": ...}`。

## 中间件和拦截器

```ts filename="src/logger.middleware.ts"
@Injectable()
export class AppHeaderMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    res.setHeader("X-App", "demo");
    next();
  }
}
```

`nexyconfig.py` 中列出的 ASGI 中间件类包装了每个请求：

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

映射响应的拦截器是相同的中间件，代码在 `call_next` 之后。

## 昂首阔步

```ts
@ApiOperation({ summary: "List cats" })
@ApiResponse({ status: 200 })
@Get()
findAll() {}
```

没有 `SwaggerModule.setup`：每个控制器都在 `/docs`服务的模式中。装饰器只添加签名中未提及的内容：

```python filename="src/apps/docs/documented_controller.py"
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller("/documented")
class DocumentedController:
    @UseRoute(summary="List cats", tags=["cats"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

## WebSocket 网关

```ts filename="src/events.gateway.ts"
@WebSocketGateway()
export class EventsGateway {
  @SubscribeMessage("echo")
  echo(@MessageBody() data: string) {
    return data;
  }
}
```

`SOCKET` 方法在其控制器的路径上打开 WebSocket：

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller("/ws/echo")
class EchoController:
    async def SOCKET(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

与每个控制器一样，一旦模块将其列在 `controllers` 中，它就会做出响应。控制器的路由以斜杠结尾：连接到 `/ws/echo/`，因为 WebSocket 不会像 HTTP 请求那样重定向。

## `ConfigModule`

```ts
@Module({ imports: [ConfigModule.forRoot()] })
export class AppModule {}

constructor(private config: ConfigService) {}
this.config.get("DATABASE_URL");
```

设置是 Pydantic 模型或普通环境变量，像任何提供者一样注入：

```python filename="src/apps/settings.py"
import os

from nexy.decorators import Injectable


@Injectable()
class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## 测试

```ts filename="src/cats/cats.controller.spec.ts"
const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
const app = moduleRef.createNestApplication();
await app.init();
await request(app.getHttpServer()).get("/cats").expect(200);
```

```python filename="测试/test_cats.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_cats():
    assert TestClient(app).get("/cats").json() == [{"name": "Tom"}]
```

要替换测试中的服务，请通过 `Depends` 依赖它并使用 FastAPI 的 `app.dependency_overrides`：请参阅 [Nexy 和 NestJS](../routing/modular/vs-nestjs.md#what-is-missing)。

## 跑步

| NestJS | 内克西 |
|---|---|
| `nest new` | `nx new`，然后选择模块化路由器 |
| `npm run start:dev` | `nx dev` |
| `npm run build && npm run start:prod` | `nx build`，然后 `nx start` |
| `npm test` | `nx test` |
| `nest generate controller` | 一个新的 `*_controller.py`，添加到其模块中 |

<!-- router:fbr,custom -->
## 或者用文件代替类

主要是 CRUD 的 NestJS 应用程序也可以移动到基于文件的路由器，其中文件夹是路径，并且没有需要保持同步的模块：

```python filename="src/routes/cats/[id].py"
async def GET(id: int):
    return {"id": id}
```

<!-- /router -->

请参阅[选择路由器](../routing/README.md)。

## 后续步骤

- [模块化路由](../routing/modular/README.md)
- [依赖注入](../routing/modular/dependency-injection.md)
- [尼克西和 NestJS](../routing/modular/vs-nestjs.md)
- [从 Express 到 Nexy](../getting-started/coming-from-other-frameworks.md#from-express-or-node-backends)
