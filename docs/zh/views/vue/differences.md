# Vue

Nexy 在服务器上渲染 Vue 3 单文件组件，然后 Vue 在浏览器中接管它们。
每个框架中的页面、布局、岛和操作都是相同的：此页面涵盖设置，然后是
与[共享合约](../frontend/pages.md)不同的部分。

| 模式 | `nexyconfig.py` | 页面为 | Vue 为 |
|---|---|---|---|
| 服务器（默认）| `useCSR = False` | `.nexy` 这些页面 | 内的文件 | [岛屿 ](../../rendering/islands.md)
| 客户端 | `useCSR = True` | `.vue` 文件 | 整个页面，带有 [布局 ](../frontend/layouts.md) 和客户端路由器 |

## 启动一个项目

```bash
nx new my-app --template web-fbr-vue
```

该模板是一个带有 Vue 岛的服务器模式项目。在没有模板的情况下运行 `nx new my-app`
回答提示：路由器、项目类型、是否使用客户端路由，然后
框架。

## 在现有项目中启用Vue

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), vue()],
  customLogger: nexy.log(),
});
```

`nx new` 写入此文件； Nexy 自己编写 `__nexy__/vite.ts`，因此请勿编辑它。

| 包 | 版本 `nx new` 写入 |
|---|---|
| `vue` | `^3.5.33` |
| `@vitejs/plugin-vue` | `^6.0.0` |

## 规则

- **每个项目一个框架。** `useFF` 只需要一个框架； `useFF = [vue(), react()]` 停止
  服务器在启动时。
- **每个文件一个组件。** `.vue` 文件默认导出其组件；您导入的名称
  下面只是您编写的标签。
- **组件位于 `src/routes/`** 之外，通常位于 `src/components/` 中，因此它们不是页面。
- **服务器模式项目没有 `.vue` 页面 **，客户端模式项目没有 `.nexy` 页面：Nexy
  拒绝启动并命名文件。请参阅[模式](../../routing/fbr/modes.md)。

## 页

在客户端模式（`useCSR = True`）下，页面是一个`.vue`文件。

### 页面组件

页面是由 `<script setup>` 块定义的组件。

```vue filename="src/routes/index.vue"
<template>
  <h1>Hello</h1>
</template>
```

### 动态片段

URL 参数作为 props 到达页面。您可以使用 `defineProps` 声明它们：

```vue filename="src/routes/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

或者，在任何组件中使用 `@nexy/client` 中的 `useParams` 钩子。

## 布局

### 实施

根布局定义文档外壳。嵌套布局将内容包装在其默认槽中。

```vue filename="src/routes/layout.vue"
<template>
  <html>
    <body>
      <header>My app</header>
      <main><slot /></main>
    </body>
  </html>
</template>
```

## 岛屿

在服务器模式下，导入到 `.nexy` 文件中的 Vue 组件是一个孤岛。

### 导入

在 `.nexy` 文件的 frontmatter 中导入组件：

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.vue" import Counter
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

使用 `useAction` 挂钩来管理操作调用的状态。在Vue中，返回的状态
(`pending`、`data`、`error`) 是计算的参考。

```vue
<script setup lang="ts">
import { ref } from "vue";
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const title = ref("");
const { run, pending, error, data } = useAction(add_todo, {
  onSuccess: () => (title.value = ""),
});
</script>

<template>
  <form @submit.prevent="run({ title })">
    <input v-model="title" />
    <button :disabled="pending">Add</button>
  </form>
</template>
```

### 导航

使用 `Link` 组件进行客户端转换：

```vue
<template>
  <Link href="/about" active-class="active">About</Link>
</template>
```

对于编程式导航，请使用 `useRouter` 挂钩：

```ts
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### 网址访问

所有位置挂钩都返回计算后的引用：

- `usePathname()`：当前路径
- `useParams()`：动态段
- `useSearchParams()`：查询字符串
- `useLocation()`：完整位置对象

## 后续步骤

- [视图](../README.md)：比较页面可以使用的格式
- [Frontend](../../guides/frontend.md)：Vite 和客户端构建