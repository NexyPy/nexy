# Îles et hydratation

## Définition

Un îlot est un composant client - React, Vue, Svelte, Solid ou Preact - importé dans une page `.nexy`. Le serveur restitue son HTML ; le navigateur rend ce composant interactif. Le reste de la page reste HTML.

Les îles existent en mode serveur. En mode client les composants *sont* les pages : voir [CSR](csr.md).

## Comment ça marche

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter directive="client:visible" />
```

Nexy restitue le composant au moment de la construction, stocke son HTML et le place à l'intérieur de la page. La réponse de la page contient ce code HTML ainsi que les accessoires en tant qu'attribut JSON. Dans le navigateur, le runtime de l'îlot charge le composant et prend en charge le conteneur.

`directive` décide **quand** cela se produit. Sans cela, l'île s'hydrate dès que son exécution est prête.

## Cycle de vie du rendu

1. Lors de la construction, chaque composant client est rendu au format HTML et écrit sous `__nexy__/client/static/`.
2. Une requête affiche la page `.nexy` ; le HTML de l'île est inséré à la place de la balise.
3. La réponse contient le code HTML, les accessoires et la directive comme attributs.
4. Dans le navigateur, le runtime planifie l'hydratation selon la directive.
5. Hydration remplace le HTML statique par le composant dynamique ; le reste de la page est intact.

En développement, il n'y a pas d'instantané de construction : le conteneur est vide et le composant s'affiche dans le navigateur. La page est la même, mais la première peinture diffère de la production.

## Quand utiliser

- Une page principalement composée de contenu et comportant un ou deux spots interactifs.
- Un widget qui doit exister dans le HTML pour les robots et toujours fonctionner.
- Un composant qui nécessite le navigateur mais ne doit pas faire glisser la page entière vers le rendu client.

## Configuration

| Directive | Hydrates |
|---|---|
| aucun, ou `client:load` | immédiatement |
| `client:idle` | lorsque le navigateur est inactif (`requestIdleCallback`, délai d'attente de 2 s) |
| `client:visible` | lorsque l'île entre dans la fenêtre, 200 px plus tôt |
| `client:media` | lorsqu'une requête multimédia correspond ; définissez-le avec le accessoire `media` |

```nexy
<Chart directive="client:media" media="(min-width: 768px)" />
```

`client:media` est par défaut `(min-width: 768px)` lorsque `media` est absent et s'hydrate une fois. Sur un navigateur sans `IntersectionObserver`, `client:visible` revient en veille.

`directive` et `media` sont consommés par Nexy : ils ne sont pas transmis à votre composant.

## Exemple

```tsx filename="src/components/Counter.tsx"
import { useState } from "react"

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Count</h1>
<Counter start=3 directive="client:idle" />
```

## Limites

- **`client:only` ne s'hydrate jamais.** Il est accepté, mais le runtime l'ignore, donc le HTML du serveur reste inerte. Utilisez une route client ([CSR](csr.md)) lorsqu'un composant ne peut pas être rendu sur le serveur.
- **`client:manual` n'a pas de déclencheur public.** Il est également ignoré automatiquement et le handle qui le reprend est interne.
- **Les accessoires doivent être JSON.** Ils sont sérialisés avec `json.dumps`; une valeur qui ne peut pas être sérialisée est supprimée et l'îlot reçoit `{}` - silencieusement.
- **Une île n'est pas un composant client avec un état partagé.** Deux îles ne partagent pas d'état sans un mécanisme que vous ajoutez vous-même.
- **L'île n'est pas restituée par le serveur.** Son HTML est l'instantané de construction, plus tout ce que fait le composant une fois hydraté.
- **Une page d'îles est une page CSR déguisée.** Si chaque bloc doit communiquer entre eux, choisissez plutôt le mode client.

## Prochaines étapes

- [Rendu](README.md) : les quatre modes
- [Composants](../views/nexy/components.md) : comment une page `.nexy` en importe un
- [React](../views/react/differences.md), [Vue](../views/vue/differences.md), [Svelte](../views/svelte/differences.md), [Solid](../views/solid/differences.md), [Preact](../views/preact/differences.md)
