# 中间件文件

路由目录中的 `middleware.py` 包装了该目录处理的请求。与布局和 `dependencies.py` 一样，文件从路由根部向下堆叠，最外层在前。

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request
from nexy.http import JSONResponse


async def middleware(request: Request, call_next):
    if request.headers.get("authorization") != "Bearer secret":
        return JSONResponse({"detail": "login required"}, status_code=401)
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

函数为 `async def middleware(request, call_next)`：FastAPI的 `@app.middleware("http")`的签名。呼叫 `await call_next(request)` 继续路线，或返回响应以停在那里。调用后的代码在退出时运行并可以更改响应。

## 它包裹着什么

中间件适用于文件位于其目录 **或以下的** 路由、页面和 API 处理程序，包括路由组：

```text
src/routes/
├─ middleware.py             every route
├─ open.py                   root only
├─ admin/
│  ├─ middleware.py          /admin and everything below
│  └─ users/
│     ├─ middleware.py       /admin/users and below
│     └─ index.py            root > admin > users
└─ (shop)/
   ├─ middleware.py          only the routes in this group
   └─ cart.py                root > shop     (URL: /cart)
```

对于对 `/admin/users` 的请求，顺序是 `root`、`admin`、`users`，然后是路由。组没有自己的 URL，因此它是通过服务请求的路由而不是 URL 进行匹配的。

不匹配任何路由（404）的 URL 仅接收按 URL 前缀选择的非组目录的中间件。 `[slug]` 匹配一个段，`[...rest]` 匹配其余部分。

## 它不包裹什么

- 框架和资产 URL：`/__nexy__/`、`/_nexy/`、`/public/`、`/assets/` 和 `/@...` (Vite)。
- WebSocket 处理程序和服务器生命周期：仅限 HTTP 请求。
- 以 `_` 或 `.` 开头的目录中的文件。

## 中间件、依赖项或防护程序

| 当 | 时使用 |
|---|---|
| `middleware.py` | 你也需要 **响应**：整个区域的标头、重定向、计时、短路 |
| [`dependencies.py`](../dependencies/README.md) | 你需要解析参数或注入一个值（当前用户，数据库会话）|
| `@UseGuard` 在处理程序上 | 一条路由需要额外检查 |
| [[配置](../../../reference/config.md)] | 中的 `useMiddlewares` 用于整个应用程序（CORS、GZip、会话）的 ASGI 中间件 |

中间件文件在 **依赖项之前运行**：当依赖项启动时，请求已通过其目录的每个 `middleware.py`。

## 规则

- 该文件必须定义 `async def middleware(request, call_next)`。否则，Nexy 将在启动时停止并命名该文件。
- 这是一个普通的 Python 模块：导入你需要的内容。当服务器启动时，它会加载一次。
- 它从来都不是一条路线：`/middleware` 是 404。
- 基本路径检查 `request.scope["path"]`，而不是 `request.url.path` 或 `Host` 标头：自 CVE-2026-48710 起，URL 对象可能与服务器收到的路径不一致。请参阅[安全性](../../../reference/security.md)。

## 成本

没有任何 `middleware.py` 的项目无需支付任何费用：未安装该层。对于文件，每个匹配的中间件都会添加一个 Starlette `BaseHTTPMiddleware`；保持它们很小。

## 后续步骤

- [继承](../inheritance.md)
- [依赖关系](../dependencies/README.md)
- [中间件和安全](../../../guides/middleware-and-security.md)
