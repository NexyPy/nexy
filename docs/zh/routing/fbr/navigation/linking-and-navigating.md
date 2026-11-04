# 链接和导航

使用客户端路由 (`useCSR = True`)，两个页面之间的链接会交换浏览器中的页面
重新加载文档。布局保持其状态。

## 普通链接已经可以使用

项目页面的每个 `<a href>` 都会在客户端上导航，没有组件也没有标记：

```html
<a href="/about">About</a>
```

在以下情况下，会向浏览器留下一个链接，并正常加载页面：

- 按住修饰键，或者该按钮不是主按钮；
- 它有`target`（`_self`除外）、`download`、`rel="external"`或`data-nexy-reload`；
- `href` 是另一个来源、`mailto:` 或 `tel:` 链接，或只是一个 `#fragment`；
- 该路径与客户端路由不匹配，因此服务器应答它。

## `Link`

`Link` 与普通锚点无法执行的操作相同：它的 `href` 会根据您的路线进行检查，
它会加热目标页面，并且知道它何时指向当前页面。 Nexy 生成 `Link`
当你运行 `nx dev` 或 `nx build` 时，你的框架在 `__nexy__/src` 中。

| 框架 | 导入 |
|---|---|
| React、Preact、Solid、Vue | `import { Link } from "@nexy/client"` |
| 苗条 | `import Link from "@nexy/Link.svelte"` |

```tsx
import { Link } from "@nexy/client";

export default function Nav() {
  return (
    <Link href="/dashboard" activeClassName="on">
      Dashboard
    </Link>
  );
}
```

| 道具 | 含义 |
|---|---|
| `href` | 项目的路径（拼写错误是类型错误），可以选择使用 `?query` 或 `#fragment`，或外部 URL。 |
| `replace` | 替换历史条目而不是添加一个。 |
| `scroll` | `false` 在导航后保留滚动位置。默认值：`true`。 |
| `prefetch` | `'intent'`（默认）在悬停、聚焦或触摸时加载页面； `'viewport'` 当链接滚动到视图中时； `false`从来没有。 |
| `activeClassName` | 当链接指向当前页面或其下一页时添加到类中（Vue 和 Svelte 中的 `activeClass`）。 |
| `exact` | 仅在特定页面上有效。 |

指向当前页面的链接也会得到`aria-current="page"`。

## 挂钩

该位置在每个框架中都可用，按照该框架的习惯用法。第一次期间，
服务器端使用请求的 URL 呈现钩子答案，因此页面无需
不匹配。

| | React，Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| 路径 | `usePathname()` | `usePathname()` 返回一个访问器 | `usePathname()` 返回一个引用 | `$pathname` 存储 |
| 路由参数 | `useParams()` | `useParams()` 访问器 | `useParams()` 引用 | `$params` 存储 |
| 查询 | `useSearchParams()` | `useSearchParams()` 访问器 | `useSearchParams()` 引用 | `$searchParams` 存储 |
| 一切 | `useLocation()` | `useLocation()` 访问器 | `useLocation()` 引用 | `$location` 存储 |
| 导航 | `useRouter()` | `useRouter()` | `useRouter()` | `router` |

查询是`URLSearchParams`。 `useRouter()` 和 `router` 给出 `push(href)`, `replace(href)`,
`back()`、`forward()`、`refresh()` 和 `prefetch(href)`； `push` 和 `replace` 接受
`{ scroll: false }`。

```tsx
import { useParams, useRouter, useSearchParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  const tab = useSearchParams().get("tab") ?? "profile";
  const router = useRouter();
  return <button onClick={() => router.push(`/users/${id}?tab=posts`)}>{tab}</button>;
}
```

## `Image`

`Image` 渲染一个 `<img>`，默认情况下是惰性的，并且当其大小为
已知。

| 框架 | 导入 |
|---|---|
| React、Preact、Solid、Vue | `import { Image } from "@nexy/client"` |
| 苗条 | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` 为必填项；使用 `alt=""` 作为装饰图像。当它丢失时，Nexy 会发出警告一次。
- 对于`width`和`height`，属性为浏览器提供宽高比和图像
  保持流动（`height: auto; max-width: 100%`）。
- `priority` 现在以高优先级加载图像，以便到达时可见。
- `fill` 使图像覆盖其定位的父级，忽略 `width` 和 `height`。
- `sizes`和`srcSet`穿过。 Nexy 不会调整图像大小或转换图像。

## 来自 `.nexy` 页面的链接

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` 渲染
`<a href="/about" data-nexy-link="true">`。每个属性和 `href` 都是 HTML 转义的。

## 路由器的作用

在导航上，路由器：

1. 将路径与客户端路由进行匹配（`.tsx`、`.jsx`、`.vue`、`.svelte`）；
2. 首先导入并渲染页面及其[布局](../layouts/README.md)****，然后
   用 `history.pushState` 移动 URL，因此地址栏永远不会显示失败的页面；
3. 在`document`上调度`nexy:navigated`事件；
4. 滚动到顶部，或滚动到`#fragment`目标。

较新的导航会取消仍在渲染的旧导航。如果页面无法呈现，浏览器
而是向服务器询问。后退和前进按钮呈现该条目的页面，并且
恢复其滚动位置。

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

路由器仅在具有客户端路由的项目中启动，因此服务器渲染的项目会保留
浏览器自带的后退按钮和滚动恢复。

## 后续步骤

- [布局](../layouts/README.md)
- [企业社会责任](../../../rendering/csr.md)
- [组件](../../../views/nexy/components.md)