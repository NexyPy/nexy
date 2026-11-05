# 异常和错误

一个请求可能会在四个地方失败，并且 Nexy 对每个地方的响应都不同。此页面是索引：找到您看到的状态，然后是生成它的行，然后是决定正文的文件。

> [!NOTE]
> 三件事是独立且容易混淆的：**HTTP 应答**（状态和正文）、**错误页面**（`notfound.nexy`、`errors.nexy`）和 **日志行**（您在终端中读取的内容）。更改页面不会更改状态，自定义页面不会隐藏日志。

## 简短版本

| 发生了什么 | 状态 | 浏览器看到 | API客户端看到 |
|---|---|---|---|
| 没有路由与 URL 匹配 | `404` | `notfound.nexy`，否则为内置页面 | `{"detail": "Not Found"}` |
| 路径段不适合其注释 | `404` | 同一页 | `{"detail": "Not Found"}` |
| 查询、标头、cookie 或正文字段丢失或无效 | `422` | FastAPI 的 JSON 正文 | FastAPI 的 JSON 正文 |
| `notFound()` | `404` | 页面 | `{"detail": ...}` |
| `unauthorized()` | `401` | 内置页面 | `{"detail": ...}` |
| `forbidden()` | `403` | 内置页面 | `{"detail": ...}` |
| `raise HTTPException(409, ...)` | `409` | 内置页面 | `{"detail": ...}` |
| 没有捕获任何异常 | `500` | `errors.nexy`，否则为内置页面 | `{"detail", "reference"}` |
| `redirect(url)` | `307` | 目的地，无页面 | 目的地，没有尸体 |
| `permanentRedirect(url)` | `308` | 目的地，无页面 | 目的地 |

API 客户端是一个请求，其 `Accept` 标头要求 JSON，而不是页面：

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!WARNING]
> `curl` 默认发送 `Accept: */*`，获取 HTML 页面。测试 JSON 形状时添加 `-H "Accept: application/json"`。浏览器不断获取页面。

## 失败从何而来

```diagram filename="一次请求，四次退出"
Browser ──► Middleware ──► Router ──► Page or handler
                 │            │             │
                 │            │             ├─ return ───────────► 200
                 │            │             ├─ HTTPException ────► its status
                 │            │             └─ other exception ───► 500
                 │            └─ no match ────────────────────────► 404
                 └─ raises ──────────────────────────────────────► 500
```

| 舞台 | 什么会失败 | 答案 |
|---|---|---|
| 中间件 | 您的 `middleware.py`、CORS、会话 | 异常的状态，否则 `500` |
| 路由器 | URL 不匹配任何文件 | `404` |
| 验证 | 路径段无法转换 | `404` |
| 验证 | 查询、标头、cookie 或正文字段 | `422` |
| 页面、处理程序、操作、防护 | `HTTPException` | 它的状态 |
| 页面、处理程序、操作、防护 | 还有什么 | `500` |

## 从任何地方离开

`redirect`、`permanentRedirect`、`notFound`、`forbidden` 和 `unauthorized` 引发 HTTP 异常，因此相同的调用在 `.nexy` 页面、API 处理程序、模块化控制器、防护、`dependencies.py` 和操作中工作。

```python filename="src/routes/posts/[slug].py"
from nexy import notFound, redirect

from src.posts import find


async def GET(slug: str):
    post = find(slug)
    if post is None:
        notFound("No such post")
    if post.moved_to:
        redirect(post.moved_to)
    return post
```

| 致电 | 回答 | 当 |
|---|---|---|
| `notFound(detail=None)` | `404` | 该资源不存在 |
| `unauthorized(detail=None, scheme=None)` | `401` | 访客必须先登录 |
| `forbidden(detail=None)` | `403` | 访客是已知的，但可能看不到此内容 |
| `redirect(url, status=307)` | `307` | 将它们发送到其他地方，保留方法 |
| `redirect(url, status=303)` | `303` | 表单之后：下一个请求是 `GET` |
| `permanentRedirect(url)` | `308` | 搜索引擎应该记住的移动页面 |

根据您信任的价值观打造目的地。 `redirect(request.query_params["next"])` 将访问者发送到链接所在的任何地方；这是一个开放的重定向。包含换行符的目的地将被拒绝。

## 验证：422 或 404

处理程序参数由 FastAPI 根据其注释进行验证。

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| 问题 | 状态 | 为什么 |
|---|---|---|
| 查询、标头、cookie 或正文字段缺失或无效 | `422` | 请求到达处理程序，数据错误 |
| 无效路径段（`/api/users/abc` 对于 `id: int`） | `404` | 该文件夹没有非号码的路由，因此该 URL 不存在 |

`422` 主体是 FastAPI 的标准形状，因此客户端和生成的 SDK 可以继续工作：

