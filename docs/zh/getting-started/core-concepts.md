# 核心理念

文档的其余部分使用的单词 - 路由、页面、视图、组件、处理程序、端点 - 每个都在一行中，并带有指向更深入页面的链接。新来内克西？从[Nexy 是什么？](what-is-nexy.md) 开始。

## 如何阅读这些文档

| 级别 | 它回答的问题 | 开始于 |
|---|---|---|
| 应用架构 | 哪一层响应请求，以及拒绝执行什么操作 | [Nexy 的工作原理](how-nexy-works.md) |
| 应用结构 | 代码所在的位置以及文件的内容 | [项目结构](project-structure.md) |
| 演示和渲染 | 读者看到什么以及谁生成 HTML | [视图](../views/README.md)、[渲染](../rendering/README.md) |
| 应用交互 | 读者做了什么，以及响应了什么 | [行动](../guides/actions.md) |

级别按该顺序读取一次。之后，您需要的页面是查找，而不是课程。

## 应用架构

决定哪些代码响应 URL 的三种方法。它们是替代方案，而不是层：

- **基于文件的路由（FBR）**：`src/routes/` 下的文件是一个路由。默认。
- **模块化路由器**：`src/apps/`下的控制器和模块，用装饰器声明，用于NestJS风格的代码库。
- **自定义路由器**：应用程序中包含的现有 FastAPI `APIRouter`。

选择的是 `nexyconfig.py` 中 `NexyConfig` 类的一行。

<!-- router:fbr -->
基于文件的路由不需要行：没有 `useRouter`，Nexy 读取 `src/routes/`。

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    pass  # file-based: no useRouter, the files of src/routes/ are the routes
```
<!-- /router -->

<!-- router:modular -->
模块化路由器是 `src/apps/`的根模块：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule  # modular: the root module of src/apps/
```
<!-- /router -->

<!-- router:custom -->
自定义路由器是您已经拥有的 `APIRouter`：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import api  # an APIRouter you already have


class NexyConfig(NexyConfigModel):
    useRouter = api  # custom: your router, included as it is
```
<!-- /router -->

选择三者之一就是一个决定。选择前端框架是另一个单独的框架：请参阅[选择路由器](../routing/README.md) 和[视图](../views/README.md)。

## 应用结构

来自 Next.js 的读者通常会将五个概念合并为一个。它们不是同一件事，这种差异解释了大多数“为什么我的页面不渲染”的问题。

| 观念 | 它是什么 | 它不是什么 |
|---|---|---|
| **路线** | 由文件路径生成的 URL 模式 | 一个文件：一个文件可以回答多个 URL (`[slug]`) |
| **页** | 渲染视图的路由文件：`.nexy`、`.md`、`.mdx`、`.tsx`、`.vue`、`.svelte` | 端点：它回答文档，而不是数据 |
| **查看** | 生成页面正文的内容：Jinja2 和 Python、Markdown 或客户端组件 | 一条路线：同一个视图可以服务多个页面 |
| **组件** | 页面导入的可重用部分 | 路由：在服务器模式下，组件永远不会单独提供服务 |
| **路由处理程序** | `.py` 路由文件的功能，以 HTTP 方法命名（`GET`、`POST`、...） | 页面：它返回 JSON、文件或 `Response` |
| **端点** | 处理程序回答的对（URL、方法） | 处理程序：一个文件可以回答多个端点 |

用一句话来说：**页面是一个路由文件，视图是渲染它的东西，组件是页面重用的东西，处理程序回答端点。**

<!-- router:fbr -->
五合一小项目：

```text
src/
├─ routes/
│  ├─ blog/[slug].nexy    a route (/blog/{slug}) whose file is a page
│  └─ api/posts.py        a route whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```nexy filename="src/routes/blog/[slug].nexy"
---
from "@/components/Like.tsx" import Like

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Like post="{{ slug }}" />
```

frontmatter及其下面的模板是页面的视图； `Like` 是它重用的组件。

```python filename="src/routes/api/posts.py"
async def GET():  # the endpoint GET /api/posts
    return {"posts": []}


async def POST():  # the endpoint POST /api/posts
    return {"created": True}
```

<!-- /router -->

<!-- router:modular -->
对于模块化路由器，路由是控制器的路径，处理程序是其方法之一，以 HTTP 动词命名：

```text
src/
├─ apps/
│  ├─ app_module.py       the root module: lists the controllers
│  └─ posts_controller.py a route (/api/posts) whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```python filename="src/apps/posts_controller.py"
from nexy.decorators import Controller


@Controller("/api/posts")
class PostsController:
    async def get(self) -> dict:  # the endpoint GET /api/posts
        return {"posts": []}

    async def post(self) -> dict:  # the endpoint POST /api/posts
        return {"created": True}
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .posts_controller import PostsController


@Module()
class AppModule:
    controllers = [PostsController]
```

页面仍然是 `src/routes/`的文件，或者控制器以 `useViews`返回的视图。
<!-- /router -->

<!-- router:custom -->
对于自定义路由器，路由是 `APIRouter` 的路径，处理程序是其装饰器注册的函数：

```python filename="src/legacy.py"
from fastapi import APIRouter

api = APIRouter()


@api.get("/api/posts")  # the endpoint GET /api/posts
async def list_posts():
    return {"posts": []}


@api.post("/api/posts")  # the endpoint POST /api/posts
async def create_post():
    return {"created": True}
