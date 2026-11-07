# NestJS से नेक्सी तक

नेक्सी का मॉड्यूलर राउटर NestJS आकार रखता है - नियंत्रक, मॉड्यूल, इंजेक्टेबल सेवाएं और गार्ड - Python में, डीटीओ कक्षाओं के स्थान पर Pydantic और आपके लिए बनाए गए OpenAPI डॉक्स के साथ।

नीचे प्रत्येक अनुभाग एक NestJS आदत दिखाता है, फिर नेक्सी में भी वही चीज़। NestJS के पास क्या है और नेक्सी के पास क्या नहीं है, यह [नेक्सी और NestJS](../routing/modular/vs-nestjs.md) में सूचीबद्ध है।

## राउटर चालू करना

```ts filename="src/main.ts"
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";

const app = await NestFactory.create(AppModule);
await app.listen(3000);
```

रूट मॉड्यूल `nexyconfig.py` का एक क्षेत्र है, और `nx dev` इसकी सेवा करता है:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

## एक नियंत्रक

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

विधि का नाम HTTP क्रिया है:

```python filename="src/apps/cats/cats_controller.py"
from nexy.decorators import Controller


@Controller("/cats")
class CatsController:
    async def get(self) -> list[dict]:
        return [{"name": "Tom"}]
```

एक नियंत्रक के पास प्रति क्रिया एक हैंडलर होता है। `GET /cats` और `GET /cats/:id` दो नियंत्रक हैं।

## मार्ग पैरामीटर

```ts filename="src/cats/cat.controller.ts"
@Controller("cats/:id")
export class CatController {
  @Get()
  findOne(@Param("id", ParseIntPipe) id: number) {
    return { id };
  }
}
```

`@Param` और `ParseIntPipe` पथ में एक `{id}` और एक `int` एनोटेशन बन जाते हैं:

```python filename="src/apps/cats/cat_controller.py"
from nexy.decorators import Controller


@Controller("/cats/{id}")
class CatController:
    async def get(self, id: int) -> dict:
        return {"id": id}
```

## क्वेरी पैरामीटर

```ts filename="src/cats/cats.controller.ts"
@Get()
findAll(@Query("limit", new DefaultValuePipe(10), ParseIntPipe) limit: number) {
  return { limit };
}
```

एक क्वेरी पैरामीटर एक डिफ़ॉल्ट पैरामीटर है:

```python filename="src/apps/search/search_controller.py"
from nexy.decorators import Controller


@Controller("/search")
class SearchController:
    async def get(self, q: str = "", limit: int = 10) -> dict:
        return {"q": q, "limit": limit}
```

## डीटीओ और `ValidationPipe`

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

डीटीओ एक Pydantic मॉडल है। यह हमेशा मान्य होता है, और एक ख़राब शरीर उत्तर देता है `422`:

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

## प्रदाता और कंस्ट्रक्टर इंजेक्शन

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

वही दो सज्जाकार; `__init__` का प्रकार एनोटेशन कंटेनर को बताता है कि क्या इंजेक्ट करना है:

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

## दायरा

```ts filename="src/cats/request-context.ts"
@Injectable({ scope: Scope.REQUEST })
export class RequestContext {}
```

```python filename="src/apps/cats/request_context.py"
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class RequestContext: ...
```

`Scope.SINGLETON` डिफ़ॉल्ट है, जैसा कि NestJS में है, और `Scope.TRANSIENT` प्रति इंजेक्शन एक नया उदाहरण देता है।

## मॉड्यूल

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

चार सरणियाँ चार वर्ग विशेषताएँ हैं:

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

`@Module(prefix="/api")` मॉड्यूल के प्रत्येक नियंत्रक को उपसर्ग करता है, जैसे `RouterModule` या `setGlobalPrefix("api")`।

## रक्षक

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

गार्ड एक फ़ंक्शन है जो तब उठाता है जब अनुरोध जारी नहीं हो सकता है:

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

## अपवाद

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

दोनों स्थिति कोड के साथ `{"detail": ...}` का उत्तर देते हैं, जैसे कि NestJS `{"message": ...}` का उत्तर देते हैं।

## मिडलवेयर और इंटरसेप्टर

```ts filename="src/logger.middleware.ts"
@Injectable()
export class AppHeaderMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    res.setHeader("X-App", "demo");
    next();
  }
}
```

