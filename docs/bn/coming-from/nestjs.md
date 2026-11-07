# NestJS থেকে নেক্সি পর্যন্ত

Nexy-এর মডুলার রাউটার NestJS আকৃতি রাখে - কন্ট্রোলার, মডিউল, ইনজেকশনযোগ্য পরিষেবা এবং গার্ড - Python-এ, Pydantic DTO ক্লাসের জায়গায় এবং OpenAPI ডক্স আপনার জন্য তৈরি।

নীচের প্রতিটি বিভাগে একটি NestJS অভ্যাস দেখায়, তারপর Nexy তে একই জিনিস। NestJS এর কি আছে এবং Nexy এর কি নেই তা [Nexy এবং NestJS](../routing/modular/vs-nestjs.md) এ তালিকাভুক্ত করা হয়েছে।

## রাউটার চালু করা হচ্ছে

```ts filename="src/main.ts"
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";

const app = await NestFactory.create(AppModule);
await app.listen(3000);
```

রুট মডিউল হল `nexyconfig.py` এর একটি ক্ষেত্র, এবং `nx dev` এটি পরিবেশন করে:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

## একজন নিয়ামক

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

পদ্ধতির নাম হল HTTP ক্রিয়া:

```python filename="src/apps/cats/cats_controller.py"
from nexy.decorators import Controller


@Controller("/cats")
class CatsController:
    async def get(self) -> list[dict]:
        return [{"name": "Tom"}]
```

একটি নিয়ন্ত্রকের ক্রিয়া প্রতি একটি হ্যান্ডলার আছে। `GET /cats` এবং `GET /cats/:id` দুটি নিয়ন্ত্রক।

## রুট পরামিতি

```ts filename="src/cats/cat.controller.ts"
@Controller("cats/:id")
export class CatController {
  @Get()
  findOne(@Param("id", ParseIntPipe) id: number) {
    return { id };
  }
}
```

`@Param` এবং `ParseIntPipe` পথের মধ্যে একটি `{id}` হয়ে ওঠে এবং একটি `int` টীকা:

```python filename="src/apps/cats/cat_controller.py"
from nexy.decorators import Controller


@Controller("/cats/{id}")
class CatController:
    async def get(self, id: int) -> dict:
        return {"id": id}
```

## ক্যোয়ারী প্যারামিটার

```ts filename="src/cats/cats.controller.ts"
@Get()
findAll(@Query("limit", new DefaultValuePipe(10), ParseIntPipe) limit: number) {
  return { limit };
}
```

একটি ক্যোয়ারী প্যারামিটার হল একটি ডিফল্ট সহ একটি প্যারামিটার:

```python filename="src/apps/search/search_controller.py"
from nexy.decorators import Controller


@Controller("/search")
class SearchController:
    async def get(self, q: str = "", limit: int = 10) -> dict:
        return {"q": q, "limit": limit}
```

## ডিটিও এবং `ValidationPipe`

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

ডিটিও একটি Pydantic মডেল। এটি সর্বদা যাচাই করা হয়, এবং একটি খারাপ শরীর উত্তর দেয় `422`:

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

## প্রদানকারী এবং কনস্ট্রাক্টর ইনজেকশন

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

একই দুই ডেকোরেটর; `__init__`-এর টাইপ টীকা কন্টেইনারকে কী ইনজেকশন দিতে হবে তা বলে:

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

## স্কোপ

```ts filename="src/cats/request-context.ts"
@Injectable({ scope: Scope.REQUEST })
export class RequestContext {}
```

```python filename="src/apps/cats/request_context.py"
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class RequestContext: ...
```

`Scope.SINGLETON` ডিফল্ট, যেমন NestJS, এবং `Scope.TRANSIENT` প্রতি ইনজেকশনে একটি নতুন উদাহরণ দেয়।

## মডিউল

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

চারটি অ্যারে চারটি শ্রেণীর বৈশিষ্ট্য:

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

`@Module(prefix="/api")` মডিউলের প্রতিটি নিয়ামকের উপসর্গ, যেমন `RouterModule` বা `setGlobalPrefix("api")`।

## রক্ষীরা

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

একটি গার্ড হল একটি ফাংশন যা উত্থাপন করে যখন অনুরোধটি নাও যেতে পারে:

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

## ব্যতিক্রম

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

উভয়ই স্ট্যাটাস কোড সহ `{"detail": ...}` উত্তর দেয়, যেমন NestJS উত্তর দেয় `{"message": ...}`।

