# Mengambil data dari server dalam sebuah komponen

Untuk mengambil data dari server dalam sebuah komponen, panggil `useFetch(url)` dari `@nexy/client`: ia mengirimkan satu `GET` ke rute proyek dan mengembalikan `data`, `error`, `pending` dan `refresh`.

## Rute yang menjawab

`useFetch` membaca JSON dari `GET` rute proyek mana pun. Kedua contoh di bawah menyajikan data yang sama:

```python filename="src/data.py"
USERS = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Linus"}]
```

<!-- router:fbr,custom -->
Rute file menjawabnya:

```python filename="src/routes/api/users/index.py"
from src.data import USERS


async def GET():
    return USERS
```
<!-- /router -->

<!-- router:modular -->
Seorang pengontrol menjawabnya:

```python filename="src/apps/users/users_controller.py"
from nexy.decorators import Controller

from src.data import USERS


@Controller("/api/users")
class UsersController:
    async def get(self):
        return USERS
```
<!-- /router -->

## Ambil data dengan `useFetch` di React dan Preact

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

## Ambil data dengan `useFetch` di Vue

`data`, `error` dan `pending` adalah referensi yang dihitung:

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

## Ambil data dengan `useFetch` di Svelte

`useFetch` mengembalikan toko: membacanya dengan `$`, dan memanggil `refresh` pada toko itu sendiri:

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

## Ambil data dengan `useFetch` di Solid

`data`, `error` dan `pending` adalah pengakses:

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

## Tampilkan komponen pada halaman

<!-- router:fbr,custom -->
Halaman file mengimpor komponen:

```tsx filename="src/rute/pengguna.tsx"
import { Users } from "@/components/Users";

export default function UsersPage() {
  return <Users />;
}
```
<!-- /router -->

<!-- router:modular -->
Pengontrol mengembalikan tampilan `.nexy`, dan tampilan tersebut memasang komponen:

```nexy filename="src/apps/users/users_view.nexy"
---
from "@/components/Users.tsx" import Users
---
<Users directive="client:load" />
```
<!-- /router -->

Komponen Vue, Svelte atau Solid dipasang dengan cara yang sama, dengan sintaks import kerangka kerjanya.

## Apa yang `useFetch` kirim dan bagikan

- Permintaannya adalah `GET` dengan `Accept: application/json` dan cookie situs, sehingga rute melihat sesi yang sama dengan halaman tersebut.
- Satu status per URL: dua komponen yang membaca `/api/users` mengirimkan satu permintaan dan menampilkan data yang sama.
- `refresh()` menyimpan `data` saat ini hingga jawaban baru tiba, dan dua penyegaran sekaligus mengirimkan satu permintaan.
- Jawaban `204` menghasilkan `data` sebagai `undefined`.
- Permintaan dikirim di browser, setelah komponen dipasang. Data yang harus disimpan oleh HTML pertama adalah milik props halaman, yang dirender di server.

## Kesalahan dari rute

Jawaban yang bukan `2xx` menjadi `error`, `FetchError` dengan `status` dan `detail` yang diberikan rute. `data` mempertahankan nilai terakhirnya:

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

Komponen membaca kesalahan dengan cara yang sama di kedua router:

```tsx filename="src/komponen/NamaPengguna.tsx"
import { useFetch, FetchError } from "@nexy/client";

export function UserName({ id }: { id: number }) {
  const { data, error } = useFetch<{ name: string }>(`/api/users/${id}`);
  if (error instanceof FetchError && error.status === 404) return <p>{String(error.detail)}</p>;
  return <p>{data?.name}</p>;
}
```

## Muat ulang data setelah suatu tindakan

Tindakan yang memanggil `revalidate()` untuk halaman yang terbuka membuat setiap `useFetch` halaman tersebut diambil lagi, setelah halaman itu sendiri di-refresh:

```python filename="src/aksi/pengguna.py"
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

Daftar `src/components/Users.tsx` menunjukkan Grace tanpa panggilan ke `refresh()`.

## Langkah selanjutnya

- [Tindakan dan navigasi](actions-and-navigation.md): mengubah data dari suatu komponen
- [Tindakan](../../guides/actions.md): `revalidate()` dan siklus tindakan
- [Perutean modular](../../routing/modular/README.md): tulis pengontrol yang menjawab
