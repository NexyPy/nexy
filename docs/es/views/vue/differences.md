# Vue

Nexy renderiza Vue 3 componentes de un solo archivo en el servidor, luego Vue los toma en el navegador. Las páginas, diseños, islas y acciones son las mismas en todos los marcos: esta página cubre la configuración y luego las partes que difieren de los [contratos compartidos](../frontend/pages.md).

| Modo | `nexyconfig.py` | Las páginas son | Vue es |
|---|---|---|---|
| Servidor (predeterminado) | `useCSR = False` | `.nexy` archivos | [islas](../../rendering/islands.md) dentro de esas páginas |
| El cliente | `useCSR = True` | `.vue` archiva | la página completa, con [diseños](../frontend/layouts.md) y un enrutador cliente |

## iniciar un proyecto

```bash
nx new my-app --template web-fbr-vue
```

La plantilla es un proyecto en modo servidor con Vue islas. Ejecute `nx new my-app` sin una plantilla para responder a las indicaciones: el enrutador, el tipo de proyecto, si se utilizará el enrutamiento del lado del cliente y luego el marco.

## Habilitar Vue en un proyecto existente

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

`nx new` escribe este archivo; Nexy escribe `__nexy__/vite.ts` por sí mismo, así que no lo edites.

| Paquete | Versión `nx new` escribe |
|---|---|
| `vue` | `^3.5.33` |
| `@vitejs/plugin-vue` | `^6.0.0` |

## Reglas

- **Un marco por proyecto.** `useFF` toma exactamente un marco; `useFF = [vue(), react()]` detiene el servidor al inicio.
- **Un componente por archivo.** Un archivo `.vue` exporta su componente de forma predeterminada; el nombre con el que lo importa es solo la etiqueta que escribe.
- **Los componentes se encuentran fuera de `src/routes/`**, generalmente en `src/components/`, por lo que no son páginas.
- **Un proyecto en modo servidor no tiene `.vue` página**, y un proyecto en modo cliente no tiene `.nexy` página: Nexy se niega a iniciar y nombra el archivo. Ver [modos](../../routing/fbr/modes.md).

## paginas

En modo cliente (`useCSR = True`), una página es un archivo `.vue`.

### Componente de página

La página es el componente definido por el bloque `<script setup>`.

```vue filename="src/rutas/index.vue"
<template>
  <h1>Hello</h1>
</template>
```

### Segmentos dinámicos

Los parámetros de URL llegan a la página como accesorios. Puedes declararlos usando `defineProps`:

```vue filename="src/rutas/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

Alternativamente, use el gancho `useParams` de `@nexy/client` en cualquier componente.

## Diseños

### Implementación

El diseño raíz define el shell del documento. Los diseños anidados envuelven el contenido en su espacio predeterminado.

```vue filename="src/rutas/layout.vue"
<template>
  <html>
    <body>
      <header>My app</header>
      <main><slot /></main>
    </body>
  </html>
</template>
```

## Islas

En modo servidor, un componente Vue importado a un archivo `.nexy` es una isla.

### Importando

Importe componentes en la portada del archivo `.nexy`:

```nexy filename="src/rutas/index.nexy"
---
from "@/components/Counter.vue" import Counter
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

### Llamar a acciones

Utilice el gancho `useAction` para administrar el estado de una llamada a la acción. En Vue, el estado devuelto (`pending`, `data`, `error`) son referencias calculadas.

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

### Navegación

Utilice el componente `Link` para transiciones del lado del cliente:

```vue
<template>
  <Link href="/about" active-class="active">About</Link>
</template>
```

Para navegación programática, use el gancho `useRouter`:

```ts
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### acceso URL

Todos los ganchos de ubicación devuelven referencias calculadas:

- `usePathname()`: ruta actual
- `useParams()`: segmentos dinámicos
- `useSearchParams()`: cadena de consulta
- `useLocation()`: objeto de ubicación completa

## Próximos pasos

- [Vistas](../README.md): compara los formatos que puede usar una página
- [Frontend](../../guides/frontend.md): Vite y la compilación del cliente
