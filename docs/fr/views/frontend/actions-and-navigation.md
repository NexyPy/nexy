# Actions et navigation

L'interaction dans Nexy est gérée via un système unifié d'**Actions** et de **Navigation**, garantissant que le frontend et le backend restent synchronisés sans code de colle API manuel.

## Le contrat d'action

Une **Action** est une fonction côté serveur qui gère une mutation (par exemple, la mise à jour d'une base de données). 

1.  **Entrée typée** : les actions sont définies dans Python avec des indications de type. Nexy génère un client TypeScript correspondant, vous obtenez donc la saisie semi-automatique et la validation dans votre IDE.
2.  **Exécution atomique** : une action est une seule requête `POST`.
3.  **Gestion des résultats** : les actions renvoient un résultat typé que le client peut utiliser pour mettre à jour l'interface utilisateur.

```python filename="src/actions/todos.py"
from pydantic import BaseModel
from nexy.decorators import Action


class Todo(BaseModel):
    title: str
    done: bool = False


@Action
async def add_todo(title: str) -> Todo:
    return Todo(title=title)
```

La page l'appelle avec l'entrée Python déclarée et récupère un retour `Todo` tapé :

```tsx filename="src/routes/todos.tsx"
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export default function Todos() {
  const { run, pending, data } = useAction(add_todo);
  return (
    <button disabled={pending} onClick={() => run({ title: "Write the docs" })}>
      {data ? `Added ${data.title}` : "Add"}
    </button>
  );
}
```

## Navigation côté client

La navigation dans Nexy est « intelligente ». Au lieu d'un rechargement complet du navigateur, Nexy échange le contenu de la page actuelle tout en gardant les mises en page actives montées.

- **Le composant `Link`** : utilisez le composant `Link` spécifique au framework pour effectuer des transitions côté client.
- **Navigation programmatique** : utilisez `useRouter()` à partir de `@nexy/client` et appelez `push()` pour changer de page en réponse à la logique (par exemple, après une connexion réussie).

```tsx filename="src/components/Nav.tsx"
import { Link } from "@nexy/client";

export function Nav() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about" activeClassName="active">About</Link>
    </nav>
  );
}
```

```tsx filename="src/components/Done.tsx"
import { useRouter } from "@nexy/client";

export function Done() {
  const router = useRouter();
  return <button onClick={() => router.push("/dashboard")}>Continue</button>;
}
```

## Coordination : Action → Navigation

Le modèle le plus courant consiste à effectuer une action, puis à diriger l'utilisateur vers une nouvelle page.

**Le flux de revalidation :**
1.  Le client appelle une action.
2.  L'action s'exécute sur le serveur et appelle `revalidate("/path")`.
3.  Le serveur renvoie le résultat avec un en-tête `x-nexy-revalidate` nommant les chemins obsolètes.
4.  Le client met à jour le contenu de la page pour refléter le nouvel état.

```python filename="src/actions/session.py"
from nexy.decorators import Action, revalidate


@Action
async def sign_in(email: str, password: str) -> bool:
    ok = check_password(email, password)
    revalidate("/dashboard")
    return ok
```

```tsx filename="src/routes/login.tsx"
import { useAction, useRouter } from "@nexy/client";
import { sign_in } from "@nexy/actions";

export default function Login() {
  const router = useRouter();
  const { run } = useAction(sign_in, {
    onSuccess: (ok) => {
      if (ok) router.push("/dashboard");
    },
  });
  return <button onClick={() => run({ email: "ada@example.com", password: "..." })}>Sign in</button>;
}
```

`check_password` représente votre propre chèque. Voir [Actions](../../guides/actions.md) pour les erreurs, les formulaires sans JavaScript et la sécurité.

## Mise en œuvre du cadre

L'API pour appeler des actions et naviguer varie selon le framework. Consultez le guide des **Différences** pour la technologie que vous avez choisie :

- [React Différences](../react/differences.md)
- [Vue Différences](../vue/differences.md)
- [Svelte Différences](../svelte/differences.md)
- [Solid Différences](../solid/differences.md)
- [Preact Différences](../preact/differences.md)
