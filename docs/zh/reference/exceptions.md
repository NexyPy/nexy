# 异常和错误

一个请求可能会在四个地方失败，并且 Nexy 对每个地方的响应都不同。此页为索引：
找到您看到的状态，然后是生成它的行，然后是决定正文的文件。

> [!注意]
> 三件事是独立且容易混淆的：**HTTP 应答**（状态和正文）、
> **错误页**（`notfound.nexy`、`errors.nexy`）和**日志行**（您在
> 终端）。改变页面不改变状态，自定义页面不隐藏
> 日志。

## 简短版本

| 发生了什么 | 状态 | 浏览器看到 | API 客户端看到 |
|---|---|---|---|
| 没有路由与 URL | `404` | `notfound.nexy` 匹配，否则内置页面 | `{"detail": "Not Found"}` |
| 路径段不适合其注释 | `404` | 同一页 | `{"detail": "Not Found"}` |
| 查询、标头、cookie 或正文字段丢失或无效 | `422` | FastAPI 的 JSON 正文 | FastAPI 的 JSON 正文 |
| `notFound()` | `404` | 页 | `{"detail": ...}` |
| `unauthorized()` | `401` | 内置页面 | `{"detail": ...}` |
| `forbidden()` | `403` | 内置页面 | `{"detail": ...}` |
| `raise HTTPException(409, ...)` | `409` | 内置页面 | `{"detail": ...}` |
| 没有捕获任何异常 | `500` | `errors.nexy`，否则内置页面 | `{"detail", "reference"}` |
| `redirect(url)` | `307` | 目标，无页面 | 目标，无正文 |
| `permanentRedirect(url)` | `308` | 目的地，无页 | 目的地 |

API 客户端是一个请求，其 `Accept` 标头要求 JSON，而不是页面：

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [！警告]
> `curl` 默认发送 `Accept: */*`，获取 HTML 页面。添加
> `-H "Accept: application/json"` 当您测试 JSON 形状时。浏览器不断获取页面。

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

| 阶段 | 什么会失败 | 答案 |
|---|---|---|
| 中间件 | 您的 `middleware.py`、CORS、会话 | 异常状态，否则 `500` |
| 路由器 | URL 与文件不匹配 | `404` |
| 验证 | 路径段无法转换 | `404` |
| 验证 | 查询、标头、cookie 或正文字段 | `422` |
| 页面、处理程序、操作、防护 | `HTTPException` | 其状态 |
| 页面、处理程序、操作、防护 | 任何其他内容 | `500` |

## 从任何地方出发

`redirect`、`permanentRedirect`、`notFound`、`forbidden` 和 `unauthorized` 引发 HTTP 异常，
所以相同的调用可以在 `.nexy` 页面、API 处理程序、模块化控制器、守卫、
`dependencies.py` 和一个动作。

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

| 呼叫 | 应答 | 当 |
|---|---|---|
| `notFound(detail=None)` | `404` | 资源不存在 |
| `unauthorized(detail=None, scheme=None)` | `401` | 访客必须先登录 |
| `forbidden(detail=None)` | `403` | 访问者是已知的，但可能看不到此 |
| `redirect(url, status=307)` | `307` | 将它们发送到其他地方，保留方法 |
| `redirect(url, status=303)` | `303` | 表单后：下一个请求是 `GET` |
| `permanentRedirect(url)` | `308` | 搜索引擎应记住的已移动页面 |

根据您信任的价值观打造目的地。 `redirect(request.query_params["next"])` 发送访客
无论链接显示什么地方；这是一个开放的重定向。包含换行符的目的地将被拒绝。

## 验证：422或404

处理程序参数由 FastAPI 根据其注释进行验证。

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| 问题 | 状态 | 为什么 |
|---|---|---|
| 查询、标头、cookie 或正文字段缺失或无效 | `422` | 请求已到达处理程序，数据错误 |
| 无效路径段（`id: int` 的 `/api/users/abc`） | `404` | 该文件夹没有非数字的路由，因此 URL 不存在 |

`422` 主体是 FastAPI 的标准形状，因此客户端和生成的 SDK 可以继续工作：

```json
{"detail": [{"loc": ["query", "q"], "msg": "Field required", "type": "missing"}]}
```

