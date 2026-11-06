# 尼克西和 NestJS

模块化路由器的灵感来自于 NestJS：控制器、模块和构造函数注入。它是 FastAPI 上的薄层，因此它不会尝试重现所有 NestJS。此页列出了双方。

## 什么匹配

| NestJS | 内克西 |
|---|---|
| `@Controller('users')` | `@Controller("/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` 具有相同的四个类属性 |
| `@Injectable()` | `@Injectable()` |
| 构造函数注入 | `__init__` 从类型注释解析的参数 |
| 单例、请求和瞬态作用域 | `Scope.SINGLETON`、`Scope.REQUEST`、`Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)`（FastAPI 依赖） |
| `@ApiOperation`、`@ApiResponse`（招摇） | `@UseRoute`，`@UseResponse`（OpenAPI，服务于 `/docs`） |
| WebSocket 网关 | `async def SOCKET(...)` 在控制器上 |
| DTO 验证（`class-validator`） | Pydantic 模型，原生于 FastAPI |
| 循环依赖检测 | `RecursionError` 命名类 |

相同的控制器及其注入的服务，首先是 NestJS：

```ts filename="用户.controller.ts"
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

## 有什么不同

- 处理程序是以 HTTP 动词（`get`、`post`...）命名的方法，每个控制器一个。
- 守卫和中间件装饰器是 FastAPI `Depends`，而不是 `canActivate` 的类。
- 参数（`@Body`、`@Param`、`@Query`）是 FastAPI 参数：类型注释、`Query`、`Path`、`Body`。
- 管道是 Pydantic 验证和 FastAPI 依赖项。

`@Query()`、DTO 和保护类成为注释、Pydantic 模型和函数：

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

## 缺少什么

| NestJS 特征 | 内克西的现状 |
|---|---|
| 自定义提供程序（`useValue`、`useFactory`、`useClass`、字符串标记） | 不可用：仅 `@Injectable()` 类 |
| 通过接口或抽象类注入 | 不可用 |
| 模块封装 | 不强制：容器是进程范围的，`exports` 仅控制急切解析 |
| 动态和全局模块（`forRoot`、`@Global`） | 不可用 |
| 生命周期挂钩（`onModuleInit`、`onApplicationShutdown`） | 不可用 |
| 拦截器 | 使用 ASGI 中间件（`useMiddlewares`）或依赖项 |
| 异常过滤器 | 使用 FastAPI 异常处理程序 |
| 使用提供者覆盖测试模块 | 没有公共API；使用 FastAPI `dependency_overrides` 和 `TestClient` |
| 配置模块、调度、队列、CQRS、微服务、缓存 | 不属于 Nexy 的一部分；使用 Python 生态系统 |

代替 `useFactory` 提供程序，使用 `Depends` 后面的普通函数，测试用 `dependency_overrides` 覆盖它：

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

## 什么时候去采摘

当您需要基于类的结构并为更大的 API 注入时，请选择模块化路由器。当 URL 结构是组织原则时，选择基于文件的路由器。两者均由 `nx new` 搭建，在同一 FastAPI 应用程序上运行，并且可以共存。

> [!NOTE]
> 上面缺失的项目是诚实的差距。如果您今天在测试中需要 `useFactory` 提供程序或可重写提供程序，请将逻辑保留在普通函数和 FastAPI `Depends` 中，它们会自然地组合和重写。

## 后续步骤

- [依赖注入](dependency-injection.md)
- [守卫和元数据](guards-and-metadata.md)
- [测试](../../guides/testing.md)
