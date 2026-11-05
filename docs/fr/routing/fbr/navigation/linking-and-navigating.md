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

| Accessoire | Signification |
|---|---|
| `href` | Un itinéraire du projet (une faute de frappe est une erreur de type), éventuellement avec `?query` ou `#fragment`, ou une URL externe. |
| `replace` | Remplacez l'entrée de l'historique au lieu d'en ajouter une. |
| `scroll` | `false` conserve la position de défilement après la navigation. Par défaut : `true`. |
| `prefetch` | `'intent'` (par défaut) charge la page au survol, au focus ou au toucher ; `'viewport'` lorsque le lien apparaît ; `false` jamais. |
| `activeClassName` | Ajouté à la classe alors que le lien pointe vers la page actuelle ou une page en dessous (`activeClass` dans Vue et Svelte). |
| `exact` | Actif uniquement sur la page exacte. |

Le lien qui pointe vers la page actuelle obtient également `aria-current="page"`.

## Crochets

L'emplacement est disponible dans chaque cadre, dans l'idiome de ce cadre. Au cours du premier, côté serveur, les hooks répondent avec l'URL de la requête, de sorte que la page s'hydrate sans décalage.

| | React, Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| Chemin | `usePathname()` | `usePathname()` renvoie un accesseur | `usePathname()` renvoie une référence | `$pathname` magasin |
| Paramètres de route | `useParams()` | `useParams()` accesseur | `useParams()` ref | `$params` magasin |
| Requête | `useSearchParams()` | `useSearchParams()` accesseur | `useSearchParams()` ref | `$searchParams` magasin |
| Tout | `useLocation()` | `useLocation()` accesseur | `useLocation()` ref | `$location` magasin |
| Naviguer | `useRouter()` | `useRouter()` | `useRouter()` | `router` |

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

`Link(href, children="", class_name=None, prefetch=True, **attrs)` restitue `<a href="/about" data-nexy-link="true">`. Chaque attribut et le `href` sont échappés en HTML.

## Ce que fait le routeur

Sur une navigation, le routeur :

1. fait correspondre le chemin avec les routes client (`.tsx`, `.jsx`, `.vue`, `.svelte`) ;
2. importe et restitue la page et ses [layouts](../layouts/README.md) **d'abord**, puis déplace ensuite l'URL avec `history.pushState`, de sorte que la barre d'adresse n'affiche jamais une page qui a échoué ;
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

- [Mise en page](../layouts/README.md)
- [RSE](../../../rendering/csr.md)
- [Composants](../../../views/nexy/components.md)
