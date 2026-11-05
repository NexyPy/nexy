# 每个文件夹的错误页

文件夹可以回答自己的错误：用自己的话来说是一个带有 404 错误的博客，一个提供登录表单而不是裸露的 `401` 的私人区域。网站的其余部分保留其已有的页面。

此页面添加其中一个文件并显示它的答案。

## 规则

**与 URL 答案匹配的最深文件。** 其他一切都保持原样：相同的状态代码、API 客户端的 JSON，以及链中没有文件夹拥有文件时的内置页面。

![错误页面的范围](../../../assets/error-page-scopes.svg)

对于 `/blog/2024/hello`，Nexy 沿着树向上走：`/blog/2024`，然后是 `/blog`，然后是 `/`。第一个包含文件的文件夹会应答。文件夹是整体匹配的：`/blogger/hello` 不在 `/blog` 下，因此 `blog/` 中的副本永远不会回答它。

## 四个文件

| 文件 | 答案 | 到达的内容 |
|---|---|---|
| `notfound.nexy` | `404` | 没有路由匹配的 URL，`notFound()` |
| `errors.nexy` | `500` | 异常未处理 |
| `forbidden.nexy` | `403` | `forbidden()`，`raise HTTPException(403)` |
| `unauthorized.nexy` | `401` | `unauthorized()`，`raise HTTPException(401)` |

`loading.nexy` 保持保留：它还没有运行时效果。

`src/routes/` 中某处的一个文件足以让 Nexy 回答该状态：根目录中的副本回答整个项目，文件夹中的副本回答该文件夹，每个副本外部的 URL 获取内置页面。在 `nexyconfig.py` 中使用 `useNotFoundExtensions`、`useErrorsExtensions`、`useForbiddenExtensions` 和 `useUnauthorizedExtensions` 为这些名称保留另一个扩展名。

## 您的第一个文件夹页面

```nexy filename="src/routes/blog/notfound.nexy"
---
title: Nothing here yet
---
<h1>That post is gone</h1>
<p>The <a href="/blog">blog</a> still has the others.</p>
```

运行项目并请求一个不存在的帖子：

```bash
curl -i -H "Accept: text/html" http://localhost:3000/blog/old
# HTTP/1.1 404 Not Found
```

文件夹外部的 URL 保留您已有的页面：

```bash
curl -i -H "Accept: text/html" http://localhost:3000/about
# HTTP/1.1 404 Not Found    (the root page, or the built-in one)
```

## 通往某处的401

受保护区域的文件夹回答 `401` 并提供以下路径的页面：

```nexy filename="src/routes/private/unauthorized.nexy"
---
title: Sign in to continue
---
<h1>Sign in to see your notes</h1>
<a href="/sign-in" class="button">Sign in</a>
```

```python filename="src/routes/private/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

每个呼叫和每个状态都有两个答案：

| 谁用文件 | `401` 询问 | `401` 而没有 |
|---|---|---|
| 浏览器 (`Accept: text/html`) | 文件夹页面 | 内置页面 |
| 客户端 (`Accept: application/json`) | `{"detail": "..."}` | `{"detail": "..."}` |

`unauthorized(scheme="Bearer")` 将 `WWW-Authenticate: Bearer` 添加到两个答案中。根据用户输入构建的详细信息在页面中进行 HTML 转义。

> [!TIP]
> `Accept: */*`，`curl` 和许多 HTTP 库的默认值，都不要求任何内容并接收 HTML 页面。当您需要 JSON 答案时添加 `-H "Accept: application/json"`。

## 检查一下

```python filename="测试/test_private.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_a_private_url_asks_for_sign_in():
    answer = TestClient(app).get("/private/notes")
    assert answer.status_code == 401
    assert "Sign in" in answer.text


def test_an_api_client_gets_json():
    answer = TestClient(app).get(
        "/private/notes", headers={"accept": "application/json"}
    )
    assert answer.json() == {"detail": "Unauthorized"}
```

## 后续步骤

- [错误页面](README.md)：触发每个状态的内容，HTML 或 JSON
- [依赖关系和防护](../dependencies/README.md)：保护整个文件夹
- [测试](../../../guides/testing.md)：第一次测试的 `TestClient`
