# Actions

Un `@Action` transforme une fonction Python en un point final `POST`. Contrairement à un gestionnaire d'API standard, il est conçu comme un pont de communication typé : Nexy génère automatiquement le client TypeScript, valide l'entrée et gère la réponse.

**Avant de commencer :** un projet créé par le [Démarrage rapide](../getting-started/quick-start.md). Les actions se trouvent à côté des pages, dans `src/actions/`.

```diagram filename="Le cycle d'action"
Client (UI)  ─── 1. Call (Typed Input) ───► [ Nexy Bridge ]
                                                  │
                                                  ▼
                                      2. Validate & Execute (Python)
                                                  │
                                                  ▼
Client (UI)  ◄─── 5. Consume (Typed Result) ◄── 4. Serialize ◄── 3. Result
```

## Le cycle d'action

### 1. Définir
Une action est une fonction Python normale marquée par `@Action`. Nexy utilise sa signature pour définir le contrat API.

```python filename="src/actions/user.py"
from pydantic import BaseModel
from nexy.decorators import Action, revalidate

class User(BaseModel):
    name: str
    age: int = 0

@Action
async def create_user(name: str, age: int = 0) -> User:
    revalidate()
    return User(name=name, age=age)
```

Les paramètres sont l'entrée, validée par Pydantic. Un paramètre nommé `request` ou `response` est injecté et ne fait pas partie de l'entrée.

### 2. Validez
Lorsque l'action est appelée, Nexy valide l'entrée par rapport aux indications de type de la fonction. Si un champ est manquant ou a un type incorrect, l'action n'est pas exécutée et un `422 Unprocessable Entity` est renvoyé.

### 3. Exécuter
La logique s'exécute sur le serveur. Puisqu'il s'agit d'une fonction Python standard, vous pouvez utiliser n'importe quelle bibliothèque, accéder à la base de données ou appeler d'autres services. Vous pouvez également déclencher une actualisation de page en utilisant `revalidate()`.

### 4. Sérialiser
La valeur de retour est automatiquement sérialisée en JSON. Les modèles Pydantic sont gérés de manière native et les types Python standard sont mappés à leurs équivalents JSON.

### 5. Consommer
Le frontend reçoit le résultat avec une sécurité de type totale. Nexy écrit `__nexy__/src/actions.ts` à partir de vos signatures et `@nexy/actions` le résout.

<!-- router:fbr,custom -->
```tsx filename="src/routes/users.tsx"
import { useAction } from "@nexy/client";
import { create_user } from "@nexy/actions";

export default function NewUser() {
  const { run, pending, error, data } = useAction(create_user);

  return (
    <button disabled={pending} onClick={() => run({ name: "Ada" })}>
      {error ? error.message : data ? `Created ${data.name}` : "Create"}
    </button>
  );
}
```
<!-- /router -->

<!-- router:modular -->
Le composant est un îlot de la vue renvoyée par un contrôleur :

```tsx filename="src/components/NewUser.tsx"
import { useAction } from "@nexy/client";
import { create_user } from "@nexy/actions";

export function NewUser() {
  const { run, pending, error, data } = useAction(create_user);

  return (
    <button disabled={pending} onClick={() => run({ name: "Ada" })}>
      {error ? error.message : data ? `Created ${data.name}` : "Create"}
    </button>
  );
}
```

```nexy filename="src/apps/users/user_view.nexy"
---
from "@/components/NewUser.tsx" import NewUser
---
<NewUser directive="client:load" />
```
<!-- /router -->

Sans hook, une action n'est qu'une fonction `async` : `const user = await create_user({ name: "Ada" })`.

| Cadre | Ce que `useAction` renvoie |
|---|---|
| React, Preact | `{ pending, data, error, run, reset }` |
| Solid | la même chose, avec `pending()`, `data()` et `error()` comme accesseurs |
| Vue | le même, avec `pending`, `data` et `error` comme références |
| Svelte | un magasin : `$save.pending`, `$save.data`, `$save.error`, plus `save.run(input)` et `save.reset()` |

`useAction(action, { onSuccess, onError })` prend également deux rappels. `run` ne lance jamais : un échec atterrit dans `error` et `run` se résout avec `undefined`.

Les types proviennent de Python : `str` est `string`, `int` et `float` sont `number`, `list[T]` est `T[]`, un modèle Pydantic ou un `Enum` est un type nommé, et un champ avec une valeur par défaut est facultatif dans l'entrée. Un type que Pydantic ne peut pas décrire devient `unknown`.

