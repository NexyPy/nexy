# 数据库

`nx new` 可以使用 SQLModel、SQLAlchemy 或 Tortoise-ORM 搭建模型层。 Nexy 不包装 ORM：您可以从处理程序和页面直接使用它。

## 脚手架增加了什么

| 文件 | 目的 |
|---|---|
| `src/configs/db.py` | 引擎（SQLModel、SQLAlchemy）或 `TORTOISE_ORM` 设置 |
| `src/models/` | 模型类 |
| `src/services/` | 查询模型的函数 |
| `.env` | `DATABASE_URL`，当您在 `nx new` 期间提供数据库 URL 时写入 |

连接字符串来自 `DATABASE_URL` 环境变量。当它被取消设置时，脚手架引擎会回退到本地 SQLite 文件，`dev.db`。

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

页面在服务器的事件循环中运行并且无法等待它，因此 `asyncio.run(...)` 在那里失败并显示“无法从正在运行的事件循环中调用”。脚手架 `src/configs/db.py` 在一个线程中为 Tortoise 提供了一个自己的循环，以及两个向其发送协程的助手：

| 你在哪里 | 致电 | 是否 |
|---|---|---|
| 同步代码，例如页面 | `run(UserService.get_all())` | 运行并返回结果 |
| 异步代码，例如处理程序或控制器 | `await arun(UserService.get_all())` | 一样，不阻塞服务器 |

```nexy filename="src/routes/users/index.nexy"
---
from src.configs.db import run
from src.services.user_service import UserService
users = run(UserService.get_all())
---
```

Tortoise 在第一次调用其中一个时连接。从 `async def`（服务内部的 `await UserModel.all()`）调用模型，而不是在模块级别：协程外部的调用在 Tortoise 连接之前运行。

列出 `TORTOISE_ORM` 中保存模型的每个模块（`src/configs/db.py` 的 `models` 条目）。脚手架列出了用户模型和 `aerich.models`；未找到模块中未列出的模型。

## 迁移

`nx migrate` 为您的 ORM 选择工具：Alembic 代表 SQLModel，SQLAlchemy，Aerich 代表 Tortoise-ORM。

| 命令 | 是否 |
|---|---|
| `nx migrate --init` | 初始化项目的迁移工具 |
| `nx migrate -m "add users"` | 根据模型更改创建迁移 |
| `nx migrate --upgrade` | 应用待处理的迁移 |

对于 Aerich，第一个 `nx migrate` 运行 `aerich init-db`，这将创建第一个迁移和表；接下来的运行 `aerich migrate --name "..."`，`--upgrade` 运行 `aerich upgrade`。

当 `DATABASE_URL` 丢失或无法访问数据库时，`nx migrate` 停止并显示明确消息（仅 Alembic：Aerich 报告其自身的错误）。

### 第一次迁移是为您准备的

当您选择 ORM 并提供数据库 URL 时，`nx new` 将设置迁移工具，创建第一个迁移并应用它，因此用户页面会在第一个 `nexy dev` 上进行回答。迁移工具（`alembic` 或 `aerich`）与 ORM 一起安装在项目中。

如果数据库没有响应（PostgreSQL 服务器未运行，缺少驱动程序），`nx new` 会说明原因，跳过迁移并列出准备就绪时要运行的两个命令：

```bash
nexy migrate -m "create tables"
nexy migrate --upgrade
```

在表存在之前，读取数据库的页面会失败并显示“没有这样的表”。

### 添加型号

Alembic 将数据库与 `alembic/env.py` 导入的模型进行比较。新模块中的模型只有在用户模型旁边导入该模块后才能看到：

```python filename="蒸馏器/env.py"
import src.models.user_model  # noqa: F401
import src.models.post_model  # noqa: F401
```

对于 Tortoise-ORM，请在 `TORTOISE_ORM` 中列出模块（参见上文）。

## 后续步骤

- [测试](testing.md)：针对临时数据库测试处理程序
- [配置](../reference/config.md)
- [部署](../deployment/README.md)：在生产中设置 `DATABASE_URL`
