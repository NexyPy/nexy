# Получить данные с сервера в компоненте

Чтобы получить данные с сервера в компоненте, вызовите `useFetch(url)` из `@nexy/client`: он отправляет один `GET` на маршрут проекта и возвращает `data`, `error`, `pending` и `refresh`.

## Маршрут, который отвечает

`useFetch` читает JSON из любого `GET` маршрута проекта. Оба примера ниже содержат одни и те же данные:

```python filename="источник/data.py"
USERS = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Linus"}]
```

<!-- router:fbr,custom -->
Маршрут файла отвечает на него:

```python filename="src/routes/api/users/index.py"
from src.data import USERS


async def GET():
    return USERS
```
<!-- /router -->

<!-- router:modular -->
На него отвечает диспетчер:

```python filename="src/apps/users/users_controller.py"
from nexy.decorators import Controller

from src.data import USERS


@Controller("/api/users")
class UsersController:
    async def get(self):
        return USERS
```
<!-- /router -->

## Получите данные с помощью `useFetch` в React и Preact

```tsx filename="источник/компоненты/Users.tsx"
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

## Получить данные с помощью `useFetch` в Vue

`data`, `error` и `pending` — вычисляемые ссылки:

```vue filename="src/компоненты/Users.vue"
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

## Получить данные с помощью `useFetch` в Svelte

`useFetch` возвращает хранилище: прочитайте его с помощью `$` и вызовите `refresh` для самого хранилища:

```svelte filename="src/компоненты/Users.svelte"
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

## Получить данные с помощью `useFetch` в Solid

`data`, `error` и `pending` являются аксессорами:

```tsx filename="источник/компоненты/Users.tsx"
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

## Показать компонент на странице

<!-- router:fbr,custom -->
Страница файла импортирует компонент:

```tsx filename="src/маршруты/users.tsx"
import { Users } from "@/components/Users";

export default function UsersPage() {
  return <Users />;
}
```
<!-- /router -->

<!-- router:modular -->
Контроллер возвращает представление `.nexy`, и представление монтирует компонент:

```nexy filename="src/apps/users/users_view.nexy"
---
from "@/components/Users.tsx" import Users
---
<Users directive="client:load" />
```
<!-- /router -->

Компонент Vue, Svelte или Solid монтируется таким же образом, с использованием синтаксиса импорта его платформы.

## Что `useFetch` отправляет и делится

- Запрос представляет собой `GET` с `Accept: application/json` и файлами cookie сайта, поэтому маршрут видит тот же сеанс, что и страница.
- Одно состояние на каждый URL: два компонента, которые читают `/api/users`, отправляют один запрос и отображают одни и те же данные.
- `refresh()` сохраняет текущий `data` до тех пор, пока не придет новый ответ, и два обновления одновременно отправляют один запрос.
- Ответ `204` дает `data` как `undefined`.
- Запрос отправляется в браузере после монтирования компонента. Данные, которые должен хранить первый HTML-код, принадлежат реквизитам страницы, отображаемым на сервере.

## Ошибки на маршруте

Ответ, отличный от `2xx`, становится `error`, `FetchError` с `status` и `detail` маршрутом. `data` сохраняет свое последнее значение:

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

Компонент считывает ошибку одинаково в обоих маршрутизаторах:

```tsx filename="src/компоненты/имя_пользователя.tsx"
import { useFetch, FetchError } from "@nexy/client";

export function UserName({ id }: { id: number }) {
  const { data, error } = useFetch<{ name: string }>(`/api/users/${id}`);
  if (error instanceof FetchError && error.status === 404) return <p>{String(error.detail)}</p>;
  return <p>{data?.name}</p>;
}
```

## Перезагрузить данные после действия

Действие, которое вызывает `revalidate()` для открытой страницы, приводит к повторной выборке каждой `useFetch` этой страницы после обновления самой страницы:

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

```tsx filename="источник/компоненты/AddUser.tsx"
import { useAction } from "@nexy/client";
import { add_user } from "@nexy/actions";

export function AddUser() {
  const { run, pending } = useAction(add_user);
  return <button disabled={pending} onClick={() => run({ name: "Grace" })}>Add Grace</button>;
}
```

В списке `src/components/Users.tsx` показана Грейс без вызова `refresh()`.

## Следующие шаги

- [Действия и навигация](actions-and-navigation.md): изменение данных из компонента
- [Действия](../../guides/actions.md): `revalidate()` и цикл действий
- [Модульная маршрутизация](../../routing/modular/README.md): напишите контроллер, который отвечает
