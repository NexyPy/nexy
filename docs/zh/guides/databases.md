# 数据库

`nx new` 可以使用 SQLModel、SQLAlchemy 或 Tortoise-ORM 构建模型层。 Nexy 不包裹
ORM：您可以从处理程序和页面直接使用它。

## 脚手架添加了什么

| 文件 | 目的 |
|---|---|
| `src/configs/db.py` | 引擎（SQLModel、SQLAlchemy）或 `TORTOISE_ORM` 设置 |
| `src/models/` | 模型类 |
| `src/services/` | 查询模型的函数 |
| `.env` | `DATABASE_URL`，在 `nx new` | 期间提供数据库 URL 时写入

连接字符串来自 `DATABASE_URL` 环境变量。当它被取消设置时，
脚手架引擎回退到本地 SQLite 文件 `dev.db`。

## 在页面中使用服务

```nexy filename="src/routes/users/index.nexy"
---
from src.services.user_service import UserService
users = UserService.get_all()
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## 在 API 处理程序中使用服务

```python filename="src/routes/api/users.py"
from src.services.user_service import UserService


async def GET():
    return UserService.get_all()
```

## Tortoise-ORM 是异步的

页面在服务器的事件循环中运行并且无法等待它，因此 `asyncio.run(...)` 失败并显示
“无法从正在运行的事件循环中调用”。脚手架 `src/configs/db.py` 为 Tortoise 提供了
它自己的循环，在一个线程中，以及两个向其发送协程的助手：

| 你在哪里 | 打电话 | 做 |
|---|---|---|
| 同步代码，例如页面 | `run(UserService.get_all())` | 运行它并返回结果 |
| 异步代码，例如处理程序或控制器 | `await arun(UserService.get_all())` | 相同，不会阻塞服务器 |

```nexy filename="src/routes/users/index.nexy"
---
from src.configs.db import run
from src.services.user_service import UserService
users = run(UserService.get_all())
---
```

当其中一个被第一次调用时，乌龟就会连接。从 `async def` 调用模型
（`await UserModel.all()` 在服务内），而不是在模块级别：协程外部的调用运行
在乌龟连接之前。

列出 `TORTOISE_ORM` 中保存模型的每个模块（`src/configs/db.py` 的 `models` 条目）。
脚手架列出了用户模型和`aerich.models`；未列出的模块中的模型不是
发现。

## 迁移

`nx migrate` 为您的 ORM 选择工具：Alembic for SQLModel 和 SQLAlchemy，Aerich for
乌龟-ORM。

| 命令 | 执行 |
|---|---|
| `nx migrate --init` | 初始化项目的迁移工具 |
| `nx migrate -m "add users"` | 根据模型更改创建迁移 |
| `nx migrate --upgrade` | 应用待处理的迁移 |

对于 Aerich，第一个 `nx migrate` 运行 `aerich init-db`，这会创建第一个迁移和
桌子放在一起；接下来的运行 `aerich migrate --name "..."`，并且 `--upgrade` 运行
`aerich upgrade`。

当 `DATABASE_URL` 丢失或数据库无法访问时，`nx migrate` 停止并显示明确消息
已达到（仅限 Alembic：Aerich 报告其自己的错误）。

### 第一次迁移是为您准备的

当您选择 ORM 并提供数据库 URL 时，`nx new` 设置迁移工具，创建
第一次迁移并应用它，因此用户页面在第一个 `nexy dev` 上回答。迁移
工具（`alembic` 或 `aerich`）与 ORM 一起安装在项目中。

如果数据库没有响应（PostgreSQL 服务器未运行、缺少驱动程序），`nx new`
说明原因，跳过迁移并列出准备就绪时要运行的两个命令：

```bash
nexy migrate -m "create tables"
nexy migrate --upgrade
```

在表存在之前，读取数据库的页面会失败并显示“没有这样的表”。

### 添加模型

Alembic 将数据库与 `alembic/env.py` 导入的模型进行比较。一个新的模型
直到该模块被导入到用户模型旁边时，才会看到该模块：

```python filename="蒸馏器/env.py"
import src.models.user_model  # noqa: F401
import src.models.post_model  # noqa: F401
```

对于 Tortoise-ORM，请在 `TORTOISE_ORM` 中列出模块（参见上文）。

## 后续步骤

- [测试](testing.md)：针对临时数据库测试处理程序
- [配置](../reference/config.md)
- [部署](../deployment/README.md)：在生产中设置`DATABASE_URL`