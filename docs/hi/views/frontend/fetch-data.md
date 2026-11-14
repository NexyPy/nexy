# किसी घटक में सर्वर से डेटा प्राप्त करें

किसी घटक में सर्वर से डेटा लाने के लिए, `@nexy/client` से `useFetch(url)` पर कॉल करें: यह एक `GET` को प्रोजेक्ट के रूट पर भेजता है और `data`, `error`, `pending` और `refresh` वापस देता है।

## वह मार्ग जो उत्तर देता है

`useFetch` प्रोजेक्ट के किसी भी `GET` रूट से JSON पढ़ता है। नीचे दिए गए दोनों उदाहरण समान डेटा प्रस्तुत करते हैं:

```python filename="src/data.py"
USERS = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Linus"}]
```

<!-- router:fbr,custom -->
एक फ़ाइल मार्ग इसका उत्तर देता है:

```python filename="src/routes/api/users/index.py"
from src.data import USERS


async def GET():
    return USERS
```
<!-- /router -->

<!-- router:modular -->
एक नियंत्रक इसका उत्तर देता है:

```python filename="src/apps/users/users_controller.py"
from nexy.decorators import Controller

from src.data import USERS


@Controller("/api/users")
class UsersController:
    async def get(self):
        return USERS
```
<!-- /router -->

## `useFetch` से React और Preact में डेटा प्राप्त करें

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

## `useFetch` से Vue में डेटा प्राप्त करें

`data`, `error` और `pending` परिकलित रेफरी हैं:

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

## Svelte में `useFetch` से डेटा प्राप्त करें

`useFetch` एक स्टोर लौटाता है: इसे `$` के साथ पढ़ें, और स्टोर पर ही `refresh` पर कॉल करें:

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

## Solid में `useFetch` से डेटा प्राप्त करें

`data`, `error` और `pending` एक्सेसर्स हैं:

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

## किसी पृष्ठ पर घटक दिखाएँ

<!-- router:fbr,custom -->
एक फ़ाइल पृष्ठ घटक आयात करता है:

```tsx filename="src/routes/users.tsx"
import { Users } from "@/components/Users";

export default function UsersPage() {
  return <Users />;
}
```
<!-- /router -->

<!-- router:modular -->
एक नियंत्रक एक `.nexy` दृश्य लौटाता है, और दृश्य घटक को माउंट करता है:

```nexy filename="src/apps/users/users_view.nexy"
---
from "@/components/Users.tsx" import Users
---
<Users directive="client:load" />
```
<!-- /router -->

एक Vue, Svelte या Solid घटक को उसके ढांचे के आयात सिंटैक्स के साथ उसी तरह माउंट किया जाता है।

## `useFetch` क्या भेजता और साझा करता है

- अनुरोध `GET` के साथ `Accept: application/json` और साइट की कुकीज़ है, इसलिए रूट पृष्ठ के समान सत्र देखता है।
- प्रति यूआरएल एक स्थिति: `/api/users` पढ़ने वाले दो घटक एक अनुरोध भेजते हैं और वही डेटा दिखाते हैं।
- `refresh()` नया उत्तर आने तक चालू `data` रखता है, और एक बार में दो रिफ्रेश एक अनुरोध भेजते हैं।
- एक `204` उत्तर `data` को `undefined` देता है।
- घटक माउंट होने के बाद, अनुरोध ब्राउज़र में भेजा जाता है। डेटा जो पहले HTML के पास होना चाहिए वह सर्वर पर रेंडर किए गए पेज प्रॉप्स में होता है।

## मार्ग से त्रुटियाँ

एक उत्तर जो `2xx` नहीं है वह `error` बन जाता है, `FetchError` के साथ `status` और `detail` का मार्ग दिया जाता है। `data` अपना अंतिम मान रखता है:

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

घटक दोनों राउटर में त्रुटि को उसी तरह पढ़ता है:

```tsx filename="src/components/UserName.tsx"
import { useFetch, FetchError } from "@nexy/client";

export function UserName({ id }: { id: number }) {
  const { data, error } = useFetch<{ name: string }>(`/api/users/${id}`);
  if (error instanceof FetchError && error.status === 404) return <p>{String(error.detail)}</p>;
  return <p>{data?.name}</p>;
}
```

## किसी कार्रवाई के बाद डेटा पुनः लोड करें

एक क्रिया जो खुले पृष्ठ के लिए `revalidate()` को कॉल करती है, उस पृष्ठ के प्रत्येक `useFetch` को फिर से लाती है, एक बार पृष्ठ स्वयं ताज़ा हो जाता है:

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

`src/components/Users.tsx` की सूची में ग्रेस को `refresh()` पर कॉल किए बिना दिखाया गया है।

## अगले चरण

- [क्रियाएँ और नेविगेशन](actions-and-navigation.md): एक घटक से डेटा बदलें
- [क्रियाएँ](../../guides/actions.md): `revalidate()` और क्रिया चक्र
- [मॉड्यूलर रूटिंग](../../routing/modular/README.md): उत्तर देने वाले नियंत्रक को लिखें
