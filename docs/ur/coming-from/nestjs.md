# NestJS سے Nexy تک

Nexy کا ماڈیولر راؤٹر NestJS کی شکل - کنٹرولرز، ماڈیولز، انجیکشن ایبل سروسز اور گارڈز کو Python میں رکھتا ہے، Pydantic کے ساتھ DTO کلاسز کی جگہ اور آپ کے لیے بنائے گئے OpenAPI دستاویزات۔

ذیل میں ہر سیکشن ایک NestJS عادت دکھاتا ہے، پھر Nexy میں وہی چیز۔ کیا NestJS کے پاس ہے اور Nexy میں کیا نہیں ہے وہ [Nexy اور NestJS](../routing/modular/vs-nestjs.md) میں درج ہے۔

## راؤٹر آن کر رہا ہے۔

```ts filename="src/main.ts"
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";

const app = await NestFactory.create(AppModule);
await app.listen(3000);
```

روٹ ماڈیول `nexyconfig.py` کا ایک فیلڈ ہے، اور `nx dev` اس کی خدمت کرتا ہے:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

## ایک کنٹرولر

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

طریقہ کار کا نام HTTP فعل ہے:

```python filename="src/apps/cats/cats_controller.py"
from nexy.decorators import Controller


@Controller("/cats")
class CatsController:
    async def get(self) -> list[dict]:
        return [{"name": "Tom"}]
```

ایک کنٹرولر کے پاس فی فعل ایک ہینڈلر ہوتا ہے۔ `GET /cats` اور `GET /cats/:id` دو کنٹرولر ہیں۔

## روٹ کے پیرامیٹرز

```ts filename="src/cats/cat.controller.ts"
@Controller("cats/:id")
export class CatController {
  @Get()
  findOne(@Param("id", ParseIntPipe) id: number) {
    return { id };
  }
}
```

`@Param` اور `ParseIntPipe` راستے میں ایک `{id}` بن جاتے ہیں اور ایک `int` تشریح:

```python filename="src/apps/cats/cat_controller.py"
from nexy.decorators import Controller


@Controller("/cats/{id}")
class CatController:
    async def get(self, id: int) -> dict:
        return {"id": id}
```

## استفسار کے پیرامیٹرز

```ts filename="src/cats/cats.controller.ts"
@Get()
findAll(@Query("limit", new DefaultValuePipe(10), ParseIntPipe) limit: number) {
  return { limit };
}
```

ایک استفسار پیرامیٹر ایک ڈیفالٹ کے ساتھ ایک پیرامیٹر ہے:

```python filename="src/apps/search/search_controller.py"
from nexy.decorators import Controller


@Controller("/search")
class SearchController:
    async def get(self, q: str = "", limit: int = 10) -> dict:
        return {"q": q, "limit": limit}
```

## ڈی ٹی اوز اور `ValidationPipe`

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

ڈی ٹی او ایک Pydantic ماڈل ہے۔ اس کی توثیق ہمیشہ کی جاتی ہے، اور خراب جسم جواب دیتا ہے `422`:

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

## فراہم کنندہ اور کنسٹرکٹر انجیکشن

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

وہی دو ڈیکوریٹر؛ `__init__` کی قسم کی تشریح کنٹینر کو بتاتی ہے کہ کیا انجیکشن لگانا ہے:

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

## دائرہ کار

```ts filename="src/cats/request-context.ts"
@Injectable({ scope: Scope.REQUEST })
export class RequestContext {}
```

```python filename="src/apps/cats/request_context.py"
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class RequestContext: ...
```

`Scope.SINGLETON` پہلے سے طے شدہ ہے، جیسا کہ NestJS میں ہے، اور `Scope.TRANSIENT` فی انجیکشن ایک نئی مثال دیتا ہے۔

## ماڈیولز

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

چار صفیں چار طبقاتی صفات ہیں:

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

`@Module(prefix="/api")` ماڈیول کے ہر کنٹرولر کا سابقہ لگاتا ہے، جیسے `RouterModule` یا `setGlobalPrefix("api")`۔

## گارڈز

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

گارڈ ایک ایسا فنکشن ہے جو اس وقت اٹھاتا ہے جب درخواست جاری نہ ہو:

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

## مستثنیات

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

دونوں جوابات اسٹیٹس کوڈ کے ساتھ `{"detail": ...}` دیتے ہیں، جیسا کہ NestJS جوابات `{"message": ...}`۔

