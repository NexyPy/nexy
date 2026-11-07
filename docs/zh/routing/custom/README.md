# 在 Nexy 中包含现有的 FastAPI 路由器

要在 Nexy 中包含现有的 FastAPI 路由器，请将 `useRouter` 设置为 `nexyconfig.py` 的 `NexyConfig` 类中的 `APIRouter`：其路由按原样提供，位于 `src/routes/` 的文件旁边。

## 何时使用自定义路由器

- **逐步迁移**：一个 FastAPI 应用按路由迁移到Nexy路由，同时其旧路由继续应答。
- **代码重用**：包已经公开了 `APIRouter`，用于身份验证或计费。
- **您保留的后端**：API 保持简单 FastAPI，Nexy 添加页面。

## 在 `nexyconfig.py` 中设置 `useRouter`

路由器是任何 FastAPI `APIRouter`，按照您已经编写的方式编写：

```python filename="src/legacy/api.py"
from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/status")
async def status():
    return {"status": "ok"}


@router.get("/users/{id}")
async def user(id: int):
    return {"id": id}
```

`useRouter` 是 `NexyConfig` 类的一个字段，就像项目的每个设置一样：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

`nx dev` 然后回答 `GET /api/status` 和 `GET /api/users/{id}`，`/docs` 列出它们。

> [!NOTE]
> `nexyconfig.py` 中的 `useRouter` 是一个设置。 `from nexy import useRouter` 是另一回事：`.nexy` 页面用来读取当前路由的钩子。不要导入它来配置路由器。

## 几个路由器

`useRouter` 需要一台路由器。使用 `include_router` 在一个父项下收集多个：

```python filename="src/legacy/__init__.py"
from fastapi import APIRouter

from .api import router as api
from .auth import router as auth

router = APIRouter()
router.include_router(api)
router.include_router(auth, prefix="/auth")
```

```python filename="src/legacy/auth.py"
from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login():
    return {"token": "demo"}
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

## 页面和旁边的路由文件

设置 `useRouter` 时仍会读取 `src/routes/`：`.nexy` 页面或 `.py` 路线文件在包含的路线旁边进行应答。

```nexy filename="src/routes/index.nexy"
---
title = "Home"
---
<h1>{{ title }}</h1>
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"ok": True}
```

设置 `useRouter` 时有两个限制：

- 页面没有被 `layout.nexy` 包裹；
- `useCSR = True` 被拒绝：`nx dev` 和 `nx build` 回答 `useCSR requires file-based routing`。

URL 被应答一次。为包含的路由器指定一个前缀，此处为 `/api`，并将 `src/routes/` 的文件保留在其使用的路径之外。

## 整个 FastAPI 应用程序

`useRouter` 需要 `APIRouter`，而不是 `FastAPI` 应用程序。应用程序的路由位于其 `router` 属性上：

```python filename="src/legacy/service.py"
from fastapi import FastAPI

service = FastAPI(title="Billing")


@service.get("/billing/invoices")
async def invoices():
    return []
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.service import service


class NexyConfig(NexyConfigModel):
    useRouter = service.router
```

应用程序自己的中间件、异常处理程序和启动事件保留在后面：将它们移至 `useMiddlewares` 和 `nexyconfig.py` 的其他字段。

## 依赖项、身份验证和数据库

路由器在 Nexy 进程中运行，因此 `Depends`、安全方案和数据库会话的工作方式与原始应用程序中一样：

```python filename="src/legacy/secure.py"
from fastapi import APIRouter, Depends, Header, HTTPException


def require_token(x_token: str = Header("")) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=401, detail="Bad token")


router = APIRouter(prefix="/secure", dependencies=[Depends(require_token)])


@router.get("/data")
async def data():
    return {"data": 42}
```

## 测试一下

```python filename="测试/test_legacy.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_the_included_route_answers():
    assert TestClient(app).get("/api/status").json() == {"status": "ok"}
```

## 后续步骤

- [从 FastAPI 到Nexy](../../coming-from/fastapi.md)：将路由一一移动到文件
- [基于文件的路由](../fbr/README.md)
- [模块化路由](../modular/README.md)：`useRouter = AppModule`
