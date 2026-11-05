# ISR（重新验证时过时）

## 定义

ISR 缓存每个 URL 的一个页面的 HTML，并为其提供服务，直到其窗口到期。过期副本仍会提供，而新副本会在后台呈现：即“重新验证时陈旧”。

## 它是如何运作的

`.nexy` 页面前面的 `revalidate = N` 将其打开。 `N` 是秒数；缺失值、零值或负值意味着根本没有缓存。

缓存键仅是 **请求路径** - `request.scope["path"]`。查询字符串不是其中的一部分。

| 什么 | 价值 |
|---|---|
| 钥匙 | URL 路径 (`/blog/hello`) |
| 存储 | 在内存中，在渲染页面的过程中 |
| 绑定 | 每个进程 256 个条目，最近最少使用已被驱逐 |
| 响应头 | `cache-control: public, s-maxage=N, stale-while-revalidate=N` |

## 渲染生命周期

1. 请求到达声明 `revalidate` 的页面。
2. 尚无条目：页面已呈现、存储并返回。
3. 条目早于 `N` 秒：按原样返回，页面不会呈现。
4. 早于 `N` 秒的条目：立即返回 **过时的** 条目，并且后台任务会渲染一个新条目。
5. 如果该背景渲染引发，则过时的条目将保留，并且下一个过时的请求将再次尝试。

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

对 `/blog/hello` 的第一个请求呈现并存储。接下来的 300 秒是凭记忆提供的。 `/blog/other` 是一个单独的条目，单独呈现和存储。在实际项目中 `posts` 来自数据库或服务，每次重新生成时调用一次。

## 局限性

**Nexy 保证** 缓存键是路径，在重新生成期间提供过时的副本，并且存储是有界的且线程安全的。

**按照惯例**，声明 `revalidate` 的页面是公共内容。编写时就像每个访问者看到相同的 HTML 一样。

**您的应用程序负责** 其他一切：

| 限制 | 这意味着什么 |
|---|---|
| 查询字符串被忽略 | `/search?q=a` 和 `/search?q=b` 共享一个条目。不要缓存搜索页面。 |
| 会话未隔离 | 响应为 `public`，并且第一个访问者的 HTML 会提供给所有人。切勿在带有 `revalidate` 的页面中读取会话。 |
| 没有服务器端失效 | 在窗口结束之前没有任何东西会清除条目。 [操作](../guides/actions.md) 内的 `revalidate(...)` 仅告诉 **浏览器** 重新加载路径；它不会触及此缓存。 |
| 每个进程一个缓存 | 多个工作人员保存多个缓存，其中包含不同的内容。 |
| 并发再生 | 没有什么可以消除它们的重复：十个过时的请求可以启动十个渲染。 |
| 错误是无声的 | 失败的再生会继续为旧页面提供服务；失败会被记录，而不是返回。 |

## 后续步骤

- [SSR](ssr.md)：页面在缓存之前如何呈现
- [操作](../guides/actions.md)：`revalidate` 标头，以及它不执行的操作
- [性能](../deployment/performance.md)
- [页面](../routing/fbr/pages/README.md)：布局和动态段
