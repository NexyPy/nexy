# 链接和导航

通过客户端路由 (`useCSR = True`)，两个页面之间的链接会交换浏览器中的页面，而不是重新加载文档。布局保持其状态。

## 普通链接已经可以使用

项目页面的每个 `<a href>` 都会在客户端上导航，没有组件也没有标记：

```html
<a href="/about">About</a>
```

在以下情况下，会向浏览器留下一个链接，并正常加载页面：

- 按住修饰键，或者该按钮不是主按钮；
- 它具有 `target`（`_self` 除外）、`download`、`rel="external"` 或 `data-nexy-reload`；
- `href` 是另一个来源、`mailto:` 或 `tel:` 链接，或只是 `#fragment`；
- 该路径与客户端路由不匹配，因此服务器应答它。

## `Link`

`Link` 与普通锚点无法执行的操作相同：它的 `href` 会根据您的路线进行检查，它会加热目标页面，并且知道它何时指向当前页面。当您运行 `nx dev` 或 `nx build` 时，Nexy 在 `__nexy__/src` 中生成框架的 `Link`。

| 框架 | 进口 |
|---|---|
| React、Preact、Solid、Vue | `import { Link } from "@nexy/client"` |
| Svelte | `import Link from "@nexy/Link.svelte"` |

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
| `replace` | 替换历史条目而不是添加历史条目。 |
| `scroll` | `false` 在导航后保留滚动位置。默认值：`true`。 |
| `prefetch` | `'intent'`（默认）在悬停、聚焦或触摸时加载页面； `'viewport'` 当链接滚动到视图中时； `false` 从来没有。 |
| `activeClassName` | 当链接指向当前页面或其下一页（Vue 和 Svelte 中的 `activeClass` 时，添加到类中。 |
| `exact` | 仅在确切的页面上有效。 |

指向当前页面的链接也会得到 `aria-current="page"`。

## 挂钩

该位置在每个框架中都可用，按照该框架的习惯用法。在第一个过程中，服务器端使用请求的 URL 呈现钩子答案，因此页面不会出现不匹配的情况。

| | React，Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| 路径 | `usePathname()` | `usePathname()` 返回一个访问器 | `usePathname()` 返回一个引用 | `$pathname` 商店 |
| 路由参数 | `useParams()` | `useParams()` 访问器 | `useParams()` 参考 | `$params` 商店 |
| 查询 | `useSearchParams()` | `useSearchParams()` 访问器 | `useSearchParams()` 参考 | `$searchParams` 商店 |
| 一切 | `useLocation()` | `useLocation()` 访问器 | `useLocation()` 参考 | `$location` 商店 |
| 导航 | `useRouter()` | `useRouter()` | `useRouter()` | `router` |
| 飞行中导航 | `useTransition()` | `useTransition()` 访问器 | `useTransition()` 参考 | `useTransition()` 商店 |
| 匹配路径 | `useMatch(path?)` | `useMatch(path?)` 访问器 | `useMatch(path?)` 参考 | `useMatch(path?)` 商店 |
| 离开前询问 | `useBlocker(dirty)` | `useBlocker(dirty())` 在 `createEffect` | `useBlocker(dirtyRef)` | `useBlocker(dirty)` 在 `$effect` |

查询是 `URLSearchParams`。 `useRouter()` 和 `router` 给出 `push(href)`、`replace(href)`、`back()`、`forward()`、`refresh()` 和 `prefetch(href)`； `push` 和 `replace` 接受 `{ scroll: false }`。

```tsx
import { useParams, useRouter, useSearchParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  const tab = useSearchParams().get("tab") ?? "profile";
  const router = useRouter();
  return <button onClick={() => router.push(`/users/${id}?tab=posts`)}>{tab}</button>;
}
```

## 使用 `useTransition` 显示加载状态

`useTransition()` 告知客户端导航是否正在飞行。 `pending` 是从点击到显示下一页的 `true`，`next` 是它要去的位置。一旦页面显示、导航停止或新页面替换它时，它就会返回到 `{ pending: false, next: null }`。

```tsx
import { useTransition } from "@nexy/client";

export default function Progress() {
  const { pending, next } = useTransition();
  return pending ? <p role="status">Loading {next?.pathname}</p> : null;
}
```

## 将路径与 `useMatch` 匹配

`useMatch(path)` 告知 `path` 是否与客户端路由匹配。它返回 `{ match, found }`，其中 `match` 保存路线 `file`、其 `layouts` 及其 `params`，或者是 `null`。如果没有路径，它会匹配当前页面并遵循每个导航。在服务器渲染期间，还没有路由器，因此 `match` 是 `null`，`found` 是 `false`。

```tsx
import { useMatch } from "@nexy/client";

export default function Breadcrumb() {
  const { match } = useMatch();
  return match?.params.id ? <span>User {match.params.id}</span> : null;
}
```

## 捕获失败并显示 `ErrorBoundary` 的页面

`ErrorBoundary` 当其中一个在浏览器中呈现时抛出异常时，将显示后备而不是其子级。后备接收错误和 `reset`，这会再次渲染子级。