```

页面仍然是 `src/routes/`的文件：`.nexy` 页面在包含的路线旁边进行回答。
<!-- /router -->

还有两个词随处可见：

- **布局**：一个 `layout.*` 文件，包裹其文件夹下的页面； root 拥有 HTML 文档。请参阅[布局](../routing/fbr/layouts/README.md)。
- **依赖项**：在处理程序之前运行的函数，应用于每个路由或每个文件夹。请参阅[依赖关系](../routing/fbr/dependencies/README.md)。

## 演示和渲染

两个独立的决定，经常混淆：

- **格式** 决定哪个文件呈现页面：[视图](../views/README.md)。
- **模式** 决定谁生成HTML以及何时生成：[渲染](../rendering/README.md)。

| 观念 | 一条线 |
|---|---|
| 服务器模式 | 服务器呈现 `.nexy` 和 `.md` 页面；组件是岛屿（[模式](../routing/fbr/modes.md)） |
| 客户端模式 | `useCSR = True`：框架文件是路线，导航发生在浏览器中 |
| SSR、ISR、CSR、岛屿 | 四种渲染模式，按页面决定，CSR 除外，CSR 是按项目决定的 ([渲染](../rendering/README.md)) |
| 保湿 | 浏览器将框架附加到服务器已发送的 HTML ([岛屿](../rendering/islands.md)) |
| 道具 | 父级传递给组件的值，在 `.nexy` 文件（[.nexy 文件](../views/nexy/README.md)）中声明为 `name: prop[type]` |

具有一个岛的服务器模式页面：服务器呈现页面，浏览器仅在图表滚动到视图中时才对图表进行水合。

<!-- router:fbr,custom -->
```nexy filename="src/routes/sales.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Sales</h1>
<Chart directive="client:visible" />
```
<!-- /router -->

<!-- router:modular -->
岛屿进入视图，控制器返回视图：

```nexy filename="src/apps/sales_view.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Sales</h1>
<Chart directive="client:visible" />
```

```python filename="src/apps/sales_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/sales")
class SalesController:
    async def get(self):
        return useViews("src/apps/sales_view.nexy")
```
<!-- /router -->

## 应用交互

| 观念 | 一条线 |
|---|---|
| 行动 | 标记为 `@Action` 的 Python 函数，用作 `POST`，可从表单调用或作为类型化函数 ([操作](../guides/actions.md)) |
| 形式 | 发布到操作的 HTML 表单，验证错误返回到页面 ([操作](../guides/actions.md)) |
| 导航 | 预取的链接，以及读取路径、查询、cookie 和会话的钩子 ([钩子](../routing/fbr/navigation/hooks.md)) |
| 数据获取 | 由需要它的页面或处理程序完成； Nexy 不提供客户端数据层（[处理函数](../routing/fbr/handlers/README.md)） |

一个操作和发布到它的表单，在任何脚本加载之前起作用：

```python filename="src/actions/newsletter.py"
from nexy.decorators import Action


@Action
async def subscribe(email: str) -> bool:
    return True
```

<!-- router:fbr,custom -->
```html filename="src/routes/index.nexy"
<form method="post" action="{{ __actions_path['subscribe'] }}">
  <input name="email" type="email">
  <button type="submit">Subscribe</button>
</form>
```
<!-- /router -->

<!-- router:modular -->
```html filename="src/apps/home_view.nexy"
<form method="post" action="{{ __actions_path['subscribe'] }}">
  <input name="email" type="email">
  <button type="submit">Subscribe</button>
</form>
```
<!-- /router -->

## Nexy 不做什么

身份验证、授权、数据库、国际化、后台作业、电子邮件、付款和搜索是 **您的应用程序的责任**，而不是框架的责任。 Nexy 给出了扩展点并说明了每个扩展点的插入位置：请参阅 [Nexy 留给您的内容 ](how-nexy-works.md#what-nexy-leaves-to-you)。

<!-- router:fbr -->
例如，身份验证插入到其保护的文件夹的依赖项中。 Nexy 在下面的每条路线之前运行它；用户是谁由您决定：

```python filename="src/routes/account/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```
<!-- /router -->

<!-- router:modular -->
例如，身份验证插入其保护的控制器上的防护装置。 Nexy 在类的每个处理程序之前运行它；用户是谁由您决定：

```python filename="src/apps/account_controller.py"
from nexy import unauthorized
from nexy.decorators import Controller, UseGuard
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


@Controller("/account")
@UseGuard(require_login)
class AccountController:
    async def get(self) -> dict:
        return {"ok": True}
```
<!-- /router -->

<!-- router:custom -->
例如，身份验证插入到它所保护的路由器的依赖项中，如 FastAPI 中所示；用户是谁由您决定：

```python filename="src/account.py"
from fastapi import APIRouter, Depends

from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


api = APIRouter(prefix="/account", dependencies=[Depends(require_login)])
```
<!-- /router -->

原因并不是极简主义本身：选择 ORM 或身份验证库的框架已经决定了只有您的应用程序才能决定的事情。

## 后续步骤

- [项目结构](project-structure.md)：项目的每个文件夹和文件
- [词汇表](../reference/glossary.md)：相同的单词，在一个字母索引中
- [Nexy 的工作原理](how-nexy-works.md)：层、谁构建什么以及 Nexy 留给您什么
