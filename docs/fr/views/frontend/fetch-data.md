# Récupérer les données du serveur dans un composant

Pour récupérer des données du serveur dans un composant, appelez `useFetch(url)` depuis `@nexy/client` : il envoie un `GET` vers une route du projet et restitue `data`, `error`, `pending` et `refresh`.

## L'itinéraire qui répond

`useFetch` lit JSON à partir de n'importe quelle route `GET` du projet. Les deux exemples ci-dessous servent les mêmes données :

```python filename="src/data.py"
USERS = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Linus"}]
```

<!-- router:fbr,custom -->
Un itinéraire de fichiers y répond :

```python filename="src/routes/api/users/index.py"
from src.data import USERS


async def GET():
    return USERS
```
<!-- /router -->

<!-- router:modular -->
Un contrôleur y répond :

```python filename="src/apps/users/users_controller.py"
from nexy.decorators import Controller

from src.data import USERS


@Controller("/api/users")
class UsersController:
    async def get(self):
        return USERS
```
<!-- /router -->

## Récupérer des données avec `useFetch` dans React et Preact

```tsx filename="src/components/Utilisateurs.tsx"
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

## Récupérer des données avec `useFetch` dans Vue

`data`, `error` et `pending` sont des références calculées :

```vue filename="src/components/Utilisateurs.vue"
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

## Récupérer des données avec `useFetch` dans Svelte

`useFetch` renvoie un magasin : lisez-le avec `$`, et appelez `refresh` sur le magasin lui-même :

```svelte filename="src/components/Utilisateurs.svelte"
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

## Récupérer des données avec `useFetch` dans Solid

`data`, `error` et `pending` sont des accesseurs :

```tsx filename="src/components/Utilisateurs.tsx"
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

## Afficher le composant sur une page

<!-- router:fbr,custom -->
Une page de fichier importe le composant :

```tsx filename="src/routes/users.tsx"
import { Users } from "@/components/Users";

export default function UsersPage() {
  return <Users />;
}
```
<!-- /router -->

<!-- router:modular -->
Un contrôleur renvoie une vue `.nexy` et la vue monte le composant :

```nexy filename="src/apps/users/users_view.nexy"
---
from "@/components/Users.tsx" import Users
---
<Users directive="client:load" />
```
<!-- /router -->

Un composant Vue, Svelte ou Solid est monté de la même manière, avec la syntaxe d'import de son framework.

## Ce que `useFetch` envoie et partage

- La requête est un `GET` avec `Accept: application/json` et les cookies du site, donc la route voit la même session que la page.
- Un état par URL : deux composants qui lisent `/api/users` envoient une requête et affichent les mêmes données.
- `refresh()` conserve le `data` actuel jusqu'à ce que la nouvelle réponse arrive, et deux actualisations simultanées envoient une demande.
- Une réponse `204` donne `data` comme `undefined`.
- La requête est envoyée dans le navigateur, après le montage du composant. Les données que le premier HTML doit contenir appartiennent aux accessoires de page, rendus sur le serveur.

## Erreurs de l'itinéraire

Une réponse qui n'est pas `2xx` devient `error`, un `FetchError` avec le `status` et le `detail` donnés par l'itinéraire. `data` conserve sa dernière valeur :

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

Le composant lit l'erreur de la même manière dans les deux routeurs :

```tsx filename="src/components/UserName.tsx"
import { useFetch, FetchError } from "@nexy/client";

export function UserName({ id }: { id: number }) {
  const { data, error } = useFetch<{ name: string }>(`/api/users/${id}`);
  if (error instanceof FetchError && error.status === 404) return <p>{String(error.detail)}</p>;
  return <p>{data?.name}</p>;
}
```

## Recharger les données après une action

Une action qui appelle `revalidate()` pour la page ouverte fait que chaque `useFetch` de cette page est à nouveau récupéré, une fois la page elle-même actualisée :

```python filename="src/actions/utilisateurs.py"
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

La liste des `src/components/Users.tsx` montre Grace sans appel à `refresh()`.

## Prochaines étapes

- [Actions et navigation](actions-and-navigation.md) : modifier les données d'un composant
- [Actions](../../guides/actions.md) : `revalidate()` et le cycle d'action
- [Routage modulaire](../../routing/modular/README.md) : écrivez le contrôleur qui répond
