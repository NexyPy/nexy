# Daten vom Server in einer Komponente abrufen

Um Daten vom Server in einer Komponente abzurufen, rufen Sie `useFetch(url)` von `@nexy/client` auf: Es sendet ein `GET` an eine Route des Projekts und gibt `data`, `error`, `pending` und `refresh` zurück.

## Der Weg, der antwortet

`useFetch` liest JSON von jeder `GET`-Route des Projekts. Die beiden folgenden Beispiele liefern dieselben Daten:

```python filename="src/data.py"
USERS = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Linus"}]
```

<!-- router:fbr,custom -->
Eine Dateiroute beantwortet es:

```python filename="src/routes/api/users/index.py"
from src.data import USERS


async def GET():
    return USERS
```
<!-- /router -->

<!-- router:modular -->
Ein Controller antwortet darauf:

```python filename="src/apps/users/users_controller.py"
from nexy.decorators import Controller

from src.data import USERS


@Controller("/api/users")
class UsersController:
    async def get(self):
        return USERS
```
<!-- /router -->

## Daten mit `useFetch` in React und Preact abrufen

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

## Daten mit `useFetch` in Vue abrufen

`data`, `error` und `pending` sind berechnete Referenzen:

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

## Daten mit `useFetch` in Svelte abrufen

`useFetch` gibt einen Store zurück: Lesen Sie ihn mit `$` und rufen Sie `refresh` für den Store selbst auf:

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

## Daten mit `useFetch` in Solid abrufen

`data`, `error` und `pending` sind Accessoren:

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

## Zeigen Sie die Komponente auf einer Seite an

<!-- router:fbr,custom -->
Eine Dateiseite importiert die Komponente:

```tsx filename="src/routes/users.tsx"
import { Users } from "@/components/Users";

export default function UsersPage() {
  return <Users />;
}
```
<!-- /router -->

<!-- router:modular -->
Ein Controller gibt eine `.nexy`-Ansicht zurück und die Ansicht mountet die Komponente:

```nexy filename="src/apps/users/users_view.nexy"
---
from "@/components/Users.tsx" import Users
---
<Users directive="client:load" />
```
<!-- /router -->

Eine Vue-, Svelte- oder Solid-Komponente wird auf die gleiche Weise mit der Importsyntax ihres Frameworks gemountet.

## Was `useFetch` sendet und teilt

- Die Anfrage ist ein `GET` mit `Accept: application/json` und den Cookies der Website, sodass die Route dieselbe Sitzung wie die Seite sieht.
- Ein Status pro URL: Zwei Komponenten, die `/api/users` lesen, senden eine Anfrage und zeigen dieselben Daten an.
- `refresh()` behält den aktuellen `data` bei, bis die neue Antwort eintrifft, und zwei Aktualisierungen gleichzeitig senden eine Anfrage.
- Eine `204`-Antwort ergibt `data` als `undefined`.
- Die Anfrage wird im Browser gesendet, nachdem die Komponente bereitgestellt wurde. Daten, die der erste HTML-Code enthalten muss, gehören zu den Seiten-Requisiten und werden auf dem Server gerendert.

## Fehler von der Route

Eine Antwort, die nicht `2xx` ist, wird zu `error`, eine `FetchError` mit dem `status` und dem `detail`, die die Route gab. `data` behält seinen letzten Wert:

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

Die Komponente liest den Fehler in beiden Routern gleich:

```tsx filename="src/components/Benutzername.tsx"
import { useFetch, FetchError } from "@nexy/client";

export function UserName({ id }: { id: number }) {
  const { data, error } = useFetch<{ name: string }>(`/api/users/${id}`);
  if (error instanceof FetchError && error.status === 404) return <p>{String(error.detail)}</p>;
  return <p>{data?.name}</p>;
}
```

## Laden Sie die Daten nach einer Aktion neu

Eine Aktion, die `revalidate()` für die geöffnete Seite aufruft, sorgt dafür, dass alle `useFetch` dieser Seite erneut abgerufen werden, sobald die Seite selbst aktualisiert wird:

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

Die Liste von `src/components/Users.tsx` zeigt Grace ohne einen Anruf bei `refresh()`.

## Nächste Schritte

- [Aktionen und Navigation](actions-and-navigation.md): Daten einer Komponente ändern
- [Aktionen](../../guides/actions.md): `revalidate()` und der Aktionszyklus
- [Modulares Routing](../../routing/modular/README.md): Schreiben Sie den Controller, der antwortet
