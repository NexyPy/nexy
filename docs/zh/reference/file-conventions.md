# 文件约定

`src/routes/` 下的保留名称和规则。

## 路线文件

| 文件 | 成为 |
|---|---|
| `index.nexy`、`index.md`、`index.mdx`、`index.py` | 其目录的路径 |
| `about.nexy` | `/about` |
| `[slug].nexy` | 动态段 `{slug}` |
| `[...path].nexy` | 包罗万象 `{path:path}` |
| `(group)/page.nexy` | `/page`：该组未出现在 URL 中 |
| `name.py` | API 处理程序；函数名 `GET`, `POST`, ... 是方法 |
| `name.tsx`、`.jsx`、`.vue`、`.svelte` | 使用 `useFF` 启用框架时的客户端路由 |

```text
src/routes/
├─ index.nexy           /
├─ about.nexy           /about
├─ (marketing)/
│  └─ pricing.nexy      /pricing
├─ blog/
│  ├─ index.md          /blog
│  └─ [slug].nexy       /blog/{slug}
├─ docs/
│  └─ [...path].nexy    /docs/{path:path}
└─ api/
   └─ users.py          GET /api/users, POST /api/users
```

```python filename="src/routes/api/users.py"
async def GET():
    return {"users": []}


async def POST():
    return {"created": True}
```

## 保留文件

| 文件 | 角色 | 详情 |
|---|---|---|
| `layout.nexy` | 服务器模式：包装其下面的每个页面；根目录拥有 HTML 文档 | [布局.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | 客户端模式（React）：根拥有 HTML 文档，嵌套包含页面 | [布局.tsx](../views/react/differences.md) |
| `layout.vue`，`layout.svelte` | 客户端模式：嵌套布局 | [布局.vue](../views/vue/differences.md), [布局.svelte](../views/svelte/differences.md) |
| `notfound.nexy` | 其目录的 404 页面 | [错误页面](../routing/fbr/errors/README.md) |
| `errors.nexy` | 目录 500 页 | [错误页面](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | 其目录的 403 页面 | [每个文件夹的错误页](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | 其目录的 401 页面 | [每个文件夹的错误页](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | 保留；还没有运行时效果 | [错误页面](../routing/fbr/errors/README.md) |
| `middleware.py` | `async def middleware(request, call_next)` 包装目录及以下目录的请求 | [中间件文件](../routing/fbr/middleware/README.md) |
| `dependencies.py` | 应用于目录及其子目录的 `dependencies = [fn, ...]` 列表 | [依赖项](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Python 包标记 | |
| `favicon.ico` | 服务于 `/favicon.ico` | |

`useLayoutExtensions`、`useNotFoundExtensions`、`useErrorsExtensions`、`useForbiddenExtensions`、`useUnauthorizedExtensions` 和 `useLoadingExtensions` 为这些名称保留更多扩展名。请参阅[配置](config.md)。

表的两个 Python 文件并排位于一个文件夹中：

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

```python filename="src/routes/admin/dependency.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

以及一个回答其文件夹 404 的页面：

```nexy filename="src/routes/notfound.nexy"
<h1>Page not found</h1>
<p><a href="/">Back home</a></p>
```

## 忽略的文件

- 以 `_` 或 `.` 开头的文件或文件夹：将其用于部分、草稿和助手。
- 扩展名对于项目无效的文件：将跳过该文件并显示警告。

```text
src/routes/
├─ index.nexy           /
├─ _card.nexy           ignored: a partial the pages include
├─ _helpers/            ignored, with everything inside
│  └─ format.py
└─ .draft.nexy          ignored: a draft
```

## 每个 URL 一个文件

解析为同一 URL 的两个文件都会注册。请勿将 `blog.nexy` 放在 `blog/index.nexy` 旁边。

```text
src/routes/
├─ blog.nexy            /blog
└─ blog/
   └─ index.nexy        /blog as well: keep only one of the two
```

## 外面 `src/routes/`

| 文件夹 | 目的 |
|---|---|
| `src/components/` | 页面导入的组件；从不路由 |
| `src/apps/` | [模块化路由器](../routing/modular/README.md) 的控制器和模块 |
| `public/` | 静态文件，位于根目录：`public/logo.svg` 是 `/logo.svg`（也在 `/public/` 下） |
| `__nexy__/` | 生成的输出；不承诺 |

```text
my-app/
├─ nexyconfig.py
├─ public/
│  └─ logo.svg          /logo.svg
├─ src/
│  ├─ routes/           the routes
│  ├─ components/
│  │  └─ Counter.tsx    imported by pages, never served on its own
│  └─ apps/             the modular router, when you use it
└─ __nexy__/            generated: add it to .gitignore
```

## 后续步骤

- [路由](../routing/README.md)
- [项目结构](../getting-started/project-structure.md)
