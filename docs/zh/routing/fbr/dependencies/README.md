# 依赖和守卫

跨具有 FastAPI 依赖项的路由共享身份验证、数据库会话和其他设置。它们在两个级别上工作，目录级别像布局一样继承。

| 级别 | 其中 | 适用于 |
|---|---|---|
| 目录 | `dependencies.py` | 目录及以下的每条路线，页面包括 |
| 处理程序 | `Depends`、`@UseGuard`、`@Middleware` | 一个处理程序 |

## 每个目录：`dependencies.py`

`dependencies.py` 声明一个 `dependencies` 普通函数列表。 Nexy 将每一项都包装在 `Depends` 中。

```python filename="src/routes/admin/dependency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

> [！注意]
> 列出函数本身。列表中的 `Depends(...)` 对象将被忽略。

`src/routes/admin/` 下的每个路由现在都需要标头、`.py` 处理程序和 `.nexy` 页面。

## 继承

依赖关系从路由根目录收集到路由目录，**最外层第一个**，与布局完全相同，并且处理程序自己的守卫最后运行：

```text
src/routes/
├─ dependencies.py              1. root
└─ admin/
   ├─ dependencies.py           2. admin
   └─ users/
      ├─ dependencies.py        3. users
      └─ index.py               4. handler guards, then the handler
```

对于 `GET /admin/users`，顺序是 `root`、`admin`、`users`、处理程序的 `@UseGuard` 函数、其 `@Middleware` 函数，然后是处理程序。路由组 (`(group)/`) 是一个与其他目录一样的目录，因此它的 `dependencies.py` 也参与其中。

## 每个处理程序

在签名中使用 `Depends`，就像在任何 FastAPI 应用程序中一样：

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header, HTTPException


def current_user(authorization: str = Header(...)) -> str:
    if authorization != "Bearer secret":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return "ada"


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## 处理程序上的警卫和中间件

`@UseGuard` 和 `@Middleware` 将 FastAPI 依赖项附加到处理程序而不更改其签名。两者都是依赖项，而不是 ASGI 中间件：

```python filename="src/routes/admin/users/index.py"
from nexy.decorators import Middleware, UseGuard


def audit() -> None: ...


def must_be_staff(x_staff: str = Header(...)) -> None: ...


@UseGuard(must_be_staff)
@Middleware(audit)
async def GET():
    return {"ok": True}
```

对于真正的 ASGI 中间件（CORS、GZip、会话、您自己的），请使用 [中间件和安全性 ](../../../guides/middleware-and-security.md) 中的 `useMiddlewares` 和 `use*` 选项。

## 依赖失败

依赖项通过引发来拒绝请求。 `HTTPException` 回答您提出的状态，作为 API 客户端 (`Accept: application/json`) 的 JSON 和浏览器的错误页面。请参阅[验证和错误](../handlers/validation-and-errors.md)。

## 后续步骤

- [继承](../inheritance.md)
- [处理程序](../handlers/README.md)
- [中间件和安全](../../../guides/middleware-and-security.md)
