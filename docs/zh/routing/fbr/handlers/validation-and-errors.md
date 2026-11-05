# 验证和错误

API 处理程序如何报告错误请求。

## 验证

处理程序参数由 FastAPI 根据其注释进行验证。

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| 问题 | 状态 | 身体 |
|---|---|---|
| 查询、标头、cookie 或正文字段缺失或无效 | `422` | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| **路径** 段无效（`/api/users/abc` 对于 `id: int`） | `404` | 未找到的页面，或 `Accept: application/json` 的 JSON |

无法转换的路径段是 `404` 而不是 `422`：动态路由捕获任何URL，并且不存在无法转换的URL。

`422` 主体是 FastAPI 的标准形状，因此现有客户端和生成的 SDK 可以继续工作。

## 引发错误

```python filename="src/routes/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    item = find(id)
    if item is None:
        raise HTTPException(status_code=404, detail="No such item")
    return item
```

| 客户端发送 | 回应 |
|---|---|
| `Accept: application/json` | `{"detail": "No such item"}` 状态为 `404` |
| `Accept: text/html` | [错误页面](../errors/README.md) |
| `Accept: */*` | 错误页面 |

在 API 客户端中设置 `Accept: application/json`。浏览器不断获取页面。

## 未处理的异常

一个例外是您的处理程序无法捕获具有相同 HTML 或 JSON 选择的答案 `500`。

## 自定义响应

当你控制 body 时返回一个响应对象：

```python
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"error": "conflict"}, status_code=409)
```

## 后续步骤

- [API 路线](README.md)
- [错误页面](../errors/README.md)
- [测试](../../../guides/testing.md)
