# নেক্সি এবং NestJS

মডুলার রাউটারটি NestJS দ্বারা অনুপ্রাণিত: কন্ট্রোলার, মডিউল এবং কনস্ট্রাক্টর ইনজেকশন। এটি FastAPI এর উপর একটি পাতলা স্তর, তাই এটি সমস্ত NestJS পুনরুত্পাদনের চেষ্টা করে না। এই পৃষ্ঠায় উভয় পক্ষের তালিকা রয়েছে।

## কি মেলে

| NestJS | নেক্সি |
|---|---|
| `@Controller('users')` | `@Controller(prefix="/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` একই চার শ্রেণীর বৈশিষ্ট্য সহ |
| `@Injectable()` | `@Injectable()` |
| কনস্ট্রাক্টর ইনজেকশন | `__init__` পরামিতি টাইপ টীকা থেকে সমাধান করা হয়েছে |
| সিঙ্গেলটন, অনুরোধ এবং ক্ষণস্থায়ী সুযোগ | `Scope.SINGLETON`, `Scope.REQUEST`, `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (একটি FastAPI নির্ভরতা) |
| `@ApiOperation`, `@ApiResponse` (সোয়াগার) | `@UseRoute`, `@UseResponse` (OpenAPI, `/docs` এ পরিবেশিত) |
| WebSocket গেটওয়ে | `async def SOCKET(...)` একটি নিয়ামক উপর |
| ডিটিও বৈধতা (`class-validator`) | Pydantic মডেল, স্থানীয় FastAPI |
| সার্কুলার নির্ভরতা সনাক্তকরণ | `RecursionError` ক্লাসের নামকরণ |

একই নিয়ামক এবং এর ইনজেকশন পরিষেবা, NestJS প্রথম:

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

## কি পার্থক্য

- হ্যান্ডলারগুলি হল HTTP ক্রিয়া (`get`, `post`...), প্রতি কন্ট্রোলারের নামে একটি পদ্ধতি।
- গার্ড এবং মিডলওয়্যার ডেকোরেটররা FastAPI `Depends`, `canActivate` এর সাথে ক্লাস নয়।
- প্যারামিটার (`@Body`, `@Param`, `@Query`) হল FastAPI প্যারামিটার: টাইপ টীকা, `Query`, `Path`, `Body`।
- পাইপ হল Pydantic বৈধতা এবং FastAPI নির্ভরতা।

`@Query()`, একটি ডিটিও এবং একটি গার্ড ক্লাস একটি টীকা, একটি Pydantic মডেল এবং একটি ফাংশন হয়ে ওঠে:

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

## কি অনুপস্থিত

| NestJS বৈশিষ্ট্য | নেক্সিতে স্ট্যাটাস |
|---|---|
| কাস্টম প্রদানকারী (`useValue`, `useFactory`, `useClass`, স্ট্রিং টোকেন) | উপলব্ধ নয়: শুধুমাত্র `@Injectable()` ক্লাস |
| ইন্টারফেস বা বিমূর্ত শ্রেণী দ্বারা ইনজেকশন | উপলব্ধ নয় |
| মডিউল এনক্যাপসুলেশন | প্রয়োগ করা হয়নি: ধারকটি প্রক্রিয়া-প্রশস্ত, `exports` শুধুমাত্র আগ্রহী রেজোলিউশন নিয়ন্ত্রণ করে |
| ডাইনামিক এবং গ্লোবাল মডিউল (`forRoot`, `@Global`) | উপলব্ধ নয় |
| লাইফসাইকেল হুক (`onModuleInit`, `onApplicationShutdown`) | উপলব্ধ নয় |
| ইন্টারসেপ্টর | ASGI মিডলওয়্যার (`useMiddlewares`) বা নির্ভরতা ব্যবহার করুন |
| ব্যতিক্রম ফিল্টার | FastAPI ব্যতিক্রম হ্যান্ডলার ব্যবহার করুন |
| প্রদানকারী ওভাররাইড সহ পরীক্ষা মডিউল | কোন পাবলিক API; FastAPI `dependency_overrides` এবং `TestClient` ব্যবহার করুন |
| কনফিগ মডিউল, সময়সূচী, সারি, CQRS, মাইক্রোসার্ভিসেস, ক্যাশিং | Nexy এর অংশ নয়; Python ইকোসিস্টেম ব্যবহার করুন |

একটি `useFactory` প্রদানকারীর জায়গায়, `Depends` এর পিছনে একটি সাধারণ ফাংশন, যা একটি পরীক্ষা `dependency_overrides` এর সাথে ওভাররাইড করে:

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

## কখন বাছাই করবেন

যখন আপনি একটি বৃহত্তর API এর জন্য ইনজেকশন সহ একটি ক্লাস-ভিত্তিক কাঠামো চান তখন মডুলার রাউটারটি বেছে নিন। ফাইল-ভিত্তিক রাউটার চয়ন করুন যখন ইউআরএল গঠনটি সংগঠিত নীতি। উভয়ই `nx new` দ্বারা ভারা, একই FastAPI অ্যাপ্লিকেশনে চালিত, এবং সহাবস্থান করতে পারে।

> [!NOTE]
> উপরের অনুপস্থিত আইটেম সৎ ফাঁক. আপনার যদি আজ পরীক্ষায় `useFactory` প্রদানকারী বা ওভাররাইডযোগ্য প্রদানকারীর প্রয়োজন হয়, তবে যুক্তিটিকে প্লেইন ফাংশনে রাখুন এবং FastAPI `Depends`, যা স্বাভাবিকভাবে রচনা এবং ওভাররাইড করে।

## পরবর্তী পদক্ষেপ

- [নির্ভরতা ইনজেকশন ](dependency-injection.md)
- [গার্ড এবং মেটাডেটা](guards-and-metadata.md)
- [পরীক্ষা ](../../guides/testing.md)
