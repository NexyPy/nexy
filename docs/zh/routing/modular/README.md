# 模块化路由

模块化路由使用带有装饰器的类而不是 `src/routes/` 下的文件：控制器处理请求，模块对它们进行分组，并注入提供程序。将生成的 `APIRouter` 与 `useRouter` 安装在 `nexyconfig.py` 中。

**开始之前：** 一个 Nexy 项目和一个工作页面。模块化路由器取代了基于文件的路由器，因此如果您尚未选择路由器，请先阅读[路由](../README.md)。

| 页面 | 它涵盖什么 |
|---|---|
| 本页 | Mount a module, write a controller, group controllers |
| [依赖注入](dependency-injection.md) | `@Injectable`，范围，容器 |
| [守卫和元数据](guards-and-metadata.md) | `@UseGuard`、`@Middleware`、`@UseRoute`、`@UseResponse` |
| [尼克西和 NestJS](vs-nestjs.md) | 什么匹配 NestJS，什么不匹配 |

## 设置路由器

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

> [!NOTE]
> 基于文件的路由继续工作。如果存在 `src/routes/`，即使设置了 `useRouter` 也会扫描。

## 写一个控制器

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
```

方法按名称匹配，不区分大小写：`get`、`post`、`put`、`patch`、`delete`、`options`、`head`、`trace`。

A controller declares one handler per HTTP method;启动时重复加注。 The first argument of `@Controller("/users")` is the path every handler answers on, `/users/`.控制器上的 `async def SOCKET(...)` 在同一路径上注册 WebSocket。

## 模块中的组控制器

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

`@Module(prefix="/api")` 返回 `APIRouter`。 `controllers` 为必填项； `providers`、`imports` 和 `exports` 是可选的。导入的模块作为子路由器安装，其导出的提供程序在启动时解析。

## 来自控制器的视图

控制器可以返回页面。 `useViews` 渲染 `.nexy` 视图；将一个嵌套在另一个中以将其包装在布局中：

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller()
class AppController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/app_view.nexy"),
        })
```

请参阅[布局](../fbr/layouts/README.md)。

## 示例

参见 `examples/Modular/api/minimal/`。

## 后续步骤

- [依赖注入](dependency-injection.md)：服务和范围
- [Guards and metadata](guards-and-metadata.md): protect and document routes
- [路由](../README.md)：基于文件的路由器
- [配置](../../reference/config.md)：每个选项，包括 `useRouter`
