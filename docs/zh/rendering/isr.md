# ISR（重新验证时过时）

## 定义

ISR 缓存每个 URL 的一个页面的 HTML，并为其提供服务，直到其窗口到期。过期副本仍会提供，而新副本会在后台呈现：即“重新验证时陈旧”。

## 它是如何运作的

`.nexy` 页面前面的 `revalidate = N` 将其打开。 `N` 是秒数；缺失值、零值或负值意味着根本没有缓存。

缓存键仅是 **请求路径** - `request.scope["path"]`。查询字符串不是其中的一部分。

| 什么 | 价值 |
|---|---|
| 钥匙 | URL 路径 (`/blog/hello`) |
| 存储 | 由 `useISRCache` 选择：默认内存、文件、Redis 或自定义存储 |
| 绑定 | 内存存储的 256 个条目，最近最少使用被逐出；文件和 Redis 保留条目直到失效 |
| 响应头 | `cache-control: public, s-maxage=N, stale-while-revalidate=N` |

每个 ISR 响应都携带该标头，包括第一次渲染和存储关闭时的后备渲染。 CDN 可以使用它来保留同一公共 URL 的自己的副本。

## 渲染生命周期

1. 请求到达声明 `revalidate` 的页面。
2. 尚无条目：页面已呈现、存储并返回。
3. 条目早于 `N` 秒：按原样返回，页面不会呈现。
4. 早于 `N` 秒的条目：立即返回 **过时的** 条目，并且后台任务会渲染一个新条目。
5. 如果该后台渲染失败，则过时的条目将保留，并且下一个过时的请求将再次尝试。
6. 如果存储失败，则呈现并返回页面，但不包含缓存条目。请求仍然成功。

## 何时使用

- 每个访问者都使用相同的 HTML：博客文章、产品页面、文档页面。
- 该页面经常被阅读并且很少更改。
- 数据可能已经过几秒钟了，而没有人注意到。

## 配置

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

`N` 是一个普通整数。其他地方没有每路由覆盖，并且 `.py` 处理程序不是页面：它们从不进入此缓存。

## 选择商店

在 `nexyconfig.py` 中设置 `useISRCache`：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useISRCache = "file"
```

| 价值 | 商店 | 分享者 |
|---|---|---|
| 未设置、`None` 或 `"memory"` | 进程内存，限制为 256 个条目 | 一名工人 |
| `"file"` | `.nexy/isr` 中的 JSON 文件 | 一台主机上的工作人员 |
| `{"type": "file", "directory": ".cache/isr"}` | 给定目录中的 JSON 文件 | 一台主机上的工作人员 |
| `"redis"` | Redis 位于 `redis://localhost:6379/0` | 任何到达服务器的工作人员 |
| `{"type": "redis", "url": "redis://cache:6379/0"}` | Redis 位于该 URL | 任何到达服务器的工作人员 |
| `{"type": "redis", "client": client}` | 您传递的 Redis 客户端 | 任何到达服务器的工作人员 |
| 具有 `get`、`set` 和 `invalidate` 的对象 | 你自己的商店 | 无论它分享什么 |

Redis 存储需要客户端包：`uv add redis`。它不随 Nexy 一起安装。自定义商店实现 `nexy.modules.runtime.cache` 中的 `ISRCache` 协议；它的 `get` 返回 `CacheEntry` 或 `None`。

文件条目是自动写入的，因此工作人员永远不会读取写了一半的页面。使用相同目录或相同 Redis 服务器的 Worker 读取相同的条目。损坏的存储只需要渲染一次：它永远不会以错误响应请求。

## 示例

一篇读取数据库的博文：

```nexy filename="src/routes/blog/[slug].nexy"
---
revalidate = 300
slug: prop[str] = "untitled"
posts = {"hello": {"title": "Hello"}, "other": {"title": "Other"}}
post = posts.get(slug, {"title": "Untitled"})
---
<h1>{{ post.title }}</h1>
```

对 `/blog/hello` 的第一个请求呈现并存储。接下来的 300 秒由所选商店提供。 `/blog/other` 是一个单独的条目，单独呈现和存储。在实际项目中 `posts` 来自数据库或服务，每次重新生成时调用一次。

## CDN 可以共享什么，不能共享什么

遵守 `cache-control` 的 CDN 可以将 `/blog/hello` 的一份副本保留 `s-maxage` 秒，并在重新验证时提供该副本。它在访客和工作人员之间共享该副本，因为响应显示为 `public`。

CDN 不知道 Nexy 存储。 [操作](../guides/actions.md) 中的 `revalidate()` 会从配置的 Nexy 存储中删除条目，但不会清除 CDN。 CDN 会保留其副本，直到其自己的窗口结束，或者直到您配置其清除。

不要为 CDN 提供 HTML 取决于访问者的页面。响应显示 `public`，Nexy 的密钥仅是路径：一条路径上的两个查询字符串共享一个条目。 HTML 中的会话、cookie 或用户 ID 可以提供给其他访问者。

## 局限性

**Nexy 保证** 缓存键是路径，在重新生成期间提供过时的副本，并且存储失败会回退到渲染。

**按照约定**，声明 `revalidate` 的页面是公共内容。编写时就像每个访问者看到相同的 HTML 一样。

**您的应用程序负责** 其他一切：

| 限制 | 这意味着什么 |
|---|---|
| 查询字符串被忽略 | `/search?q=a` 和 `/search?q=b` 共享一个条目。不要缓存搜索页面。 |
| 会话未隔离 | 响应为 `public`，并且第一个访问者的 HTML 会提供给所有人。切勿在带有 `revalidate` 的页面中读取会话。 |
| CDN 未清除 | `revalidate()` 清除 Nexy 存储，而不是其前面的 CDN 或其他代理。 |
| 文件和 Redis 存储中没有 TTL | 条目会一直保留到 `revalidate()` 或您自己的清理操作将其删除。内存存储会逐出 256 之后最近最少使用的条目。 |
| 并发再生 | 没有什么可以消除它们的重复：十个过时的请求可以启动十个渲染。 |
| 错误是无声的 | 失败的重新生成或存储操作会继续为页面提供服务；失败不返回。 |

## 后续步骤

- [SSR](ssr.md)：页面在缓存之前如何呈现
- [操作](../guides/actions.md)：`revalidate` 标头和存储失效
- [配置](../reference/config.md#server)：`useISRCache`
- [性能](../deployment/performance.md)
- [页面](../routing/fbr/pages/README.md)：布局和动态段
