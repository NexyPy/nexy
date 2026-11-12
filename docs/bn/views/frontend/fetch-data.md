# একটি কম্পোনেন্টে সার্ভার থেকে ডেটা আনুন

একটি উপাদানে সার্ভার থেকে ডেটা আনতে, `@nexy/client` থেকে `useFetch(url)` কল করুন: এটি একটি `GET` কে প্রকল্পের একটি রুটে পাঠায় এবং `data`, `error`, `pending` এবং `refresh` ফেরত দেয়।

## উত্তর যে রুট

`useFetch` প্রকল্পের যেকোনো `GET` রুট থেকে JSON পড়ে। নীচের উভয় উদাহরণ একই ডেটা পরিবেশন করে:

```python filename="src/data.py"
USERS = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Linus"}]
```

<!-- router:fbr,custom -->
একটি ফাইল রুট এটির উত্তর দেয়:

```python filename="src/routes/api/users/index.py"
from src.data import USERS


async def GET():
    return USERS
```
<!-- /router -->

<!-- router:modular -->
একজন নিয়ামক এটির উত্তর দেয়:

```python filename="src/apps/users/users_controller.py"
from nexy.decorators import Controller

from src.data import USERS


@Controller("/api/users")
class UsersController:
    async def get(self):
        return USERS
```
<!-- /router -->

## React এবং Preact এ `useFetch` সহ ডেটা আনুন

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

## Vue এর মধ্যে `useFetch` দিয়ে ডেটা আনুন

`data`, `error` এবং `pending` গণনাকৃত রেফ:

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

## Svelte এর মধ্যে `useFetch` দিয়ে ডেটা আনুন

`useFetch` একটি দোকান ফেরত দেয়: এটি `$` দিয়ে পড়ুন, এবং দোকানেই `refresh` কল করুন:

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

## Solid এ `useFetch` দিয়ে ডেটা আনুন

`data`, `error` এবং `pending` হল অ্যাক্সেসর:

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

## একটি পৃষ্ঠায় উপাদান দেখান

<!-- router:fbr,custom -->
একটি ফাইল পৃষ্ঠা উপাদান আমদানি করে:

```tsx filename="src/routes/users.tsx"
import { Users } from "@/components/Users";

export default function UsersPage() {
  return <Users />;
}
```
<!-- /router -->

<!-- router:modular -->
একটি কন্ট্রোলার একটি `.nexy` ভিউ প্রদান করে এবং ভিউটি উপাদানটিকে মাউন্ট করে:

```nexy filename="src/apps/users/users_view.nexy"
---
from "@/components/Users.tsx" import Users
---
<Users directive="client:load" />
```
<!-- /router -->

একটি Vue, Svelte বা Solid উপাদান একইভাবে মাউন্ট করা হয়, এর কাঠামোর আমদানি সিনট্যাক্স সহ।

## যা `useFetch` পাঠায় এবং শেয়ার করে

- অনুরোধ একটি `GET` সঙ্গে `Accept: application/json` এবং সাইটের কুকিজ, তাই রুটটি পৃষ্ঠার মতো একই সেশন দেখায়।
- ইউআরএল প্রতি একটি অবস্থা: দুটি উপাদান যা পড়ে `/api/users` একটি অনুরোধ পাঠায় এবং একই ডেটা দেখায়।
- `refresh()` নতুন উত্তর না আসা পর্যন্ত বর্তমান `data` রাখে এবং একবারে দুটি রিফ্রেশ করে একটি অনুরোধ পাঠায়।
- একটি `204` উত্তর দেয় `data` `undefined` হিসাবে।
- কম্পোনেন্ট মাউন্ট করার পরে অনুরোধটি ব্রাউজারে পাঠানো হয়। সার্ভারে রেন্ডার করা পৃষ্ঠা প্রপসের মধ্যে থাকা প্রথম এইচটিএমএল-এর ডেটা থাকতে হবে।

## রুট থেকে ত্রুটি

একটি উত্তর যা `2xx` নয় `error` হয়ে যায়, একটি `FetchError` এর সাথে `status` এবং `detail` রুট দেওয়া হয়। `data` তার শেষ মান রাখে:

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

উপাদানটি উভয় রাউটারে একইভাবে ত্রুটিটি পড়ে:

```tsx filename="src/components/UserName.tsx"
import { useFetch, FetchError } from "@nexy/client";

export function UserName({ id }: { id: number }) {
  const { data, error } = useFetch<{ name: string }>(`/api/users/${id}`);
  if (error instanceof FetchError && error.status === 404) return <p>{String(error.detail)}</p>;
  return <p>{data?.name}</p>;
}
```

## একটি কর্মের পরে ডেটা পুনরায় লোড করুন

একটি ক্রিয়া যা খোলা পৃষ্ঠার জন্য `revalidate()` কল করে সেই পৃষ্ঠাটির প্রতিটি `useFetch` আবার আনয়ন করে, একবার পৃষ্ঠাটি নিজেই রিফ্রেশ হয়ে গেলে:

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

`src/components/Users.tsx`-এর তালিকাটি `refresh()`-এ কল ছাড়াই গ্রেসকে দেখায়।

## পরবর্তী পদক্ষেপ

- [কর্ম এবং নেভিগেশন ](actions-and-navigation.md): একটি উপাদান থেকে তথ্য পরিবর্তন
- [ক্রিয়া ](../../guides/actions.md): `revalidate()` এবং কর্মচক্র
- [মডুলার রাউটিং ](../../routing/modular/README.md): উত্তর দেয় এমন নিয়ামকটি লিখুন
