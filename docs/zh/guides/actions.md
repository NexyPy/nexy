# 行动

`@Action` 将 Python 函数转换为 `POST` 端点。与标准 API 处理程序不同，它被设计为类型化通信桥梁：Nexy 自动生成 TypeScript 客户端、验证输入并处理响应。

**开始之前：**由[快速启动](../getting-started/quick-start.md)创建的项目。
操作位于页面旁边的 `src/actions/` 中。

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

### 1。定义
动作是一个标有 `@Action` 的普通 Python 函数。 Nexy 使用其签名来定义 API 合约。

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

参数是输入，由 Pydantic 验证。名为 `request` 或 `response` 的参数被注入，但不是输入的一部分。

### 2。验证
当调用该操作时，Nexy 会根据函数的类型提示验证输入。如果字段丢失或类型错误，则不会执行操作，并返回 `422 Unprocessable Entity`。

### 3。执行
逻辑在服务器上运行。由于它是标准的Python函数，因此您可以使用任何库、访问数据库或调用其他服务。您还可以使用 `revalidate()` 触发页面刷新。

### 4。序列化
返回值自动序列化为JSON。 Pydantic 模型是本机处理的，标准 Python 类型映射到它们的 JSON 等效项。

### 5。消费
前端接收具有完全类型安全的结果。 Nexy 根据您的签名写入 `__nexy__/src/actions.ts`，然后 `@nexy/actions` 解析为它。

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

如果没有钩子，动作只是一个 `async` 函数：`const user = await create_user({ name: "Ada" })`。

| 框架 | `useAction` 返回什么 |
|---|---|
| 反应，预反应 | `{ pending, data, error, run, reset }` |
| Solid | 相同，以 `pending()`、`data()` 和 `error()` 作为访问器 |
| Vue | 相同，以 `pending`、`data` 和 `error` 作为参考 |
| Svelte | 商店：`$save.pending`、`$save.data`、`$save.error`，加上 `save.run(input)` 和 `save.reset()` |

`useAction(action, { onSuccess, onError })` 也需要两个回调。 `run` 永远不会抛出：失败落在 `error` 中，并且 `run` 解决为 `undefined`。

来自Python的类型：`str`是`string`，`int`和`float`是`number`，`list[T]`是`T[]`，
Pydantic 模型或 `Enum` 是命名类型，并且输入中具有默认值的字段是可选的。
Pydantic 无法描述的类型变成了 `unknown`。

## 错误和失败

一项操作可能会在不同阶段失败。您应该在 UI 中区分它们：

1.  **验证错误 (422)**：输入与 Python 签名不匹配。 `error.fields` 将每个无效字段映射到其消息。
2.  **业务错误 (`HTTPException`)**：您的代码拒绝调用，例如 `403 Forbidden` 或 `409 Conflict`。
3.  **服务器错误 (500)**：Python 代码中发生未处理的异常。
4.  **网络错误**：请求从未到达服务器，例如超时或连接丢失。
5.  **授权错误（401、403）**：您自己的检查拒绝了调用者。 Nexy 不会为您做出决定。

下面描述的来源检查是 CSRF 保护，而不是授权：它说明了调用的位置
来自，从来没有允许谁成功。

## 执行操作后刷新页面

一个操作表明哪些页面的更改变得过时，就像 Next.js 对 `revalidatePath` 所做的那样：

```python
revalidate()            # the page that is open
revalidate("/users")    # that page, if it is the one open
```

答案在 `x-nexy-revalidate` 标头中携带路径。然后客户端通过路由器重新获取当前页面，或者在没有客户端路由器时重新加载当前页面。

## 没有 JavaScript 的表单

操作也采用标准 HTML 表单，因此页面在加载任何脚本之前即可运行：

```html
<form method="post" action="{{ __actions_path['create_user'] }}">
  <input name="name">
  <button type="submit">Create</button>
</form>
```

在 `.nexy` 模板中，`__actions_path["name"]` 是路径，`__actions["name"]` 是函数，并且该函数也在其自己的名称下的范围内。

成功后，访问者将被发送回表单所在的页面，状态为 `303`。要以不同方式回答，请返回 `Response` 对象（例如 `RedirectResponse("/done", status_code=303)`）。

## 安全

### 路径模糊不是授权
操作路径是 `/_nx_`，后跟函数模块的哈希值、其名称和函数的秘密
项目。它由`NEXY_ACTION_SECRET`设置，或者保存在`__nexy__/action.key`中，其中`nx build`
创建，以便客户端捆绑包和 `nx start` 达成一致：将该文件与构建一起保留。路径隐藏了
来自偶然发现的端点，并且**生成的路径不是授权机制**。

任何知道路径的人都可以调用该操作。您**必须**在操作中验证用户的身份和权限：
```python
@Action
async def delete_user(user_id: str, request: Request):
    if not request.state.user.is_admin:
        raise HTTPException(403, "Admin rights required")
    # ...
```

### 原产地保护
为了防止跨站点请求伪造 (CSRF)，Nexy 拒绝 `Origin` 是另一个站点的请求或浏览器用 `403` 标记 `Sec-Fetch-Site: cross-site` 的请求。在 `NEXY_ALLOWED_ORIGINS` 中列出可能调用您的操作的站点。接受没有 `Origin`（如 `curl`）的呼叫。

## 导入错误

启动时，Nexy 导入 `src/` 的每个模块以查找操作。报某个模块导入失败，其他的依然加载：

```text
  x src.actions.billing: src/actions/billing.py:3  ModuleNotFoundError: No module named 'stripe'
```

## 后续步骤

- [API](../routing/fbr/handlers/README.md)：显式处理程序
- [测试](testing.md#what-to-assert)：如何测试操作
- [Config](../reference/config.md)：中间件和身份验证选项