# 自定义路由集成

Nexy 允许您将现有的 FastAPI 应用程序作为路由器包含到您的项目中。当您想要重用其他服务的后端逻辑、与第三方 API 集成或构建具有多个路由问题的复合应用程序时，这非常有用。

与 Nexy 固有的基于文件和模块化路由器不同，自定义路由器只是您安装到应用程序中的 `APIRouter`。

## 何时使用自定义路由器

- **第三方服务**：您有一个现有的 FastAPI 应用程序，想要通过 Nexy 的客户端公开。
- **代码重用**：将后端逻辑从另一个项目提取到路由器中并将其包含在新项目中。
- **多租户或微前端模式**：每个租户或模块提供自己的路由器。
- **逐步迁移**：从`APIRouter`开始，稍后将其发展为完整的Nexy模块。

## 它是如何工作的

```python
from fastapi import APIRouter
from nexy import useRouter

# An existing FastAPI router (from another service)
third_party = APIRouter()
@third_party.get("/info")
async def info():
    return {"name": "Foo"}

# In your nexyconfig.py:
useRouter = third_party
```

路由器由 Nexy 的路由器解析器自动安装。它的路由在与原始应用程序相同的 URL 模式下可用。不需要额外的配置。

## 构建自定义路由器

1. **创建路由器**
   ````蟒蛇
   从 fastapi 导入 APIRouter

   api = API 路由器()
   @api.get("/状态")
   异步定义状态（）：
       返回{“状态”：“确定”}
   ````

2. **参考`nexyconfig.py`**
   ````蟒蛇
   从 .my_backend 导入 api

   使用路由器=api
   ````

3. **访问路线**
   - 基于文件的页面（`.nexy`、`.md`）和模块化处理程序可以像引用任何其他路由一样引用`/status`。
   - 路由器在同一进程中运行，因此依赖项、数据库连接和身份验证的工作方式与原始应用程序中完全相同。

## 与其他路由器集成

Nexy 项目可以结合：

- **基于文件的路由**（`src/routes/`）用于页面和简单端点
- **结构化后端的模块化路由**（`useRouter = AppModule`）
- **第三方代码的自定义路由** (`useRouter = APIRouter`)

三者共存；每条路线仅注册一次。当 `src/routes/` 存在时，始终会扫描基于文件的路由器。

## 对包含的应用程序的 CLI 访问

`nexy dev` 和 `nx` 命令在已安装的路由器上运行，就像内置路由器一样。你得到：

- 自定义路由器中定义的端点的热重载（如果它使用`nexy`或FastAPI的常用开发服务器功能）
- 在`nexyconfig.py`中验证（任何`APIRouter`作品）
- 为所包含的路由自动生成文档（如果启用它们）

## 安全和隔离

因为包含路由器，而不是通过 `app.mount` 安装，所以没有额外的 ASGI 层。路由器与基于文件的模块化路由位于同一应用程序对象中。这意味着：

- 自定义路由器添加的中间件适用于所有请求。
- 自定义路由器中定义的防护和依赖项注入可以访问与您自己的代码相同的容器（如果您使用模块化注入）。
- 除了路由器本身定义的之外，没有其他 URL 前缀。

如果需要隔离，请在包含路由器之前将其包装在子应用程序中，或使用标准 FastAPI 技术。

## 示例：包括现有的 FastAPI 项目

假设你在另一个包中有 `auth.py`：

```python
from fastapi import FastAPI, APIRouter

auth = FastAPI(title="Auth service")
api = APIRouter()

@api.get("/login")
async def login():
    return {"msg": "Login"}

auth.include_router(api)
```

在`nexyconfig.py`中：

```python
from other_package.auth import api

useRouter = api
```

现在无需移动任何代码即可从您的 Nexy 站点访问 `/login` 端点。

## 如何开始

1. 创建您的`APIRouter`（或在现有包中找到一个）。
2. 将`useRouter`指向`nexyconfig.py`中的它。
3. 通过页面、处理程序或客户端框架访问其路由。
4. 如果您需要更多控制，请使用`AppModule`将自定义路由器转换为模块化路由器。

## 后续步骤

- [基于文件的路由](../fbr/README.md) – 从文件构建页面和简单的处理程序。
- [模块化路由](../modular/README.md) – 具有注入和防护的结构化后端。
- [路由处理程序](../fbr/handlers/README.md) – 定义Python端点。

自定义路由器使您能够灵活地重用现有的 FastAPI 代码，同时保持基于文件的页面和模块化结构的简单性。