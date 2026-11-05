# Vue

Nexy restitue Vue 3 composants mono-fichier sur le serveur, puis Vue les reprend dans le navigateur. Les pages, mises en page, îlots et actions sont les mêmes dans tous les frameworks : cette page couvre la configuration, puis les parties qui diffèrent des [contrats partagés](../frontend/pages.md).

| Mode | `nexyconfig.py` | Les pages sont | Vue est |
|---|---|---|---|
| Serveur (par défaut) | `useCSR = False` | `.nexy` fichiers | [îles](../../rendering/islands.md) à l'intérieur de ces pages |
| Le client | `useCSR = True` | `.vue` classe | la page entière, avec des [layouts](../frontend/layouts.md) et un routeur client |

## Démarrer un projet

```bash
nx new my-app --template web-fbr-vue
```

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

| Le package | Version `nx new` écrit |
|---|---|
| `vue` | `^3.5.33` |
| `@vitejs/plugin-vue` | `^6.0.0` |

## Règles

- **One framework per project.** `useFF` takes exactly one framework; `useFF = [vue(), react()]` arrête le serveur au démarrage.
- **Un composant par fichier.** Un fichier `.vue` exporte son composant par défaut ; le nom sous lequel vous l'importez est uniquement la balise que vous écrivez.
- **Les composants se trouvent à l'extérieur de `src/routes/`**, généralement dans `src/components/`, ce ne sont donc pas des pages.
- **A server-mode project has no `.vue` page**, and a client-mode project has no `.nexy` page: Nexy refuses to start and names the file. Voir [modes](../../routing/fbr/modes.md).

## Pages

In client mode (`useCSR = True`), a page is a `.vue` file.

### Composant de page

The page is the component defined by the `<script setup>` block.

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

Alternatively, use the `useParams` hook from `@nexy/client` in any component.

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

## Îles

In server mode, a Vue component imported into a `.nexy` file is an island.

### Importation

Importez des composants dans le frontmatter du fichier `.nexy` :

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.vue" import Counter
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

Use the `useAction` hook to manage the state of an action call. In Vue, the returned state (`pending`, `data`, `error`) are computed refs.

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

Use the `Link` component for client-side transitions:

```vue
<template>
  <Link href="/about" active-class="active">About</Link>
</template>
```

For programmatic navigation, use the `useRouter` hook:

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

- [Views](../README.md): compare the formats a page can use
- [Frontend](../../guides/frontend.md) : Vite et la build client
