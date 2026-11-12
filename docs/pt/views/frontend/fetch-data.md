# Buscar dados do servidor em um componente

Para buscar dados do servidor em um componente, chame `useFetch(url)` de `@nexy/client`: ele envia um `GET` para uma rota do projeto e devolve `data`, `error`, `pending` e `refresh`.

## A rota que responde

`useFetch` lê JSON de qualquer rota `GET` do projeto. Ambos os exemplos abaixo fornecem os mesmos dados:

```python filename="src/data.py"
USERS = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Linus"}]
```

<!-- router:fbr,custom -->
Uma rota de arquivo responde:

```python filename="src/routes/api/users/index.py"
from src.data import USERS


async def GET():
    return USERS
```
<!-- /router -->

<!-- router:modular -->
Um controlador responde:

```python filename="src/apps/users/users_controller.py"
from nexy.decorators import Controller

from src.data import USERS


@Controller("/api/users")
class UsersController:
    async def get(self):
        return USERS
```
<!-- /router -->

## Busque dados com `useFetch` em React e Preact

```tsx filename="src/componentes/Users.tsx"
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

## Buscar dados com `useFetch` em Vue

`data`, `error` e `pending` são referências calculadas:

```vue filename="src/componentes/Users.vue"
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

## Buscar dados com `useFetch` em Svelte

`useFetch` retorna uma loja: leia-a com `$` e chame `refresh` na própria loja:

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

## Buscar dados com `useFetch` em Solid

`data`, `error` e `pending` são acessadores:

```tsx filename="src/componentes/Users.tsx"
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

## Mostrar o componente em uma página

<!-- router:fbr,custom -->
Uma página de arquivo importa o componente:

```tsx filename="src/routes/users.tsx"
import { Users } from "@/components/Users";

export default function UsersPage() {
  return <Users />;
}
```
<!-- /router -->

<!-- router:modular -->
Um controlador retorna uma visualização `.nexy`, e a visualização monta o componente:

```nexy filename="src/apps/users/users_view.nexy"
---
from "@/components/Users.tsx" import Users
---
<Users directive="client:load" />
```
<!-- /router -->

Um componente Vue, Svelte ou Solid é montado da mesma forma, com a sintaxe de importação de seu framework.

## O que `useFetch` envia e compartilha

- A solicitação é um `GET` com `Accept: application/json` e os cookies do site, então a rota vê a mesma sessão da página.
- Um estado por URL: dois componentes que leem `/api/users` enviam uma solicitação e mostram os mesmos dados.
- `refresh()` mantém o `data` atual até que a nova resposta chegue e duas atualizações de uma vez enviam uma solicitação.
- Uma resposta `204` dá `data` como `undefined`.
- A solicitação é enviada no navegador, após a montagem do componente. Os dados que o primeiro HTML deve conter pertencem aos atributos da página, renderizados no servidor.

## Erros da rota

Uma resposta que não é `2xx` torna-se `error`, um `FetchError` com o `status` e o `detail` que a rota deu. `data` mantém seu último valor:

<!-- router:fbr,custom -->
```python filename="src/rotas/api/users/[id].py"
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

O componente lê o erro da mesma forma em ambos os roteadores:

```tsx filename="src/componentes/UserName.tsx"
import { useFetch, FetchError } from "@nexy/client";

export function UserName({ id }: { id: number }) {
  const { data, error } = useFetch<{ name: string }>(`/api/users/${id}`);
  if (error instanceof FetchError && error.status === 404) return <p>{String(error.detail)}</p>;
  return <p>{data?.name}</p>;
}
```

## Recarregue os dados após uma ação

Uma ação que chama `revalidate()` para a página aberta faz com que cada `useFetch` dessa página seja buscada novamente, assim que a própria página for atualizada:

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

```tsx filename="src/componentes/AddUser.tsx"
import { useAction } from "@nexy/client";
import { add_user } from "@nexy/actions";

export function AddUser() {
  const { run, pending } = useAction(add_user);
  return <button disabled={pending} onClick={() => run({ name: "Grace" })}>Add Grace</button>;
}
```

A lista de `src/components/Users.tsx` mostra Grace sem uma chamada para `refresh()`.

## Próximas etapas

- [Ações e navegação](actions-and-navigation.md): alterar dados de um componente
- [Ações](../../guides/actions.md): `revalidate()` e o ciclo de ação
- [Roteamento modular](../../routing/modular/README.md): escreva o controlador que responde
