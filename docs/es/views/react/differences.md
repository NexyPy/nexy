# React

Nexy renderiza React 19 componentes en el servidor, luego React los hidrata en el navegador. Las páginas, diseños, islas y acciones son las mismas en todos los marcos: esta página cubre la configuración y luego las partes que difieren de los [contratos compartidos](../frontend/pages.md).

<!-- router:fbr,custom -->
| Modo | `nexyconfig.py` | Las páginas son | React es |
|---|---|---|---|
| Servidor (predeterminado) | `useCSR = False` | `.nexy` archivos | [islas](../../rendering/islands.md) dentro de esas páginas |
| Cliente | `useCSR = True` | `.tsx` archivos | toda la página, con [diseños](../frontend/layouts.md) y un enrutador cliente |
<!-- /router -->

<!-- router:modular -->
Con el enrutador modular, los React componentes son [islas](../../rendering/islands.md) dentro de las `.nexy` vistas que devuelve un controlador: no hay ningún archivo de página ni enrutador cliente.
<!-- /router -->

## iniciar un proyecto

<!-- router:fbr,custom -->
```bash
nx new my-app --template web-fbr-react
```
<!-- /router -->

<!-- router:modular -->
```bash
nx new my-app --template web-modular-react
```
<!-- /router -->

La plantilla es un proyecto en modo servidor con React islas. Ejecute `nx new my-app` sin una plantilla para responder a las indicaciones: el enrutador, el tipo de proyecto, si se utilizará el enrutamiento del lado del cliente y luego el marco.

## Habilitar React en un proyecto existente

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

`nx new` escribe este archivo; Nexy escribe `__nexy__/vite.ts` por sí mismo, así que no lo edites.

| Paquete | La versión `nx new` escribe |
|---|---|
| `react`, `react-dom` | `^19.2.5` |
| `@vitejs/plugin-react` | `^5.2.0` |
| `@types/react`, `@types/react-dom` | dependencias de desarrollo |

## Reglas

- **Un marco por proyecto.** `useFF` toma exactamente un marco; `useFF = [react(), vue()]` detiene el servidor al inicio.
<!-- router:fbr,custom -->
- **Las páginas son `.tsx`.** React posee `.tsx` y `.jsx` para los componentes, pero solo un archivo `.tsx` bajo `src/routes/` se convierte en una página.
- **Los componentes se encuentran fuera de `src/routes/`**, generalmente en `src/components/`, por lo que no son páginas.
- **Un proyecto en modo servidor no tiene `.tsx` página**, y un proyecto en modo cliente no tiene `.nexy` página: Nexy se niega a iniciar y nombra el archivo. Ver [modos](../../routing/fbr/modes.md).
<!-- /router -->
<!-- router:modular -->
- **Los componentes viven en `src/components/`** y una vista los importa como islas.
<!-- /router -->

<!-- router:fbr,custom -->
## paginas

En modo cliente (`useCSR = True`), una página es un archivo `.tsx`.

### Componente de página

Una página es la exportación predeterminada del archivo. Si no existe una exportación predeterminada, Nexy elige la primera exportación nombrada.

```tsx filename="src/rutas/index.tsx"
export default function Home() {
  return <h1>Hello</h1>;
}
```

### Segmentos dinámicos

Los parámetros de URL están disponibles a través del enlace `useParams`:

```tsx filename="src/rutas/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

## Diseños

### Implementación

El diseño raíz define el shell del documento. Los diseños anidados envuelven el contenido debajo de ellos.

```tsx filename="src/rutas/layout.tsx"
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
```
<!-- /router -->

## Islas

En modo servidor, un componente React importado a un archivo `.nexy` es una isla.

### Importando

Importe componentes en la portada del archivo `.nexy`:

<!-- router:fbr,custom -->
```nexy filename="src/rutas/index.nexy"
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

### Directivas de hidratación

Utilice el accesorio `directive` para controlar cuándo se hidrata la isla:

- `client:load` (predeterminado): inmediatamente
- `client:idle`: cuando el navegador está inactivo
- `client:visible`: cuando se desplaza a la vista
- `client:media`: cuando la consulta de medios coincide

## Acciones y navegación

### Llamar a acciones

Utilice el gancho `useAction` para administrar el estado de una llamada a la acción:

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const { run, pending, error, data } = useAction(add_todo);
// ...
<button onClick={() => run({ title: "New Task" })}>Add</button>
```

### Navegación

Utilice el componente `Link` para transiciones del lado del cliente:

```tsx
import { Link } from "@nexy/client";

<Link href="/about">About</Link>
```

Para navegación programática, use el gancho `useRouter`:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### acceso URL

- `usePathname()`: ruta actual
- `useParams()`: segmentos dinámicos
- `useSearchParams()`: cadena de consulta
- `useLocation()`: objeto de ubicación completa

## Próximos pasos

- [Vistas](../README.md): compara los formatos que puede usar una página
- [Frontend](../../guides/frontend.md): Vite y la compilación del cliente
