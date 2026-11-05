# 中间件和安全

Nexy 在 FastAPI 和 Starlette 上运行，因此它们的中间件适用。常见的是 `nexyconfig.py`中的一行。

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {
        "allow_origins": ["https://app.example.com"],
        "allow_methods": ["GET", "POST"],
        "allow_credentials": True,
    }
    useGZip = {"minimum_size": 1000}
    useTrustedHost = {"allowed_hosts": ["example.com", "*.example.com"]}
    useHTTPSRedirect = True
    useSession = {"secret_key": "change-me"}
```

每个 `use*` 字典都作为关键字参数传递给匹配的 Starlette 中间件：`CORSMiddleware`、`GZipMiddleware`、`TrustedHostMiddleware`、`SessionMiddleware`。

## 您自己的中间件

```python filename="nexyconfig.py"
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` 采用 ASGI 中间件类。

## HTTPS

直接使用 `useSslKeyfile` 和 `useSslCertfile` 提供 HTTPS，或在反向代理处终止 TLS 并设置 `useHTTPSRedirect`。在开发过程中，Vite 开发服务器保持在 Nexy 源后面的环回 HTTP 上，因此 TLS 永远不会到达它。

## 生产清单

- `useDocs = False` 如果 OpenAPI 架构不应公开。
- `useTrustedHost` 设置为您的域，以阻止主机标头攻击。
- `useCORS` 具有明确的来源，绝不 `["*"]` 与凭证一起。
- 一个真正的会话 `secret_key`，从环境中读取。
- 传递给客户端组件的属性由 Nexy 进行 HTML 转义。不要在模板中标记用户输入 `| safe`。

## 守卫和依赖

每个路由的保护使用 FastAPI 依赖项。路由目录中的 `dependencies.py` 适用于其下面的所有内容：请参阅 [依赖项 ](../routing/fbr/dependencies/README.md)。在模块化路由器中使用[`@UseGuard`](../routing/modular/guards-and-metadata.md)。

## 后续步骤

- [配置](../reference/config.md)：每个中间件字段
- [部署](../deployment/README.md)
- [性能](../deployment/performance.md)
