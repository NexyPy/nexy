# Actions

An `@Action` turns a Python function into a `POST` endpoint. Unlike a standard API handler, it is designed as a typed communication bridge: Nexy automatically generates the TypeScript client, validates the input, and handles the response.

**Before you start:** a project created by the [Quick start](../getting-started/quick-start.md).
Actions live next to the pages, in `src/actions/`.

```diagram filename="The Action Cycle"
Client (UI)  ─── 1. Call (Typed Input) ───► [ Nexy Bridge ]
                                                  │
                                                  ▼
                                      2. Validate & Execute (Python)
                                                  │
                                                  ▼
Client (UI)  ◄─── 5. Consume (Typed Result) ◄── 4. Serialize ◄── 3. Result
```

## The Action Cycle

### 1. Define
An action is a normal Python function marked with `@Action`. Nexy uses its signature to define the API contract.

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

The parameters are the input, validated by Pydantic. A parameter named `request` or `response` is injected and is not part of the input.

### 2. Validate
When the action is called, Nexy validates the input against the function's type hints. If a field is missing or has the wrong type, the action is not executed, and a `422 Unprocessable Entity` is returned.

### 3. Execute
The logic runs on the server. Since it is a standard Python function, you can use any library, access the database, or call other services. You can also trigger a page refresh using `revalidate()`.

### 4. Serialize
The return value is automatically serialized to JSON. Pydantic models are handled natively, and standard Python types are mapped to their JSON equivalents.

### 5. Consume
The frontend receives the result with full type safety. Nexy writes `__nexy__/src/actions.ts` from your signatures, and `@nexy/actions` resolves to it.

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

| Framework | What `useAction` returns |
|---|---|
| React, Preact | `{ pending, data, error, run, reset }` |
| Solid | the same, with `pending()`, `data()` and `error()` as accessors |
| Vue | the same, with `pending`, `data` and `error` as refs |
| Svelte | a store: `$save.pending`, `$save.data`, `$save.error`, plus `save.run(input)` and `save.reset()` |

`useAction(action, { onSuccess, onError })` also takes two callbacks. `run` never throws: a failure lands in `error` and `run` resolves with `undefined`.

The types come from Python: `str` is `string`, `int` and `float` are `number`, `list[T]` is `T[]`,
a Pydantic model or an `Enum` is a named type, and a field with a default is optional in the input.
A type Pydantic cannot describe becomes `unknown`.

## Errors and Failures

An action can fail at different stages. You should distinguish between them in your UI:

1.  **Validation errors (422)**: the input did not match the Python signature. `error.fields` maps each invalid field to its message.
2.  **Business errors (`HTTPException`)**: your code refused the call, for example `403 Forbidden` or `409 Conflict`.
3.  **Server errors (500)**: an unhandled exception occurred in your Python code.
4.  **Network errors**: the request never reached the server, for example a timeout or a lost connection.
5.  **Authorization errors (401, 403)**: your own check rejected the caller. Nexy does not decide this for you.

The origin check described below is a CSRF protection, not an authorization: it says where the call
came from, never who is allowed to make it.

## Refresh the page after an action

An action says which pages its change made stale, as Next.js does with `revalidatePath`:

```python
revalidate()            # the page that is open
revalidate("/users")    # that page, if it is the one open
```

The answer carries the paths in an `x-nexy-revalidate` header. The client then re-fetches the current page through the router, or reloads it when there is no client router.

## Forms without JavaScript

An action also takes a standard HTML form, so the page works before any script loads:

```html
<form method="post" action="{{ __actions_path['create_user'] }}">
  <input name="name">
  <button type="submit">Create</button>
</form>
```

In a `.nexy` template `__actions_path["name"]` is the path, `__actions["name"]` the function, and the function is also in scope under its own name.

On success, the visitor is sent back to the page the form was on, with status `303`. To answer differently, return a `Response` object (e.g., `RedirectResponse("/done", status_code=303)`).

### Multipart forms (`file` inputs)

A form with `enctype="multipart/form-data"` (for example a file input) needs the `python-multipart` package to parse the body. Nexy does not declare it as a hard dependency, so add it to your project when you use multipart forms:

```bash
uv add python-multipart
```

Without it, Nexy answers `400` with a message naming the missing package instead of a bare `500`.


## Security

### Path obscurity is not authorization
The action path is `/_nx_` followed by a hash of the function's module, its name and a secret of the
project. It is set by `NEXY_ACTION_SECRET`, or kept in `__nexy__/action.key`, which `nx build`
creates so the client bundle and `nx start` agree: keep that file with the build. The path hides the
endpoint from casual discovery, and **the generated path is not an authorization mechanism**.

Anyone who knows the path can call the action. You **must** verify the user's identity and permissions inside the action:
```python
@Action
async def delete_user(user_id: str, request: Request):
    if not request.state.user.is_admin:
        raise HTTPException(403, "Admin rights required")
    # ...
```

### Origin protection
To prevent Cross-Site Request Forgery (CSRF), Nexy refuses requests whose `Origin` is another site or that the browser marks `Sec-Fetch-Site: cross-site` with a `403`. List the sites that may call your actions in `NEXY_ALLOWED_ORIGINS`. Calls without an `Origin` (like `curl`) are accepted.

## Import errors

At startup Nexy imports every module of `src/` to find the actions. A module that fails to import is reported, and the others still load:

```text
  x src.actions.billing: src/actions/billing.py:3  ModuleNotFoundError: No module named 'stripe'
```

## Next steps

- [API](../routing/fbr/handlers/README.md): explicit handlers
- [Testing](testing.md#what-to-assert): how to test an action
- [Config](../reference/config.md): middleware and auth options
