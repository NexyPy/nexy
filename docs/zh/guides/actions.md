# 行动

`@Action` 将 Python 函数转换为 `POST` 端点。与标准 API 处理程序不同，它被设计为类型化通信桥：Nexy 自动生成 TypeScript 客户端、验证输入并处理响应。

**开始之前：** 由[快速启动](../getting-started/quick-start.md)创建的项目。操作位于页面旁边的 `src/actions/` 中。

```diagram filename="行动周期"
Client (UI)  ─── 1. Call (Typed Input) ───► [ Nexy Bridge ]
                                                  │
                                                  ▼
                                      2. Validate & Execute (Python)
                                                  │
                                                  ▼
Client (UI)  ◄─── 5. Consume (Typed Result) ◄── 4. Serialize ◄── 3. Result
```

## 行动周期

### 1. 定义
动作是一个标有 `@Action` 的普通 Python 函数。 Nexy uses its signature to define the API contract.

```python filename="src/actions/user.py"
from pydantic import BaseModel
from nexy.decorators import Action, revalidate

class User(BaseModel):
    name: str
    age: int = 0

@Action
async def create_user(name: str, age: int = 0) -> User:
    revalidate()
    return User(name=name, age=age)
```

参数是输入，由 Pydantic验证。名为 `request` 或 `response` 的参数被注入，但不是输入的一部分。

### 2. 验证
当调用该操作时，Nexy 会根据函数的类型提示验证输入。如果字段丢失或类型错误，则不会执行操作，并返回 `422 Unprocessable Entity`。

### 3. 执行
The logic runs on the server.由于它是标准的 Python 函数，因此您可以使用任何库、访问数据库或调用其他服务。您还可以使用 `revalidate()` 触发页面刷新。

### 4. 序列化
The return value is automatically serialized to JSON. Pydantic 模型是本机处理的，标准 Python 类型映射到它们的 JSON 等效项。

### 5. 消费
The frontend receives the result with full type safety. Nexy 根据您的签名写入 `__nexy__/src/actions.ts`，然后 `@nexy/actions` 解析为它。

<!-- router:fbr,custom -->
```tsx filename="src/routes/users.tsx"
import { useAction } from "@nexy/client";
import { create_user } from "@nexy/actions";

export default function NewUser() {
  const { run, pending, error, data } = useAction(create_user);

  return (
    <button disabled={pending} onClick={() => run({ name: "Ada" })}>
      {error ? error.message : data ? `Created ${data.name}` : "Create"}
    </button>
  );
}
```
<!-- /router -->

<!-- router:modular -->
The component is an island of the view a controller returns:

```tsx filename="src/components/NewUser.tsx"
import { useAction } from "@nexy/client";
import { create_user } from "@nexy/actions";

export function NewUser() {
  const { run, pending, error, data } = useAction(create_user);

  return (
    <button disabled={pending} onClick={() => run({ name: "Ada" })}>
      {error ? error.message : data ? `Created ${data.name}` : "Create"}
    </button>
  );
}
```

```nexy filename="src/apps/users/user_view.nexy"
---
from "@/components/NewUser.tsx" import NewUser
---
<NewUser directive="client:load" />
```
<!-- /router -->

Without a hook, an action is just an `async` function: `const user = await create_user({ name: "Ada" })`.

| 框架 | `useAction` 返回什么 |
|---|---|
| React，Preact | `{ pending, data, error, run, reset }` |
| Solid | 相同，使用 `pending()`、`data()` 和 `error()` 作为访问器 |
| Vue | the same, with `pending`, `data` and `error` as refs |
| Svelte | a store: `$save.pending`, `$save.data`, `$save.error`, plus `save.run(input)` and `save.reset()` |

`useAction(action, { onSuccess, onError })` also takes two callbacks. `run` never throws: a failure lands in `error` and `run` resolves with `undefined`.

类型来自 Python：`str` 是 `string`，`int` 和 `float` 是 `number`，`list[T]` 是 `T[]`，Pydantic 模型或 `Enum` 是命名类型，并且具有默认值的字段在输入中是可选的。 A type Pydantic cannot describe becomes `unknown`.

## 错误和失败

An action can fail at different stages. You should distinguish between them in your UI:

1.  **Validation errors (422)**: the input did not match the Python signature. `error.fields` maps each invalid field to its message.
2.  **Business errors (`HTTPException`)**: your code refused the call, for example `403 Forbidden` or `409 Conflict`.
3.  **服务器错误 (500)**：您的 Python 代码中发生未处理的异常。
4.  **Network errors**: the request never reached the server, for example a timeout or a lost connection.
5.  **授权错误 (401, 403)**：您自己的检查拒绝了调用者。 Nexy does not decide this for you.

下面描述的来源检查是 CSRF 保护，而不是授权：它说明呼叫来自哪里，而不是允许谁拨打。

## 执行操作后刷新页面

一个操作表明哪些页面的更改变得过时，就像 Next.js 对 `revalidatePath` 所做的那样：

```python
revalidate()            # the page that is open
revalidate("/users")    # that page, if it is the one open
```

The answer carries the paths in an `x-nexy-revalidate` header. The client then re-fetches the current page through the router, or reloads it when there is no client router.

## 没有 JavaScript 的表格

操作也采用标准 HTML 表单，因此页面在加载任何脚本之前即可运行：

```html
<form method="post" action="{{ __actions_path['create_user'] }}">
  <input name="name">
  <button type="submit">Create</button>
</form>
```

In a `.nexy` template `__actions_path["name"]` is the path, `__actions["name"]` the function, and the function is also in scope under its own name.

成功后，访问者将被发送回表单所在的页面，状态为 `303`。要以不同方式回答，请返回 `Response` 对象（例如 `RedirectResponse("/done", status_code=303)`）。

## 安全性

### 路径模糊不等于授权
操作路径是 `/_nx_`，后跟函数模块的哈希值、其名称和项目的秘密。 It is set by `NEXY_ACTION_SECRET`, or kept in `__nexy__/action.key`, which `nx build` creates so the client bundle and `nx start` agree: keep that file with the build.该路径隐藏端点以防止偶然发现，并且 **生成的路径不是授权机制**。

Anyone who knows the path can call the action. You **must** verify the user's identity and permissions inside the action:
```python
@Action
async def delete_user(user_id: str, request: Request):
    if not request.state.user.is_admin:
        raise HTTPException(403, "Admin rights required")
    # ...
```

### 原产地保护
To prevent Cross-Site Request Forgery (CSRF), Nexy refuses requests whose `Origin` is another site or that the browser marks `Sec-Fetch-Site: cross-site` with a `403`.在 `NEXY_ALLOWED_ORIGINS` 中列出可能调用您的操作的站点。接受没有 `Origin`（例如 `curl`）的呼叫。

## 导入错误

启动时，Nexy 导入 `src/` 的每个模块以查找操作。报某个模块导入失败，其他的依然加载：

```text
  x src.actions.billing: src/actions/billing.py:3  ModuleNotFoundError: No module named 'stripe'
```

## 后续步骤

- [API](../routing/fbr/handlers/README.md): explicit handlers
- [测试](testing.md#what-to-assert): how to test an action
- [配置](../reference/config.md): middleware and auth options
