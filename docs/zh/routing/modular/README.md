# 模块化路由

模块化路由使用带有装饰器的类而不是 `src/routes/`: 控制器下的文件
处理请求，模块将它们分组，并注入提供者。安装生成的 `APIRouter`
与`nexyconfig.py`中的`useRouter`。

**开始之前：**一个 Nexy 项目和一个工作页面。模块化路由器取代了
基于文件的路由器，因此如果您还没有选择路由器，请先阅读[路由](../README.md)。

| 页 | 涵盖内容 |
|---|---|
| 本页 | 安装模块、写入控制器、组控制器 |
| [依赖注入](dependency-injection.md) | `@Injectable`，作用域，容器|
| [守卫和元数据](guards-and-metadata.md) | `@UseGuard`、`@Middleware`、`@UseRoute`、`@UseResponse` |
| [Nexy 和 NestJS](vs-nestjs.md) | 什么与 NestJS 匹配，什么不匹配 |

## 设置路由器

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

> [！注意]
> 基于文件的路由继续工作。如果 `src/routes/` 存在，则即使
> 当设置`useRouter`时。

## 编写一个控制器

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
```

方法按名称匹配，不区分大小写：`get`、`post`、`put`、`patch`、`delete`、`options`、
`head`，`trace`。

控制器为每个 HTTP 方法声明一个处理程序；启动时重复加注。添加前缀
`@Controller(prefix="/users")` - 每个处理程序都安装在 `prefix/` 上。 `async def SOCKET(...)` 上
控制器在同一路径注册一个 WebSocket。

## 模块中的组控制器

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

`@Module(prefix="/api")` 返回 `APIRouter`。 `controllers` 为必填项； `providers`，`imports`
和 `exports` 是可选的。导入的模块作为子路由器安装，其导出的提供程序
在启动时解决。

## 来自控制器的视图

控制器可以返回页面。 `useViews` 渲染 `.nexy` 视图；将一个嵌套在另一个中以将其包裹起来
在布局中：

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

参见`examples/Modular/api/minimal/`。

## 后续步骤

- [依赖注入](dependency-injection.md)：服务和范围
- [守卫和元数据](guards-and-metadata.md)：保护和记录路径
- [路由](../README.md)：基于文件的路由器
- [配置](../../reference/config.md)：每个选项，包括`useRouter`