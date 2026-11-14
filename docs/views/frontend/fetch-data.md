# Fetch data from the server in a component

To fetch data from the server in a component, call `useFetch(url)` from `@nexy/client`: it sends
one `GET` to a route of the project and gives back `data`, `error`, `pending` and `refresh`.

## The route that answers

`useFetch` reads JSON from any `GET` route of the project. Both examples below serve the same data:

```python filename="src/data.py"
USERS = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Linus"}]
```

<!-- router:fbr,custom -->
A file route answers it:

```python filename="src/routes/api/users/index.py"
from src.data import USERS


async def GET():
    return USERS
```
<!-- /router -->

<!-- router:modular -->
A controller answers it:

```python filename="src/apps/users/users_controller.py"
from nexy.decorators import Controller

from src.data import USERS


@Controller("/api/users")
class UsersController:
    async def get(self):
        return USERS
```
<!-- /router -->

## Fetch data with `useFetch` in React and Preact

```tsx filename="src/components/Users.tsx"
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

## Fetch data with `useFetch` in Vue

`data`, `error` and `pending` are computed refs:

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

## Fetch data with `useFetch` in Svelte

`useFetch` returns a store: read it with `$`, and call `refresh` on the store itself:

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

## Fetch data with `useFetch` in Solid

`data`, `error` and `pending` are accessors:

```tsx filename="src/components/Users.tsx"
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

## Show the component on a page

<!-- router:fbr,custom -->
A file page imports the component:

```tsx filename="src/routes/users.tsx"
import { Users } from "@/components/Users";

export default function UsersPage() {
  return <Users />;
}
```
<!-- /router -->

<!-- router:modular -->
A controller returns a `.nexy` view, and the view mounts the component:

```nexy filename="src/apps/users/users_view.nexy"
---
from "@/components/Users.tsx" import Users
---
<Users directive="client:load" />
```
<!-- /router -->

A Vue, Svelte or Solid component is mounted the same way, with the import syntax of its framework.

## What `useFetch` sends and shares

- The request is a `GET` with `Accept: application/json` and the cookies of the site, so the route
  sees the same session as the page.
- One state per URL: two components that read `/api/users` send one request and show the same
  data.
- `refresh()` keeps the current `data` until the new answer arrives, and two refreshes at once send
  one request.
- A `204` answer gives `data` as `undefined`.
- The request is sent in the browser, after the component mounts. Data the first HTML must hold
  belongs in the page props, rendered on the server.

## Errors from the route

An answer that is not `2xx` becomes `error`, a `FetchError` with the `status` and the `detail` the
route gave. `data` keeps its last value:

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

The component reads the error the same way in both routers:

```tsx filename="src/components/UserName.tsx"
import { useFetch, FetchError } from "@nexy/client";

export function UserName({ id }: { id: number }) {
  const { data, error } = useFetch<{ name: string }>(`/api/users/${id}`);
  if (error instanceof FetchError && error.status === 404) return <p>{String(error.detail)}</p>;
  return <p>{data?.name}</p>;
}
```

## Reload the data after an action

An action that calls `revalidate()` for the open page makes every `useFetch` of that page fetch
again, once the page itself is refreshed:

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

The list of `src/components/Users.tsx` shows Grace without a call to `refresh()`.

## Next steps

- [Actions and navigation](actions-and-navigation.md): change data from a component
- [Actions](../../guides/actions.md): `revalidate()` and the action cycle
- [Modular routing](../../routing/modular/README.md): write the controller that answers
