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

| 领域 | 默认 | 含义 |
|---|---|---|
| `usePort` | `3000` | `dev` 和 `start` 的端口 |
| `useHost` | `"0.0.0.0"` | 绑定地址 |
| `useSslKeyfile`，`useSslCertfile` | `None` | 直接提供HTTPS服务 |
| `useDevTools` | `True` | 工具栏 `nexy dev` 添加到每个页面（页面信息、路由、错误、配置）； `False` 将其删除。从未出现在生产中 |
| `useHealth` | `False` | 为负载均衡器和 Kubernetes 探测器提供 `GET /health/live` 和 `GET /health/ready` 服务；请参阅[部署](../deployment/README.md#built-in-endpoints) |
| `useMaxBodySize` | `1048576` | 工作线程读取的最大请求正文，以字节为单位 (1 MiB)；较大的为 `413`，`0` 则关闭限制。为需要文件上传的路由提高它 |
| `useSiteUrl` | `None` | 网站的公共来源，例如 `"https://example.com"`；一旦设置，Nexy 将服务 `/sitemap.xml` 和 `/robots.txt`。请参阅[站点地图和 robots.txt](../guides/sitemap.md) |
| `useWorkers` | `0` | 进程 `nx start` 运行； `0` 是 Linux 和 macOS 上每个 CPU 一个，Windows 上一个 |
| `useCSR` | `False` | 客户端路由模式； `.nexy` 路线已禁用 |
| `useBasePath` | `None` | 整个应用程序的公共前缀，例如 `"/app"`；外部的请求回答 404，生成的链接、客户端路由、操作调用和资产都带有前缀。请参阅[部署](../deployment/README.md#serve-under-a-sub-path) |
| `useImageWidths` | `[320, 640, 960, 1280]` | 像素宽度 `nx build` 为局部图像生成；转换需要 `Pillow`，如果没有它，图像将保留其原始 URL。请参阅[图片](../routing/fbr/navigation/linking-and-navigating.md#image) |
| `useISRCache` | `None` | ISR 存储：`None` 或 `"memory"` 用于一个进程，`"file"` 用于一台主机，`"redis"` 用于多个工作进程，带有 `type` 和选项的映射，或者带有 `get`、`set` 和 `invalidate` 的对象。参见[ISR](../rendering/isr.md#choose-a-store) |

## 数据库

| 领域 | 默认 | 含义 |
|---|---|---|
| `useORM` | `None` | 项目的 ORM：`"SQLModel"`、`"SQLAlchemy"` 或 `"Tortoise-ORM"`。 `nx new` 写入它，`nx migrate` 从中选择 Alembic 或 Aerich；如果没有它，`nx migrate` 将采用第一个安装的 ORM。请参阅[数据库](../guides/databases.md#migrations) |

## 路线

| 领域 | 默认 | 含义 |
|---|---|---|
| `useRouter` | `None` | 安装在基于文件的路由旁边的 `APIRouter` 实例或类； `None` 表示仅基于文件 |
| `excludeDirs` | `["templates", "extension", "docs"]` | 扫描路由时跳过的目录 |
| `useAliases` | `None` | 导入别名，例如 `{"@": "src"}`（`@/components/Counter.tsx` 表示 `src/components/Counter.tsx`）； `nx new` 写入您选择的内容，Vite 和 `tsconfig.json` 紧随其后 |

## 前端

| 领域 | 默认 | 含义 |
|---|---|---|
| `useFF` | `None` | 客户端框架工厂：`react()`、`vue()`、`svelte()`、`solid()`、`preact()` |
| `useVite` | `True` | 使用 Vite 构建并提供客户端捆绑包 |
| `useMarkdownExtensions` | `[]` | `.md`/`.mdx` 渲染的额外扩展 |
| `useWatchExtensions` | `None` | 开发服务器监视的额外扩展 |
| `useWatchExcludePatterns` | `None` | 开发服务器忽略的 glob 模式 |

> **很高兴知道**：`NexyConfigModel` 声明 `useVite = False`；运行时 `Config` 默认为 `True`。

## 保留文件名

每个字段都会为保留角色添加扩展。 `useLayoutExtensions = ["md"]` 使 `layout.md` 保留，与 `layout.nexy` 完全相同。

| 领域 | 添加扩展 |
|---|---|
| `useLayoutExtensions` | `layout.*` |
| `useNotFoundExtensions` | `notfound.*` |
| `useErrorsExtensions` | `errors.*` |
| `useForbiddenExtensions` | `forbidden.*` |
| `useUnauthorizedExtensions` | `unauthorized.*` |
| `useLoadingExtensions` | `loading.*` |

## API文档

| 领域 | 默认 | 含义 |
|---|---|---|
| `useDocs` | `"dev"` | 其中提供标量参考页面和 `/openapi.json`：`"dev"` 仅在 `nx dev` 上，`True` 也在生产中（架构列出了每个路由和服务器操作），`False` 无处 |
| `useDocsUrl` | `"/docs"` | API参考页面路径 |
| `useRedocsUrl` | `"/redocs"` | 已声明但未安装路由 |
| `useTitle` | `"Nexy App"` | OpenAPI 标题和页面标题（`NexyConfigModel` 中的 `"Nexy"`） |

### 项目页面的免费 `/docs`

API 参考在任何路由之前回答 `/docs`，因此永远不会在那里提供 `src/routes/docs.nexy` 或 `src/routes/docs/[[...slug]].nexy`。 `nx dev` 和 `nx start` 在启动时命名这样的页面。使用 `useDocsUrl` 移动引用：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useDocsUrl = "/api-reference"
```

或者使用 `useDocs = False` 将其关闭，这也会停止服务 `/openapi.json`。当参考打开时，使项目的路线远离该路径。

## 中间件

| 领域 | 默认 | 含义 |
|---|---|---|
| `useMiddlewares` | `[]` | ASGI中间件类 |
| `useCORS` | `None` | 夸格斯 `CORSMiddleware` |
| `useGZip` | `None` | 夸格斯 `GZipMiddleware` |
| `useTrustedHost` | `None` | 夸格斯 `TrustedHostMiddleware` |
| `useSession` | `None` | 夸格斯 `SessionMiddleware` |
| `useAuth` | `None` | 身份验证中间件配置 |
| `useHTTPSRedirect` | `False` | 将 HTTP 重定向到 HTTPS |

## Markdown

| 领域 | 默认 | 含义 |
|---|---|---|
| `useTocDepth` | `"2-6"` | 目录中包含的标题级别 |
| `useTocTitle` | `"Table of Contents"` | 目录标题 |
| `useTocAuto` | `True` | 生成 Markdown 页的目录 |

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
