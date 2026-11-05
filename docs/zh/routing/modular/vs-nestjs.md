# 尼克西和 NestJS

模块化路由器的灵感来自于 NestJS：控制器、模块和构造函数注入。它是 FastAPI 上的薄层，因此它不会尝试重现所有 NestJS。此页列出了双方。

## 什么匹配

| NestJS | 尼克西 |
|---|---|
| `@Controller('users')` | `@Controller(prefix="/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` 具有相同的四个类属性 |
| `@Injectable()` | `@Injectable()` |
| 从类型注释 | 解析的构造函数注入 | `__init__` 参数
| 单例、请求和瞬态作用域 | `Scope.SINGLETON`、`Scope.REQUEST`、`Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)`（FastAPI 依赖项）|
| `@ApiOperation`、`@ApiResponse`（招摇）| `@UseRoute`、`@UseResponse`（OpenAPI，服务于 `/docs`）|
| 控制器 | 上的 WebSocket 网关 | `async def SOCKET(...)`
| DTO 验证 (`class-validator`) | Pydantic 模型，原生于 FastAPI |
| 循环依赖检测 | `RecursionError` 命名类 |

## 有什么不同

- 处理程序是以 HTTP 动词（`get`、`post`...）命名的方法，每个控制器一个。
- 守卫和中间件装饰器是 FastAPI `Depends`，而不是 `canActivate` 的类。
- 参数（`@Body`、`@Param`、`@Query`）是 FastAPI 参数：类型注释、`Query`、`Path`、`Body`。
- 管道是 Pydantic 验证和 FastAPI 依赖项。

## 缺少什么

| NestJS 功能 | Nexy 的状态 |
|---|---|
| 自定义提供程序（`useValue`、`useFactory`、`useClass`、字符串标记）| 不可用：仅 `@Injectable()` 类 |
| 通过接口或抽象类注入 | 不可用 |
| 不强制执行模块封装 |：容器是进程范围的，`exports` 仅控制急切解析 |
| 动态和全局模块（`forRoot`、`@Global`）| 不可用 |
| 生命周期挂钩（`onModuleInit`、`onApplicationShutdown`）| 不可用 |
| 拦截器 | 使用ASGI中间件（`useMiddlewares`）或依赖项 |
| 异常过滤器 | 使用 FastAPI 异常处理程序 |
| 使用提供者覆盖的测试模块 | 无公共 API；使用 FastAPI `dependency_overrides` 和 `TestClient` |
| 配置模块、调度、队列、CQRS、微服务、缓存 | 不是 Nexy 的一部分；使用 Python 生态系统 |

## 什么时候去采摘

当您需要基于类的结构并为更大的 API 注入时，请选择模块化路由器。当 URL 结构是组织原则时，选择基于文件的路由器。两者均由 `nx new` 搭建，在同一 FastAPI 应用程序上运行，并且可以共存。

> [!NOTE]
> 上面缺失的项目是诚实的差距。如果您今天在测试中需要 `useFactory` 提供程序或可重写提供程序，请将逻辑保留在普通函数和 FastAPI `Depends` 中，它们会自然地组合和重写。

## 后续步骤

- [依赖注入](dependency-injection.md)
- [守卫和元数据](guards-and-metadata.md)
- [测试](../../guides/testing.md)
