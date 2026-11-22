# Liens et navigation

Avec le routage client (`useCSR = True`), un lien entre deux pages permute la page dans le navigateur au lieu de recharger le document. Les mises en page conservent leur état.

## Les liens simples fonctionnent déjà

Chaque `<a href>` vers une page de votre projet navigue sur le client, sans composant ni marqueur :

```html
<a href="/about">About</a>
```

Un lien est laissé au navigateur, et charge la page normalement, lorsque :

- une touche de modification est maintenue enfoncée, ou le bouton n'est pas le bouton principal ;
- il a `target` (autre que `_self`), `download`, `rel="external"` ou `data-nexy-reload` ;
- le `href` est une autre origine, un lien `mailto:` ou `tel:`, ou seulement un `#fragment` ;
- le chemin ne correspond à aucune route client, donc le serveur y répond.

## `Link`

`Link` est la même ancre avec ce qu'une simple ancre ne peut pas faire : son `href` est vérifié par rapport à vos itinéraires, il réchauffe la page cible et il sait quand il pointe vers la page en cours. Nexy génère le `Link` de votre framework dans `__nexy__/src` lorsque vous exécutez `nx dev` ou `nx build`.

| Cadre | Importer |
|---|---|
| React, Preact, Solid, Vue | `import { Link } from "@nexy/client"` |
| Svelte | `import Link from "@nexy/Link.svelte"` |

```tsx
import { Link } from "@nexy/client";

export default function Nav() {
  return (
    <Link href="/dashboard" activeClassName="on">
      Dashboard
    </Link>
  );
}
```

| Prop | Signification |
|---|---|
| `href` | Un itinéraire du projet (une faute de frappe est une erreur de type), éventuellement avec `?query` ou `#fragment`, ou une URL externe. |
| `replace` | Remplacez l’entrée de l’historique au lieu d’en ajouter une. |
| `scroll` | `false` conserve la position de défilement après la navigation. Par défaut : `true`. |
| `prefetch` | `'intent'` (par défaut) charge la page au survol, au focus ou au toucher ; `'viewport'` lorsque le lien défile vers l'écran ; `false` jamais. |
| `activeClassName` | Ajouté à la classe lorsque le lien pointe vers la page actuelle ou une page en dessous (`activeClass` dans Vue et Svelte). |
| `exact` | Actif uniquement sur la page exacte. |

Le lien qui pointe vers la page actuelle obtient également `aria-current="page"`.

## Crochets

L'emplacement est disponible dans chaque cadre, dans l'idiome de ce cadre. Au cours du premier, côté serveur, les hooks répondent avec l'URL de la requête, de sorte que la page s'hydrate sans décalage.

| | React, Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| Chemin | `usePathname()` | `usePathname()` renvoie un accesseur | `usePathname()` renvoie une référence | `$pathname` magasin |
| Paramètres d'itinéraire | `useParams()` | `useParams()` accesseur | `useParams()` réf | `$params` magasin |
| Requête | `useSearchParams()` | `useSearchParams()` accesseur | `useSearchParams()` réf | `$searchParams` magasin |
| Tout | `useLocation()` | `useLocation()` accesseur | `useLocation()` réf | `$location` magasin |
| Naviguer | `useRouter()` | `useRouter()` | `useRouter()` | `router` |
| Navigation en vol | `useTransition()` | `useTransition()` accesseur | `useTransition()` réf | `useTransition()` magasin |
| Faire correspondre un chemin | `useMatch(path?)` | `useMatch(path?)` accesseur | `useMatch(path?)` réf | `useMatch(path?)` magasin |
| Demander avant de partir | `useBlocker(dirty)` | `useBlocker(dirty())` dans `createEffect` | `useBlocker(dirtyRef)` | `useBlocker(dirty)` dans `$effect` |

La requête est un `URLSearchParams`. `useRouter()` et `router` donnent `push(href)`, `replace(href)`, `back()`, `forward()`, `refresh()` et `prefetch(href)` ; `push` et `replace` acceptent `{ scroll: false }`.

```tsx
import { useParams, useRouter, useSearchParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  const tab = useSearchParams().get("tab") ?? "profile";
  const router = useRouter();
  return <button onClick={() => router.push(`/users/${id}?tab=posts`)}>{tab}</button>;
}
```

## Afficher un état de chargement avec `useTransition`

`useTransition()` indique si un client de navigation est en vol. `pending` est `true` à partir du clic jusqu'à ce que la page suivante soit affichée, et `next` est l'emplacement vers lequel il va. Il remonte à `{ pending: false, next: null }` une fois la page affichée, lorsque la navigation s'arrête ou lorsqu'une plus récente la remplace.

```tsx
import { useTransition } from "@nexy/client";

export default function Progress() {
  const { pending, next } = useTransition();
  return pending ? <p role="status">Loading {next?.pathname}</p> : null;
}
```

## Faites correspondre un chemin avec `useMatch`

`useMatch(path)` indique si `path` correspond à une route client. Il renvoie `{ match, found }`, où `match` contient la route `file`, son `layouts` et son `params`, ou est `null`. Sans chemin, il correspond à la page actuelle et suit chaque navigation. Pendant le rendu du serveur, il n'y a pas encore de routeur, donc `match` est `null` et `found` est `false`.

```tsx
import { useMatch } from "@nexy/client";

export default function Breadcrumb() {
  const { match } = useMatch();
  return match?.params.id ? <span>User {match.params.id}</span> : null;
}
```

## Attrapez une page qui échoue avec `ErrorBoundary`

