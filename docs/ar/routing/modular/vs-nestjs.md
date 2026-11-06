# نكسي و NestJS

جهاز التوجيه المعياري مستوحى من NestJS: وحدات التحكم والوحدات النمطية وحقن المنشئ. إنها طبقة رقيقة فوق FastAPI، لذلك لا تحاول إعادة إنتاج كل NestJS. هذه الصفحة تسرد كلا الجانبين.

## ما يتطابق

| NestJS | نكسي |
|---|---|
| `@Controller('users')` | `@Controller("/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` بنفس سمات الصنف الأربع |
| `@Injectable()` | `@Injectable()` |
| حقن المنشئ | `__init__` تم حل المعلمات من التعليقات التوضيحية للنوع |
| نطاقات فردية وطلبية وعابرة | `Scope.SINGLETON`، `Scope.REQUEST`، `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (تبعية FastAPI) |
| `@ApiOperation`، `@ApiResponse` (اختيال) | `@UseRoute`، `@UseResponse` (OpenAPI، خدم في `/docs`) |
| WebSocket البوابات | `async def SOCKET(...)` على جهاز التحكم |
| التحقق من صحة DTO (`class-validator`) | Pydantic نماذج أصلية في FastAPI |
| كشف التبعية الدائرية | `RecursionError` تسمية الفصل |

نفس المتحكم والخدمة المحقونة به، NestJS أولا:

```ts filename="users.controller.ts"
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


@Controller("/users")
class UserController:
    def __init__(self, users: UserService) -> None:
        self.users = users

    async def get(self) -> list[dict]:
        return self.users.find_all()
```

## ما يختلف

- المعالجات هي طرق مسماة على اسم فعل HTTP (`get`، `post`...)، واحدة لكل وحدة تحكم.
- الحراس ومصممو البرمجيات الوسيطة هم FastAPI `Depends`، وليسوا فئات ذات `canActivate`.
- المعلمات (`@Body`، `@Param`، `@Query`) هي FastAPI معلمات: نوع التعليقات التوضيحية، `Query`، `Path`، `Body`.
- الأنابيب هي Pydantic التحقق من الصحة و FastAPI التبعيات.

`@Query()`، تصبح DTO وفئة الحماية بمثابة تعليق توضيحي ونموذج Pydantic ووظيفة:

```python filename="src/apps/posts/post_controller.py"
from fastapi import Header, HTTPException, Query
from pydantic import BaseModel
from nexy.decorators import Controller, UseGuard


class NewPost(BaseModel):
    title: str


def require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller("/posts")
@UseGuard(require_token)
class PostController:
    async def get(self, limit: int = Query(10)) -> list[dict]:
        return []

    async def post(self, body: NewPost) -> dict:
        return {"title": body.title}
```

## ما هو مفقود

| NestJS ميزة | الحالة في Nexy |
|---|---|
| موفرو مخصصون (`useValue`، `useFactory`، `useClass`، رموز السلسلة) | غير متوفر: فقط `@Injectable()` فصول |
| الحقن عن طريق الواجهة أو الطبقة المجردة | غير متوفر |
| تغليف الوحدة النمطية | غير مطبقة: الحاوية على مستوى العملية، `exports` تتحكم فقط في الدقة المتحمسة |
| الوحدات الديناميكية والعالمية (`forRoot`، `@Global`) | غير متوفر |
| خطافات دورة الحياة (`onModuleInit`، `onApplicationShutdown`) | غير متوفر |
| اعتراضية | استخدم برامج ASGI الوسيطة (`useMiddlewares`) أو التبعيات |
| مرشحات الاستثناء | استخدم FastAPI معالجات الاستثناء |
| وحدة الاختبار مع تجاوزات الموفر | لا توجد واجهة برمجة تطبيقات عامة؛ استخدم FastAPI `dependency_overrides` و `TestClient` |
| وحدة التكوين، الجدولة، قوائم الانتظار، CQRS، الخدمات المصغرة، التخزين المؤقت | ليس جزءًا من Nexy؛ استخدام Python النظام البيئي |

بدلاً من موفر `useFactory`، توجد وظيفة عادية خلف `Depends`، والتي يتجاوزها الاختبار بـ `dependency_overrides`:

```python filename="src/apps/reports/report_controller.py"
from fastapi import Depends
from nexy.decorators import Controller


def get_settings() -> dict:
    return {"currency": "EUR"}


@Controller("/reports")
class ReportController:
    async def get(self, settings: dict = Depends(get_settings)) -> dict:
        return {"currency": settings["currency"]}
```

## متى تختاره

اختر جهاز التوجيه المعياري عندما تريد بنية قائمة على الفئة مع حقن واجهة برمجة تطبيقات أكبر. اختر جهاز التوجيه المستند إلى الملف عندما تكون بنية عنوان URL هي المبدأ التنظيمي. كلاهما مدعوم بواسطة `nx new`، ويعملان على نفس التطبيق FastAPI، ويمكنهما التواجد معًا.

> [!NOTE]
> العناصر المفقودة أعلاه هي الفجوة الصادقة. إذا كنت بحاجة إلى موفري `useFactory` أو موفري خدمات يمكن تجاوزهم في الاختبارات اليوم، فاحتفظ بالمنطق في الوظائف البسيطة و FastAPI `Depends`، التي يتم تركيبها وتجاوزها بشكل طبيعي.

## الخطوات التالية

- [حقن التبعية](dependency-injection.md)
- [الحراس والبيانات الوصفية](guards-and-metadata.md)
- [الاختبار](../../guides/testing.md)
