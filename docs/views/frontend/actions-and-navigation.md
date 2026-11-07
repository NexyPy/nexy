# Actions and Navigation

Interaction in Nexy is handled through a unified system of **Actions** and **Navigation**, ensuring that the frontend and backend remain in sync without manual API glue code.

## The Action Contract

An **Action** is a server-side function that handles a mutation (e.g., updating a database). 

1.  **Typed Input**: Actions are defined in Python with type hints. Nexy generates a matching TypeScript client, so you get autocomplete and validation in your IDE.
2.  **Atomic Execution**: An action is a single `POST` request.
3.  **Result Handling**: Actions return a typed result that the client can use to update the UI.

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

The page calls it with the input Python declared, and gets a typed `Todo` back:

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
The component is an island of a view, and a controller returns the view:

```tsx filename="src/components/Todos.tsx"
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

## Client-Side Navigation

Navigation in Nexy is "intelligent." Instead of a full browser reload, Nexy swaps the content of the current page while keeping the active layouts mounted.

- **The `Link` Component**: Use the framework-specific `Link` component to perform client-side transitions.
- **Programmatic Navigation**: Use `useRouter()` from `@nexy/client` and call `push()` to change
  pages in response to logic (e.g., after a successful login).

```tsx filename="src/components/Nav.tsx"
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

```tsx filename="src/components/Done.tsx"
import { useRouter } from "@nexy/client";

export function Done() {
  const router = useRouter();
  return <button onClick={() => router.push("/dashboard")}>Continue</button>;
}
```

## Coordination: Action → Navigation

The most common pattern is to perform an action and then navigate the user to a new page.

**The Revalidation Flow:**
1.  The client calls an Action.
2.  The Action executes on the server and calls `revalidate("/path")`.
3.  The server returns the result with an `x-nexy-revalidate` header naming the stale paths.
4.  The client updates the page content to reflect the new state.

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
```tsx filename="src/components/Login.tsx"
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

`check_password` stands for your own check. See [Actions](../../guides/actions.md) for errors,
forms without JavaScript and security.

## Framework Implementation

The API for calling actions and navigating varies by framework. See the **Differences** guide for your chosen technology:

- [React Differences](../react/differences.md)
- [Vue Differences](../vue/differences.md)
- [Svelte Differences](../svelte/differences.md)
- [Solid Differences](../solid/differences.md)
- [Preact Differences](../preact/differences.md)
