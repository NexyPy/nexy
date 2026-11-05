# Nexy اور NestJS

ماڈیولر راؤٹر NestJS: کنٹرولرز، ماڈیولز اور کنسٹرکٹر انجیکشن سے متاثر ہے۔ یہ FastAPI پر ایک پتلی تہہ ہے، اس لیے یہ تمام NestJS کو دوبارہ بنانے کی کوشش نہیں کرتی ہے۔ یہ صفحہ دونوں اطراف کی فہرست دیتا ہے۔

## کیا مماثل ہے

| NestJS | نیکسی |
|---|---|
| `@Controller('users')` | `@Controller(prefix="/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` ایک ہی چار طبقاتی صفات کے ساتھ |
| `@Injectable()` | `@Injectable()` |
| کنسٹرکٹر انجیکشن | `__init__` پیرامیٹرز ٹائپ تشریحات سے حل ہوئے۔ |
| سنگلٹن، درخواست اور عارضی دائرہ کار | `Scope.SINGLETON`، `Scope.REQUEST`، `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (ایک FastAPI انحصار) |
| `@ApiOperation`، `@ApiResponse` (بیڑیاں) | `@UseRoute`، `@UseResponse` (OpenAPI، پیش خدمت `/docs`) |
| WebSocket گیٹ ویز | ایک کنٹرولر پر `async def SOCKET(...)` |
| ڈی ٹی او کی توثیق (`class-validator`) | Pydantic ماڈل، FastAPI کے مقامی |
| سرکلر انحصار کا پتہ لگانا | `RecursionError` کلاس کا نام دینا |

وہی کنٹرولر اور اس کی انجیکشن سروس، NestJS پہلے:

```ts filename="user.controller.ts"
@Injectable()
export class UsersService {
  findAll() {
    return [{ id: 1, name: "Ada" }];
  }
}

@Controller("users")
export class UsersController {
  constructor(private readonly users: UsersService) {}

  @Get()
  findAll() {
    return this.users.findAll();
  }
}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller, Injectable


@Injectable()
class UserService:
    def find_all(self) -> list[dict]:
        return [{"id": 1, "name": "Ada"}]


@Controller(prefix="/users")
class UserController:
    def __init__(self, users: UserService) -> None:
        self.users = users

    async def get(self) -> list[dict]:
        return self.users.find_all()
```

## کیا فرق ہے

- ہینڈلرز ایسے طریقے ہیں جن کا نام HTTP فعل (`get`، `post`...)، ایک فی کنٹرولر کے نام پر رکھا گیا ہے۔
- گارڈز اور مڈل ویئر ڈیکوریٹر FastAPI `Depends` ہیں، `canActivate` کے ساتھ کلاس نہیں۔
- پیرامیٹرز (`@Body`، `@Param`، `@Query`) ہیں FastAPI پیرامیٹرز: ٹائپ تشریحات، `Query`، `Path`، `Body`۔
- پائپس ہیں Pydantic توثیق اور FastAPI انحصار۔

`@Query()`، ایک ڈی ٹی او اور گارڈ کلاس ایک تشریح، ایک Pydantic ماڈل اور ایک فنکشن بن جاتے ہیں:

```python filename="src/apps/posts/post_controller.py"
from fastapi import Header, HTTPException, Query
from pydantic import BaseModel
from nexy.decorators import Controller, UseGuard


class NewPost(BaseModel):
    title: str


def require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller(prefix="/posts")
@UseGuard(require_token)
class PostController:
    async def get(self, limit: int = Query(10)) -> list[dict]:
        return []

    async def post(self, body: NewPost) -> dict:
        return {"title": body.title}
```

## کیا غائب ہے

| NestJS خصوصیت | Nexy میں حیثیت |
|---|---|
| حسب ضرورت فراہم کنندگان (`useValue`، `useFactory`، `useClass`، سٹرنگ ٹوکنز) | دستیاب نہیں: صرف `@Injectable()` کلاسز |
| انٹرفیس یا خلاصہ کلاس کے ذریعہ انجیکشن لگانا | دستیاب نہیں |
| ماڈیول انکیپسولیشن | نافذ نہیں کیا گیا: کنٹینر مکمل عمل ہے، `exports` صرف بے چین ریزولوشن کو کنٹرول کرتا ہے |
| متحرک اور عالمی ماڈیولز (`forRoot`، `@Global`) | دستیاب نہیں |
| لائف سائیکل ہکس (`onModuleInit`، `onApplicationShutdown`) | دستیاب نہیں |
| انٹرسیپٹرز | ASGI مڈل ویئر (`useMiddlewares`) یا انحصار استعمال کریں۔ |
| استثنائی فلٹرز | استثنیٰ ہینڈلرز FastAPI استعمال کریں۔ |
| فراہم کنندہ اوور رائیڈز کے ساتھ ٹیسٹنگ ماڈیول | کوئی عوامی API نہیں؛ استعمال کریں FastAPI `dependency_overrides` اور `TestClient` |
| کنفیگ ماڈیول، شیڈولنگ، قطاریں، CQRS، مائیکرو سروسز، کیشنگ | Nexy کا حصہ نہیں؛ Python ماحولیاتی نظام کا استعمال کریں۔ |

ایک `useFactory` فراہم کنندہ کی جگہ، `Depends` کے پیچھے ایک سادہ فنکشن، جسے ایک ٹیسٹ `dependency_overrides` سے اوور رائیڈ کرتا ہے:

```python filename="src/apps/reports/report_controller.py"
from fastapi import Depends
from nexy.decorators import Controller


def get_settings() -> dict:
    return {"currency": "EUR"}


@Controller(prefix="/reports")
class ReportController:
    async def get(self, settings: dict = Depends(get_settings)) -> dict:
        return {"currency": settings["currency"]}
```

## اسے کب چننا ہے۔

جب آپ کسی بڑے API کے لیے انجیکشن کے ساتھ کلاس پر مبنی ڈھانچہ چاہتے ہیں تو ماڈیولر راؤٹر کا انتخاب کریں۔ جب یو آر ایل کا ڈھانچہ ترتیب دینے والا اصول ہو تو فائل پر مبنی روٹر کا انتخاب کریں۔ دونوں کو `nx new` کے ذریعے بنایا گیا ہے، ایک ہی FastAPI ایپلی کیشن پر چلتے ہیں، اور ایک ساتھ رہ سکتے ہیں۔

> [!NOTE]
> مندرجہ بالا لاپتہ اشیاء ایماندار خلا ہیں. اگر آپ کو آج ٹیسٹوں میں `useFactory` فراہم کنندگان یا اوور رائیڈ ایبل فراہم کنندگان کی ضرورت ہے، تو منطق کو سادہ فنکشنز اور FastAPI `Depends` میں رکھیں، جو قدرتی طور پر تحریر اور اوور رائیڈ کرتے ہیں۔

## اگلے اقدامات

- [انحصار انجکشن](dependency-injection.md)
- [گارڈز اور میٹا ڈیٹا](guards-and-metadata.md)
- [جانچ](../../guides/testing.md)