## Erreurs et échecs

Une action peut échouer à différentes étapes. Vous devez les distinguer dans votre interface utilisateur :

1.  **Erreurs de validation (422)** : l'entrée ne correspondait pas à la signature Python. `error.fields` mappe chaque champ invalide à son message.
2.  **Erreurs commerciales (`HTTPException`)** : votre code a refusé l'appel, par exemple `403 Forbidden` ou `409 Conflict`.
3.  **Erreurs de serveur (500)** : une exception non gérée s'est produite dans votre code Python.
4.  **Erreurs réseau** : la requête n'est jamais parvenue au serveur, par exemple un timeout ou une perte de connexion.
5.  **Erreurs d'autorisation (401, 403)** : votre propre chèque a rejeté l'appelant. Nexy ne décide pas de cela à votre place.

Le contrôle d'origine décrit ci-dessous est une protection CSRF, pas une autorisation : il indique d'où vient l'appel, jamais qui est autorisé à le passer.

## Actualiser la page après une action

Une action indique quelles pages sa modification a rendues obsolètes, comme le fait Next.js avec `revalidatePath` :

```python
revalidate()            # the page that is open
revalidate("/users")    # that page, if it is the one open
```

La réponse comporte les chemins dans un en-tête `x-nexy-revalidate`. Le client récupère ensuite la page actuelle via le routeur ou la recharge lorsqu'il n'y a pas de routeur client.

## Formulaires sans JavaScript

Une action prend également une forme HTML standard, de sorte que la page fonctionne avant le chargement de tout script :

```html
<form method="post" action="{{ __actions_path['create_user'] }}">
  <input name="name">
  <button type="submit">Create</button>
</form>
```

Dans un modèle `.nexy`, `__actions_path["name"]` est le chemin, `__actions["name"]` la fonction, et la fonction est également dans la portée sous son propre nom.

En cas de succès, le visiteur est renvoyé vers la page sur laquelle se trouvait le formulaire, avec le statut `303`. Pour répondre différemment, renvoyez un objet `Response` (par exemple, `RedirectResponse("/done", status_code=303)`).

Un formulaire envoyé en `application/x-www-form-urlencoded`, ce que fait un navigateur par défaut, ne demande aucun paquet supplémentaire. Ajoutez `enctype="multipart/form-data"` et l'appel a besoin de `python-multipart` : sans lui, l'action répond `500` avec un message qui nomme la commande, `uv add python-multipart`.

Une action lit des champs, pas des fichiers : un champ fichier lui parvient sous forme de chaîne. Pour recevoir un envoi de fichier, écrivez une route dans `src/routes/api/` avec un paramètre `File` ou `UploadFile`.

## Sécurité

### L'obscurité du chemin n'est pas une autorisation
Le chemin de l'action est `/_nx_` suivi d'un hachage du module de la fonction, de son nom et d'un secret du projet. Il est défini par `NEXY_ACTION_SECRET`, ou conservé dans `__nexy__/action.key`, que `nx build` crée afin que le bundle client et `nx start` soient d'accord : conservez ce fichier avec la build. Le chemin cache le point de terminaison de toute découverte occasionnelle et **le chemin généré n'est pas un mécanisme d'autorisation**.

Quiconque connaît le chemin peut déclencher l'action. Vous **devez** vérifier l'identité et les autorisations de l'utilisateur dans l'action :
```python
@Action
async def delete_user(user_id: str, request: Request):
    if not request.state.user.is_admin:
        raise HTTPException(403, "Admin rights required")
    # ...
```

### Protection de l'origine
Pour éviter le Cross-Site Request Forgery (CSRF), Nexy refuse les requêtes dont `Origin` est un autre site ou que le navigateur marque `Sec-Fetch-Site: cross-site` avec un `403`. Listez les sites susceptibles d'appeler vos actions dans `NEXY_ALLOWED_ORIGINS`. Les appels sans `Origin` (comme `curl`) sont acceptés.

## Erreurs d'importation

Au démarrage, Nexy importe chaque module de `src/` pour retrouver les actions. Un module dont l'importation échoue est signalé, et les autres se chargent toujours :

```text
  x src.actions.billing: src/actions/billing.py:3  ModuleNotFoundError: No module named 'stripe'
```

## Prochaines étapes

- [API](../routing/fbr/handlers/README.md) : gestionnaires explicites
- [Tests](testing.md#what-to-assert) : comment tester une action
- [Configuration](../reference/config.md) : options de middleware et d'authentification
