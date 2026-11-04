# 守卫和元数据

保护路由并在 OpenAPI 模式中描述它的装饰器。

## 守卫

`@UseGuard(*guards)` 适用于控制器（每种方法）或一种方法。每个守卫都被添加为
FastAPI `Depends`，因此它声明了它需要的参数并引发拒绝调用：

```python filename="src/apps/admin/admin_controller.py"
from fastapi import Header, HTTPException
from nexy.decorators import Controller, UseGuard


def require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller(prefix="/admin")
@UseGuard(require_token)
class AdminController:
    async def get(self) -> dict:
        return {"ok": True}
```

## 中间件装饰器

`@Middleware(*middlewares)` 的行为方式相同：这些是 FastAPI 依赖项，而不是 ASGI
中间件。对于真正的 ASGI 中间件，请使用 `useMiddlewares`
[配置](../../reference/config.md)或[中间件和安全性](../../guides/middleware-and-security.md)。

## 路线元数据

`@UseRoute(...)` 设置 OpenAPI 元数据。它不会改变路径。

| 参数 | 含义 |
|---|---|
| `name` | 路线名称 |
| `tags` | OpenAPI 标签 |
API 参考中的 | `summary`、`description` | 文本 |
| `deprecated` | 标记该操作已弃用 |
| `include_in_schema` | 从架构中隐藏路由 |
| `operation_id` | 显式操作 ID |
| `openapi_extra` | 额外的 OpenAPI 字段 |

## 回应

`@UseResponse(...)` 设置 `status_code`、`response_class`、`response_model`、`responses` 和
序列化选项。

```python
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller(prefix="/users")
class UserController:
    @UseRoute(summary="List users", tags=["users"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

生成的 API 参考在 `/docs` 处提供，除非 `useDocs = False`。

## 后续步骤

- [依赖注入](dependency-injection.md)
- [API 路由](../fbr/handlers/README.md)：基于文件的处理程序的相同选项