## মিডলওয়্যার এবং ইন্টারসেপ্টর

```ts filename="src/logger.middleware.ts"
@Injectable()
export class AppHeaderMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    res.setHeader("X-App", "demo");
    next();
  }
}
```

একটি ASGI মিডলওয়্যার শ্রেণী, `nexyconfig.py`-এ তালিকাভুক্ত, প্রতিটি অনুরোধকে মোড়ানো হয়:

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

একটি ইন্টারসেপ্টর যা প্রতিক্রিয়া ম্যাপ করে একই মিডলওয়্যার, `call_next` এর পরে কোড সহ।

## সোয়াগার

```ts
@ApiOperation({ summary: "List cats" })
@ApiResponse({ status: 200 })
@Get()
findAll() {}
```

এখানে কোন `SwaggerModule.setup` নেই: প্রতিটি কন্ট্রোলার `/docs` এ পরিবেশিত স্কিমার মধ্যে রয়েছে। অলঙ্করণকারীরা কেবল যা স্বাক্ষর করে না তা যোগ করে:

```python filename="src/apps/docs/documented_controller.py"
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller("/documented")
class DocumentedController:
    @UseRoute(summary="List cats", tags=["cats"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

## WebSocket গেটওয়ে

```ts filename="src/events.gateway.ts"
@WebSocketGateway()
export class EventsGateway {
  @SubscribeMessage("echo")
  echo(@MessageBody() data: string) {
    return data;
  }
}
```

একটি `SOCKET` পদ্ধতি তার নিয়ামকের পথে একটি WebSocket খোলে:

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller("/ws/echo")
class EchoController:
    async def SOCKET(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

প্রতিটি কন্ট্রোলারের মতো, এটি একটি মডিউল এটিকে `controllers` তালিকাভুক্ত করার পরে উত্তর দেয়। একটি কন্ট্রোলারের রুট একটি স্ল্যাশ দিয়ে শেষ হয়: `/ws/echo/` এর সাথে সংযোগ করুন, যেহেতু একটি WebSocket একটি HTTP অনুরোধের মতো পুনঃনির্দেশিত হয় না।

## `ConfigModule`

```ts
@Module({ imports: [ConfigModule.forRoot()] })
export class AppModule {}

constructor(private config: ConfigService) {}
this.config.get("DATABASE_URL");
```

সেটিংস হল একটি Pydantic মডেল বা প্লেইন এনভায়রনমেন্ট ভেরিয়েবল, যেকোনো প্রদানকারীর মতো ইনজেকশন করা হয়:

```python filename="src/apps/settings.py"
import os

from nexy.decorators import Injectable


@Injectable()
class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## টেস্ট

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

একটি পরীক্ষায় একটি পরিষেবা প্রতিস্থাপন করতে, `Depends` এর মাধ্যমে এটির উপর নির্ভর করুন এবং FastAPI এর `app.dependency_overrides` ব্যবহার করুন: দেখুন [Nexy এবং NestJS](../routing/modular/vs-nestjs.md#what-is-missing)।

## চলমান

| NestJS | নেক্সি |
|---|---|
| `nest new` | `nx new`, তারপর মডুলার রাউটার বাছাই করুন |
| `npm run start:dev` | `nx dev` |
| `npm run build && npm run start:prod` | `nx build`, তারপর `nx start` |
| `npm test` | `nx test` |
| `nest generate controller` | একটি নতুন `*_controller.py`, এর মডিউলে যোগ করা হয়েছে |

<!-- router:fbr,custom -->
## অথবা ক্লাসের পরিবর্তে ফাইল

একটি NestJS অ্যাপ যা বেশিরভাগ CRUD হয় ফাইল-ভিত্তিক রাউটারেও যেতে পারে, যেখানে ফোল্ডারটি পাথ এবং সিঙ্কে রাখার জন্য কোনও মডিউল নেই:

```python filename="src/routes/cats/[id].py"
async def GET(id: int):
    return {"id": id}
```

<!-- /router -->

[একটি রাউটার চয়ন করুন](../routing/README.md) দেখুন।

## পরবর্তী পদক্ষেপ

- [মডুলার রাউটিং](../routing/modular/README.md)
- [নির্ভরতা ইনজেকশন ](../routing/modular/dependency-injection.md)
- [নেক্সি এবং NestJS](../routing/modular/vs-nestjs.md)
- [এক্সপ্রেস থেকে নেক্সি পর্যন্ত](../getting-started/coming-from-other-frameworks.md#from-express-or-node-backends)
