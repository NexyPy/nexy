# 预反应

Nexy 在服务器上渲染 Preact 10 组件，然后 Preact 在浏览器中接管它们。页数，
每个框架中的布局、岛和操作都是相同的：此页面介绍设置，然后是各个部分
与[共享合约](../frontend/pages.md)不同。

| 模式 | `nexyconfig.py` | 页数为 | Preact 为 |
|---|---|---|---|
| 服务器（默认）| `useCSR = False` | `.nexy` 这些页面 | 内的文件 | [岛屿 ](../../rendering/islands.md)
| 客户端 | `useCSR = True` | `.tsx` 文件 | 整个页面，带有 [布局 ](../frontend/layouts.md) 和客户端路由器 |

## 启动一个项目

```bash
nx new my-app --template web-fbr-preact
```

该模板是一个带有 Preact 岛的服务器模式项目。在没有模板的情况下运行 `nx new my-app`
回答提示：路由器、项目类型、是否使用客户端路由，然后
框架。

## 在现有项目中启用 Preact

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import preact


class NexyConfig(NexyConfigModel):
    useFF = preact()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import preact from "@preact/preset-vite";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), preact()],
  customLogger: nexy.log(),
});
```

`nx new` 写入此文件； Nexy 自己编写 `__nexy__/vite.ts`，因此请勿编辑它。

| 包 | 版本 `nx new` 写入 |
|---|---|
| `preact` | `^10.25.4` |
| `@preact/preset-vite` | `^2.10.1`（开发依赖）|
| `preact-render-to-string` | `^6.7.0`（开发依赖项，在服务器上呈现）|

## 编写Preact

Preact 组件是一个 React 风格的函数。这里重要的区别是：

```tsx filename="src/组件/Counter.tsx"
import { useState } from "preact/hooks";

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start);
  return <button class="counter" onClick={() => setCount(count + 1)}>{count}</button>;
}
```

- 钩子来自`preact/hooks`，类型例如`ComponentChildren`来自`preact`。
- 写入 HTML 属性：`class`、`for`、`charset`。 `Link` 从 `class` 读取其类。

## 规则

- **每个项目一个框架。** `useFF` 只需要一个框架； `useFF = [preact(), react()]`
  在启动时停止服务器。对于 `useFF = preact()`，每个 `.tsx` 文件都是 Preact。
- **页面为`.tsx`。**只有`src/routes/`下的`.tsx`文件成为页面； `.jsx` 适合
  组件。
- **组件位于`src/routes/`**之外，通常位于`src/components/`中，因此它们不是页面。
- **服务器模式项目没有 `.tsx` 页面 **，客户端模式项目没有 `.nexy` 页面：Nexy
  拒绝启动并命名文件。请参阅[模式](../../routing/fbr/modes.md)。
- **`.mdx` 页面从 `"preact"` 导入。** Nexy 仅在以下情况下才使用 Preact 编译 `.mdx` 文件
  看到导入，例如 `import { h } from "preact"`，否则使用 React。参见
  [Markdown 和 MDX](../nexy/markdown.md)。

## 页

在客户端模式（`useCSR = True`）下，页面是一个`.tsx`文件。

### 页面组件

页面是文件的默认导出。如果不存在默认导出，Nexy 会选择第一个指定的导出
出口。

```tsx filename="src/routes/index.tsx"
export default function Home() {
  return <h1>Hello</h1>;
}
```

### 动态片段

URL 参数可通过 `useParams` 挂钩获得：

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

## 布局

### 实施

根布局定义文档外壳。嵌套布局包裹内容。

```tsx filename="src/routes/layout.tsx"
import type { ComponentChildren } from "preact";

export default function RootLayout({ children }: { children: ComponentChildren }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

## 岛屿

在服务器模式下，导入到 `.nexy` 文件中的 Preact 组件是一个岛。

### 导入

在 `.nexy` 文件的 frontmatter 中导入组件：

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```

### 水合作用指令

使用 `directive` 道具来控制岛屿何时水合：

- `client:load`（默认）：立即
- `client:idle`：当浏览器空闲时
- `client:visible`：当它滚动到视图中时
- `client:media`：当媒体查询匹配时

## 操作和导航

### 调用操作

使用 `useAction` 钩子来管理操作调用的状态：

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const { run, pending, error, data } = useAction(add_todo);
// ...
<button onClick={() => run({ title: "New Task" })}>Add</button>
```

### 导航

使用 `Link` 组件进行客户端转换。请注意，Preact 使用 `class` 而不是
`className`：

```tsx
import { Link } from "@nexy/client";

<Link href="/about" class="nav" activeClassName="active">About</Link>
```

对于编程式导航，请使用 `useRouter` 挂钩：

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### 网址访问

- `usePathname()`：当前路径
- `useParams()`：动态段
- `useSearchParams()`：查询字符串
- `useLocation()`：完整位置对象

## 后续步骤

- [视图](../README.md)：比较页面可以使用的格式
- [Frontend](../../guides/frontend.md)：Vite 和客户端构建