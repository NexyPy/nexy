# Solid

Nexy restitue les composants Solid 1.9 sur le serveur, puis Solid les reprend dans le navigateur. Les pages, mises en page, îlots et actions sont les mêmes dans tous les frameworks : cette page couvre la configuration, puis les parties qui diffèrent des [contrats partagés](../frontend/pages.md).

<!-- router:fbr,custom -->
| Mode | `nexyconfig.py` | Les pages sont | Solid est |
|---|---|---|---|
| Serveur (par défaut) | `useCSR = False` | `.nexy` fichiers | [îles](../../rendering/islands.md) à l'intérieur de ces pages |
| Client | `useCSR = True` | `.tsx` fichiers | la page entière, avec [mises en page](../frontend/layouts.md) et un routeur client |
<!-- /router -->

<!-- router:modular -->
Avec le routeur modulaire, les composants Solid sont des [îlots](../../rendering/islands.md) à l'intérieur des `.nexy` vues renvoyées par un contrôleur : il n'y a pas de fichier d'échange ni de routeur client.
<!-- /router -->

## Démarrer un projet

<!-- router:fbr,custom -->
```bash
nx new my-app --template web-fbr-solid
```
<!-- /router -->

<!-- router:modular -->
```bash
nx new my-app --template web-modular-solid
```
<!-- /router -->

Le modèle est un projet en mode serveur avec Solid îles. Exécutez `nx new my-app` sans modèle pour répondre aux invites : le routeur, le type de projet, l'utilisation ou non du routage côté client, puis le framework.

## Activer Solid dans un projet existant

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import solid


class NexyConfig(NexyConfigModel):
    useFF = solid()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import solid from "vite-plugin-solid";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), solid()],
  customLogger: nexy.log(),
});
```

En mode client, écrivez `solid({ ssr: true })` : Solid compile un composant différemment pour le serveur et pour le navigateur, et le mode client a besoin des deux. `nx new` écrit ce fichier ; Nexy écrit lui-même `__nexy__/vite.ts`, alors ne le modifiez pas.

| Forfait | La version `nx new` écrit |
|---|---|
| `solid-js` | `^1.9.12` |
| `vite-plugin-solid` | `^2.11.0` (dépendance du développeur) |

## Pensez aux signaux

Une fonction de composant Solid s'exécute **une fois**. Ce qui change plus tard est lu via un signal, et seules les expressions qui le lisent sont mises à jour :

```tsx filename="src/components/Counter.tsx"
import { createSignal } from "solid-js";

export default function Counter(props: { start?: number }) {
  const [count, setCount] = createSignal(props.start ?? 0);
  return <button onClick={() => setCount(count() + 1)}>{count()}</button>;
}
```

- Appelez le signal, `count()`, à l'intérieur du JSX, pas dans une variable au-dessus.
- Lisez les accessoires comme `props.start`. La déstructuration `{ start }` lit la valeur une fois et perd les mises à jour.
- Solid écrit les attributs HTML : `class`, `for`, `charset`, et non `className`.

## Règles

- **Un framework par projet.** `useFF` prend exactement un framework ; `useFF = [solid(), react()]` arrête le serveur au démarrage. Avec `useFF = solid()`, chaque fichier `.tsx` est Solid.
<!-- router:fbr,custom -->
- **Les pages sont `.tsx`.** Seul un fichier `.tsx` sous `src/routes/` devient une page ; `.jsx` convient pour un composant.
- **Les composants se trouvent à l'extérieur de `src/routes/`**, généralement dans `src/components/`, ce ne sont donc pas des pages.
- **Un projet en mode serveur n'a pas de page `.tsx`**, et un projet en mode client n'a pas de page `.nexy` : Nexy refuse de démarrer et nomme le fichier. Voir [modes](../../routing/fbr/modes.md).
<!-- /router -->
<!-- router:modular -->
- **Les composants résident dans `src/components/`** et une vue les importe sous forme d'îlots.
<!-- /router -->
- **Non `.mdx` avec Solid.** MDX se compile en React ou Preact ; `.md` pages fonctionnent.

<!-- router:fbr,custom -->
## Pages

En mode client (`useCSR = True`), une page est un fichier `.tsx`.

### Composant de page

Une page est l'exportation par défaut du fichier. Si aucune exportation par défaut n'existe, Nexy sélectionne la première exportation nommée.

```tsx filename="src/routes/index.tsx"
export default function Home() {
  return <h1>Hello</h1>;
}
```

### Segments dynamiques

Les paramètres d'URL sont disponibles via le hook `useParams`, qui renvoie un accesseur :

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const params = useParams<{ slug: string }>();
  return <h1>{params().slug}</h1>;
}
```

## Mises en page

### Mise en œuvre

La disposition racine définit le shell du document. Les mises en page imbriquées enveloppent le contenu.

```tsx filename="src/routes/layout.tsx"
import type { JSX } from "solid-js";

export default function RootLayout(props: { children: JSX.Element }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{props.children}</main>
      </body>
    </html>
  );
}
```

Ne déstructurez pas `props.children`, comme Solid le lit paresseusement.
<!-- /router -->

## Îles

En mode serveur, un composant Solid importé dans un fichier `.nexy` est un îlot.

### Importation

Importez des composants dans le frontmatter du fichier `.nexy` :

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```
<!-- /router -->

### Directives d'hydratation

Utilisez l'accessoire `directive` pour contrôler le moment où l'île s'hydrate :

- `client:load` (par défaut) : immédiatement
- `client:idle` : lorsque le navigateur est inactif
- `client:visible` : lorsqu'il défile dans la vue
- `client:media` : lorsque la requête multimédia correspond

## Actions et navigation

### Appeler des actions

Utilisez le hook `useAction` pour gérer l'état d'un appel à l'action. Dans Solid, cela renvoie les accesseurs (appelez-les en tant que fonctions).

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const save = useAction(add_todo);
// ...
<button disabled={save.pending()}>Add</button>
```

### Navigation

Utilisez le composant `Link` pour les transitions côté client :

```tsx
import { Link } from "@nexy/client";

<Link href="/about">About</Link>
```

Pour la navigation par programmation, utilisez le hook `useRouter` :

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### Accès aux URL

Tous les hooks de localisation renvoient des accesseurs :

- `usePathname()` : chemin actuel
- `useParams()` : segments dynamiques
- `useSearchParams()` : chaîne de requête
- `useLocation()` : objet de localisation complet

## Prochaines étapes

- [Vues](../README.md) : comparez les formats qu'une page peut utiliser
- [Frontend](../../guides/frontend.md) : Vite et la build client
