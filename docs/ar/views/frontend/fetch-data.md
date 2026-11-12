# جلب البيانات من الخادم في مكون

لجلب البيانات من الخادم في مكون، اتصل بـ `useFetch(url)` من `@nexy/client`: يرسل واحدًا `GET` إلى مسار المشروع ويعيد `data`، `error`، `pending` و `refresh`.

## الطريق الذي يجيب

`useFetch` يقرأ JSON من أي `GET` مسار المشروع. كلا المثالين أدناه يخدمان نفس البيانات:

```python filename="src/data.py"
USERS = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Linus"}]
```

<!-- router:fbr,custom -->
يجيب عليه مسار الملف:

```python filename="src/routes/api/users/index.py"
from src.data import USERS


async def GET():
    return USERS
```
<!-- /router -->

<!-- router:modular -->
يجيب عليه المراقب المالي:

```python filename="src/apps/users/users_controller.py"
from nexy.decorators import Controller

from src.data import USERS


@Controller("/api/users")
class UsersController:
    async def get(self):
        return USERS
```
<!-- /router -->

## جلب البيانات باستخدام `useFetch` في React و Preact

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

## جلب البيانات باستخدام `useFetch` في Vue

`data`، `error` و `pending` هي مراجع محسوبة:

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

## جلب البيانات باستخدام `useFetch` في Svelte

`useFetch` يُرجع متجرًا: اقرأه مع `$`، واتصل بـ `refresh` على المتجر نفسه:

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

## جلب البيانات باستخدام `useFetch` في Solid

`data`، `error` و `pending` هي أدوات الوصول:

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

## إظهار المكون على الصفحة

<!-- router:fbr,custom -->
تستورد صفحة الملف المكون:

```tsx filename="src/routes/users.tsx"
import { Users } from "@/components/Users";

export default function UsersPage() {
  return <Users />;
}
```
<!-- /router -->

<!-- router:modular -->
تقوم وحدة التحكم بإرجاع عرض `.nexy`، ويقوم العرض بتثبيت المكون:

```nexy filename="src/apps/users/users_view.nexy"
---
from "@/components/Users.tsx" import Users
---
<Users directive="client:load" />
```
<!-- /router -->

يتم تركيب المكون Vue أو Svelte أو Solid بنفس الطريقة، مع بناء جملة الاستيراد الخاص بإطار العمل الخاص به.

## ما `useFetch` يرسل ويشارك

- الطلب عبارة عن `GET` مع `Accept: application/json` وملفات تعريف الارتباط الخاصة بالموقع، لذلك يرى المسار نفس الجلسة مثل الصفحة.
- حالة واحدة لكل عنوان URL: مكونان يقرأان `/api/users` يرسلان طلبًا واحدًا ويعرضان نفس البيانات.
- `refresh()` يحتفظ بالرقم `data` الحالي حتى وصول الإجابة الجديدة، ويقوم التحديث مرتين في وقت واحد بإرسال طلب واحد.
- الجواب `204` يعطي `data` كـ `undefined`.
- يتم إرسال الطلب في المتصفح، بعد تحميل المكون. البيانات التي يجب أن يحتفظ بها HTML الأول تنتمي إلى دعائم الصفحة، والتي يتم عرضها على الخادم.

## أخطاء من الطريق

الإجابة التي ليست `2xx` تصبح `error`، و `FetchError` مع `status` و `detail` أعطى الطريق. `data` يحتفظ بقيمته الأخيرة:

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

يقرأ المكون الخطأ بنفس الطريقة في كلا الموجهين:

```tsx filename="src/components/UserName.tsx"
import { useFetch, FetchError } from "@nexy/client";

export function UserName({ id }: { id: number }) {
  const { data, error } = useFetch<{ name: string }>(`/api/users/${id}`);
  if (error instanceof FetchError && error.status === 404) return <p>{String(error.detail)}</p>;
  return <p>{data?.name}</p>;
}
```

## إعادة تحميل البيانات بعد الإجراء

الإجراء الذي يستدعي `revalidate()` للصفحة المفتوحة يجعل كل `useFetch` من تلك الصفحة يتم جلبه مرة أخرى، بمجرد تحديث الصفحة نفسها:

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

قائمة `src/components/Users.tsx` تظهر النعمة بدون استدعاء `refresh()`.

## الخطوات التالية

- [الإجراءات والتنقل](actions-and-navigation.md): تغيير البيانات من أحد المكونات
- [الأفعال](../../guides/actions.md): `revalidate()` ودورة الفعل
- [التوجيه المعياري](../../routing/modular/README.md): اكتب وحدة التحكم التي تجيب
