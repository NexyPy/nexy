# من NestJS إلى النكسي

يحافظ جهاز التوجيه المعياري الخاص بـ Nexy على الشكل NestJS - وحدات التحكم والوحدات النمطية والخدمات القابلة للحقن والحراس - في Python، مع Pydantic بدلاً من فئات DTO والمستندات OpenAPI المصممة خصيصًا لك.

كل قسم أدناه يوضح عادة NestJS، ثم نفس الشيء في Nexy. ما يحتويه NestJS وما لا يحتوي عليه Nexy مدرج في [Nexy و NestJS](../routing/modular/vs-nestjs.md).

## تشغيل جهاز التوجيه

```ts filename="src/main.ts"
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";

const app = await NestFactory.create(AppModule);
await app.listen(3000);
```

الوحدة الجذرية هي حقل `nexyconfig.py`، و `nx dev` تخدمه:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

## وحدة تحكم

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

اسم الطريقة هو فعل HTTP:

```python filename="src/apps/cats/cats_controller.py"
from nexy.decorators import Controller


@Controller("/cats")
class CatsController:
    async def get(self) -> list[dict]:
        return [{"name": "Tom"}]
```

وحدة التحكم لديها معالج واحد لكل فعل. `GET /cats` و `GET /cats/:id` هما متحكمان.

## معلمات الطريق

```ts filename="src/cats/cat.controller.ts"
@Controller("cats/:id")
export class CatController {
  @Get()
  findOne(@Param("id", ParseIntPipe) id: number) {
    return { id };
  }
}
```

`@Param` و `ParseIntPipe` تصبح `{id}` في المسار وتعليق `int`:

```python filename="src/apps/cats/cat_controller.py"
from nexy.decorators import Controller


@Controller("/cats/{id}")
class CatController:
    async def get(self, id: int) -> dict:
        return {"id": id}
```

## معلمات الاستعلام

```ts filename="src/cats/cats.controller.ts"
@Get()
findAll(@Query("limit", new DefaultValuePipe(10), ParseIntPipe) limit: number) {
  return { limit };
}
```

معلمة الاستعلام هي معلمة ذات قيمة افتراضية:

```python filename="src/apps/search/search_controller.py"
from nexy.decorators import Controller


@Controller("/search")
class SearchController:
    async def get(self, q: str = "", limit: int = 10) -> dict:
        return {"q": q, "limit": limit}
```

## DTOs و `ValidationPipe`

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

إن DTO هو نموذج Pydantic . يتم التحقق من صحته دائمًا، ويجيب الجسم السيئ `422`:

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

## مقدمي وحقن المنشئ

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

نفس الديكورين؛ يوضح التعليق التوضيحي للنوع `__init__` الحاوية ما يجب حقنه:

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

## النطاقات

```ts filename="src/cats/request-context.ts"
@Injectable({ scope: Scope.REQUEST })
export class RequestContext {}
```

```python filename="src/apps/cats/request_context.py"
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class RequestContext: ...
```

`Scope.SINGLETON` هو الإعداد الافتراضي، كما في NestJS، و `Scope.TRANSIENT` يعطي مثيلًا جديدًا لكل حقنة.

## وحدات

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

المصفوفات الأربع هي أربع سمات فئة:

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

`@Module(prefix="/api")` تسبق كل وحدة تحكم في الوحدة، مثل `RouterModule` أو `setGlobalPrefix("api")`.

## حراس

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

الحارس عبارة عن وظيفة يتم رفعها عندما لا يستمر الطلب:

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

## الاستثناءات

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

كلاهما يجيب `{"detail": ...}` برمز الحالة، كما يجيب NestJS `{"message": ...}`.

## الوسيطة والمعترضات

```ts filename="src/logger.middleware.ts"
@Injectable()
export class AppHeaderMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    res.setHeader("X-App", "demo");
    next();
  }
}
```

فئة البرمجيات الوسيطة ASGI، المدرجة في `nexyconfig.py`، تغطي كل طلب:

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

إن المعترض الذي يعين الاستجابة هو نفس البرنامج الوسيط، مع رمز بعد `call_next`.

## اختيال

```ts
@ApiOperation({ summary: "List cats" })
@ApiResponse({ status: 200 })
@Get()
findAll() {}
```

لا يوجد `SwaggerModule.setup`: كل وحدة تحكم موجودة في المخطط المقدم في `/docs`. يضيف المصممون فقط ما لا يقوله التوقيع:

```python filename="src/apps/docs/documented_controller.py"
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller("/documented")
class DocumentedController:
    @UseRoute(summary="List cats", tags=["cats"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

## WebSocket البوابات

```ts filename="src/events.gateway.ts"
@WebSocketGateway()
export class EventsGateway {
  @SubscribeMessage("echo")
  echo(@MessageBody() data: string) {
    return data;
  }
}
```

تفتح الطريقة `SOCKET` WebSocket على مسار وحدة التحكم الخاصة بها:

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller("/ws/echo")
class EchoController:
    async def SOCKET(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

مثل كل وحدة تحكم، فإنها تجيب بمجرد إدراجها في الوحدة النمطية في `controllers`. ينتهي مسار وحدة التحكم بشرطة مائلة: اتصل بـ `/ws/echo/`، حيث لا تتم إعادة توجيه WebSocket بالطريقة التي تتم بها طلبات HTTP.

## `ConfigModule`

```ts
@Module({ imports: [ConfigModule.forRoot()] })
export class AppModule {}

constructor(private config: ConfigService) {}
this.config.get("DATABASE_URL");
```

الإعدادات هي نموذج Pydantic أو متغيرات بيئة عادية، يتم إدخالها مثل أي مزود:

```python filename="src/apps/settings.py"
import os

from nexy.decorators import Injectable


@Injectable()
class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## الاختبارات

```ts filename="src/cats/cats.controller.spec.ts"
const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
const app = moduleRef.createNestApplication();
await app.init();
await request(app.getHttpServer()).get("/cats").expect(200);
```

```python filename="الاختبارات/test_cats.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_cats():
    assert TestClient(app).get("/cats").json() == [{"name": "Tom"}]
```

لاستبدال خدمة في اختبار، اعتمد عليها من خلال `Depends` واستخدم FastAPI الخاص بـ `app.dependency_overrides`: راجع [[Nexy و NestJS ](../routing/modular/vs-nestjs.md#what-is-missing).

## الجري

| NestJS | نكسي |
|---|---|
| `nest new` | `nx new`، ثم اختر جهاز التوجيه المعياري |
| `npm run start:dev` | `nx dev` |
| `npm run build && npm run start:prod` | `nx build`، ثم `nx start` |
| `npm test` | `nx test` |
| `nest generate controller` | `*_controller.py` جديد، يضاف إلى وحدته |

## أو الملفات بدلا من الطبقات

يمكن أيضًا أن ينتقل تطبيق NestJS الذي يكون في الغالب CRUD إلى جهاز التوجيه المستند إلى الملف، حيث يكون المجلد هو المسار ولا توجد وحدات نمطية للحفاظ على مزامنتها:

```python filename="src/routes/cats/[id].py"
async def GET(id: int):
    return {"id": id}
```

انظر [اختيار جهاز توجيه](../routing/README.md).

## الخطوات التالية

- [التوجيه المعياري](../routing/modular/README.md)
- [حقن التبعية](../routing/modular/dependency-injection.md)
- [نكسي و NestJS](../routing/modular/vs-nestjs.md)
- [من إكسبريس إلى نيكسي](../getting-started/coming-from-other-frameworks.md#from-express-or-node-backends)
