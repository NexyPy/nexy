# 配置

Configuration 是项目根目录 `nexyconfig.py` 中的一个类。 Nexy 从它运行的目录加载它；没有该文件的项目使用默认值。

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    usePort = 3000
    useTitle = "My App"
    useAliases = {"@": "src"}
```

## 服务器

| 字段 | 默认 | 含义 |
|---|---|---|
| `usePort` | `3000` | 端口用于 `dev` 和 `start` |
| `useHost` | `"0.0.0.0"` | 绑定地址 |
| `useSslKeyfile`、`useSslCertfile` | `None` | 直接提供 HTTPS |
| `useDevTools` | `True` | 工具栏 `nexy dev` 添加到每个页面（页面信息、路由、错误、配置）； `False` 将其删除。从未出现在生产中 |
| `useWorkers` | `0` | 进程 `nx start` 运行； `0` 在 Linux 和 macOS 上是每个 CPU 一个，在 Windows 上是每个 CPU |
| `useCSR` | `False` | 客户端路由模式； `.nexy` 路线已禁用 |

## 路线

| 字段 | 默认 | 含义 |
|---|---|---|
| `useRouter` | `None` | 一个 `APIRouter` 实例或类安装在基于文件的路由旁边； `None` 表示仅基于文件 |
| `excludeDirs` | `["templates", "extension", "docs"]` | 扫描路线时跳过的目录 |
| `useAliases` | `None` | 导入别名，例如 `{"@": "src"}`（`@/components/Counter.tsx` 表示 `src/components/Counter.tsx`）； `nx new` 写入您选择的内容，Vite 和 `tsconfig.json` 紧随其后 |

## 前端

| 字段 | 默认 | 含义 |
|---|---|---|
| `useFF` | `None` | 客户端框架工厂：`react()`、`vue()`、`svelte()`、`solid()`、`preact()` |
| `useVite` | `True` | 使用 Vite | 构建并提供客户端捆绑包
| `useMarkdownExtensions` | `[]` | 用于 `.md`/`.mdx` 渲染 | 的额外扩展
| `useWatchExtensions` | `None` | 开发服务器监视的额外扩展 |
| `useWatchExcludePatterns` | `None` | 开发服务器忽略的 glob 模式 |

> **很高兴知道**：`NexyConfigModel` 声明 `useVite = False`；运行时 `Config` 默认为 `True`。

## 保留文件名

每个字段都会为保留角色添加扩展。 `useLayoutExtensions = ["md"]` 保留 `layout.md`，与 `layout.nexy` 完全相同。

| 字段 | 将扩展添加到 |
|---|---|
| `useLayoutExtensions` | `layout.*` |
| `useNotFoundExtensions` | `notfound.*` |
| `useErrorsExtensions` | `errors.*` |
| `useForbiddenExtensions` | `forbidden.*` |
| `useUnauthorizedExtensions` | `unauthorized.*` |
| `useLoadingExtensions` | `loading.*` |

## API文档

| 字段 | 默认 | 含义 |
|---|---|---|
| `useDocs` | `True` | 服务于 OpenAPI 模式及其标量参考页 |
| `useDocsUrl` | `"/docs"` | API 参考页面的路径 |
| `useRedocsUrl` | `"/redocs"` | 声明但未安装路由 |
| `useTitle` | `"Nexy App"` | OpenAPI 标题和页面标题（`NexyConfigModel` 中的 `"Nexy"`）|

## 中间件

| 字段 | 默认 | 含义 |
|---|---|---|
| `useMiddlewares` | `[]` | ASGI 中间件类 |
| `useCORS` | `None` | kwargs 为 `CORSMiddleware` |
| `useGZip` | `None` | kwargs 为 `GZipMiddleware` |
| `useTrustedHost` | `None` | kwargs 为 `TrustedHostMiddleware` |
| `useSession` | `None` | kwargs 为 `SessionMiddleware` |
| `useAuth` | `None` | 身份验证中间件配置 |
| `useHTTPSRedirect` | `False` | 将 HTTP 重定向到 HTTPS |

## Markdown

| 字段 | 默认 | 含义 |
|---|---|---|
| `useTocDepth` | `"2-6"` | 目录中包含的标题级别 |
| `useTocTitle` | `"Table of Contents"` | 目录标题 |
| `useTocAuto` | `True` | 生成 Markdown 页 | 的目录

## 文件树外的路由

构建一个 FastAPI `APIRouter` 并用 `useRouter` 安装它。它在基于文件的路由旁边提供：

```python filename="nexyconfig.py"
from fastapi import APIRouter
from nexy.core.models import NexyConfigModel

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


class NexyConfig(NexyConfigModel):
    useRouter = router
```

上面的默认值是从 `nexy/core/config.py`读取的。

## 已声明，尚未阅读

这些字段存在于 `NexyConfigModel` 中，但没有代码使用它们。设置它们没有效果：

`useViteDevUrl`，`useRTL`。

## 后续步骤

- [i18n](../guides/i18n.md)：国际化
- [前端](../guides/frontend.md)：`useFF` 和客户端构建
- [部署](../deployment/README.md)：生产选项
