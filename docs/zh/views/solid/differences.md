# 固体

Nexy 在服务器上渲染 Solid 1.9 组件，然后 Solid 在浏览器中接管它们。页数，
每个框架中的布局、岛和操作都是相同的：此页面介绍设置，然后是各个部分
与[共享合约](../frontend/pages.md)不同。

| 模式 | `nexyconfig.py` | 页数为 | 实体为 |
|---|---|---|---|
| 服务器（默认）| `useCSR = False` | `.nexy` 这些页面 | 内的文件 | [岛屿 ](../../rendering/islands.md)
| 客户端 | `useCSR = True` | `.tsx` 文件 | 整个页面，带有 [布局 ](../frontend/layouts.md) 和客户端路由器 |

## 启动一个项目

```bash
nx new my-app --template web-fbr-solid
```

该模板是一个带有实体岛的服务器模式项目。在没有模板的情况下运行 `nx new my-app`
回答提示：路由器、项目类型、是否使用客户端路由，然后
框架。

## 在现有项目中启用 Solid

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import solid


class NexyConfig(NexyConfigModel):
    useFF = solid()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import solid from "vite-plugin-solid";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), solid()],
  customLogger: nexy.log(),
});
```

在客户端模式下写`solid({ ssr: true })`：Solid为服务器编译一个不同的组件
而对于浏览器和客户端模式两者都需要。 `nx new` 写入此文件；内克西写道
`__nexy__/vite.ts` 本身，所以不要编辑它。

| 包 | 版本 `nx new` 写入 |
|---|---|
| `solid-js` | `^1.9.12` |
| `vite-plugin-solid` | `^2.11.0`（开发依赖）|

## 思考信号

实体分量函数运行 ** 一次 **。后来发生的变化是通过信号读取的，并且只有
读取它的表达式更新：

```tsx filename="src/组件/Counter.tsx"
import { createSignal } from "solid-js";

export default function Counter(props: { start?: number }) {
  const [count, setCount] = createSignal(props.start ?? 0);
  return <button onClick={() => setCount(count() + 1)}>{count()}</button>;
}
```

- 在 JSX 内部调用信号 `count()`，而不是在其上方的变量中。
- 将 props 读为 `props.start`。解构 `{ start }` 读取该值一次并丢失更新。
- Solid 写入 HTML 属性：`class`、`for`、`charset`，而不是 `className`。

## 规则

- **每个项目一个框架。** `useFF` 只需要一个框架； `useFF = [solid(), react()]`
  在启动时停止服务器。对于 `useFF = solid()`，每个 `.tsx` 文件都是 Solid。
- **页面为`.tsx`.**只有`src/routes/`下的`.tsx`文件才成为页面； `.jsx` 适合
  组件。
- **组件位于 `src/routes/`** 之外，通常位于 `src/components/` 中，因此它们不是页面。
- **服务器模式项目没有 `.tsx` 页面 **，客户端模式项目没有 `.nexy` 页面：Nexy
  拒绝启动并命名文件。请参阅[模式](../../routing/fbr/modes.md)。
- **没有 `.mdx` Solid.** MDX 编译为 React 或 Preact； `.md` 页面有效。

## 页数

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

URL 参数可通过 `useParams` 挂钩获得，该挂钩返回一个访问器：

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const params = useParams<{ slug: string }>();
  return <h1>{params().slug}</h1>;
}
```

## 布局

### 实施

根布局定义文档外壳。嵌套布局包裹内容。

```tsx filename="src/routes/layout.tsx"
import type { JSX } from "solid-js";

export default function RootLayout(props: { children: JSX.Element }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{props.children}</main>
      </body>
    </html>
  );
}
```

不要解构 `props.children`，因为 Solid 会懒惰地读取它。

## 岛屿

在服务器模式下，导入到 `.nexy` 文件中的实体组件是一个岛。

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

使用 `useAction` 挂钩来管理操作调用的状态。在 Solid 中，这会返回访问器（调用
它们作为函数）。

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const save = useAction(add_todo);
// ...
<button disabled={save.pending()}>Add</button>
```

### 导航

使用 `Link` 组件进行客户端转换：

```tsx
import { Link } from "@nexy/client";

<Link href="/about">About</Link>
```

对于编程式导航，请使用 `useRouter` 挂钩：

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### 网址访问

所有位置挂钩返回访问器：

- `usePathname()`：当前路径
- `useParams()`：动态段
- `useSearchParams()`：查询字符串
- `useLocation()`：完整位置对象

## 后续步骤

- [视图](../README.md)：比较页面可以使用的格式
- [Frontend](../../guides/frontend.md)：Vite 和客户端构建