`nexyconfig.py` में सूचीबद्ध एक एएसजीआई मिडलवेयर क्लास, हर अनुरोध को लपेटता है:

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

एक इंटरसेप्टर जो प्रतिक्रिया को मैप करता है वह वही मिडलवेयर है, जिसका कोड `call_next` के बाद होता है।

## स्वैगर

```ts
@ApiOperation({ summary: "List cats" })
@ApiResponse({ status: 200 })
@Get()
findAll() {}
```

कोई `SwaggerModule.setup` नहीं है: प्रत्येक नियंत्रक `/docs` पर दी गई स्कीमा में है। सज्जाकार केवल वही जोड़ते हैं जो हस्ताक्षर में नहीं कहा गया है:

```python filename="src/apps/docs/documented_controller.py"
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller("/documented")
class DocumentedController:
    @UseRoute(summary="List cats", tags=["cats"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

## WebSocket प्रवेश द्वार

```ts filename="src/events.gateway.ts"
@WebSocketGateway()
export class EventsGateway {
  @SubscribeMessage("echo")
  echo(@MessageBody() data: string) {
    return data;
  }
}
```

एक `SOCKET` विधि अपने नियंत्रक के पथ पर एक WebSocket खोलती है:

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller("/ws/echo")
class EchoController:
    async def SOCKET(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

प्रत्येक नियंत्रक की तरह, मॉड्यूल द्वारा इसे `controllers` में सूचीबद्ध करने के बाद यह उत्तर देता है। नियंत्रक का मार्ग एक स्लैश के साथ समाप्त होता है: `/ws/echo/` से कनेक्ट करें, क्योंकि WebSocket को HTTP अनुरोध की तरह पुनर्निर्देशित नहीं किया जाता है।

## `ConfigModule`

```ts
@Module({ imports: [ConfigModule.forRoot()] })
export class AppModule {}

constructor(private config: ConfigService) {}
this.config.get("DATABASE_URL");
```

सेटिंग्स एक Pydantic मॉडल या सादे पर्यावरण चर हैं, जिन्हें किसी भी प्रदाता की तरह इंजेक्ट किया जाता है:

```python filename="src/apps/settings.py"
import os

from nexy.decorators import Injectable


@Injectable()
class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## परीक्षण

```ts filename="src/cats/cats.controller.spec.ts"
const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
const app = moduleRef.createNestApplication();
await app.init();
await request(app.getHttpServer()).get("/cats").expect(200);
```

```python filename="परीक्षण/test_cats.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_cats():
    assert TestClient(app).get("/cats").json() == [{"name": "Tom"}]
```

किसी परीक्षण में किसी सेवा को बदलने के लिए, `Depends` के माध्यम से उस पर निर्भर रहें और FastAPI के `app.dependency_overrides` का उपयोग करें: [नेक्सी और NestJS](../routing/modular/vs-nestjs.md#what-is-missing) देखें।

## चल रहा है

| NestJS | नेक्सी |
|---|---|
| `nest new` | `nx new`, फिर मॉड्यूलर राउटर चुनें |
| `npm run start:dev` | `nx dev` |
| `npm run build && npm run start:prod` | `nx build`, फिर `nx start` |
| `npm test` | `nx test` |
| `nest generate controller` | इसके मॉड्यूल में एक नया `*_controller.py` जोड़ा गया |

<!-- router:fbr,custom -->
## या कक्षाओं के बजाय फ़ाइलें

एक NestJS ऐप जो अधिकतर सीआरयूडी है, फ़ाइल-आधारित राउटर पर भी जा सकता है, जहां फ़ोल्डर पथ है और सिंक में रखने के लिए कोई मॉड्यूल नहीं हैं:

```python filename="src/routes/cats/[id].py"
async def GET(id: int):
    return {"id": id}
```

<!-- /router -->

देखें [राउटर चुनें](../routing/README.md)।

## अगले चरण

- [मॉड्यूलर रूटिंग](../routing/modular/README.md)
- [निर्भरता इंजेक्शन](../routing/modular/dependency-injection.md)
- [नेक्सी और NestJS](../routing/modular/vs-nestjs.md)
- [एक्सप्रेस से नेक्सी तक](../getting-started/coming-from-other-frameworks.md#from-express-or-node-backends)
