# Python API

Nexy 按模块将每个名称导出到您的 Python 代码。测试会在两个方向上对照代码检查此页面：此处列出的名称必须存在，并且此处必须列出代码导出的名称。

## `nexy`

`.nexy` 模板和请求挂钩的组件。

| 名称 | 它是什么 |
|---|---|
| `Audio`，`Video` | 原生 `<audio>` 和 `<video>` 玩家，请参阅 [组件 ](../views/nexy/components.md) |
| `Image` | 默认情况下延迟加载的 `<img>` |
| `Link` | 具有可选预取功能的客户端 `<a>` |
| `Import` | 将客户端组件导入 `.nexy` 页面 |
| `Template` | 渲染 Jinja2 和 Markdown 模板 |
| `Vite` | 每个页面都需要的 Vite 客户端标签 |
| `Form` | 没有行为的占位符：使用带有 [操作](../guides/actions.md) 的普通 `<form>` |
| `usePathname` | 当前请求的路径 |
| `useSearchParams` | 作为字典的查询字符串 |
| `useParams` | 动态路径参数作为字典，例如客户端上的 `useParams()` |
| `useQuery` | `useParams` 的原始名称，为现有页面保留（它不读取查询字符串） |
| `useRequest` | 当前请求，其他钩子未涵盖的内容 |
| `useHeaders` | 请求标头作为具有小写名称的字典 |
| `useUrl` | 完整网址：`.scheme`、`.hostname`、`.path`、`.query` |
| `useIsActive` | 对于导航栏，链接是否指向当前页面或其父页面之一 |
| `useRouter` | 当前请求的 `path`、`base_url` 和 `url_for` |
| `useSession` | 会话字典，会话关闭时为空 |
| `useCookies` | 请求 cookie 作为字典 |
| `useToc` | 当前页面的目录，HTML 格式 |
| `useViews` | 从处理程序渲染视图文件，例如 `about.tsx` |
| `setMetadata`，`useMetadata` | 命名页面的标题和头标签，并将它们写在布局中 |
| `redirect`，`permanentRedirect` | 将访问者发送到其他地方（307、308）并停止请求 |
| `notFound`，`forbidden`，`unauthorized` | 从任何地方接听 404、403 或 401 |

挂钩仅在请求内工作：请参阅[钩子](../routing/fbr/navigation/hooks.md)。

## `nexy.http`

处理程序的 HTTP 词汇。从这里导入而不是从 FastAPI 导入，因此您的处理程序取决于 Nexy 的合同。

| 名称 | 它是什么 |
|---|---|
| `Request`，`Response` | 传入请求和传出响应 |
| `HTTPException` | 使用状态和 `detail` 停止处理程序 |
| `status` | 命名状态代码，例如 `status.HTTP_404_NOT_FOUND` |
| `Depends` | 首先运行一个函数并将其结果传递给 |
| `Header`、`Cookie`、`Query`、`Path`、`Body` | 参数从哪里来 |
| `Form`，`File`，`UploadFile` | 表单字段和上传（需要 `python-multipart`） |
| `BackgroundTasks` | 发送答案后运行的工作 |
| `JSONResponse`，`HTMLResponse`，`PlainTextResponse` | 具有固定内容类型的答案 |
| `RedirectResponse` | HTTP 重定向 |
| `redirect`，`permanentRedirect` | 从页面、处理程序、控制器或防护程序引发重定向（307、308） |
| `notFound`，`forbidden`，`unauthorized` | 从同一地点提出 404、403 或 401 |
| `FileResponse`，`StreamingResponse` | 用文件或流回答 |

## `nexy.decorators`

| 名称 | 它是什么 |
|---|---|
| `Action` | 将函数转换为 `POST` 端点，请参阅 [操作](../guides/actions.md) |
| `revalidate` | 告诉浏览器哪些页面的操作已过时 |
| `Module`，`Controller` | 在[模块化路由器](../routing/modular/README.md) 中声明一个模块和一个控制器 |
| `Injectable`，`Container`，`Scope` | [依赖注入](../routing/modular/dependency-injection.md) 及其生命周期 |
| `UseGuard`，`Middleware` | 保护或包装一个处理程序，请参阅 [守卫](../routing/modular/guards-and-metadata.md) |
| `UseRoute`，`useRoute`，`RouteMeta` | 命名一条路线并为 OpenAPI 描述它 |
| `UseResponse`，`ResponseMeta` | 描述一条路线的答案 |
| `HTTP_METHODS` | 处理程序文件可以定义的 HTTP 方法 |
| `ACTIONS_STORE` | 用于工具和测试的操作注册表 |

## `nexy.testing`

| 名称 | 它是什么 |
|---|---|
| `render` | 给定 props 的 `.nexy` 组件的 HTML，没有服务器，请参阅 [测试](../guides/testing.md) |

## 下一步去哪里

- [配置](config.md)：这些名称后面的 `use*` 字段
- [异常和错误](exceptions.md)：每个失败的答案
- [文档索引](../README.md)：您正在构建的页面
