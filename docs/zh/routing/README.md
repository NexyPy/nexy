# 路由

Nexy 有两个本地路由器。您可以为每个功能选择一个；它们可以共存于同一应用程序中。

**没有把握？使用基于文件的路由。** 它涵盖了无需设置的页面和 API 端点。当后端需要控制器、注入服务或防护时添加模块化路由器。

| 你正在建造 | 使用 |
|---|---|
| 页面、内容、具有几个端点的站点 | 基于文件 |
| 具有跨路由共享服务的大型 API | 模块化 |
| 两者：为人服务的页面，为机器服务的结构化 API | 基于文件和模块化相结合 |

```diagram filename="基于文件的路由器概览"
src/routes/index.nexy           →  /
src/routes/about.nexy           →  /about
src/routes/blog/index.nexy      →  /blog
src/routes/blog/[slug].nexy     →  /blog/:slug
src/routes/(app)/dashboard.nexy →  /dashboard
src/routes/api/users.py         →  /api/users  (GET, POST, …)
```

| 路由器 | 来源 | 启用者 |
|---|---|---|
| [基于文件 (FBR)](fbr/README.md) | `src/routes/` 下的每个文件 | 该目录存在 |
| [模块化](modular/README.md) | 控制器和模块 | `useRouter = AppModule` 在 `nexyconfig.py` |

只要 `src/routes/` 存在，即使安装了模块化路由器，FBR 也会被扫描。

## 共存和优先事项

您可以结合 FBR、模块化和自定义集成。 Nexy 按照发现的顺序注册这些路由。如果两个路由器定义相同的 URL 路径，则第一个注册的路由器获胜。 

*注意：Nexy 目前不提供 URL 冲突诊断；第一条声明路径的路线只会遮蔽其他路线。*

## 基于文件的路由

路线是一个文件。 URL 是 `src/routes/` 下的路径，减去扩展名。与 Next.js 一样，项目处于两种模式之一，通过 `useCSR` 选择：

| | `useCSR = False`（默认） | `useCSR = True` |
|---|---|---|
| 页数 | `.nexy`，`.md`，`.mdx` | 您的客户端框架的文件 |
| 根布局 | `layout.nexy` | `layout.tsx`（React） |
| 客户端组件 | 允许，作为页面内的岛屿 | 页面本身 |
| API路线 | `.py` | `.py` |

请参阅[服务器模式和客户端模式](fbr/modes.md)。

| 部分 | 它涵盖什么 |
|---|---|
| [fbr/页](fbr/pages/README.md) | 页面、[动态路由](fbr/pages/dynamic-routes.md) 和路由组 |
| [fbr/布局](fbr/layouts/README.md) | `layout.nexy`、`layout.tsx`、`layout.vue`、`layout.svelte` |
| [fbr/处理程序](fbr/handlers/README.md) | `.py` 路由处理程序，[验证和错误](fbr/handlers/validation-and-errors.md) |
| [fbr/依赖项](fbr/dependencies/README.md) | `dependencies.py` 和守卫，由目录继承 |
| [fbr/中间件](fbr/middleware/README.md) | `middleware.py`，由目录继承 |
| [fbr/错误](fbr/errors/README.md) | `notfound.nexy`、`errors.nexy`、JSON 错误 |
| [fbr/导航](fbr/navigation/linking-and-navigating.md) | 链接、客户端导航、[钩子](fbr/navigation/hooks.md) |
| [fbr/实时](fbr/realtime/websocket.md) | WebSocket 处理程序 |
| [fbr/继承](fbr/inheritance.md) | 布局、依赖关系和错误页面如何继承 |

## 模块化路由

控制器、模块和依赖注入，采用 NestJS 的风格。请参阅[模块化路由](modular/README.md) 和[Nexy 和 NestJS](modular/vs-nestjs.md)。

## 定制集成

您还可以将现有的 FastAPI 路由器集成到您的 Nexy 项目中。请参阅[自定义路由集成](custom/README.md)。

## 后续步骤

- [基于文件的路由](fbr/README.md)
- [渲染](../rendering/README.md)
- [视图](../views/README.md)：文件内部的内容
