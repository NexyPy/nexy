# Obtener datos del servidor en un componente

Para recuperar datos del servidor en un componente, llame a `useFetch(url)` desde `@nexy/client`: envía un `GET` a una ruta del proyecto y devuelve `data`, `error`, `pending` y `refresh`.

## La ruta que responde

`useFetch` lee JSON de cualquier `GET` ruta del proyecto. Los dos ejemplos siguientes ofrecen los mismos datos:

```python filename="src/datos.py"
USERS = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Linus"}]
```

<!-- router:fbr,custom -->
Una ruta de archivo responde:

```python filename="src/rutas/api/users/index.py"
from src.data import USERS


async def GET():
    return USERS
```
<!-- /router -->

<!-- router:modular -->
Un controlador le responde:

```python filename="src/apps/users/users_controller.py"
from nexy.decorators import Controller

from src.data import USERS


@Controller("/api/users")
class UsersController:
    async def get(self):
        return USERS
```
<!-- /router -->

## Obtener datos con `useFetch` en React y Preact

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

## Obtener datos con `useFetch` en Vue

`data`, `error` y `pending` son referencias calculadas:

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

## Obtener datos con `useFetch` en Svelte

`useFetch` devuelve una tienda: léela con `$` y llama a `refresh` en la propia tienda:

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

## Obtener datos con `useFetch` en Solid

`data`, `error` y `pending` son descriptores de acceso:

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

## Mostrar el componente en una página.

<!-- router:fbr,custom -->
Una página de archivo importa el componente:

```tsx filename="src/rutas/usuarios.tsx"
import { Users } from "@/components/Users";

export default function UsersPage() {
  return <Users />;
}
```
<!-- /router -->

<!-- router:modular -->
Un controlador devuelve una vista `.nexy` y la vista monta el componente:

```nexy filename="src/apps/users/users_view.nexy"
---
from "@/components/Users.tsx" import Users
---
<Users directive="client:load" />
```
<!-- /router -->

Un componente Vue, Svelte o Solid se monta de la misma manera, con la sintaxis de importación de su marco.

## Lo que `useFetch` envía y comparte

- La solicitud es un `GET` con `Accept: application/json` y las cookies del sitio, por lo que la ruta ve la misma sesión que la página.
- Un estado por URL: dos componentes que leen `/api/users` envían una solicitud y muestran los mismos datos.
- `refresh()` mantiene el `data` actual hasta que llega la nueva respuesta, y dos actualizaciones a la vez envían una solicitud.
- Una respuesta `204` da `data` como `undefined`.
- La solicitud se envía en el navegador, después de que se monta el componente. Los datos que debe contener el primer HTML pertenecen a los accesorios de la página, representados en el servidor.

## Errores de la ruta.

Una respuesta que no es `2xx` se convierte en `error`, un `FetchError` con el `status` y el `detail` que dio la ruta. `data` mantiene su último valor:

<!-- router:fbr,custom -->
```python filename="src/rutas/api/usuarios/[id].py"
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

El componente lee el error de la misma manera en ambos enrutadores:

```tsx filename="src/components/Nombre de usuario.tsx"
import { useFetch, FetchError } from "@nexy/client";

export function UserName({ id }: { id: number }) {
  const { data, error } = useFetch<{ name: string }>(`/api/users/${id}`);
  if (error instanceof FetchError && error.status === 404) return <p>{String(error.detail)}</p>;
  return <p>{data?.name}</p>;
}
```

## Recargar los datos después de una acción.

Una acción que llama a `revalidate()` para la página abierta hace que cada `useFetch` de esa página se recupere nuevamente, una vez que se actualiza la página:

```python filename="src/acciones/usuarios.py"
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

La lista de `src/components/Users.tsx` muestra a Grace sin una llamada a `refresh()`.

## Próximos pasos

- [Acciones y navegación](actions-and-navigation.md): cambiar datos de un componente
- [Acciones](../../guides/actions.md): `revalidate()` y el ciclo de acción
- [Enrutamiento modular](../../routing/modular/README.md): escribe el controlador que responde
