# 岛屿和水合作用

## 定义

岛是一个客户端组件 - React、Vue、Svelte、Solid 或 Preact - 导入到 `.nexy`
页。服务器呈现其 HTML；浏览器使该组件具有交互性。其余的
页面保持 HTML。

孤岛以服务器模式存在。在客户端模式下，组件*是*页面：请参阅[CSR](csr.md)。

## 它是如何工作的

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter directive="client:visible" />
```

Nexy 在构建时呈现组件、存储其 HTML 并将其放置在页面内。页面
响应携带 HTML 加上 props 作为 JSON 属性。在浏览器中，孤岛运行时
加载组件并接管容器。

`directive` 决定**何时**发生这种情况。如果没有水，岛上一运行就会吸水
准备好了。

## 渲染生命周期

1. 在构建时，每个客户端组件都会呈现为 HTML 并编写在 `__nexy__/client/static/` 下。
2. 请求呈现`.nexy`页面；岛屿的 HTML 被插入来代替标签。
3. 响应携带 HTML、props 和指令作为属性。
4. 在浏览器中，运行时根据指令安排水合作用。
5. Hydration 用实时组件替换了静态 HTML；页面的其余部分保持不变。

在开发过程中，没有构建快照：容器是空的，组件在
浏览器。页面看起来相同，但第一次绘制与生产不同。

## 何时使用

- 主要是内容并具有一两个交互点的页面。
- 一个小部件必须存在于 HTML 中才能供爬虫使用并且仍然可以工作。
- 需要浏览器但不应该将整个页面拖入客户端渲染的组件。

## 配置

| 指令 | 水合物 |
|---|---|
|无，或`client:load`|立即|
| `client:idle` | 浏览器空闲时（`requestIdleCallback`，2 秒超时）|
| `client:visible` | 当岛屿进入视口时，提前 200 像素 |
| `client:media` | 当媒体查询匹配时；使用 `media` 属性 | 设置它

```nexy
<Chart directive="client:media" media="(min-width: 768px)" />
```

当`media`不存在时，`client:media`默认为`(min-width: 768px)`，并水合一次。上一个
没有 `IntersectionObserver`、`client:visible` 的浏览器将返回空闲状态。

`directive` 和 `media` 被 Nexy 消耗：它们不会传递给您的组件。

## 示例

```tsx filename="src/组件/Counter.tsx"
import { useState } from "react"

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Count</h1>
<Counter start=3 directive="client:idle" />
```

## 局限性

- **`client:only` 永远不会水合。** 它被接受，但运行时会跳过它，因此服务器 HTML 保持不变
  惰性的。当组件无法在服务器上呈现时，请使用客户端路由 ([CSR](csr.md))。
- **`client:manual`没有公共触发器。**也会自动跳过，并且该句柄
  恢复它是内部的。
- **Props 必须是 JSON。** 它们用 `json.dumps` 序列化；无法序列化的值是
  掉落，岛屿收到`{}` - 默默地。
- **岛屿不是具有共享状态的客户端组件。**如果没有
  您自己添加的机制。
- **服务器不会重新渲染岛屿。**它的 HTML 是构建快照，加上任何内容
  成分一旦水合就会发生。
- **岛屿页面是变相的 CSR 页面。** 如果每个块都需要彼此通信，请选择
  改为客户端模式。

## 后续步骤

- [渲染](README.md)：四种模式
- [组件](../views/nexy/components.md)：`.nexy`页面如何导入一个
- [反应](../views/react/differences.md)，[Vue](../views/vue/differences.md)，
  [细长](../views/svelte/differences.md)、[实心](../views/solid/differences.md)、
  [预](../views/preact/differences.md)