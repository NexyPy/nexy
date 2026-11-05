# React

Nexy restitue React 19 composants sur le serveur, puis React les hydrate dans le navigateur. Les pages, mises en page, îlots et actions sont les mêmes dans tous les frameworks : cette page couvre la configuration, puis les parties qui diffèrent des [contrats partagés](../frontend/pages.md).

| Mode | `nexyconfig.py` | Les pages sont | React est |
|---|---|---|---|
| Serveur (par défaut) | `useCSR = False` | `.nexy` fichiers | [îles](../../rendering/islands.md) à l'intérieur de ces pages |
| Le client | `useCSR = True` | `.tsx` classe | la page entière, avec des [layouts](../frontend/layouts.md) et un routeur client |

## Démarrer un projet

```bash
nx new my-app --template web-fbr-react
```

Le modèle est un projet en mode serveur avec React îles. Exécutez `nx new my-app` sans modèle pour répondre aux invites : le routeur, le type de projet, l'utilisation ou non du routage côté client, puis le framework.

## Activer React dans un projet existant

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), react()],
  customLogger: nexy.log(),
});
```

`nx new` écrit ce fichier ; Nexy écrit lui-même `__nexy__/vite.ts`, alors ne le modifiez pas.

| Le package | Version `nx new` écrit |
|---|---|
| `react`, `react-dom` | `^19.2.5` |
| `@vitejs/plugin-react` | `^5.2.0` |
| `@types/react`, `@types/react-dom` | dépendances de développement |

## Règles

- **Un framework par projet.** `useFF` prend exactement un framework ; `useFF = [react(), vue()]` arrête le serveur au démarrage.
- **Les pages sont `.tsx`.** React possède `.tsx` et `.jsx` pour les composants, mais seul un fichier `.tsx` sous `src/routes/` devient une page.
- **Les composants se trouvent à l'extérieur de `src/routes/`**, généralement dans `src/components/`, ce ne sont donc pas des pages.
- **Un projet en mode serveur n'a pas de page `.tsx`**, et un projet en mode client n'a pas de page `.nexy` : Nexy refuse de démarrer et nomme le fichier. Voir [modes](../../routing/fbr/modes.md).

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

Les paramètres d'URL sont disponibles via le hook `useParams` :

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

## Mises en page

### Mise en œuvre

La disposition racine définit le shell du document. Les mises en page imbriquées enveloppent le contenu en dessous d'elles.

```tsx filename="src/routes/layout.tsx"
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
```

## Îles

En mode serveur, un composant React importé dans un fichier `.nexy` est un îlot.

### Importation

Importez des composants dans le frontmatter du fichier `.nexy` :

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```

### Directives d'hydratation

Utilisez l'accessoire `directive` pour contrôler le moment où l'île s'hydrate :

- `client:load` (par défaut) : immédiatement
- `client:idle` : lorsque le navigateur est inactif
- `client:visible` : lorsqu'il défile dans la vue
- `client:media` : lorsque la requête multimédia correspond

## Actions et navigation

### Appeler des actions

Utilisez le hook `useAction` pour gérer l'état d'un appel à l'action :

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const { run, pending, error, data } = useAction(add_todo);
// ...
<button onClick={() => run({ title: "New Task" })}>Add</button>
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

- `usePathname()` : chemin actuel
- `useParams()` : segments dynamiques
- `useSearchParams()` : chaîne de requête
- `useLocation()` : objet de localisation complet

## Prochaines étapes

- [Vues](../README.md) : comparez les formats qu'une page peut utiliser
- [Frontend](../../guides/frontend.md) : Vite et le build client
