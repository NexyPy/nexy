# 来自另一个框架

Nexy 是 FastAPI 加上基于文件的路由、服务器渲染页面和可选的 React、Vue、Svelte、Solid 或 Preact 岛。此页面映射了您已经知道的内容。

下面的每个框架也有自己的页面，逐个任务，包含您知道的代码，然后是 Nexy 代码：

| Python | 后端 | 全栈 JavaScript |
|---|---|---|
| [FastAPI](../coming-from/fastapi.md) | [表达](../coming-from/express.md)，[快速](../coming-from/fastify.md) | [Next.js](../coming-from/nextjs.md)，[Remix](../coming-from/remix.md) |
| [Flask](../coming-from/flask.md) | [艾丽西亚](../coming-from/elysia.md)、[霍诺](../coming-from/hono.md) | [努克斯特](../coming-from/nuxt.md) |
| [Django](../coming-from/django.md) | [NestJS](../coming-from/nestjs.md)，[Spring Boot](../coming-from/spring-boot.md) | [SvelteKit](../coming-from/sveltekit.md) |
| | [Laravel](../coming-from/laravel.md)、[Ruby on Rails](../coming-from/rails.md) | [Astro](../coming-from/astro.md) |

## 来自 FastAPI

<!-- router:fbr,custom -->
| FastAPI | 内克西 |
|---|---|
| `@app.get("/users")` 在您导入的模块中 | `GET` 函数在 `src/routes/users.py` 中 |
| `app.include_router(router)` | 文件路径是 URL；无需注册 |
| 路径参数 `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | 仍然 `Depends(...)`：处理程序是 FastAPI 处理程序 |
| Jinja2 `TemplateResponse` | 端点旁边的 `.nexy` 页面 |
| 使用 `uvicorn main:app` 运行 | `nx dev`，然后 `nx build && nx start` |

`src/routes/*.py` 下的所有内容都是普通的 FastAPI：依赖项、Pydantic 模型、中间件和 `/docs` 继续工作。

相同的端点，之前和之后：

```python filename="主要.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{id}")
async def get_user(id: int):
    return {"id": id}
```

```python filename="src/routes/users/[id].py"
async def GET(id: int):
    return {"id": id}
```
<!-- /router -->

<!-- router:modular -->
| FastAPI | 内克西 |
|---|---|
| `@app.get("/users")` 在您导入的模块中 | `async def get(self)` 在 `@Controller("/users")` 班级 |
| `app.include_router(router)` | `@Module` 的 `controllers` 中列出的控制器 |
| 路径参数 `/users/{id}` | `@Controller("/users/{id}")`，与 `async def get(self, id: int)` |
| `Depends(...)` | 还是 `Depends(...)`：控制器方法是 FastAPI 端点 |
| Jinja2 `TemplateResponse` | `useViews("src/apps/....nexy")`，由方法返回 |
| 使用 `uvicorn main:app` 运行 | `nx dev`，然后 `nx build && nx start` |

依赖项、Pydantic 模型、中间件和 `/docs` 继续工作。

相同的端点，之前和之后：

```python filename="主要.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{id}")
async def get_user(id: int):
    return {"id": id}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users/{id}")
class UserController:
    async def get(self, id: int):
        return {"id": id}
```
<!-- /router -->

## 来自 Next.js

<!-- router:fbr,custom -->
| Next.js | 内克西 |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` 或 `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx`（拥有 `<html>`） | `src/routes/layout.tsx` 与 `useCSR = True` (React)，或服务器模式下的 `src/routes/layout.nexy` |
| 嵌套 `layout.tsx` | 客户端模式下嵌套 `layout.tsx` / `layout.vue` / `layout.svelte`，服务器模式下嵌套 `layout.nexy` |
| `use client` 服务器页面中的组件 | [服务器模式下的岛屿](../rendering/islands.md) |
| 路线处理程序 `route.ts` | `src/routes/api/x.py`，写在 Python |
| `(group)` 文件夹 | 相同：`(group)/` |
| 服务器操作 | [`@Action`](../guides/actions.md) 从表单调用的函数或作为类型化客户端函数 |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

后端是 Python，因此您的 API 与您的数据和 ML 工作共享代码。客户端组件作为岛屿而不是整个页面的 React 树进行水合。

Next.js 页面几乎按原样移动，其 `"use client"` 组件成为服务器页面的孤岛：

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

```nexy filename="src/routes/blog/[slug].nexy"
---
from "@/components/Comments.tsx" import Comments

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Comments post="{{ slug }}" directive="client:visible" />
```
<!-- /router -->

<!-- router:modular -->
| Next.js | 内克西 |
|---|---|
| `app/page.tsx` | 返回 `useViews("src/apps/home_view.nexy")` 的控制器 |
| `app/blog/[slug]/page.tsx` | `@Controller("/blog/{slug}")`，与 `async def get(self, slug: str)` |
| `app/layout.tsx`（拥有 `<html>`） | 控制器通过 `children` 包裹其视图的布局视图 |
| 服务器页面中的 `use client` 组件 | [视图中的岛屿](../rendering/islands.md) |
| 路线处理程序 `route.ts` | 返回字典的控制器，用 Python 编写 |
| 服务器操作 | [`@Action`](../guides/actions.md) 从表单调用的函数或作为类型化客户端函数 |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

后端是 Python，因此您的 API 与您的数据和 ML 工作共享代码。客户端组件作为岛屿而不是整个页面的 React 树进行水合。

Next.js 页面成为控制器及其视图，其 `"use client"` 组件成为视图的孤岛：

```python filename="src/apps/blog/post_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/blog/post_view.nexy", context={"slug": slug})
```

```nexy filename="src/apps/blog/post_view.nexy"
---
from "@/components/Comments.tsx" import Comments

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Comments post="{{ slug }}" directive="client:visible" />
```
<!-- /router -->

## 来自 Express 或 Node 后端

<!-- router:fbr,custom -->
| 快递 | 内克西 |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` 与 `async def GET(id)` |
| `app.use(middleware)` | FastAPI 中间件，从 `nexyconfig.py` 注册 |
| `res.json(obj)` | 返回字典或 Pydantic 模型 |
| EJS / 哈巴狗观点 | `.nexy`（Jinja2）页 |
| `npm run dev` | `nx dev` |

`app.use(...)` 成为 `nexyconfig.py` 的字段，`res.json(...)` 成为返回值：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

```python filename="src/routes/users/[id].py"
async def GET(id: int):
    return {"id": id, "name": "Ada"}  # res.json({ id, name })
```
<!-- /router -->

<!-- router:modular -->
| 快递 | 内克西 |
|---|---|
| `app.get("/users/:id", handler)` | `@Controller("/users/{id}")`，与 `async def get(self, id: int)` |
| `app.use(middleware)` | FastAPI 中间件，从 `nexyconfig.py` 注册 |
| `res.json(obj)` | 返回字典或 Pydantic 模型 |
| EJS / 哈巴狗观点 | `.nexy` (Jinja2) 视图，由 `useViews` 返回 |
| `npm run dev` | `nx dev` |

`app.use(...)` 成为 `nexyconfig.py` 的字段，`res.json(...)` 成为返回值：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users/{id}")
class UserController:
    async def get(self, id: int):
        return {"id": id, "name": "Ada"}  # res.json({ id, name })
```
<!-- /router -->

## 选择路由器

| 使用 | 当 |
|---|---|
| 基于文件的路由器 | 从文件映射的页面和端点；默认值 |
| 模块化路由器 | 控制器、模块和依赖注入，NestJS 风格 |

模块化路由器分为两个文件：一个控制器，模块 `nexyconfig.py` 指向 `useRouter = AppModule`：

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller


@Controller()
class AppController:
    async def get(self):
        return {"message": "Hello"}
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

两者都由 `nx new` 搭建，并由相同的端到端测试覆盖。请参阅[路由](../routing/README.md) 和[模块化路由](../routing/modular/README.md)。

## 下一步去哪里

- [快速入门](quick-start.md)：创建项目并运行
- [项目结构](project-structure.md)：每个文件所属的位置
- [路由](../routing/README.md)：选择路由器
