# React

Nexy 在服务器上渲染 React 19 个组件，然后 React 在浏览器中对它们进行水合。每个框架中的页面、布局、岛和操作都是相同的：此页面涵盖设置，然后是与[共享合约](../frontend/pages.md)不同的部分。

<!-- router:fbr,custom -->
| 模式 | `nexyconfig.py` | 页面是 | React 是 |
|---|---|---|---|
| 服务器（默认） | `useCSR = False` | `.nexy` 文件 | [这些页面内的岛屿](../../rendering/islands.md) |
| 客户 | `useCSR = True` | `.tsx` 文件 | 整个页面，带有 [布局](../frontend/layouts.md) 和客户端路由器 |
<!-- /router -->

<!-- router:modular -->
对于模块化路由器，React 组件是控制器返回的 `.nexy` 视图内的[岛](../../rendering/islands.md)：没有页面文件，也没有客户端路由器。
<!-- /router -->

## 开始一个项目

<!-- router:fbr,custom -->
```bash
nx new my-app --template web-fbr-react
```
<!-- /router -->

<!-- router:modular -->
```bash
nx new my-app --template web-modular-react
```
<!-- /router -->

该模板是一个带有 React 岛屿的服务器模式项目。在没有模板的情况下运行 `nx new my-app` 来回答提示：路由器、项目类型、是否使用客户端路由，然后是框架。

## 在现有项目中启用 React

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), react()],
  customLogger: nexy.log(),
});
```

`nx new` 写入此文件； Nexy 自己编写 `__nexy__/vite.ts`，因此请勿编辑它。

| 套餐 | 版本 `nx new` 写道 |
|---|---|
| `react`，`react-dom` | `^19.2.5` |
| `@vitejs/plugin-react` | `^5.2.0` |
| `@types/react`，`@types/react-dom` | 开发依赖 |

## 规则

- **每个项目一个框架。** `useFF` 只需要一个框架； `useFF = [react(), vue()]` 在启动时停止服务器。
<!-- router:fbr,custom -->
- **页面为 `.tsx`.** React 拥有 `.tsx` 和 `.jsx` 组件，但只有 `src/routes/` 下的 `.tsx` 文件成为页面。
- **组件位于 `src/routes/`** 之外，通常位于 `src/components/` 中，因此它们不是页面。
- **服务器模式项目没有 `.tsx` 页面**，客户端模式项目没有 `.nexy` 页面：Nexy 拒绝启动并命名文件。请参阅[模式](../../routing/fbr/modes.md)。
<!-- /router -->
<!-- router:modular -->
- **组件位于 `src/components/`** 中，视图将它们作为岛屿导入。
<!-- /router -->

<!-- router:fbr,custom -->
## 页数

在客户端模式（`useCSR = True`）下，页面是一个 `.tsx` 文件。

### 页面组件

页面是文件的默认导出。如果不存在默认导出，Nexy 将选择第一个命名的导出。

```tsx filename="src/routes/index.tsx"
export default function Home() {
  return <h1>Hello</h1>;
}
```

### 动态细分

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

根布局定义文档外壳。嵌套布局将其下方的内容包裹起来。

```tsx filename="src/routes/layout.tsx"
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
```
<!-- /router -->

## 岛屿

在服务器模式下，导入到 `.nexy` 文件中的 React 组件是一个岛。

### 导入

在 `.nexy` 文件的 frontmatter 中导入组件：

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```
<!-- /router -->

### 补水指令

使用 `directive` 道具来控制岛屿何时水合：

- `client:load`（默认）：立即
- `client:idle`：当浏览器空闲时
- `client:visible`：当它滚动到视图中时
- `client:media`：当媒体查询匹配时

## 操作和导航

### 调用动作

使用 `useAction` 钩子来管理操作调用的状态：

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const { run, pending, error, data } = useAction(add_todo);
// ...
<button onClick={() => run({ title: "New Task" })}>Add</button>
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

- `usePathname()`：当前路径
- `useParams()`：动态段
- `useSearchParams()`：查询字符串
- `useLocation()`：完整位置对象

## 后续步骤

- [视图](../README.md)：比较页面可以使用的格式
- [前端](../../guides/frontend.md)：Vite 和客户端构建
