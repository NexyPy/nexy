# 路线处理程序

`src/routes/` 下的 `.py` 文件是 API 处理程序。文件路径就是 URL，每个以 HTTP 方法命名的函数都成为一个端点。

## 创建端点

```python filename="src/routes/api/items.py"
from nexy.http import Request
from pydantic import BaseModel


class Item(BaseModel):
    name: str


async def GET(request: Request):
    return {"items": []}


async def POST(request: Request, body: Item):
    return {"created": body.name}
```

该文件回答 `GET /api/items` 和 `POST /api/items`。

支持的函数名称：`GET`、`POST`、`PUT`、`PATCH`、`DELETE`、`OPTIONS`、`HEAD`。 `SOCKET` 在同一路径打开 WebSocket - 请参阅 [WebSocket](../realtime/websocket.md)。

## HTTP 词汇

从 `nexy.http` 导入处理程序所需的内容：

```python
from nexy.http import Depends, Header, HTTPException, JSONResponse, Request, status
```

它公开请求和响应类（`Request`、`Response`、`JSONResponse`、`HTMLResponse`、`PlainTextResponse`、`RedirectResponse`、`StreamingResponse`、`FileResponse`）、参数源（`Header`、`Query`、`Cookie`、`Path`、`Body`）、`Depends`、 `BackgroundTasks`、`HTTPException` 和 `status`。针对该模块编写的处理程序取决于 Nexy 的合约，而不是为其提供服务的引擎。 Pydantic 模型照常描述身体和反应。

## 参数

| 来源 | 它是如何到达的 |
|---|---|
| 路径段 `[id]` | 函数参数 `id`，转换为其注释 |
| 查询字符串 | `page: int = 1` |
| JSON 正文 | Pydantic 模型论证 |
| FastAPI 原语 | `Depends`、`Header`、`Cookie`、`Form`、`UploadFile` - 不变 |

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

路径段是 `{id}`，因此 FastAPI 验证 `id: int`。非整数的值回答 `404`，因为动态路由捕获任何 URL，并且不存在无法转换的 URL。请参阅[验证和错误](validation-and-errors.md)。

## 回应

| 返回 | 回应 |
|---|---|
| `dict`、`list`、`BaseModel` | JSON |
| `JSONResponse`、`HTMLResponse`、任意 `Response` | 完全按照声明的那样 |
| `None` | 空响应 - 当状态重要时返回 `Response` |

对于自定义状态代码或内容类型，返回响应对象：

```python filename="src/routes/api/items.py"
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"created": True}, status_code=201)
```

## 错误

为客户提出 FastAPI 例外情况。发送 `Accept: application/json` 的客户端会收到 `{"detail": "..."}` 以及您提出的状态；浏览器收到错误页面。 `notfound.nexy` 呈现 `404` 和 `errors.nexy` 呈现 `500`，每个范围仅限于其目录。请参阅[验证和错误](validation-and-errors.md) 和[错误页面](../errors/README.md)。

## OpenAPI

每个 API 路由都会出现在生成的架构中，因为这些路由是普通的 FastAPI 路由。该模式在 `/openapi.json` 处提供服务，并由 `/docs` 处的 Scalar 呈现。使用 `nexyconfig.py` 中的 `useDocs = False` 禁用两者。

## 后续步骤

- [依赖项](../dependencies/README.md)：每个处理程序或每个目录的共享身份验证和设置
- [验证和错误](validation-and-errors.md)：`422`、`404` 和JSON错误
- [路由](../../README.md)：URL 的文件路径
- [操作](../../../guides/actions.md)：具有生成路径的端点
- [配置](../../../reference/config.md)：中间件、CORS、会话