## مڈل ویئر اور انٹرسیپٹرز

```ts filename="src/logger.middleware.ts"
@Injectable()
export class AppHeaderMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    res.setHeader("X-App", "demo");
    next();
  }
}
```

ASGI مڈل ویئر کلاس، جو `nexyconfig.py` میں درج ہے، ہر درخواست کو سمیٹتی ہے:

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

ایک انٹرسیپٹر جو ردعمل کا نقشہ بناتا ہے وہی مڈل ویئر ہے، `call_next` کے بعد کوڈ کے ساتھ۔

## اکڑ

```ts
@ApiOperation({ summary: "List cats" })
@ApiResponse({ status: 200 })
@Get()
findAll() {}
```

کوئی `SwaggerModule.setup` نہیں ہے: ہر کنٹرولر `/docs` پر پیش کردہ اسکیما میں ہے۔ ڈیکوریٹر صرف وہی شامل کرتے ہیں جو دستخط نہیں کہتے ہیں:

```python filename="src/apps/docs/documented_controller.py"
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller("/documented")
class DocumentedController:
    @UseRoute(summary="List cats", tags=["cats"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

## WebSocket گیٹ ویز

```ts filename="src/events.gateway.ts"
@WebSocketGateway()
export class EventsGateway {
  @SubscribeMessage("echo")
  echo(@MessageBody() data: string) {
    return data;
  }
}
```

ایک `SOCKET` طریقہ اپنے کنٹرولر کے راستے پر ایک WebSocket کو کھولتا ہے:

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller("/ws/echo")
class EchoController:
    async def SOCKET(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

ہر کنٹرولر کی طرح، یہ ایک بار جواب دیتا ہے جب ماڈیول اسے `controllers` میں درج کرتا ہے۔ کنٹرولر کا راستہ سلیش کے ساتھ ختم ہوتا ہے: `/ws/echo/` سے جڑیں، کیونکہ WebSocket کو HTTP درخواست کی طرح ری ڈائریکٹ نہیں کیا جاتا ہے۔

## `ConfigModule`

```ts
@Module({ imports: [ConfigModule.forRoot()] })
export class AppModule {}

constructor(private config: ConfigService) {}
this.config.get("DATABASE_URL");
```

سیٹنگز ایک Pydantic ماڈل یا سادہ ماحول کے متغیرات ہیں، کسی بھی فراہم کنندہ کی طرح انجیکشن:

```python filename="src/apps/settings.py"
import os

from nexy.decorators import Injectable


@Injectable()
class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## ٹیسٹ

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

کسی سروس کو ٹیسٹ میں تبدیل کرنے کے لیے، `Depends` کے ذریعے اس پر انحصار کریں اور FastAPI کے `app.dependency_overrides` کا استعمال کریں: دیکھیں [Nexy اور NestJS](../routing/modular/vs-nestjs.md#what-is-missing)۔

## چل رہا ہے۔

| NestJS | نیکسی |
|---|---|
| `nest new` | `nx new`، پھر ماڈیولر راؤٹر چنیں۔ |
| `npm run start:dev` | `nx dev` |
| `npm run build && npm run start:prod` | `nx build`، پھر `nx start` |
| `npm test` | `nx test` |
| `nest generate controller` | ایک نیا `*_controller.py`، اس کے ماڈیول میں شامل کیا گیا۔ |

## یا کلاسز کے بجائے فائلز

ایک NestJS ایپ جو زیادہ تر CRUD ہے فائل پر مبنی روٹر میں بھی جا سکتی ہے، جہاں فولڈر ہی راستہ ہے اور مطابقت پذیر رکھنے کے لیے کوئی ماڈیول نہیں ہیں:

```python filename="src/routes/cats/[id].py"
async def GET(id: int):
    return {"id": id}
```

دیکھیں [روٹر کا انتخاب کریں](../routing/README.md)۔

## اگلے اقدامات

- [ماڈیولر روٹنگ ](../routing/modular/README.md)
- [انحصار انجکشن](../routing/modular/dependency-injection.md)
- [Nexy اور NestJS](../routing/modular/vs-nestjs.md)
- [ایکسپریس سے Nexy تک](../getting-started/coming-from-other-frameworks.md#from-express-or-node-backends)
