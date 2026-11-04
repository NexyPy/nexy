# 错误页面

失败的请求仍应像站点的其余部分一样进行回答：用您自己的话来表示一个页面
访问者，与 API 客户端的 JSON 相同的失败。 Nexy 回答了两个问题，并用一个文件替换了每个问题
回答。

此页面是地图：哪个文件回答哪个状态，以及如何制作您的第一个。的页面
文件夹获得[自己的页面](folder-pages.md)。

## 一次失败，两种答案

```diagram filename="谁回答失败的请求"
a request that fails
      │
      ├── a browser (Accept: text/html)              ──►  an HTML page
      └── an API client (Accept: application/json)   ──►  {"detail": "…"}  with the same status

the HTML page
      ├── the deepest folder of the URL that holds a file   ──►  your file
      └── no folder of the chain holds one                 ──►  the built-in page
```

## 您的第一页

创建 `src/routes/notfound.nexy` 并写入访问者应该阅读的内容：

```nexy filename="src/routes/notfound.nexy"
---
title: Page not found
---
<h1>Page not found</h1>
<p>The page moved or never existed. <a href="/">Back home</a>.</p>
```

保存并请求 URL，但没有任何服务：

```bash
curl -i -H "Accept: text/html" http://localhost:3000/nowhere
# HTTP/1.1 404 Not Found
```

路由根目录下的文件回答了整个项目；文件夹中的副本仅应答该文件夹
并[保持其余部分不变](folder-pages.md)。没有任何文件，Nexy 提供其内置样式
页。

## 哪个文件回答

| 文件 | 答案 |
|---|---|
| `notfound.nexy` | `404` 为其目录 |
| `errors.nexy` | `500` 为其目录 |
| `forbidden.nexy` | `403` 为其目录 |
| `unauthorized.nexy` | `401` 为其目录 |
| `loading.nexy` | 保留；还没有运行时效果 |

|情况|答案|
|---|---|
| 没有路由匹配 | `404` |
| 动态段无法转换为其注释 | `404` |
| 页面或 API 处理程序中未处理的异常 | `500` |
| `raise HTTPException(status_code=403)` | 您提出的状态，HTML 或 JSON |
| `notFound()`、`forbidden()`、`unauthorized()` | `404`、`403`、`401`，来自请求 | 中的任何位置
| `redirect()`，`permanentRedirect()` | 真正的重定向，没有错误页面 |

## 通过代码留下页面或答案

`redirect`、`permanentRedirect`、`notFound`、`forbidden` 和 `unauthorized` 引发 HTTP 异常，
所以相同的调用可以在 `.nexy` 页面、API 处理程序、模块化控制器、警卫和
`dependencies.py`。它们在客户端上具有相同的名称 (`@nexy/client`)。

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound, redirect

from src.posts import find

slug: prop[str]
post = find(slug)
if post is None:
    notFound()
if post.moved_to:
    redirect(post.moved_to)
---
<h1>{{ post.title }}</h1>
```

| 呼叫 | 应答 |
|---|---|
| `redirect(url)` | `307`； `redirect(url, status=303)` 在表单 | 之后将 POST 转换为 GET
| `permanentRedirect(url)` | `308`；浏览器和搜索引擎会记住它|
| `notFound(detail=None)` | `404`：`notfound` 页面，或 API 客户端的 JSON |
| `forbidden(detail=None)` | `403`：访问者是已知的，但可能看不到此 |
| `unauthorized(detail=None, scheme=None)` | `401`； `scheme="Bearer"` 添加 `WWW-Authenticate` |

重定向响应带有 `Location` 标头，但没有页面，也返回到 API 客户端。构建
来自您信任的值的目的地：`redirect(request.query_params["next"])` 发送访客
无论链接说什么。带有换行符的目的地将被拒绝。

警卫保护整个文件夹：

```python filename="src/routes/private/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

## HTML 或 JSON

对于相同的异常，不同的提问者会给出不同的答案：

- 浏览器（`Accept: text/html`）获取 HTML 页面。详细信息是 HTML 转义的，因此构建了一条消息
  用户输入无法注入标记。
- 请求 JSON 而不是页面的客户端 (`Accept: application/json`) 得到
  `{"detail": "..."}` 具有相同的状态代码。

```python filename="src/routes/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=403, detail="Out of range")
    return {"id": id}
```

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [！注意]
> 发送`Accept: */*`的客户端（`curl`的默认值和许多HTTP
> libraries) 接收 HTML 页面。针对 JSON 错误设置 `Accept: application/json`。

## 未处理的异常

没有任何处理的异常会被记录一次，除了异常的来源和异常
围绕它的代码，并根据模式进行回答。

| | `nx dev` | `nx start` |
|---|---|---|
| 浏览器 | 出现错误的页面、引发该错误的代码行以及完整回溯 | 内置 `500` 页面（或您的 `errors.nexy`）以及引用 |
| JSON 客户端 | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| 服务器日志 | 异常和代码行 | 异常和整个回溯，具有相同的引用 |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

参考号是八个字符，每次失败都是新的。访客可以引用它，然后您会发现
通过搜索日志进行回溯。异常和代码都没有到达访问者
生产。自定义 `errors.nexy` 仅替换页面；日志行保留。

## 验证错误

对于每个缺失的标头、查询参数或主体字段，都会使用 FastAPI 的 JSON 主体来回答 `422`
客户。请参阅[验证和错误](../handlers/validation-and-errors.md)。

## 后续步骤

- [每个文件夹的错误页面](folder-pages.md)：一个文件夹中您自己的 404、403 或 401
- [动态路线](../pages/dynamic-routes.md)
- [API 路由](../handlers/README.md)
- [测试](../../../guides/testing.md)