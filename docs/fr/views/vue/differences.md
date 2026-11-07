# Vue

Nexy restitue Vue 3 composants mono-fichier sur le serveur, puis Vue les reprend dans le navigateur. Les pages, mises en page, îlots et actions sont les mêmes dans tous les frameworks : cette page couvre la configuration, puis les parties qui diffèrent des [contrats partagés](../frontend/pages.md).

<!-- router:fbr,custom -->
| Mode | `nexyconfig.py` | Les pages sont | Vue est |
|---|---|---|---|
| Serveur (par défaut) | `useCSR = False` | `.nexy` fichiers | [îles](../../rendering/islands.md) à l'intérieur de ces pages |
| Client | `useCSR = True` | `.vue` fichiers | la page entière, avec [mises en page](../frontend/layouts.md) et un routeur client |
<!-- /router -->

<!-- router:modular -->
Avec le routeur modulaire, les composants Vue sont des [îlots](../../rendering/islands.md) à l'intérieur des `.nexy` vues renvoyées par un contrôleur : il n'y a pas de fichier d'échange ni de routeur client.
<!-- /router -->

## Démarrer un projet

<!-- router:fbr,custom -->
```bash
nx new my-app --template web-fbr-vue
```
<!-- /router -->

<!-- router:modular -->
```bash
nx new my-app --template web-modular-vue
```
<!-- /router -->

Le modèle est un projet en mode serveur avec Vue îles. Exécutez `nx new my-app` sans modèle pour répondre aux invites : le routeur, le type de projet, l'utilisation ou non du routage côté client, puis le framework.

## Activer Vue dans un projet existant

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), vue()],
  customLogger: nexy.log(),
});
```

`nx new` écrit ce fichier ; Nexy écrit lui-même `__nexy__/vite.ts`, alors ne le modifiez pas.

| Forfait | La version `nx new` écrit |
|---|---|
| `vue` | `^3.5.33` |
| `@vitejs/plugin-vue` | `^6.0.0` |

## Règles

- **Un framework par projet.** `useFF` prend exactement un framework ; `useFF = [vue(), react()]` arrête le serveur au démarrage.
- **Un composant par fichier.** Un fichier `.vue` exporte son composant par défaut ; le nom sous lequel vous l'importez est uniquement la balise que vous écrivez.
<!-- router:fbr,custom -->
- **Les composants se trouvent à l'extérieur de `src/routes/`**, généralement dans `src/components/`, ce ne sont donc pas des pages.
- **Un projet en mode serveur n'a pas de page `.vue`**, et un projet en mode client n'a pas de page `.nexy` : Nexy refuse de démarrer et nomme le fichier. Voir [modes](../../routing/fbr/modes.md).
<!-- /router -->
<!-- router:modular -->
- **Les composants résident dans `src/components/`** et une vue les importe sous forme d'îlots.
<!-- /router -->

<!-- router:fbr,custom -->
## Pages

En mode client (`useCSR = True`), une page est un fichier `.vue`.

### Composant de page

La page est le composant défini par le bloc `<script setup>`.

```vue filename="src/routes/index.vue"
<template>
  <h1>Hello</h1>
</template>
```

### Segments dynamiques

Les paramètres d'URL atteignent la page en tant qu'accessoires. Vous pouvez les déclarer en utilisant `defineProps` :

```vue filename="src/routes/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

Vous pouvez également utiliser le hook `useParams` de `@nexy/client` dans n'importe quel composant.

## Mises en page

### Mise en œuvre

La disposition racine définit le shell du document. Les mises en page imbriquées enveloppent le contenu dans leur emplacement par défaut.

```vue filename="src/routes/layout.vue"
<template>
  <html>
    <body>
      <header>My app</header>
      <main><slot /></main>
    </body>
  </html>
</template>
```
<!-- /router -->

## Îles

En mode serveur, un composant Vue importé dans un fichier `.nexy` est un îlot.

### Importation

Importez des composants dans le frontmatter du fichier `.nexy` :

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.vue" import Counter
---
<Counter start=3 />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.vue" import Counter
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

Utilisez le hook `useAction` pour gérer l'état d'un appel à l'action. Dans Vue, les états renvoyés (`pending`, `data`, `error`) sont des références calculées.

```vue
<script setup lang="ts">
import { ref } from "vue";
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const title = ref("");
const { run, pending, error, data } = useAction(add_todo, {
  onSuccess: () => (title.value = ""),
});
</script>

<template>
  <form @submit.prevent="run({ title })">
    <input v-model="title" />
    <button :disabled="pending">Add</button>
  </form>
</template>
```

### Navigation

Utilisez le composant `Link` pour les transitions côté client :

```vue
<template>
  <Link href="/about" active-class="active">About</Link>
</template>
```

Pour la navigation par programmation, utilisez le hook `useRouter` :

```ts
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### Accès aux URL

Tous les hooks de localisation renvoient des références calculées :

- `usePathname()` : chemin actuel
- `useParams()` : segments dynamiques
- `useSearchParams()` : chaîne de requête
- `useLocation()` : objet de localisation complet

## Prochaines étapes

- [Vues](../README.md) : comparez les formats qu'une page peut utiliser
- [Frontend](../../guides/frontend.md) : Vite et la build client