| 框架 | 进口 | 回退 |
|---|---|---|
| React，Preact，Solid | `import { ErrorBoundary } from "@nexy/client"` | `fallback={(error, reset) => ...}` |
| Vue | `import { ErrorBoundary } from "@nexy/client"` | 一个 `fallback` 函数道具；孩子们进入默认插槽 |
| Svelte | `import ErrorBoundary from "@nexy/ErrorBoundary.svelte"` | 一个 `fallback` 片段 |

```tsx
import { ErrorBoundary } from "@nexy/client";

<ErrorBoundary fallback={(error, reset) => <button onClick={reset}>{error.message}: retry</button>}>
  <Dashboard />
</ErrorBoundary>
```

```svelte
<ErrorBoundary>
  {#snippet fallback(error, reset)}
    <button onclick={reset}>{error.message}: retry</button>
  {/snippet}
  <Dashboard />
</ErrorBoundary>
```

它没有捕获：

- 稍后在事件处理程序、计时器或承诺中抛出的错误：在发生的地方捕获它。 Vue 是其自身事件处理程序的异常，其错误到达边界；
- 路由器无法加载的页面：浏览器向服务器请求该页面（请参阅[路由器的作用](#what-the-router-does)）。

## 在离开未保存更改的页面之前询问

`useBlocker(dirty, message?)` 在访问者离开前询问，而 `dirty` 为 true：链接、`router.push`、后退和前进按钮、重新加载和关闭选项卡。客户端导航在 `confirm()` 中显示 `message`：yes 继续，no 停留在页面上。重新加载或关闭选项卡会显示浏览器自己的问题，没有页面可以说出该问题。如果没有消息，问题是“您有未保存的更改。离开此页面吗？”。

```tsx
import { useState } from "react";
import { useBlocker } from "@nexy/client";

export default function Editor() {
  const [text, setText] = useState("");
  const [saved, setSaved] = useState("");
  useBlocker(text !== saved, "Your draft is not saved. Leave anyway?");
  return (
    <form onSubmit={(event) => (event.preventDefault(), setSaved(text))}>
      <textarea value={text} onChange={(event) => setText(event.target.value)} />
      <button>Save</button>
    </form>
  );
}
```

在每个框架的惯用语中，标志在发生变化的地方被读取：

| 框架 | 跟随旗帜 |
|---|---|
| React，Preact | `useBlocker(dirty)` 在每个渲染上 |
| Vue | `useBlocker(dirty)` 和 `dirty` 一个 ref 或一个计算的 |
| Solid | `createEffect(() => useBlocker(dirty()))` |
| Svelte | `$effect(() => useBlocker(dirty))` |

`useBlocker` 还采用一个函数，根据访问者的去向做出决定。它接收下一个位置和当前位置，并返回停留的原因（字符串），或者不进行任何操作：

```tsx
useBlocker((next) => (next.pathname.startsWith("/admin") ? "Admins only" : undefined));
```

函数不会自行询问，也不会重新加载；拨打其中的 `confirm()` 询问。

## `Image`

`Image` 渲染默认情况下惰性的 `<img>`，并且在已知其大小时不会移动布局。

| 框架 | 进口 |
|---|---|
| React、Preact、Solid、Vue | `import { Image } from "@nexy/client"` |
| Svelte | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` 为必填项；使用 `alt=""` 作为装饰图像。当它丢失时，Nexy 会发出警告一次。
- 对于 `width` 和 `height`，属性为浏览器提供宽高比，并且图像保持流畅 (`height: auto; max-width: 100%`)。
- `priority` 现在以高优先级加载图像，以便在到达时可见。
- `fill` 使图像覆盖其定位的父级，忽略 `width` 和 `height`。
- `sizes` 和 `srcSet` 穿过。 Nexy 不会调整图像大小或转换图像。

## 来自 `.nexy` 页面的链接

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` 渲染 `<a href="/about" data-nexy-link="true">`。每个属性和 `href` 都是 HTML 转义的。

## 路由器的作用是什么

在导航上，路由器：

1. 将路径与客户端路由进行匹配（`.tsx`、`.jsx`、`.vue`、`.svelte`）；
2. 导入并渲染页面及其 [布局](../layouts/README.md) **first**，然后才使用 `history.pushState` 移动 URL，因此地址栏永远不会显示失败的页面；
3. 在 `document` 上调度 `nexy:navigated` 事件；
4. 滚动到顶部，或滚动到 `#fragment` 目标。

较新的导航会取消仍在渲染的旧导航。如果页面无法呈现，浏览器会向服务器请求该页面。后退和前进按钮呈现该条目的页面并恢复其滚动位置。

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

路由器仅在具有客户端路由的项目中启动，因此服务器渲染的项目保留浏览器自己的后退按钮和滚动恢复。

## 后续步骤

- [布局](../layouts/README.md)
- [企业社会责任](../../../rendering/csr.md)
- [组件](../../../views/nexy/components.md)
