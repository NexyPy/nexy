# Svelte

Nexy 在服务器上渲染 Svelte 5 个组件，然后 Svelte 在浏览器中接管它们。每个框架中的页面、布局、岛和操作都是相同的：此页面涵盖设置，然后是与[共享合约](../frontend/pages.md)不同的部分。

| 模式 | `nexyconfig.py` | 页面是 | Svelte 是 |
|---|---|---|---|
| 服务器（默认） | `useCSR = False` | `.nexy` 文件 | 这些页面内的[岛屿](../../rendering/islands.md) |
| 客户 | `useCSR = True` | `.svelte` 文件 | 整个页面，带有 [布局](../frontend/layouts.md) 和客户端路由器 |

## 开始一个项目

```bash
nx new my-app --template web-fbr-svelte
```

该模板是一个带有 Svelte 岛屿的服务器模式项目。在没有模板的情况下运行 `nx new my-app` 来回答提示：路由器、项目类型、是否使用客户端路由，然后是框架。

## 在现有项目中启用 Svelte

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), svelte()],
  customLogger: nexy.log(),
});
```

`nx new` 写入此文件； Nexy 自己编写 `__nexy__/vite.ts`，因此请勿编辑它。

| 套餐 | 版本 `nx new` 写道 |
|---|---|
| `svelte` | `^5.20.2` |
| `@sveltejs/vite-plugin-svelte` | `^5.0.0` |

## 规则

- **Svelte 5.** 组件使用符文：`$props()`、`$state()` 和子级片段。
- **每个项目一个框架。** `useFF` 只需要一个框架； `useFF = [svelte(), vue()]` 在启动时停止服务器。
- **每个文件一个组件。** 您导入的 `.svelte` 文件的名称只是您编写的标签。
- **组件位于 `src/routes/`** 之外，通常位于 `src/components/` 中，因此它们不是页面。
- **服务器模式项目没有 `.svelte` 页面**，客户端模式项目没有 `.nexy` 页面：Nexy 拒绝启动并命名文件。请参阅[模式](../../routing/fbr/modes.md)。

## 页数

在客户端模式（`useCSR = True`）下，页面是一个 `.svelte` 文件。

### 页面组件

该页面是由 `.svelte` 文件的脚本块定义的组件。

```svelte filename="src/routes/index.svelte"
<script lang="ts">
</script>

<h1>Hello</h1>
```

### 动态细分

URL 参数通过 `$props()` 符文作为 props 到达页面：

```svelte filename="src/routes/blog/[slug].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

或者，在任何组件中使用 `@nexy/client` 中的 `$params` 存储。

## 布局

### 实施

根布局定义文档外壳。嵌套布局使用 `children` 片段包裹内容。

```svelte filename="src/routes/layout.svelte"
<script lang="ts">
  import type { Snippet } from "svelte";
  let { children }: { children?: Snippet } = $props();
</script>

<html>
  <body>
    <header>My app</header>
    <main>{@render children?.()}</main>
  </body>
</html>
```

## 岛屿

在服务器模式下，导入到 `.nexy` 文件中的 Svelte 组件是一个岛。

### 导入

在 `.nexy` 文件的 frontmatter 中导入组件：

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.svelte" import Counter
---
<Counter start=3 />
```

### 补水指令

使用 `directive` 道具来控制岛屿何时水合：

- `client:load`（默认）：立即
- `client:idle`：当浏览器空闲时
- `client:visible`：当它滚动到视图中时
- `client:media`：当媒体查询匹配时

## 操作和导航

### 调用动作

使用 `useAction` 挂钩来管理操作调用的状态。在 Svelte 中，这将返回一个存储（用 `$` 读取）。

```svelte
<script lang="ts">
  import { useAction } from "@nexy/client";
  import { add_todo } from "@nexy/actions";

  let title = $state("");
  const save = useAction(add_todo, { onSuccess: () => (title = "") });
</script>

<form onsubmit={(e) => { e.preventDefault(); save.run({ title }); }}>
  <input bind:value={title} />
  <button disabled={$save.pending}>Add</button>
</form>
```

### 导航

使用 `Link` 组件进行客户端转换：

```svelte
<script lang="ts">
  import Link from "@nexy/Link.svelte";
</script>

<Link href="/about" activeClass="active">About</Link>
```

对于编程式导航，请使用 `@nexy/client` 中的 `router` 对象：

```ts
import { router } from "@nexy/client";

router.push("/dashboard");
```

### 网址访问

所有位置数据均以存储形式提供：

- `$pathname`：当前路径
- `$params`：动态段
- `$searchParams`：查询字符串
- `$location`：完整位置对象

## 后续步骤

- [视图](../README.md)：比较页面可以使用的格式
- [前端](../../guides/frontend.md)：Vite 和客户端构建
