# 继承

`src/routes/` 中的几个文件适用于其目录下的所有内容。它们都以相同的方式解析：Nexy 从路线的目录开始，一直走到 `src/routes/`。

```text
src/routes/
├─ layout.nexy               1. outermost
├─ dependencies.py           1. runs first
├─ middleware.py             1. wraps first
├─ notfound.nexy             fallback for every URL
├─ (shop)/                   a group is a directory: it takes part, it is not in the URL
│  ├─ layout.nexy            2.
│  ├─ dependencies.py        2.
│  └─ cart/
│     ├─ layout.nexy         3. innermost
│     ├─ dependencies.py     3. runs last
│     └─ index.nexy          the page
```

| 文件 | 规则 |
|---|---|
| `layout.nexy`、`layout.tsx`、`layout.vue`、`layout.svelte` | 从根到页面的每个布局都会包裹它，**最外面的第一个** |
| `middleware.py` | 从根到路由的每个文件都在依赖项之前包装请求，**最外层第一个** |
| `dependencies.py` | 从根到路由的每个文件都运行，**最外面的第一个**，然后是处理程序自己的守卫 |
| `notfound.nexy`，`errors.nexy` | 根据状态代码，**最近的** 获胜 |

对于上面的页面，布局嵌套为 `root layout > (shop) layout > cart layout > page`，依赖项运行为 `root > (shop) > cart > handler guards`。

## 为什么最外层先

外部布局绘制框架，外部依赖关系决定谁可以进来。将它们放在第一位意味着内部目录可以依赖它们：需要身份验证的目录在读取用户的处理程序之前运行。

树的 `(shop)` 依赖项会检查购物车 cookie，因此它下面的购物车依赖项可以读取购物车，而无需再次检查：

```python filename="src/routes/(shop)/dependencies.py"
from nexy.http import HTTPException, Request


def require_cart(request: Request) -> None:
    if "cart" not in request.cookies:
        raise HTTPException(status_code=400, detail="No cart")


dependencies = [require_cart]
```

## 布局

文件夹族堆栈的所有布局文件：请参阅[布局](layouts/README.md)。不同的系列不会混合：`layout.vue` 永远不会包装 `.tsx` 页面，并且项目具有 `layout.nexy` 或客户端布局，而绝不会同时具有两者 ([模式](modes.md))。

树的最里面的布局只添加自己的框架：它周围的根布局仍然绘制文档。

```nexy filename="src/routes/(shop)/cart/layout.nexy"
---
children: prop[NexyElement]
---
<section class="cart">
  <h2>Your cart</h2>
  {{ children | safe }}
</section>
```

## 中间件文件

请参阅[中间件文件](middleware/README.md)：它们在依赖项之前运行，并且可以在不到达路由的情况下进行应答。

根 `middleware.py` 包裹了树的每条路线，包括购物车：

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## 依赖关系

有关处理程序文件中的顺序，请参阅[依赖关系](dependencies/README.md)，包括 `@UseGuard` 和 `@Middleware`。

## 错误页面

`notfound.nexy` 和 `errors.nexy` 在路由根目录安装一次；子目录中的副本会优化该前缀的页面。请参阅[错误页面](errors/README.md)。

`cart/` 中的副本回答 `/cart` 下的 404，根副本保留其余部分：

```nexy filename="src/routes/(shop)/cart/notfound.nexy"
<h1>This product is gone</h1>
<p><a href="/cart">Back to your cart</a></p>
```

## 后续步骤

- [布局](layouts/README.md)
- [依赖项](dependencies/README.md)
- [错误页面](errors/README.md)
