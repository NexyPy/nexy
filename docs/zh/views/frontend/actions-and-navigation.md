# 操作和导航

Nexy 中的交互是通过 **Actions** 和 **Navigation** 的统一系统进行处理，确保前端和后端保持同步，无需手动 API 粘合代码。

## 行动契约

**Action** 是一个处理突变（例如更新数据库）的服务器端函数。 

1.  **类型化输入**：操作在 Python 中定义，带有类型提示。 Nexy 生成匹配的 TypeScript 客户端，因此您可以在 IDE 中获得自动完成和验证。
2.  **原子执行**：一个操作是单个 `POST` 请求。
3.  **结果处理**：操作返回客户端可用于更新 UI 的类型化结果。

```python filename="src/actions/todos.py"
from pydantic import BaseModel
from nexy.decorators import Action


class Todo(BaseModel):
    title: str
    done: bool = False


@Action
async def add_todo(title: str) -> Todo:
    return Todo(title=title)
```

该页面使用声明的输入 Python 调用它，并返回一个类型化的 `Todo`：

<!-- router:fbr,custom -->
```tsx filename="src/routes/todos.tsx"
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export default function Todos() {
  const { run, pending, data } = useAction(add_todo);
  return (
    <button disabled={pending} onClick={() => run({ title: "Write the docs" })}>
      {data ? `Added ${data.title}` : "Add"}
    </button>
  );
}
```
<!-- /router -->

<!-- router:modular -->
该组件是一个视图岛，控制器返回该视图：

```tsx filename="src/组件/Todos.tsx"
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export function Todos() {
  const { run, pending, data } = useAction(add_todo);
  return (
    <button disabled={pending} onClick={() => run({ title: "Write the docs" })}>
      {data ? `Added ${data.title}` : "Add"}
    </button>
  );
}
```

```nexy filename="src/apps/todos_view.nexy"
---
from "@/components/Todos.tsx" import Todos
---
<Todos directive="client:load" />
```
<!-- /router -->

## 客户端导航

Nexy 的导航是“智能的”。 Nexy 不是完全重新加载浏览器，而是交换当前页面的内容，同时保持活动布局的安装。

- **`Link` 组件**：使用特定于框架的 `Link` 组件执行客户端转换。
- **编程式导航**：使用 `@nexy/client` 中的 `useRouter()` 并调用 `push()` 来更改页面以响应逻辑（例如，成功登录后）。

```tsx filename="src/组件/Nav.tsx"
import { Link } from "@nexy/client";

export function Nav() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about" activeClassName="active">About</Link>
    </nav>
  );
}
```

```tsx filename="src/组件/Done.tsx"
import { useRouter } from "@nexy/client";

export function Done() {
  const router = useRouter();
  return <button onClick={() => router.push("/dashboard")}>Continue</button>;
}
```

## 协调：行动→导航

最常见的模式是执行操作，然后将用户导航到新页面。

**重新验证流程：**
1.  客户端调用一个操作。
2.  该操作在服务器上执行并调用 `revalidate("/path")`。
3.  服务器返回带有 `x-nexy-revalidate` 标头的结果，该标头命名了过时路径。
4.  客户端更新页面内容以反映新状态。

```python filename="src/actions/session.py"
from nexy.decorators import Action, revalidate


@Action
async def sign_in(email: str, password: str) -> bool:
    ok = check_password(email, password)
    revalidate("/dashboard")
    return ok
```

<!-- router:fbr,custom -->
```tsx filename="src/routes/login.tsx"
import { useAction, useRouter } from "@nexy/client";
import { sign_in } from "@nexy/actions";

export default function Login() {
  const router = useRouter();
  const { run } = useAction(sign_in, {
    onSuccess: (ok) => {
      if (ok) router.push("/dashboard");
    },
  });
  return <button onClick={() => run({ email: "ada@example.com", password: "..." })}>Sign in</button>;
}
```
<!-- /router -->

<!-- router:modular -->
```tsx filename="src/组件/Login.tsx"
import { useAction } from "@nexy/client";
import { sign_in } from "@nexy/actions";

export function Login() {
  const { run } = useAction(sign_in, {
    onSuccess: (ok) => {
      if (ok) window.location.assign("/dashboard/");
    },
  });
  return <button onClick={() => run({ email: "ada@example.com", password: "..." })}>Sign in</button>;
}
```
<!-- /router -->

`check_password` 代表您自己的支票。有关错误、没有 JavaScript 和安全性的表单，请参阅 [操作 ](../../guides/actions.md)。

## 框架实施

用于调用操作和导航的 API 因框架而异。请参阅您选择的技术的 **差异** 指南：

- [React 差异](../react/differences.md)
- [Vue 差异](../vue/differences.md)
- [Svelte 差异](../svelte/differences.md)
- [Solid 差异](../solid/differences.md)
- [Preact 差异](../preact/differences.md)
