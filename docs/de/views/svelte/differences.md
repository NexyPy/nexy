# Schlank

Nexy rendert Svelte 5-Komponenten auf dem Server, dann übernimmt Svelte sie im Browser. Seiten,
Layouts, Inseln und Aktionen sind in jedem Framework gleich: Auf dieser Seite geht es um die Einrichtung und dann um die Teile
die von den [gemeinsamen Verträgen](../frontend/pages.md) abweichen.

| Modus | `nexyconfig.py` | Seiten sind | Svelte ist |
|---|---|---|---|
| Server (Standard) | `useCSR = False` | `.nexy` Dateien | [Inseln](../../rendering/islands.md) innerhalb dieser Seiten |
| Client | `useCSR = True` | `.svelte` Dateien | die gesamte Seite, mit [Layouts](../frontend/layouts.md) und einem Client-Router |

## Starten Sie ein Projekt

```bash
nx new my-app --template web-fbr-svelte
```

Die Vorlage ist ein Servermodus-Projekt mit Svelte-Inseln. Führen Sie `nx new my-app` ohne Vorlage aus
Beantworten Sie stattdessen die Eingabeaufforderungen: den Router, den Projekttyp, ob clientseitiges Routing verwendet werden soll
der Rahmen.

## Aktivieren Sie Svelte in einem vorhandenen Projekt

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

`nx new` schreibt diese Datei; Nexy schreibt `__nexy__/vite.ts` selbst, also bearbeiten Sie es nicht.

| Paket | Version `nx new` schreibt |
|---|---|
| `svelte` | `^5.20.2` |
| `@sveltejs/vite-plugin-svelte` | `^5.0.0` |

## Regeln

- **Svelte 5.** Komponenten verwenden Runen: `$props()`, `$state()` und Schnipsel für Kinder.
- **Ein Framework pro Projekt.** `useFF` benötigt genau ein Framework; `useFF = [svelte(), vue()]`
  Stoppt den Server beim Start.
- **Eine Komponente pro Datei.** Der Name, unter dem Sie eine `.svelte` Datei importieren, ist nur das Tag, das Sie schreiben.
- **Komponenten befinden sich außerhalb von `src/routes/`**, normalerweise in `src/components/`, also sind sie keine Seiten.
- **Ein Projekt im Servermodus hat keine `.svelte` Seite**, und ein Projekt im Clientmodus hat keine `.nexy` Seite: Nexy
  weigert sich zu starten und benennt die Datei. Siehe [Modi](../../routing/fbr/modes.md).

## Seiten

Im Client-Modus (`useCSR = True`) ist eine Seite eine `.svelte`-Datei.

### Seitenkomponente

Die Seite ist die Komponente, die durch den Skriptblock der Datei `.svelte` definiert wird.

```svelte filename="src/routes/index.svelte"
<script lang="ts">
</script>

<h1>Hello</h1>
```

### Dynamische Segmente

URL-Parameter gelangen als Requisiten über die Rune `$props()` auf die Seite:

```svelte filename="src/routes/blog/[slug].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

Alternativ können Sie den Speicher `$params` von `@nexy/client` in einer beliebigen Komponente verwenden.

## Layouts

### Implementierung

Das Root-Layout definiert die Dokumenthülle. Verschachtelte Layouts umschließen den Inhalt mit dem `children`
Ausschnitt.

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

## Inseln

Im Servermodus ist eine in eine `.nexy`-Datei importierte Svelte-Komponente eine Insel.

### Importieren

Importieren Sie Komponenten in die Frontmatter der Datei `.nexy`:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.svelte" import Counter
---
<Counter start=3 />
```

### Hydrationsanweisungen

Verwenden Sie die Requisite `directive`, um zu steuern, wann die Insel hydratisiert:

- `client:load` (Standard): sofort
- `client:idle`: wenn der Browser inaktiv ist
- `client:visible`: wenn es in die Ansicht scrollt
- `client:media`: wenn die Medienabfrage übereinstimmt

## Aktionen und Navigation

### Aktionen aufrufen

Verwenden Sie den Hook `useAction`, um den Status eines Aktionsaufrufs zu verwalten. In Svelte gibt dies einen Store zurück (read
mit `$`).

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

Verwenden Sie die Komponente `Link` für clientseitige Übergänge:

```svelte
<script lang="ts">
  import Link from "@nexy/Link.svelte";
</script>

<Link href="/about" activeClass="active">About</Link>
```

Für die programmatische Navigation verwenden Sie das `router`-Objekt von `@nexy/client`:

```ts
import { router } from "@nexy/client";

router.push("/dashboard");
```

### URL-Zugriff

Alle Standortdaten werden als Speicher bereitgestellt:

- `$pathname`: aktueller Pfad
- `$params`: dynamische Segmente
- `$searchParams`: Abfragezeichenfolge
- `$location`: vollständiges Standortobjekt

## Nächste Schritte

- [Ansichten](../README.md): Vergleichen Sie die Formate, die eine Seite verwenden kann
- [Frontend](../../guides/frontend.md): Vite und der Client-Build