# Vue

Nexy rendert Vue 3 Einzeldateikomponenten auf dem Server und übernimmt sie dann Vue im Browser. Seiten, Layouts, Inseln und Aktionen sind in jedem Framework gleich: Auf dieser Seite geht es um die Einrichtung und dann um die Teile, die sich von den [gemeinsamen Verträgen](../frontend/pages.md) unterscheiden.

| Modus | `nexyconfig.py` | Seiten sind | Vue ist |
|---|---|---|---|
| Server (Standard) | `useCSR = False` | `.nexy` Dateien | [Inseln](../../rendering/islands.md) innerhalb dieser Seiten |
| Der Client | `useCSR = True` | `.vue` speichert die gesamte Seite | mit [Layouts](../frontend/layouts.md) und einem Client-Router |

## Starten Sie ein Projekt

```bash
nx new my-app --template web-fbr-vue
```

Die Vorlage ist ein Servermodus-Projekt mit Vue Inseln. Führen Sie stattdessen `nx new my-app` ohne Vorlage aus, um die Eingabeaufforderungen zu beantworten: den Router, den Projekttyp, ob clientseitiges Routing verwendet werden soll, dann das Framework.

## Aktivieren Sie Vue in einem vorhandenen Projekt

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

`nx new` schreibt diese Datei; Nexy schreibt `__nexy__/vite.ts` selbst, also bearbeiten Sie es nicht.

| Paket | Version `nx new` schreibt |
|---|---|
| `vue` | `^3.5.33` |
| `@vitejs/plugin-vue` | `^6.0.0` |

## Regeln

- **Ein Framework pro Projekt.** `useFF` benötigt genau ein Framework; `useFF = [vue(), react()]` stoppt den Server beim Start.
- **Eine Komponente pro Datei.** Eine `.vue`-Datei exportiert ihre Komponente standardmäßig; Der Name, unter dem Sie es importieren, ist nur das Tag, das Sie schreiben.
- **Komponenten befinden sich außerhalb von `src/routes/`**, normalerweise in `src/components/`, daher sind sie keine Seiten.
- **Ein Servermodus-Projekt hat keine `.vue` Seite**, und ein Clientmodus-Projekt hat keine `.nexy` Seite: Nexy weigert sich zu starten und benennt die Datei. Siehe [Modi](../../routing/fbr/modes.md).

## Seiten

Im Client-Modus (`useCSR = True`) ist eine Seite eine `.vue`-Datei.

### Seitenkomponente

Die Seite ist die durch den Block `<script setup>` definierte Komponente.

```vue filename="src/routes/index.vue"
<template>
  <h1>Hello</h1>
</template>
```

### Dynamische Segmente

URL-Parameter gelangen als Requisiten auf die Seite. Sie können sie mit `defineProps` deklarieren:

```vue filename="src/routes/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

Alternativ können Sie den Hook `useParams` von `@nexy/client` in einer beliebigen Komponente verwenden.

## Layouts

### Umsetzung

Das Root-Layout definiert die Dokumenthülle. Verschachtelte Layouts umschließen den Inhalt in ihrem Standard-Slot.

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

## Inseln

Im Servermodus ist eine in eine `.nexy`-Datei importierte Vue-Komponente eine Insel.

### Importieren

Importieren Sie Komponenten in die Frontmatter der Datei `.nexy`:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.vue" import Counter
---
<Counter start=3 />
```

### Trinkrichtlinien

Verwenden Sie die Requisite `directive`, um zu steuern, wann die Insel hydratisiert:

- `client:load` (Standard): sofort
- `client:idle`: wenn der Browser inaktiv ist
- `client:visible`: wenn es in die Ansicht scrollt
- `client:media`: wenn die Medienabfrage übereinstimmt

## Aktionen und Navigation

### Aktionen aufrufen

Verwenden Sie den Hook `useAction`, um den Status eines Aktionsaufrufs zu verwalten. In Vue sind die zurückgegebenen Zustände (`pending`, `data`, `error`) berechnete Referenzen.

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

Verwenden Sie die Komponente `Link` für clientseitige Übergänge:

```vue
<template>
  <Link href="/about" active-class="active">About</Link>
</template>
```

Verwenden Sie für die programmatische Navigation den Hook `useRouter`:

```ts
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### URL-Zugriff

Alle Standort-Hooks geben berechnete Referenzen zurück:

- `usePathname()`: aktueller Pfad
- `useParams()`: dynamische Segmente
- `useSearchParams()`: Abfragezeichenfolge
- `useLocation()`: vollständiges Standortobjekt

## Nächste Schritte

- [Ansichten](../README.md): Vergleichen Sie die Formate, die eine Seite verwenden kann
- [Frontend](../../guides/frontend.md): Vite und der Client-Build
