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

## 速率限制

`useRateLimit` 应答 `429 Too Many Requests` 到在 `per` 秒的一个窗口内发送超过 `requests` 个请求的客户端地址。

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useRateLimit = {"requests": 60, "per": 60, "paths": ["/api/", "/_nx_"]}
```

Nexy 保证超出限制的请求会获得带有 `Retry-After` 标头的 `429`、窗口中剩余的秒数，并且永远不会到达您的路由、操作或中间件。

Nexy 保证在没有 `useRateLimit` 的情况下不会添加速率限制中间件。

Nexy 保证 `useHealth` 探针永远不受限制。

`paths` 是可选的：没有它，每条路径都会受到限制。服务器操作在 `/_nx_` 下提供，因此前缀限制了所有这些操作。

该窗口是固定的并由所有客户端共享：计数在每个 `per` 秒的倍数处重新开始。因此，客户端最多可以跨窗口边缘发送两次 `requests`。

计数存在于每个工人的记忆中。当 `useWorkers` 大于 1 时，客户端可以向每个工作线程发送 `requests`，并且当服务器重新启动时计数会重新开始。

客户端地址是 uvicorn 发出请求的地址。在同一台机器上的反向代理后面，uvicorn 从 `X-Forwarded-For` 读取它；对于另一台计算机上的代理，请在 `FORWARDED_ALLOW_IPS` 环境变量中列出其地址，或者每个客户端共享代理的地址。

您的应用程序负责由多个工作人员或服务器共享的限制：反向代理或存储（例如 Redis）。

## HTTPS

直接使用 `useSslKeyfile` 和 `useSslCertfile` 提供 HTTPS，或在反向代理处终止 TLS 并设置 `useHTTPSRedirect`。在开发过程中，Vite 开发服务器保持在 Nexy 源后面的环回 HTTP 上，因此 TLS 永远不会到达它。

## 生产清单

- `useDocs = False` 如果 OpenAPI 架构不应公开。
- `useTrustedHost` 设置为您的域，以阻止主机标头攻击。
- `useCORS` 具有明确的来源，绝不 `["*"]` 与凭证一起。
- 一个真正的会话 `secret_key`，从环境中读取。
- 传递给客户端组件的 Props 由 Nexy 进行 HTML 转义。不要在模板中标记用户输入 `| safe`。

## 守卫和依赖

每个路由的保护使用 FastAPI 依赖项。路由目录中的 `dependencies.py` 适用于其下面的所有内容：请参阅 [依赖关系 ](../routing/fbr/dependencies/README.md)。在模块化路由器中使用[`@UseGuard`](../routing/modular/guards-and-metadata.md)。

## 后续步骤

- [配置](../reference/config.md)：每个中间件字段
- [部署](../deployment/README.md)
- [性能](../deployment/performance.md)
