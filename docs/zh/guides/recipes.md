# 食谱

几乎每个应用程序都需要三件事，作为您可以复制的完整文件。下面的每个代码块都带有
`filename` 被写入一个新项目并由测试套件执行，所以您读到的就是
运行。

他们使用简单的 API 处理程序；相同的功能在任一[模式](../routing/fbr/modes.md)下的页面后面工作。

## 通过会话登录

访问者发布姓名和密码，服务器会在签名的 cookie 中记住它们，以及所有内容
`/api/account` 下的内容对其他人不开放。

打开会话。他们需要`itsdangerous`（`uv add itsdangerous`）：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me-in-production"}
```

登录和退出：

```python filename="src/routes/api/login.py"
from pydantic import BaseModel

from nexy.http import HTTPException, Request

USERS = {"ada": "lovelace"}


class Credentials(BaseModel):
    name: str
    password: str


async def POST(request: Request, body: Credentials):
    if USERS.get(body.name) != body.password:
        raise HTTPException(status_code=401, detail="Wrong name or password")
    request.session["user"] = body.name
    return {"user": body.name}
```

```python filename="src/routes/api/logout.py"
from nexy.http import Request


async def POST(request: Request):
    request.session.clear()
    return {"signed_out": True}
```

用一个 [`dependencies.py`](../routing/fbr/dependencies/README.md) 保护整个文件夹：

```python filename="src/routes/api/account/dependency.py"
from nexy.http import HTTPException, Request


def current_user(request: Request) -> str:
    if not request.session.get("user"):
        raise HTTPException(status_code=401, detail="Sign in first")
    return request.session["user"]


dependencies = [current_user]
```

```python filename="src/routes/api/account/index.py"
from nexy.http import Request


async def GET(request: Request):
    return {"user": request.session["user"]}
```

> [!注意]
> 不要将真实密码泄露给来源。存储哈希值 (`argon2`, `bcrypt`) 并读取
> 来自环境的密钥。会话 cookie 已签名，未加密。

## 具有创建、读取和删除功能的 JSON API

模块中的商店、收集路线和物品路线。将字典替换为
[数据库](databases.md)，数据必须在重新启动后继续存在。

```python filename="src/notes.py"
from pydantic import BaseModel


class Note(BaseModel):
    id: int
    title: str


NOTES: dict[int, Note] = {}
```

```python filename="src/routes/api/notes/index.py"
from pydantic import BaseModel

from src.notes import NOTES, Note


class NewNote(BaseModel):
    title: str


async def GET() -> list[Note]:
    return list(NOTES.values())


async def POST(body: NewNote) -> Note:
    note = Note(id=max(NOTES, default=0) + 1, title=body.title)
    NOTES[note.id] = note
    return note
```

```python filename="src/routes/api/notes/[id].py"
from nexy.http import HTTPException

from src.notes import NOTES, Note


async def GET(id: int) -> Note:
    if id not in NOTES:
        raise HTTPException(status_code=404, detail="No such note")
    return NOTES[id]


async def DELETE(id: int) -> dict[str, bool]:
    if NOTES.pop(id, None) is None:
        raise HTTPException(status_code=404, detail="No such note")
    return {"deleted": True}
```

在代码运行之前，不适合 `NewNote` 的主体会被 `422` 拒绝，并且返回
注释成为记录的响应。参见
[验证和错误](../routing/fbr/handlers/validation-and-errors.md)。

## 接收文件

上传需要`python-multipart`（`uv add python-multipart`）。请自行检查尺寸，切勿使用
客户端的文件名作为路径：

```python filename="src/routes/api/upload.py"
from pathlib import Path

from nexy.http import HTTPException, UploadFile

MAX_BYTES = 1_000_000


async def POST(file: UploadFile) -> dict[str, int | str]:
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    name = Path(file.filename or "upload").name
    return {"name": name, "size": len(data)}
```

`Path(...).name` 删除客户端输入名称的任何文件夹，例如 `../../etc/passwd`。保存
bytes 在您生成的名称下，而不是在此名称下。

## 后续步骤

- [Actions](actions.md)：表单和按钮的类型化服务器函数
- [中间件和安全性](middleware-and-security.md)：CORS、主机、会话
- [测试](testing.md)：以同样的方式测试你自己的处理程序