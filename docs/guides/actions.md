# Actions

`@Action` turns a Python function into a `POST` endpoint. A page calls it as a typed function, or
a plain HTML form posts to it, and no route file is needed.

```diagram filename="One function, two callers"
page (Jinja2 form)  ── POST ──┐
                               ├──► /_nx_/<hash> ──► async def create_user ──► JSON
client (TypeScript) ── fetch ──┘                                        └──► 303 after a form
```

## Define an action

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

The parameters are the input, validated by Pydantic. A parameter named `request` or `response` is
injected and is not part of the input. The function may be `async` or not, and stays a normal
function you can call and test directly.

## Call it from the client

Nexy writes `__nexy__/src/actions.ts` from your signatures, with the input and result types, and
`@nexy/actions` resolves to it:

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

Without a hook, an action is an `async` function: `const user = await create_user({ name: "Ada" })`.

| Framework | What `useAction` returns |
|---|---|
| React, Preact | `{ pending, data, error, run, reset }` |
| Solid | the same, with `pending()`, `data()` and `error()` as accessors |
| Vue | the same, with `pending`, `data` and `error` as refs |
| Svelte | a store: `$save.pending`, `$save.data`, `$save.error`, plus `save.run(input)` and `save.reset()` |

`useAction(action, { onSuccess, onError })` also takes two callbacks. `run` never throws: a failure
lands in `error` and `run` resolves with `undefined`. Only the latest call updates the state.

### Errors

A failed call throws (or sets `error` to) an `ActionError` with the HTTP `status` and the server's
`detail`. For a `422`, `error.fields` maps each invalid field to its message:

```ts
error.fields // { name: "Field required" }
```

The types come from Python: `str` is `string`, `int` and `float` are `number`, `list[T]` is `T[]`,
a Pydantic model or an `Enum` is a named type, and a field with a default is optional in the input.
A type Pydantic cannot describe becomes `unknown`.

## Refresh the page after an action

An action says which pages its change made stale, as Next.js does with `revalidatePath`:

```python
revalidate()            # the page that is open
revalidate("/users")    # that page, if it is the one open
```

The answer carries the paths in an `x-nexy-revalidate` header. The client then re-fetches the
current page through the router, or reloads it when there is no client router. An action that
never calls `revalidate` refreshes nothing.

## Forms without JavaScript

An action also takes a form, so the page works before any script loads:

```html
<form method="post" action="{{ __actions_path['create_user'] }}">
  <input name="name">
  <button type="submit">Create</button>
</form>
```

In a `.nexy` template `__actions_path["name"]` is the path, `__actions["name"]` the function, and
the function is also in scope under its own name. In client code `create_user.url` is the same
path.

The fields are validated like a JSON input (a name that appears twice becomes a list). On success
the visitor is sent back to the page the form was on, with status `303`. To answer differently,
return a response from the action, for example `RedirectResponse("/done", status_code=303)`:
a returned `Response` is sent as it is.

## Security

- **Origin**: a call whose `Origin` is another site, or that the browser marks
  `Sec-Fetch-Site: cross-site`, is refused with `403`. List the sites that may call your actions in
  `NEXY_ALLOWED_ORIGINS` (comma-separated, for example `https://app.example.com`). Calls without an
  `Origin`, such as `curl` or a test client, are accepted.
- **Path**: the path is `/_nx_` and a hash of the function's module, its name and a secret of the
  project. It is set by `NEXY_ACTION_SECRET`, or kept in `__nexy__/action.key`, which `nx build`
  creates so the client bundle and `nx start` agree. Keep that file with the build. The path
  hides the endpoint from casual discovery; it is not authorization, so check the user in the
  action.

Authorization is yours: read the session or cookies from `request`, and raise
`HTTPException(403)` when the caller may not do it.

## Import errors

At startup Nexy imports every module of `src/` to find the actions. A module that fails to import
is reported, with its file and line, and the others still load:

```text
  x src.actions.billing: src/actions/billing.py:3  ModuleNotFoundError: No module named 'stripe'
```

## Next steps

- [API](../routing/fbr/handlers/README.md): explicit handlers
- [Testing](testing.md#what-to-assert): how to test an action
- [Config](../reference/config.md): middleware and auth options
