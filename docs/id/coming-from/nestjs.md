# Dari NestJS hingga Nexy

Router modular Nexy menyimpan bentuk NestJS - pengontrol, modul, layanan injeksi, dan pelindung - di Python, dengan Pydantic sebagai pengganti kelas DTO dan OpenAPI dokumen yang dibuat untuk Anda.

Setiap bagian di bawah menunjukkan kebiasaan NestJS, lalu hal yang sama di Nexy. Apa yang dimiliki NestJS dan tidak dimiliki Nexy tercantum dalam [Nexy dan NestJS](../routing/modular/vs-nestjs.md).

## Menghidupkan router

```ts filename="src/main.ts"
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";

const app = await NestFactory.create(AppModule);
await app.listen(3000);
```

Modul root adalah bidang `nexyconfig.py`, dan `nx dev` menyajikannya:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

## Sebuah pengontrol

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

Nama metodenya adalah kata kerja HTTP:

```python filename="src/apps/cats/cats_controller.py"
from nexy.decorators import Controller


@Controller(prefix="/cats")
class CatsController:
    async def get(self) -> list[dict]:
        return [{"name": "Tom"}]
```

Pengontrol memiliki satu penangan per kata kerja. `GET /cats` dan `GET /cats/:id` adalah dua pengontrol.

## Parameter rute

```ts filename="src/cats/cat.controller.ts"
@Controller("cats/:id")
export class CatController {
  @Get()
  findOne(@Param("id", ParseIntPipe) id: number) {
    return { id };
  }
}
```

`@Param` dan `ParseIntPipe` menjadi `{id}` di awalan dan anotasi `int`:

```python filename="src/apps/cats/cat_controller.py"
from nexy.decorators import Controller


@Controller(prefix="/cats/{id}")
class CatController:
    async def get(self, id: int) -> dict:
        return {"id": id}
```

## Parameter kueri

```ts filename="src/cats/cats.controller.ts"
@Get()
findAll(@Query("limit", new DefaultValuePipe(10), ParseIntPipe) limit: number) {
  return { limit };
}
```

Parameter kueri adalah parameter dengan default:

```python filename="src/apps/search/search_controller.py"
from nexy.decorators import Controller


@Controller(prefix="/search")
class SearchController:
    async def get(self, q: str = "", limit: int = 10) -> dict:
        return {"q": q, "limit": limit}
```

## DTO dan `ValidationPipe`

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

DTO adalah model Pydantic. Itu selalu divalidasi, dan tubuh yang buruk menjawab `422`:

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

## Penyedia dan injeksi konstruktor

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

Dua dekorator yang sama; anotasi tipe `__init__` memberi tahu container apa yang harus disuntikkan:

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

## Lingkup

```ts filename="src/cats/request-context.ts"
@Injectable({ scope: Scope.REQUEST })
export class RequestContext {}
```

```python filename="src/apps/cats/request_context.py"
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class RequestContext: ...
```

`Scope.SINGLETON` adalah defaultnya, seperti pada NestJS, dan `Scope.TRANSIENT` memberikan instance baru per injeksi.

## Modul

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

Empat array adalah empat atribut kelas:

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

`@Module(prefix="/api")` mengawali setiap pengontrol modul, seperti `RouterModule` atau `setGlobalPrefix("api")`.

## Penjaga

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

Penjaga adalah fungsi yang muncul ketika permintaan tidak dapat dilanjutkan:

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

## Pengecualian

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

Keduanya menjawab `{"detail": ...}` dengan kode status, seperti NestJS menjawab `{"message": ...}`.

## Middleware dan pencegat

```ts filename="src/logger.middleware.ts"
@Injectable()
export class AppHeaderMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    res.setHeader("X-App", "demo");
    next();
  }
}
```

Kelas middleware ASGI, yang tercantum di `nexyconfig.py`, membungkus setiap permintaan:

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

Pencegat yang memetakan respons adalah middleware yang sama, dengan kode setelah `call_next`.

## Kesombongan

```ts
@ApiOperation({ summary: "List cats" })
@ApiResponse({ status: 200 })
@Get()
findAll() {}
```

Tidak ada `SwaggerModule.setup`: setiap pengontrol ada dalam skema yang disajikan di `/docs`. Dekorator hanya menambahkan apa yang tidak tertulis di tanda tangan:

```python filename="src/apps/docs/documented_controller.py"
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller(prefix="/documented")
class DocumentedController:
    @UseRoute(summary="List cats", tags=["cats"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

## WebSocket gerbang

```ts filename="src/events.gateway.ts"
@WebSocketGateway()
export class EventsGateway {
  @SubscribeMessage("echo")
  echo(@MessageBody() data: string) {
    return data;
  }
}
```

Metode `SOCKET` membuka WebSocket di jalur pengontrolnya:

```python filename="src/apps/ws/echo_controller.py"
from fastapi import WebSocket

from nexy.decorators import Controller


@Controller(prefix="/ws/echo")
class EchoController:
    async def SOCKET(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())
```

Seperti setiap pengontrol, ia menjawab setelah modul mencantumkannya di `controllers`. Rute pengontrol diakhiri dengan garis miring: sambungkan ke `/ws/echo/`, karena WebSocket tidak dialihkan seperti permintaan HTTP.

## `ConfigModule`

```ts
@Module({ imports: [ConfigModule.forRoot()] })
export class AppModule {}

constructor(private config: ConfigService) {}
this.config.get("DATABASE_URL");
```

Pengaturan adalah model Pydantic atau variabel lingkungan biasa, yang dimasukkan seperti penyedia mana pun:

```python filename="src/apps/settings.py"
import os

from nexy.decorators import Injectable


@Injectable()
class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///dev.db")
```

## Tes

```ts filename="src/cats/cats.controller.spec.ts"
const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
const app = moduleRef.createNestApplication();
await app.init();
await request(app.getHttpServer()).get("/cats").expect(200);
```

```python filename="tes/test_cats.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_cats():
    assert TestClient(app).get("/cats").json() == [{"name": "Tom"}]
```

Untuk mengganti layanan dalam pengujian, bergantung padanya melalui `Depends` dan gunakan `app.dependency_overrides` FastAPI: lihat [Nexy dan NestJS](../routing/modular/vs-nestjs.md#what-is-missing).

## Berlari

| NestJS | Nexy |
|---|---|
| `nest new` | `nx new`, lalu pilih router modular |
| `npm run start:dev` | `nx dev` |
| `npm run build && npm run start:prod` | `nx build`, lalu `nx start` |
| `npm test` | `nx test` |
| `nest generate controller` | `*_controller.py` baru, ditambahkan ke modulnya |

## Atau file, bukan kelas

Aplikasi NestJS yang sebagian besar CRUD juga dapat berpindah ke router berbasis file, dengan folder sebagai awalan dan tidak ada modul untuk tetap disinkronkan:

```python filename="src/rute/kucing/[id].py"
async def GET(id: int):
    return {"id": id}
```

Lihat [Memilih router](../routing/README.md).

## Langkah selanjutnya

- [Perutean modular](../routing/modular/README.md)
- [Injeksi ketergantungan](../routing/modular/dependency-injection.md)
- [Nexy dan NestJS](../routing/modular/vs-nestjs.md)
- [Dari Ekspres ke Nexy](../getting-started/coming-from-other-frameworks.md#from-express-or-node-backends)
