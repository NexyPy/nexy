# Svelte

Nexy restitue Svelte 5 composants sur le serveur, puis Svelte les reprend dans le navigateur. Les pages, mises en page, îlots et actions sont les mêmes dans tous les frameworks : cette page couvre la configuration, puis les parties qui diffèrent des [contrats partagés](../frontend/pages.md).

<!-- router:fbr,custom -->
| Mode | `nexyconfig.py` | Les pages sont | Svelte est |
|---|---|---|---|
| Serveur (par défaut) | `useCSR = False` | `.nexy` fichiers | [îles](../../rendering/islands.md) à l'intérieur de ces pages |
| Client | `useCSR = True` | `.svelte` fichiers | la page entière, avec [mises en page](../frontend/layouts.md) et un routeur client |
<!-- /router -->

<!-- router:modular -->
Avec le routeur modulaire, les composants Svelte sont des [îlots](../../rendering/islands.md) à l'intérieur des `.nexy` vues renvoyées par un contrôleur : il n'y a pas de fichier d'échange ni de routeur client.
<!-- /router -->

## Démarrer un projet

<!-- router:fbr,custom -->
```bash
nx new my-app --template web-fbr-svelte
```
<!-- /router -->

<!-- router:modular -->
```bash
nx new my-app --template web-modular-svelte
```
<!-- /router -->

Le modèle est un projet en mode serveur avec Svelte îles. Exécutez `nx new my-app` sans modèle pour répondre aux invites : le routeur, le type de projet, l'utilisation ou non du routage côté client, puis le framework.

## Activer Svelte dans un projet existant

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), svelte()],
  customLogger: nexy.log(),
});
```

`nx new` écrit ce fichier ; Nexy écrit lui-même `__nexy__/vite.ts`, alors ne le modifiez pas.

| Forfait | La version `nx new` écrit |
|---|---|
| `svelte` | `^5.20.2` |
| `@sveltejs/vite-plugin-svelte` | `^5.0.0` |

## Règles

- **Svelte 5.** Les composants utilisent des runes : `$props()`, `$state()` et des extraits pour les enfants.
- **Un framework par projet.** `useFF` prend exactement un framework ; `useFF = [svelte(), vue()]` arrête le serveur au démarrage.
- **Un composant par fichier.** Le nom sous lequel vous importez un fichier `.svelte` est uniquement la balise que vous écrivez.
<!-- router:fbr,custom -->
- **Les composants se trouvent à l'extérieur de `src/routes/`**, généralement dans `src/components/`, ce ne sont donc pas des pages.
- **Un projet en mode serveur n'a pas de page `.svelte`**, et un projet en mode client n'a pas de page `.nexy` : Nexy refuse de démarrer et nomme le fichier. Voir [modes](../../routing/fbr/modes.md).
<!-- /router -->
<!-- router:modular -->
- **Les composants résident dans `src/components/`** et une vue les importe sous forme d'îlots.
<!-- /router -->

<!-- router:fbr,custom -->
## Pages

En mode client (`useCSR = True`), une page est un fichier `.svelte`.

### Composant de page

La page est le composant défini par le bloc de script du fichier `.svelte`.

```svelte filename="src/routes/index.svelte"
<script lang="ts">
</script>

<h1>Hello</h1>
```

### Segments dynamiques

Les paramètres d'URL atteignent la page en tant qu'accessoires via la rune `$props()` :

```svelte filename="src/routes/blog/[slug].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

Vous pouvez également utiliser le magasin `$params` de `@nexy/client` dans n'importe quel composant.

## Mises en page

### Mise en œuvre

La disposition racine définit le shell du document. Les mises en page imbriquées enveloppent le contenu à l'aide de l'extrait `children`.

```svelte filename="src/routes/layout.svelte"
<script lang="ts">
  import type { Snippet } from "svelte";
  let { children }: { children?: Snippet } = $props();
</script>

<html>
  <body>
    <header>My app</header>
    <main>{@render children?.()}</main>
  </body>
</html>
```
<!-- /router -->

## Îles

En mode serveur, un composant Svelte importé dans un fichier `.nexy` est un îlot.

### Importation

Importez des composants dans le frontmatter du fichier `.nexy` :

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.svelte" import Counter
---
<Counter start=3 />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.svelte" import Counter
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

Utilisez le hook `useAction` pour gérer l'état d'un appel à l'action. Dans Svelte, cela renvoie un magasin (lu avec `$`).

```svelte
<script lang="ts">
  import { useAction } from "@nexy/client";
  import { add_todo } from "@nexy/actions";

  let title = $state("");
  const save = useAction(add_todo, { onSuccess: () => (title = "") });
</script>

<form onsubmit={(e) => { e.preventDefault(); save.run({ title }); }}>
  <input bind:value={title} />
  <button disabled={$save.pending}>Add</button>
</form>
```

### Navigation

Utilisez le composant `Link` pour les transitions côté client :

```svelte
<script lang="ts">
  import Link from "@nexy/Link.svelte";
</script>

<Link href="/about" activeClass="active">About</Link>
```

Pour la navigation par programmation, utilisez l'objet `router` de `@nexy/client` :

```ts
import { router } from "@nexy/client";

router.push("/dashboard");
```

### Accès aux URL

Toutes les données de localisation sont fournies sous forme de magasins :

- `$pathname` : chemin actuel
- `$params` : segments dynamiques
- `$searchParams` : chaîne de requête
- `$location` : objet de localisation complet

## Prochaines étapes

- [Vues](../README.md) : comparez les formats qu'une page peut utiliser
- [Frontend](../../guides/frontend.md) : Vite et le build client
