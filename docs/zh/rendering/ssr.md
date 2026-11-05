# SSR（服务器渲染）

## 定义

SSR 是默认设置：服务器针对每个请求将页面呈现为 HTML。没有任何东西可以启用它，也没有标志可以将其关闭 - 服务器模式项目会在每个请求上呈现，除非页面声明 `revalidate`。

## 它是如何运作的

| 路线文件 | HTML 是由什么产生的 | 当 |
|---|---|---|
| `.nexy` | 编译后的 Python 模块，通过 Jinja2 | 每个请求 |
| `.md` | Markdown，然后是最近的布局 | 每个请求 |
| `.mdx`、`.tsx`、`.vue`、`.svelte` | 框架，在 Node 中呈现 | 在构建时，当路由没有布局时，否则在浏览器中 |
| `.py` | 什么都没有：它返回 JSON 或 `Response` | - |

一个 Markdown 页面和一个处理程序，并排位于同一项目中：

```md filename="src/routes/changelog.md"
# Changelog

Rendered to HTML on every request, then wrapped in the nearest layout.
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```

组件路由是需要第二句话的一种情况。在生产中，没有**布局的组件路径**与构建时生成的HTML一起提供，并且组件将其水化。对于布局或在开发中，容器是空的，组件在浏览器中呈现 - 然后页面是一个填充自身的外壳。

表的组件路由，没有布局，因此生产环境从构建中提供其 HTML：

```tsx filename="src/routes/pricing.tsx"
export default function Pricing() {
  return <h1>Pricing</h1>;
}
```

## 渲染生命周期

1. 请求到达基于文件的路由器。路径被匹配，动态段被转换为组件声明的类型。

   ```nexy filename="src/routes/orders/[id].nexy"
   ---
   id: 属性[int]
   ---
   <h1>订单#{{ id + 1000 }}</h1>
   ````

   `/orders/42` 渲染 `Order #1042`； `/orders/abc` 答案 `404`。
2. 组件运行。等待 Node（客户端文档）的一个在线程池中运行，因此它不会停止事件循环。
3. 正文作为 `text/html` 进行流式传输。生成块的组件在生成块时对它们进行流式传输。
4. 浏览器接收 HTML。岛屿根据其[指令](islands.md)进行水合。

当项目有错误时，渲染时引发的错误会被 `errors.nexy` 转换为页面：请参阅 [错误页面 ](../routing/fbr/errors/README.md)。

## 何时使用

- 该页面显示读者拥有的东西：会话、帐户、购物车。
- 每次加载时数据都必须是最新的。
- 对于不运行 JavaScript 的爬网程序，内容必须位于 HTML 中。
- 该页面的渲染成本很低：一个查询，一个模板。

第一种情况，一个在会话中向读者致意的页面：

```nexy filename="src/routes/account.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```

## 配置

没有。有两种出路，而且它们的粒度不同：

| 离开SSR | 这样做 | 谷物 |
|---|---|---|
| 一页，带有缓存 | `revalidate = 60` 在其 frontmatter → [ISR](isr.md) | 页面 |
| 整个项目，由客户主导 | `nexyconfig.py` 中的 `useCSR = True` → [CSR](csr.md) | 项目 |

项目范围的切换，在 `nexyconfig.py`中。客户端模式需要一个客户端框架：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

## 示例

```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` 运行此模板一次，并将 `slug` 设置为 `hello`。第二个请求再次运行它：两者之间没有任何保留。查询字符串不是道具 - 使用 [导航](../routing/fbr/navigation/hooks.md) 中的钩子读取它。

## 局限性

- **每个请求一次渲染。** 同一秒内的两个访问者各自为渲染及其背后的查询付费。
- **无缓存。** 没有要预热的共享响应缓存：[ISR](isr.md) 对每个 URL 添加一个。
- **流式传输仅有助于产生收益的组件。** 页面顶部的缓慢查询仍然会延迟第一个字节。
- **无静态输出。** 在服务器模式下，构建时不会冻结任何内容：没有 SSG 模式，也没有导出命令。请参阅[渲染](README.md)。
- **`.nexy` 模板中的自动转义已关闭**。使用 `| e` 转义不受信任的值。

```nexy filename="src/routes/search.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```

## 后续步骤

- [ISR](isr.md)：按 URL 缓存此页面
- [群岛](islands.md)：保持 SSR 并使一个小部件具有交互性
- [CSR](csr.md)：手动导航到浏览器
- [性能](../deployment/performance.md)
