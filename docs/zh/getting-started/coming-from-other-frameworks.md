# 来自另一个框架

Nexy 是 FastAPI 加上基于文件的路由、服务器渲染页面和可选的 React、Vue、Svelte、Solid 或 Preact 岛。此页面映射了您已经知道的内容。

## 来自 FastAPI

| FastAPI | 尼克西 |
|---|---|
| `@app.get("/users")` 在模块中导入 | `GET` 函数 `src/routes/users.py` |
| `app.include_router(router)` | 文件路径为 URL；无需注册 |
| 路径参数 `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | 仍然 `Depends(...)`：处理程序是 FastAPI 处理程序 |
| Jinja2 `TemplateResponse` | 端点 | 旁边的 `.nexy` 页面
| 使用 `uvicorn main:app` | `nx dev` 运行，然后 `nx build && nx start` |

`src/routes/*.py` 下的所有内容都是普通的 FastAPI：依赖项、Pydantic 模型、中间件和 `/docs` 继续工作。

## 来自 Next.js

| Next.js | 尼克西 |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` 或 `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx`（拥有 `<html>`）|`src/routes/layout.tsx` 与 `useCSR = True`（React），或服务器模式 | 中的 `src/routes/layout.nexy`
| 客户端模式下嵌套 `layout.tsx` | 客户端模式下嵌套 `layout.tsx` / `layout.vue` / `layout.svelte`，服务器模式 | 下嵌套 `layout.nexy`
| `use client` 服务器页面中的组件 | [服务器模式中的岛屿 ](../rendering/islands.md) |
| 路由处理程序 `route.ts` | `src/routes/api/x.py`，写在 Python | 中
| `(group)` 文件夹 | 相同：`(group)/`|
| 服务器操作 | [`@Action`](../guides/actions.md) 从表单调用的函数或作为键入的客户端函数 |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

后端是 Python，因此您的 API 与您的数据和 ML 工作共享代码。客户端组件作为岛屿而不是整个页面的 React 树进行水合。

## 来自 Express 或 Node 后端

| 快递 | 尼克西 |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` 与 `async def GET(id)` |
| `app.use(middleware)` | FastAPI 中间件，从 `nexyconfig.py` | 注册
| `res.json(obj)` | 返回一个字典或 Pydantic 模型 |
| EJS / Pug 视图 | `.nexy` (Jinja2) 页 |
| `npm run dev` | `nx dev` |

## 选择路由器

| 当 | 时使用 |
|---|---|
| 基于文件的路由器 | 页面和从文件映射的端点；默认 |
| 模块化路由器 | 控制器、模块和依赖项注入，NestJS 风格 |

两者都由 `nx new` 搭建，并由相同的端到端测试覆盖。请参阅[路由](../routing/README.md) 和[模块化路由](../routing/modular/README.md)。

## 下一步去哪里

- [快速启动](quick-start.md)：创建项目并运行
- [项目结构](project-structure.md)：每个文件所属的位置
- [路由](../routing/README.md)：选择路由器