`ErrorBoundary` affiche une solution de repli à la place de ses enfants lorsque l'un d'eux lance un lancer pendant le rendu dans le navigateur. La solution de secours reçoit l'erreur et `reset`, ce qui restitue à nouveau les enfants.

| Cadre | Importer | Repli |
|---|---|---|
| React, Preact, Solid | `import { ErrorBoundary } from "@nexy/client"` | `fallback={(error, reset) => ...}` |
| Vue | `import { ErrorBoundary } from "@nexy/client"` | une fonction `fallback` prop ; les enfants vont dans l'emplacement par défaut |
| Svelte | `import ErrorBoundary from "@nexy/ErrorBoundary.svelte"` | un extrait de `fallback` |

```tsx
import { ErrorBoundary } from "@nexy/client";

<ErrorBoundary fallback={(error, reset) => <button onClick={reset}>{error.message}: retry</button>}>
  <Dashboard />
</ErrorBoundary>
```

```svelte
<ErrorBoundary>
  {#snippet fallback(error, reset)}
    <button onclick={reset}>{error.message}: retry</button>
  {/snippet}
  <Dashboard />
</ErrorBoundary>
```

Il n'attrape pas :

- une erreur générée plus tard, dans un gestionnaire d'événements, un timer ou une promesse : détectez-la là où elle se produit. Vue est l'exception pour ses propres gestionnaires d'événements, dont les erreurs atteignent la limite ;
- une page que le routeur ne peut pas charger : le navigateur la demande au serveur (voir [Ce que fait le routeur](#what-the-router-does)).

## Demander avant de quitter une page avec des modifications non enregistrées

`useBlocker(dirty, message?)` demande au visiteur avant son départ alors que `dirty` est vrai : un lien, un `router.push`, les boutons Précédent et Suivant, un rechargement et un onglet fermé. Une navigation client affiche `message` dans `confirm()` : oui continue, non reste sur la page. Un rechargement ou un onglet fermé affiche la propre question du navigateur, qu'aucune page ne peut formuler. Sans message, la question est « Vous avez des modifications non enregistrées. Quitter cette page ? ».

```tsx
import { useState } from "react";
import { useBlocker } from "@nexy/client";

export default function Editor() {
  const [text, setText] = useState("");
  const [saved, setSaved] = useState("");
  useBlocker(text !== saved, "Your draft is not saved. Leave anyway?");
  return (
    <form onSubmit={(event) => (event.preventDefault(), setSaved(text))}>
      <textarea value={text} onChange={(event) => setText(event.target.value)} />
      <button>Save</button>
    </form>
  );
}
```

Le drapeau se lit là où il change, dans le langage de chaque framework :

| Cadre | Suivez le drapeau |
|---|---|
| React, Preact | `useBlocker(dirty)` sur chaque rendu |
| Vue | `useBlocker(dirty)` avec `dirty` une référence ou un calcul |
| Solid | `createEffect(() => useBlocker(dirty()))` |
| Svelte | `$effect(() => useBlocker(dirty))` |

`useBlocker` assume également une fonction, pour une décision qui dépend de l'endroit où se rend le visiteur. Il reçoit l'emplacement suivant et l'emplacement actuel, et renvoie une raison (une chaîne) pour rester, ou rien pour continuer :

```tsx
useBlocker((next) => (next.pathname.startsWith("/admin") ? "Admins only" : undefined));
```

Une fonction ne demande pas toute seule et ne tient pas de rechargement ; appelez `confirm()` pour demander.

## `Image`

`Image` rend un `<img>` qui est paresseux par défaut et ne décale pas la mise en page lorsque sa taille est connue.

| Cadre | Importer |
|---|---|
| React, Preact, Solid, Vue | `import { Image } from "@nexy/client"` |
| Svelte | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` est requis ; utilisez `alt=""` pour une image décorative. Nexy prévient une fois lorsqu'il manque.
- Avec `width` et `height`, les attributs donnent au navigateur le rapport hauteur/largeur et l'image reste fluide (`height: auto; max-width: 100%`).
- `priority` charge désormais l'image en haute priorité, pour celle qui est visible à l'arrivée.
- `fill` fait que l'image recouvre son parent positionné, en ignorant `width` et `height`.
- `sizes` et `srcSet` passent. Nexy ne redimensionne ni ne convertit les images.

## Lien depuis une page `.nexy`

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` rend `<a href="/about" data-nexy-link="true">`. Chaque attribut et le `href` sont échappés en HTML.

## Ce que fait le routeur

Sur une navigation, le routeur :

1. fait correspondre le chemin avec les routes client (`.tsx`, `.jsx`, `.vue`, `.svelte`) ;
2. importe et restitue la page et ses [mises en page](../layouts/README.md) **d'abord**, puis déplace ensuite l'URL avec `history.pushState`, de sorte que la barre d'adresse n'affiche jamais une page qui a échoué ;
3. distribue un événement `nexy:navigated` sur `document` ;
4. fait défiler vers le haut ou vers la cible `#fragment`.

Une navigation plus récente annule une navigation plus ancienne qui est toujours en cours de rendu. Si une page ne peut pas s'afficher, le navigateur la demande au serveur à la place. Les boutons Précédent et Suivant affichent la page de cette entrée et restaurent sa position de défilement.

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

Le routeur démarre uniquement dans un projet avec des routes client, donc un projet rendu par le serveur conserve le bouton de retour et la restauration du défilement du navigateur.

## Prochaines étapes

- [Mises en page](../layouts/README.md)
- [RSE](../../../rendering/csr.md)
- [Composants](../../../views/nexy/components.md)
