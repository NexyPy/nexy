# Esbelto

Nexy renderiza los componentes de Svelte 5 en el servidor, luego Svelte los toma en el navegador. páginas,
Los diseños, islas y acciones son los mismos en todos los marcos: esta página cubre la configuración, luego las partes.
que difieren de los [contratos compartidos](../frontend/pages.md).

| Modo | `nexyconfig.py` | Las páginas son | Esbeltas son |
|---|---|---|---|
| Servidor (predeterminado) | `useCSR = False` | `.nexy` archivos | [islas](../../rendering/islands.md) dentro de esas páginas |
| Cliente | `useCSR = True` | `.svelte` archivos | toda la página, con [diseños](../frontend/layouts.md) y un enrutador cliente |

## Iniciar un proyecto

```bash
nx new my-app --template web-fbr-svelte
```

La plantilla es un proyecto en modo servidor con islas Svelte. Ejecute `nx new my-app` sin una plantilla para
En su lugar, responda las indicaciones: el enrutador, el tipo de proyecto, si desea utilizar el enrutamiento del lado del cliente y luego
el marco.

## Habilitar Svelte en un proyecto existente

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

`nx new` escribe este archivo; Nexy escribe `__nexy__/vite.ts` por sí mismo, así que no lo edites.

| Paquete | Versión `nx new` escribe |
|---|---|
| `svelte` | `^5.20.2` |
| `@sveltejs/vite-plugin-svelte` | `^5.0.0` |

## Reglas

- **Svelte 5.** Los componentes usan runas: `$props()`, `$state()` y fragmentos para niños.
- **Un marco por proyecto.** `useFF` toma exactamente un marco; `useFF = [svelte(), vue()]`
  detiene el servidor al inicio.
- **Un componente por archivo.** El nombre con el que importas un archivo `.svelte` es solo la etiqueta que escribes.
- **Los componentes viven fuera de `src/routes/`**, generalmente en `src/components/`, por lo que no son páginas.
- **Un proyecto en modo servidor no tiene `.svelte` página**, y un proyecto en modo cliente no tiene `.nexy` página: Nexy
  se niega a iniciar y nombra el archivo. Ver [modos](../../routing/fbr/modes.md).

## Páginas

En modo cliente (`useCSR = True`), una página es un archivo `.svelte`.

### Componente de página

La página es el componente definido por el bloque de script del archivo `.svelte`.

```svelte filename="src/rutas/index.svelte"
<script lang="ts">
</script>

<h1>Hello</h1>
```

### Segmentos dinámicos

Los parámetros de URL llegan a la página como accesorios a través de la runa `$props()`:

```svelte filename="src/routes/blog/[slug].esbelto"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

Alternativamente, use la tienda `$params` de `@nexy/client` en cualquier componente.

## Diseños

### Implementación

El diseño raíz define el shell del documento. Los diseños anidados envuelven el contenido usando el `children`
fragmento.

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

## Islas

En modo servidor, un componente Svelte importado a un archivo `.nexy` es una isla.

### Importando

Importe componentes en la portada del archivo `.nexy`:

```nexy filename="src/rutas/index.nexy"
---
from "@/components/Counter.svelte" import Counter
---
<Counter start=3 />
```

### Directivas de hidratación

Utilice el accesorio `directive` para controlar cuándo se hidrata la isla:

- `client:load` (predeterminado): inmediatamente
- `client:idle`: cuando el navegador está inactivo
- `client:visible`: cuando se desplaza a la vista
- `client:media`: cuando la consulta de medios coincide

## Acciones y navegación

### Llamando acciones

Utilice el gancho `useAction` para administrar el estado de una llamada a la acción. En Svelte, esto devuelve una tienda (leer
con `$`).

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

### Navegación

Utilice el componente `Link` para transiciones del lado del cliente:

```svelte
<script lang="ts">
  import Link from "@nexy/Link.svelte";
</script>

<Link href="/about" activeClass="active">About</Link>
```

Para navegación programática, utilice el objeto `router` de `@nexy/client`:

```ts
import { router } from "@nexy/client";

router.push("/dashboard");
```

### Acceso URL

Todos los datos de ubicación se proporcionan como tiendas:

- `$pathname`: ruta actual
- `$params`: segmentos dinámicos
- `$searchParams`: cadena de consulta
- `$location`: objeto de ubicación completa

## Próximos pasos

- [Vistas](../README.md): compara los formatos que puede usar una página
- [Frontend](../../guides/frontend.md): Vite y la compilación del cliente