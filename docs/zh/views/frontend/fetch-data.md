# 在组件中从服务器获取数据

要从组件中的服务器获取数据，请从 `@nexy/client` 调用 `useFetch(url)`：它将一个 `GET` 发送到项目的路由并返回 `data`、`error`、`pending` 和 `refresh`。

## 回答的路线

`useFetch` 从项目的任何 `GET` 路径读取 JSON。下面的两个示例提供相同的数据：

```python filename="src/data.py"
USERS = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Linus"}]
```

<!-- router:fbr,custom -->
文件路径回答了这个问题：

```python filename="src/routes/api/users/index.py"
from src.data import USERS


async def GET():
    return USERS
```
<!-- /router -->

<!-- router:modular -->
控制器回答它：

```python filename="src/apps/users/users_controller.py"
from nexy.decorators import Controller

from src.data import USERS


@Controller("/api/users")
class UsersController:
    async def get(self):
        return USERS
```
<!-- /router -->

## 使用 React 和 Preact 中的 `useFetch` 获取数据

```tsx filename="src/组件/Users.tsx"
import { useFetch } from "@nexy/client";

type User = { id: number; name: string };

export function Users() {
  const { data, error, pending, refresh } = useFetch<User[]>("/api/users");
  if (error) return <p>Could not load the users: {error.message}</p>;
  if (pending && !data) return <p>Loading...</p>;
  return (
    <>
      <ul>{data?.map((user) => <li key={user.id}>{user.name}</li>)}</ul>
      <button onClick={() => refresh()}>Reload</button>
    </>
  );
}
```

## 使用 `useFetch` 在 Vue 中获取数据

`data`、`error` 和 `pending` 是计算的引用：

```vue filename="src/components/Users.vue"
<script setup lang="ts">
import { useFetch } from "@nexy/client";

type User = { id: number; name: string };
const { data, error, pending, refresh } = useFetch<User[]>("/api/users");
</script>

<template>
  <p v-if="error">Could not load the users: {{ error.message }}</p>
  <p v-else-if="pending && !data">Loading...</p>
  <ul v-else>
    <li v-for="user in data" :key="user.id">{{ user.name }}</li>
  </ul>
  <button @click="refresh()">Reload</button>
</template>
```

## 使用 `useFetch` in Svelte 获取数据

`useFetch` 返回一个存储：使用 `$` 读取它，并在存储本身上调用 `refresh`：

```svelte filename="src/components/Users.svelte"
<script lang="ts">
  import { useFetch } from "@nexy/client";

  type User = { id: number; name: string };
  const users = useFetch<User[]>("/api/users");
</script>

{#if $users.error}
  <p>Could not load the users: {$users.error.message}</p>
{:else if $users.pending && !$users.data}
  <p>Loading...</p>
{:else}
  <ul>
    {#each $users.data ?? [] as user (user.id)}<li>{user.name}</li>{/each}
  </ul>
{/if}
<button onclick={() => users.refresh()}>Reload</button>
```

## 使用 `useFetch` 在 Solid 中获取数据

`data`、`error` 和 `pending` 是访问器：

```tsx filename="src/组件/Users.tsx"
import { For, Show } from "solid-js";
import { useFetch } from "@nexy/client";

type User = { id: number; name: string };

export function Users() {
  const users = useFetch<User[]>("/api/users");
  return (
    <Show when={!users.error()} fallback={<p>Could not load the users.</p>}>
      <ul><For each={users.data() ?? []}>{(user) => <li>{user.name}</li>}</For></ul>
      <button onClick={() => users.refresh()}>Reload</button>
    </Show>
  );
}
```

## 在页面上显示组件

<!-- router:fbr,custom -->
文件页面导入组件：

```tsx filename="src/routes/users.tsx"
import { Users } from "@/components/Users";

export default function UsersPage() {
  return <Users />;
}
```
<!-- /router -->

<!-- router:modular -->
控制器返回 `.nexy` 视图，该视图安装组件：

```nexy filename="src/apps/users/users_view.nexy"
---
from "@/components/Users.tsx" import Users
---
<Users directive="client:load" />
```
<!-- /router -->

Vue、Svelte 或 Solid 组件以相同的方式安装，使用其框架的导入语法。

## `useFetch` 发送和分享的内容

- 该请求是带有 `Accept: application/json` 和站点 cookie 的 `GET`，因此路由看到与页面相同的会话。
- 每个 URL 一种状态：读取 `/api/users` 的两个组件发送一个请求并显示相同的数据。
- `refresh()` 保留当前的 ​​`data` 直到新答案到达，并且一次两次刷新发送一个请求。
- `204` 答案将 `data` 给出为 `undefined`。
- 组件安装后，请求将在浏览器中发送。第一个 HTML 必须保存的数据属于页面 props，在服务器上呈现。

## 路线错误

不是 `2xx` 的答案将变为 `error`，即 `FetchError` 以及路线给出的 `status` 和 `detail`。 `data` 保持其最后的值：

<!-- router:fbr,custom -->
```python filename="src/routes/api/users/[id].py"
from nexy.http import HTTPException

from src.data import USERS


async def GET(id: int):
    for user in USERS:
        if user["id"] == id:
            return user
    raise HTTPException(status_code=404, detail="No such user")
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/users/user_by_id_controller.py"
from fastapi import HTTPException
from nexy.decorators import Controller

from src.data import USERS


@Controller("/api/users/{id}")
class UserByIdController:
    async def get(self, id: int):
        for user in USERS:
            if user["id"] == id:
                return user
        raise HTTPException(status_code=404, detail="No such user")
```
<!-- /router -->

该组件在两个路由器中以相同的方式读取错误：

```tsx filename="src/组件/用户名.tsx"
import { useFetch, FetchError } from "@nexy/client";

export function UserName({ id }: { id: number }) {
  const { data, error } = useFetch<{ name: string }>(`/api/users/${id}`);
  if (error instanceof FetchError && error.status === 404) return <p>{String(error.detail)}</p>;
  return <p>{data?.name}</p>;
}
```

## 执行操作后重新加载数据

一旦刷新页面本身，为打开的页面调用 `revalidate()` 的操作会使该页面的每个 `useFetch` 再次获取：

```python filename="src/actions/users.py"
from nexy.decorators import Action, revalidate

from src.data import USERS


@Action
async def add_user(name: str) -> dict:
    user = {"id": len(USERS) + 1, "name": name}
    USERS.append(user)
    revalidate()
    return user
```

```tsx filename="src/components/AddUser.tsx"
import { useAction } from "@nexy/client";
import { add_user } from "@nexy/actions";

export function AddUser() {
  const { run, pending } = useAction(add_user);
  return <button disabled={pending} onClick={() => run({ name: "Grace" })}>Add Grace</button>;
}
```

`src/components/Users.tsx` 列表显示 Grace 没有调用 `refresh()`。

## 后续步骤

- [操作和导航](actions-and-navigation.md)：更改组件中的数据
- [动作](../../guides/actions.md)：`revalidate()` 和动作周期
- [模块化路由](../../routing/modular/README.md)：编写应答的控制器
