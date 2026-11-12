# سرور سے کسی جزو میں ڈیٹا حاصل کریں۔

کسی جزو میں سرور سے ڈیٹا حاصل کرنے کے لیے، `@nexy/client` سے `useFetch(url)` کو کال کریں: یہ ایک `GET` کو پروجیکٹ کے روٹ پر بھیجتا ہے اور `data`، `error`، `pending` اور `refresh` کو واپس دیتا ہے۔

## وہ راستہ جو جواب دیتا ہے۔

`useFetch` پروجیکٹ کے کسی بھی `GET` راستے سے JSON پڑھتا ہے۔ ذیل میں دونوں مثالیں ایک ہی ڈیٹا پیش کرتی ہیں:

```python filename="src/data.py"
USERS = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Linus"}]
```

<!-- router:fbr,custom -->
ایک فائل روٹ اس کا جواب دیتا ہے:

```python filename="src/routes/api/users/index.py"
from src.data import USERS


async def GET():
    return USERS
```
<!-- /router -->

<!-- router:modular -->
ایک کنٹرولر اس کا جواب دیتا ہے:

```python filename="src/apps/users/users_controller.py"
from nexy.decorators import Controller

from src.data import USERS


@Controller("/api/users")
class UsersController:
    async def get(self):
        return USERS
```
<!-- /router -->

## React اور Preact میں `useFetch` کے ساتھ ڈیٹا حاصل کریں

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

## Vue میں `useFetch` کے ساتھ ڈیٹا حاصل کریں

`data`، `error` اور `pending` حسابی حوالہ جات ہیں:

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

## Svelte میں `useFetch` کے ساتھ ڈیٹا حاصل کریں

`useFetch` ایک اسٹور واپس کرتا ہے: اسے `$` کے ساتھ پڑھیں، اور اسٹور پر ہی `refresh` کو کال کریں:

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

## Solid میں `useFetch` کے ساتھ ڈیٹا حاصل کریں

`data`، `error` اور `pending` رسائی کرنے والے ہیں:

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

## ایک صفحہ پر جزو دکھائیں۔

<!-- router:fbr,custom -->
فائل کا صفحہ جزو درآمد کرتا ہے:

```tsx filename="src/routes/users.tsx"
import { Users } from "@/components/Users";

export default function UsersPage() {
  return <Users />;
}
```
<!-- /router -->

<!-- router:modular -->
ایک کنٹرولر ایک `.nexy` منظر لوٹاتا ہے، اور منظر جزو کو ماؤنٹ کرتا ہے:

```nexy filename="src/apps/users/users_view.nexy"
---
from "@/components/Users.tsx" import Users
---
<Users directive="client:load" />
```
<!-- /router -->

ایک Vue، Svelte یا Solid جزو اسی طرح نصب کیا جاتا ہے، اس کے فریم ورک کی درآمدی ترکیب کے ساتھ۔

## کیا `useFetch` بھیجتا ہے اور شیئر کرتا ہے۔

- درخواست ایک `GET` ہے جس میں `Accept: application/json` اور سائٹ کی کوکیز ہیں، لہذا روٹ وہی سیشن دیکھتا ہے جیسا کہ صفحہ ہے۔
- ایک حالت فی یو آر ایل: دو اجزاء جو پڑھتے ہیں `/api/users` ایک درخواست بھیجتے ہیں اور وہی ڈیٹا دکھاتے ہیں۔
- `refresh()` نیا جواب آنے تک موجودہ `data` کو برقرار رکھتا ہے، اور ایک بار میں دو ریفریش ایک درخواست بھیجتا ہے۔
- ایک `204` جواب دیتا ہے `data` بطور `undefined`۔
- اجزاء کے ماؤنٹ ہونے کے بعد درخواست براؤزر میں بھیجی جاتی ہے۔ ڈیٹا جو پہلے ایچ ٹی ایم ایل کے پاس ہونا ضروری ہے وہ صفحہ پروپس میں ہے، جو سرور پر پیش کیا گیا ہے۔

## راستے سے خرابیاں

جو جواب `2xx` نہیں ہے وہ `error` بن جاتا ہے، `FetchError` کے ساتھ `status` اور `detail` نے راستہ دیا۔ `data` اپنی آخری قدر رکھتا ہے:

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

جزو دونوں راؤٹرز میں غلطی کو اسی طرح پڑھتا ہے:

```tsx filename="src/components/UserName.tsx"
import { useFetch, FetchError } from "@nexy/client";

export function UserName({ id }: { id: number }) {
  const { data, error } = useFetch<{ name: string }>(`/api/users/${id}`);
  if (error instanceof FetchError && error.status === 404) return <p>{String(error.detail)}</p>;
  return <p>{data?.name}</p>;
}
```

## ایک کارروائی کے بعد ڈیٹا کو دوبارہ لوڈ کریں۔

ایک ایسا عمل جو کھلے صفحہ کے لیے `revalidate()` کو کال کرتا ہے اس صفحے کے ہر `useFetch` کو دوبارہ حاصل کرتا ہے، ایک بار جب صفحہ خود تازہ ہوجاتا ہے:

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

`src/components/Users.tsx` کی فہرست `refresh()` پر کال کیے بغیر فضل کو ظاہر کرتی ہے۔

## اگلے اقدامات

- [ایکشن اور نیویگیشن](actions-and-navigation.md): کسی جزو سے ڈیٹا تبدیل کریں۔
- [اعمال](../../guides/actions.md): `revalidate()` اور ایکشن سائیکل
- [ماڈیولر روٹنگ](../../routing/modular/README.md): جواب دینے والا کنٹرولر لکھیں۔
