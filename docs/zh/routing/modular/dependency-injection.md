# 依赖注入

Nexy 解决控制器和服务的构造函数依赖关系。一个类选择加入 `@Injectable()`。

## 注入服务

```python filename="src/apps/users/user_service.py"
from nexy.decorators import Injectable


@Injectable()
class UserService:
    def get_all(self) -> list[dict]:
        return [{"id": 1, "name": "Ada"}]
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller
from .user_service import UserService


@Controller("/users")
class UserController:
    def __init__(self, svc: UserService) -> None:
        self.svc = svc

    def get(self) -> list[dict]:
        return self.svc.get_all()
```

在模块中注册控制器。在 `providers` 中列出服务还可以在启动时急切地解决它：

```python filename="src/apps/users/users_module.py"
from nexy.decorators import Module
from .user_controller import UserController
from .user_service import UserService


@Module()
class UsersModule:
    controllers = [UserController]
    providers = [UserService]
```

## 分辨率如何运作

- 每个 `__init__` 参数都是从其 **类型注释** 解析的。注解必须是 `@Injectable()` 类，或者参数必须有默认值；否则分辨率会提高 `ValueError`。
- 控制器在启动时用 `Container.resolve()` 实例化。
- 依赖循环引发 `RecursionError` 命名类。
- 服务可以注入其他服务到任何深度。

## 范围

```python
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class CurrentUser: ...
```

| 适用范围 | 终身 |
|---|---|
| `Scope.SINGLETON`（默认） | 一个实例说明整个过程 |
| `Scope.REQUEST` | 每个请求上下文一个实例 |
| `Scope.TRANSIENT` | 每个决议都有一个新实例 |

## 容器

```python
from nexy.decorators import Container

service = Container.resolve(UserService)
```

自己构造一个 `@Injectable()` 类会引发 `TypeError`：容器拥有其生命周期。使用 `Container.resolve(...)` 或通过另一个构造函数接收类。

`Container.clear_request_scope()` 删除当前请求的实例。

## 路由参数

FastAPI `Depends` 像往常一样处理处理程序参数，在构造函数注入旁边：

```python
from fastapi import Depends


def get(self, limit: int = Depends(pagination)) -> list[dict]: ...
```

## 限制

该容器是进程范围的。每个模块的提供程序并不是隔离的，`exports` 仅决定导入模块急切解析哪些提供程序，并且没有公共 API 可以在测试中交换提供程序。有关完整比较，请参阅 [Nexy 和 NestJS](vs-nestjs.md)。

## 后续步骤

- [守卫和元数据](guards-and-metadata.md)
- [测试](../../guides/testing.md)