对于表单或操作，客户端会收到带有 `status` 和 `detail` 的 `ActionError`；一个`422`
还为每个字段填充一条消息 `error.fields`。请参阅[操作](../guides/actions.md#errors-and-failures)。

> [!提示]
> 当规则是关于一个字段（`limit: int = 10`）时在签名中进行验证。验证在
> 正文，当规则需要数据库或其他字段时（“此电子邮件已被使用”）：raise
> `HTTPException(409)`并为客户端保留消息。

## 自定义错误页面

```nexy filename="src/routes/notfound.nexy"
<h1>Page not found</h1>
<p>The link may be old. <a href="/">Start from the home page</a>.</p>
```

```nexy filename="src/routes/errors.nexy"
<h1>Something went wrong</h1>
<p>Try again in a moment.</p>
```

| 文件 | 状态 | 范围 |
|---|---|---|
| `src/routes/notfound.nexy` | `404` | 项目每条路线 |
| `src/routes/errors.nexy` | `500` | 项目每条路线 |
| `src/routes/forbidden.nexy` | `403` |该项目的每条路线|
| `src/routes/unauthorized.nexy` | `401` | 项目每条路线 |
| `src/routes/blog/notfound.nexy` | `404` | `/blog` 及以下 |
| `src/routes/blog/errors.nexy` | `500` | `/blog` 及以下 |
| `src/routes/loading.nexy` | - | 保留，尚未运行时效果 |

路由中某处的一个文件安装了其状态的答案：根目录的一个副本回答了
整个项目，文件夹中的副本回答该文件夹，以及与 URL 匹配的最深文件
获胜。每个副本外部的 URL 以及根本没有文件的状态，获取内置样式的页面。
请参阅[每个文件夹的错误页](../routing/fbr/errors/folder-pages.md)。

> [！重要]
> `errors.nexy`页面取代`500`页面；它没有捕获异常并且它没有
> 更改日志行。如果引发的处理程序是页面本身，则该页面无法显示自己的
> 错误详细信息：保持`errors.nexy`简单且独立。

## 未处理的异常

一个例外，即没有捕获任何内容，并且会记录一次，并包含其引用、来源和代码
围绕它。状态是`500`，身体取决于环境。

| | `nexy dev` | `nexy build` 然后 `nexy start` |
|---|---|---|
| 浏览器 | 错误、代码行和回溯 | `errors.nexy`，其他内置页面，带有引用 |
| API 客户端 | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| 终端 | 异常和代码行 | 异常、整个回溯和引用 |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

参考号是八个字符，每次失败都是新的。访客可以引用它，然后您会发现
通过搜索日志进行回溯。异常和代码都没有到达访问者
生产。

> [！警告]
> 不要将回溯返回给生产中的访问者，并且不要将机密放入错误中
> 消息：`HTTPException`的`detail`被发送到客户端，HTML转义。把秘密放进去
> 日志，不在答案中。

## 行动和形式

操作是具有生成路径的 `POST` 端点。它的失败遵循相同的规则：

| 情况 | 状态 | 客户端 |
|---|---|---|
| 字段丢失或无效 | `422` | `ActionError` 和 `fields` |
| `HTTPException(403)` 在 | `403` | `ActionError` 中与 `status` 和 `detail` | 一起提出
| 未处理的异常 | `500` | `ActionError`；参考位于服务器日志 |
| `Origin` 标头是另一个站点 | `403` | 在操作运行之前被拒绝 |

没有 JavaScript 的表单会发布到操作路径；成功回答`303`返回页面，a
失败显示错误页面。请参阅[操作](../guides/actions.md#forms-without-javascript)。

## 页面回答错误时的清单

1. **查看状态**，而不是页面。自定义 `notfound.nexy` 仍会回答 `404`。
2. **读取终端。**导入失败的页面未注册，因此其 URL 会回答 `404`
   当文件存在时。导入错误在日志中。
3. **检查扩展名。**与`useCSR = True`、`.nexy`页面属于服务器模式；中的一个页面
   错误的模式不是路线。
4. **检查深度。** `notfound.nexy` 或 `errors.nexy` 仅在根副本存在时才有效。
5. **使用 `Accept: application/json` 请求 JSON** 以查看 API 客户端收到的形状。
6. **在打开问题或搜索日志时引用 `500` 的参考文献 **。

## 后续步骤

- [错误页面](../routing/fbr/errors/README.md)：完整页面行为，带有示例
- [验证和错误](../routing/fbr/handlers/validation-and-errors.md)：API 处理程序
- [故障排除](../guides/troubleshooting.md)：人们实际遇到的错误
- [测试](../guides/testing.md)：断言状态和主体