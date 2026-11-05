# 挂钩

Hooks 从 `.nexy` 页面、API 处理程序或模块化控制器内部读取当前的 HTTP 请求。它们的名称与客户端路由器 (`@nexy/client`) 的钩子匹配，它们在其中执行相同的操作。

> [!NOTE]
> 挂钩仅在处理请求时起作用。在其他地方跟注 1 会加注 `RuntimeError`。

## 钩子

| 钩子 | 返回 |
|---|---|
| `usePathname()` | 请求路径，例如 `"/blog/post-1"` |
| `useSearchParams()` | 查询字符串为 `dict[str, str]`，每个键的第一个值 |
| `useParams()` | 动态路径参数，例如 `{"slug": "post-1"}` |
| `useQuery()` | `useParams()` 的原始名称，为现有页面保留 |
| `useRequest()` | Starlette 请求，其他钩子没有覆盖 |
| `useHeaders()` | 请求标头为 `dict[str, str]`，名称小写 |
| `useUrl()` | 完整 URL：`.scheme`、`.hostname`、`.port`、`.path`、`.query` |
| `useIsActive(href, exact=False)` | `href` 是否是当前页面或其父页面之一 |
| `useRouter()` | `{"path", "base_url", "url_for"}` |
| `useCookies()` | 所有 cookie 为 `dict[str, str]` |
| `useSession()` | 会话字典，`{}` 未启用会话时 |
| `useToc(depth_range="2-6")` | 当前页面的 HTML 目录，`""` 没有时 |
| `useViews(path, context=None)` | 渲染另一个视图并返回 `HTMLResponse` |

## 阅读请求

```nexy filename="src/routes/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```

## 导航栏中的活动链接

`useIsActive` 遵循与客户端相同的规则：查询字符串、片段和尾部斜杠被忽略，除非设置 `exact`，否则到父级的链接在其子级上处于活动状态，并且 `/` 仅在 `/` 上处于活动状态。

```nexy filename="src/components/NavLink.nexy"
---
from nexy import useIsActive

href: prop[str]
label: prop[str]
---
<a href="{{ href }}"{% if useIsActive(href) %} aria-current="page"{% endif %}>{{ label }}</a>
```

## 注释

- `useQuery()` 返回 **path** 参数，而不是查询字符串，这就是 `useParams()` 存在的原因。查询字符串是 `useSearchParams()`。
- `useRouter()` 这是请求挂钩。挂载 `APIRouter` 的不是 `useRouter` 配置字段。
- `useSession()` 需要 `nexyconfig.py`中的 `useSession = {...}`；没有它，字典就是空的。
- `useViews("about.tsx", {"title": "About"})` 返回 HTML：`.nexy` 视图由其编译模块呈现，`.tsx`/`.jsx`/`.vue`/`.svelte`/`.mdx` 视图成为客户端安装容器。

## 后续步骤

- [页面](../pages/README.md)：动态段和布局
- [食谱](../../../guides/recipes.md)：基于 `useSession()` 构建的经过测试的登录流程
- [配置](../../../reference/config.md)：启用会话和区域设置
- [.nexy 文件](../../../views/nexy/README.md)：通常调用钩子的地方