```json
{"detail": [{"loc": ["query", "q"], "msg": "Field required", "type": "missing"}]}
```

对于表单或操作，客户端会收到带有 `status` 和 `detail` 的 `ActionError`； `422` 还用每个字段一条消息填充 `error.fields`。请参阅[操作](../guides/actions.md#errors-and-failures)。

> [!TIP]
> 当规则涉及一个字段 (`limit: int = 10`) 时，在签名中进行验证。当规则需要数据库或其他字段（“此电子邮件已被使用”）时，在正文中进行验证：引发 `HTTPException(409)` 并为客户端保留消息。

## 自定义错误页面

```nexy filename="src/routes/notfound.nexy"
<h1>Page not found</h1>
<p>The link may be old. <a href="/">Start from the home page</a>.</p>
```

```nexy filename="src/routes/errors.nexy"
<h1>Something went wrong</h1>
<p>Try again in a moment.</p>
```

| 文件 | 状态 | 适用范围 |
|---|---|---|
| `src/routes/notfound.nexy` | `404` | 项目的每条路线 |
| `src/routes/errors.nexy` | `500` | 项目的每条路线 |
| `src/routes/forbidden.nexy` | `403` | 项目的每条路线 |
| `src/routes/unauthorized.nexy` | `401` | 项目的每条路线 |
| `src/routes/blog/notfound.nexy` | `404` | `/blog` 及以下 |
| `src/routes/blog/errors.nexy` | `500` | `/blog` 及以下 |
| `src/routes/loading.nexy` | - | 保留，还没有运行时效果 |

路由中某处的一个文件会安装其状态的答案：根目录中的副本会回答整个项目，文件夹中的副本会回答该文件夹，而与 URL 匹配的最深文件将获胜。每个副本外部的 URL 以及根本没有文件的状态，获取内置样式的页面。请参阅[每个文件夹的错误页](../routing/fbr/errors/folder-pages.md)。

> [!IMPORTANT]
> `errors.nexy` 页面取代 `500` 页面；它不会捕获异常，也不会更改日志行。如果引发的处理程序是页面本身，则页面无法显示自己的错误详细信息：保持 `errors.nexy` 简单且独立。

## 未处理的异常

一个例外是，没有捕获任何内容都会被记录一次，并包含其引用、它来自哪里以及它周围的代码。状态是 `500`，身体取决于环境。

| | `nexy dev` | `nexy build` 然后 `nexy start` |
|---|---|---|
| 浏览器 | 错误、代码行和回溯 | `errors.nexy`，否则内置页面，带有参考 |
| API客户端 | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| 终端 | 异常和代码行 | 异常、整个回溯和引用 |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

参考号是八个字符，每次失败都是新的。访问者可以引用它，您可以通过在日志中搜索它来找到回溯。异常和代码都不会到达生产中的访问者。

> [!CAUTION]
> 不要将回溯返回给生产中的访问者，也不要将机密放入错误消息中：`HTTPException` 的 `detail` 被发送到客户端，经过 HTML 转义。将秘密放在日志中，而不是答案中。

## 动作和形式

操作是具有生成路径的 `POST` 端点。它的失败遵循相同的规则：

| 情况 | 状态 | 客户 |
|---|---|---|
| 字段缺失或无效 | `422` | `ActionError` 与 `fields` |
| `HTTPException(403)` 在行动中提出 | `403` | `ActionError` 与 `status` 和 `detail` |
| 未处理的异常 | `500` | `ActionError`；参考位于服务器日志中 |
| `Origin` 标头是另一个站点 | `403` | 在操作运行之前被拒绝 |

没有 JavaScript 的表单发布到操作路径；成功则返回 `303` 页面，失败则显示错误页面。请参阅[操作](../guides/actions.md#forms-without-javascript)。

## 当页面回答错误时的清单

1. **查看状态**，而不是页面。自定义 `notfound.nexy` 仍会回答 `404`。
2. **读取终端。** 导入失败的页面未注册，因此当文件存在时其 URL 会回答 `404`。导入错误在日志中。
3. **检查扩展名。** 与 `useCSR = True`、`.nexy` 页面属于服务器模式；错误模式的页面不是路由。
4. **检查深度。** `notfound.nexy` 或 `errors.nexy` 仅在根副本存在时才有效。
5. **请求 JSON** 和 `Accept: application/json` 以查看 API 客户端收到的形状。
6. **当您打开问题或搜索日志时，引用 `500` 的参考文献**。

## 后续步骤

- [错误页面](../routing/fbr/errors/README.md)：完整页面行为，带有示例
- [验证和错误](../routing/fbr/handlers/validation-and-errors.md)：API 处理程序
- [故障排除](../guides/troubleshooting.md)：人们实际遇到的错误
- [测试](../guides/testing.md)：断言状态和主体
