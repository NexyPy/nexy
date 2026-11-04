# 路由处理程序

`src/routes/` 下的 `.py` 文件是 API 处理程序。文件路径就是URL，各个函数
以 HTTP 方法命名成为端点。

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

该文件回答`GET /api/items`和`POST /api/items`。

支持的函数名称：`GET`、`POST`、`PUT`、`PATCH`、`DELETE`、`OPTIONS`、`HEAD`。 `SOCKET` 打开
同一路径上的 WebSocket - 请参阅 [WebSocket](../realtime/websocket.md)。

## HTTP 词汇

从 `nexy.http` 导入处理程序所需的内容：

```python
from nexy.http import Depends, Header, HTTPException, JSONResponse, Request, status
```

它公开请求和响应类（`Request`、`Response`、`JSONResponse`、`HTMLResponse`、
`PlainTextResponse`、`RedirectResponse`、`StreamingResponse`、`FileResponse`），参数源
(`Header`、`Query`、`Cookie`、`Path`、`Body`)、`Depends`、`BackgroundTasks`、`HTTPException` 和
`status`。针对此模块编写的处理程序取决于 Nexy 的合约，而不是引擎
为他们服务。 Pydantic 模型照常描述身体和反应。

## 参数

| 来源 | 它如何到达 |
|---|---|
| 路径段 `[id]` | 函数参数 `id`，转换为其注释 |
| 查询字符串 | `page: int = 1` |
| JSON 主体 | Pydantic 模型参数 |
| FastAPI 原语 | `Depends`、`Header`、`Cookie`、`Form`、`UploadFile` - 不变 |

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

路径段是`{id}`，因此FastAPI验证`id: int`。答案不是整数的值
`404`，因为动态路由捕获任何URL，并且不存在无法转换的URL。
请参阅[验证和错误](validation-and-errors.md)。

## 回应

| 返回 | 响应 |
|---|---|
| `dict`、`list`、`BaseModel` | JSON |
| `JSONResponse`、`HTMLResponse`、任何 `Response` | 与声明的 | 完全相同
| `None` | 空响应 - 当状态重要时返回 `Response` |

对于自定义状态代码或内容类型，返回响应对象：

```python filename="src/routes/api/items.py"
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"created": True}, status_code=201)
```

## 错误

为客户端引发 FastAPI 异常。发送 `Accept: application/json` 的客户端收到
`{"detail": "..."}` 与您提升的地位；浏览器收到错误页面。 `notfound.nexy`
渲染 `404` 和 `errors.nexy` 渲染 `500`，每个范围仅限于其目录。参见
[验证和错误](validation-and-errors.md)和[错误页面](../errors/README.md)。

## 开放API

每个 API 路由都会出现在生成的架构中，因为这些路由是普通的 FastAPI 路由。的
架构在 `/openapi.json` 处提供服务，并由标量在 `/docs` 处呈现。禁用两者
`useDocs = False`在`nexyconfig.py`中。

## 后续步骤

- [依赖项](../dependencies/README.md)：每个处理程序或每个目录的共享身份验证和设置
- [验证和错误](validation-and-errors.md)：`422`、`404`和JSON错误
- [路由](../../README.md)：URL 的文件路径
- [操作](../../../guides/actions.md)：具有生成路径的端点
- [配置](../../../reference/config.md)：中间件、CORS、会话